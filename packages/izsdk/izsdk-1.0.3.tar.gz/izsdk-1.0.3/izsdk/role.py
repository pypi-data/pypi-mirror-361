from typing import List, Dict
from . import request_pb2 as request
from .connectionPool import get_connection_pool

ROLE_PERMISSIONS: List[str] = [
    "RemoveUser", "PasswordReset", "InitiatePayment", "InviteUser",
    "GetChunk", "StartWrite", "PutChunk", "FinalizeWrite", "CreateFolder",
    "VerifyPayment", "GetSecret", "AddSecret", "DeleteSecret", "UpdateSecret",
    "ListSecrets", "QuickListSecrets", "ListSecretSubkeys", "UndeleteSecret", "DestroySecret",
    "AddRole", "RemoveRole", "UpdateRole", "ListRoles", "GetRole",
    "AddTeam", "RemoveTeam", "UpdateTeam", "ListTeams", "GetTeam",
    "MoveFile", "MoveFolder", "CopyFile", "CopyFolder", "RestoreVersion",
    "RemoveFile", "RemoveFolder", "UntrashFile", "UntrashFolder",
    "RenameFile", "RenameFolder", "List", "AuditLogMessage", "ResetVersion",
    "Share", "Unshare", "UpdateShare", "ListShares", "SetRolesTeamsToUser", "RestartPutChunk"
]

STRING_TO_NUMBER = {
    "RemoveUser": 2,
    "PasswordReset": 3,
    "InitiatePayment": 6,
    "InviteUser": 9,
    "GetChunk": 21,
    "StartWrite": 22,
    "PutChunk": 23,
    "FinalizeWrite": 24,
    "CreateFolder": 30,
    "VerifyPayment": 32,
    "GetSecret": 33,
    "AddSecret": 34,
    "DeleteSecret": 35,
    "UpdateSecret": 36,
    "ListSecrets": 37,
    "QuickListSecrets": 87,
    "ListSecretSubkeys": 38,
    "UndeleteSecret": 39,
    "DestroySecret": 40,
    "AddRole": 41,
    "RemoveRole": 42,
    "UpdateRole": 43,
    "ListRoles": 44,
    "GetRole": 81,
    "AddTeam": 46,
    "RemoveTeam": 47,
    "UpdateTeam": 48,
    "ListTeams": 45,
    "GetTeam": 80,
    "MoveFile": 50,
    "MoveFolder": 51,
    "CopyFile": 52,
    "CopyFolder": 53,
    "RestoreVersion": 82,
    "RemoveFile": 55,
    "RemoveFolder": 56,
    "UntrashFile": 57,
    "UntrashFolder": 58,
    "RenameFile": 62,
    "RenameFolder": 63,
    "List": 64,
    "AuditLogMessage": 65,
    "ResetVersion": 66,
    "Share": 73,
    "Unshare": 74,
    "UpdateShare": 75,
    "ListShares": 76,
    "SetRolesTeamsToUser": 83,
    "RestartPutChunk": 88,
}

NUMBER_TO_STRING = {v: k for k, v in STRING_TO_NUMBER.items()}

def get_type_of_op(op: str) -> int:
    if op in {
        "RemoveUser", "PasswordReset", "InitiatePayment", "InviteUser",
        "VerifyPayment", "AddRole", "RemoveRole", "UpdateRole",
        "ListRoles", "GetRole", "AddTeam", "RemoveTeam",
        "UpdateTeam", "ListTeams", "GetTeam", "SetRolesTeamsToUser"
    }:
        return 0
    if op in {
        "GetChunk", "StartWrite", "PutChunk", "FinalizeWrite", "CreateFolder",
        "MoveFile", "MoveFolder", "CopyFile", "CopyFolder", "RestoreVersion",
        "RemoveFile", "RemoveFolder", "UntrashFile", "UntrashFolder",
        "RenameFile", "RenameFolder", "List", "ResetVersion",
        "Share", "Unshare", "UpdateShare", "ListShares", "RestartPutChunk"
    }:
        return 1
    if op == "AuditLogMessage":
        return 2
    if op in {
        "GetSecret", "AddSecret", "DeleteSecret", "UpdateSecret",
        "ListSecrets", "QuickListSecrets", "ListSecretSubkeys",
        "UndeleteSecret", "DestroySecret"
    }:
        return 3
    return -1


class Role:
    def __init__(self, name: str, permissions: List[str]):
        self._name = name
        self._permissions = permissions

    def get_name(self) -> str:
        return self._name

    def get_permissions(self) -> List[str]:
        return self._permissions

    @staticmethod
    def get_permission(num: int) -> str:
        return NUMBER_TO_STRING.get(num, "")

    @staticmethod
    async def add_role(name: str, permissions: List[str]):
        op_codes = [STRING_TO_NUMBER[perm] for perm in permissions]
        add_role = request.AddRole(name=name, permissions=op_codes)
        req = request.Request(addRole=add_role)
        pool = get_connection_pool()
        resp = await pool.send_and_receive(req)
        if not resp.HasField("addRole") or resp.addRole.status != 0:
            raise Exception(resp.addRole.message or "Failed to add role")

    @staticmethod
    async def update_role(name: str, permissions: List[str]):
        op_codes = [STRING_TO_NUMBER[perm] for perm in permissions]
        update_role = request.UpdateRole(name=name, permissions=op_codes)
        req = request.Request(updateRole=update_role)
        pool = get_connection_pool()
        resp = await pool.send_and_receive(req)
        if not resp.HasField("updateRole") or resp.updateRole.status != 0:
            raise Exception(resp.updateRole.message or "Failed to update role")

    @staticmethod
    async def remove_role(name: str):
        remove_role = request.RemoveRole(name=name)
        req = request.Request(removeRole=remove_role)
        pool = get_connection_pool()
        resp = await pool.send_and_receive(req)
        if not resp.HasField("removeRole") or resp.removeRole.status != 0:
            raise Exception(resp.removeRole.message or "Failed to remove role")

    @staticmethod
    async def get_role(name: str) -> "Role":
        get_role = request.GetRole(name=name)
        req = request.Request(getRole=get_role)
        pool = get_connection_pool()
        resp = await pool.send_and_receive(req)

        if not resp.HasField("getRole") or resp.getRole.status != 0:
            raise Exception(resp.getRole.message or "Failed to get role")

        role_proto = request.Role()
        role_proto.ParseFromString(resp.getRole.role)
        perms = [NUMBER_TO_STRING.get(val, "") for val in role_proto.permissions]
        return Role(role_proto.name, perms)

    @staticmethod
    async def list_role_names() -> List[str]:
        list_roles = request.ListRoles()
        req = request.Request(listRoles=list_roles)
        pool = get_connection_pool()
        resp = await pool.send_and_receive(req)

        if not resp.HasField("listRoles") or resp.listRoles.status != 0:
            raise Exception(resp.listRoles.message or "List roles failed")
        return list(resp.listRoles.roles)

    @staticmethod
    async def list_roles() -> List["Role"]:
        role_names = await Role.list_role_names()
        roles = []
        for name in role_names:
            roles.append(await Role.get_role(name))
        return roles


def list_permissions() -> List[str]:
    return ROLE_PERMISSIONS
