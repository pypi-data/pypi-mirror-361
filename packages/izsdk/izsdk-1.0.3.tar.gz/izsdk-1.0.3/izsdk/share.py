from typing import List, Dict, Optional
from dataclasses import dataclass

from . import request_pb2 as request, response_pb2 as response
from .connectionPool import get_connection_pool


@dataclass
class ActionEntry:
    subject: str
    subject_type: str  # "USER" | "TEAM"
    action: str        # "ALLOW" | "DENY"
    op_ids: List[int]


@dataclass
class Entry:
    subject: str
    subject_type: str
    action: str
    ops: List[str]

    def get_subject(self) -> str:
        return self.subject

    def get_subject_type(self) -> str:
        return self.subject_type

    def get_action(self) -> str:
        return self.action

    def get_ops(self) -> List[str]:
        return self.ops


class Share:
    def __init__(self, parent_path: str, owner: str):
        self.parent_path = parent_path
        self.owner = owner
        self.entries: List[request.ActionEntry] = []

    def get_read_op_ids(self) -> List[int]:
        return [17, 21, 29, 25]

    def get_write_op_ids(self) -> List[int]:
        return [17, 21, 29, 25, 22, 23, 24, 30]

    def get_copy_op_ids(self) -> List[int]:
        return [17, 52, 53, 27, 25, 27]

    def get_op_ids_from_string(self, i: int) -> List[int]:
        if i == 1:
            return self.get_read_op_ids()
        elif i == 2:
            return self.get_write_op_ids()
        elif i == 3:
            return self.get_copy_op_ids()
        elif i == 4:
            return [7]
        else:
            return []

    def get_operation_from_id(self, ids: List[int]) -> List[str]:
        operations = []
        id_set = set(ids)

        if all(id in id_set for id in self.get_read_op_ids()):
            operations.append("Read")
        if all(id in id_set for id in self.get_write_op_ids()):
            operations.append("Write")
        if all(id in id_set for id in self.get_copy_op_ids()):
            operations.append("Copy")

        return operations

    async def add_entry(self, entry: ActionEntry) -> None:
        opids = entry.op_ids
        arr = []

        for i in opids:
            arr.extend(self.get_op_ids_from_string(i))

        arr.extend(self.get_op_ids_from_string(4))

        unique_op_ids = list(set(arr))

        action = (
            request.Action.ALLOW
            if entry.action == "ALLOW"
            else request.Action.DENY
        )

        subject_type = (
            request.SubjectType.USER
            if entry.subject_type == "USER"
            else request.SubjectType.TEAM
        )

        acl_entry = request.ActionEntry(
            action=action,
            subject=entry.subject,
            subject_type=subject_type,
            op_ids=unique_op_ids,
        )

        self.entries.append(acl_entry)

    async def list_team_of_users(self) -> List[str]:
        pool = get_connection_pool()

        req = request.Request(
            getRolesAndTeamsOfUser=request.GetRolesAndTeamsOfUser(
                emailOfUser=self.owner
            )
        )

        resp = await pool.send_and_receive(req)

        if not resp.HasField("getRolesAndTeamsOfUser"):
            raise RuntimeError("Failed to get teams of user: field missing")

        result = resp.getRolesAndTeamsOfUser

        if result.status != response.Status.SUCCESS:
            raise RuntimeError("Failed to get teams of user")

        return list(result.nameOfTeams)

    async def list_users(self) -> List[Dict[str, List[str]]]:
        pool = get_connection_pool()
        users_list = []
        page_token = None

        while True:
            req = request.Request(
                listUsers=request.ListUsers(
                    page_token_list_user=page_token,
                    page_size=20 if page_token is None else None,
                )
            )

            resp = await pool.send_and_receive(req)

            if not resp.HasField("listUsers") or resp.listUsers.status != response.Status.SUCCESS:
                raise RuntimeError("Failed to list users")

            result = resp.listUsers

            for user in result.users:
                users_list.append({
                    "email": user.email,
                    "teamsOfUser": list(user.teams_of_user),
                    "rolesOfUser": list(user.roles_of_user),
                })

            page_token = result.page_token_list_user if result.page_token_list_user else None

            if not page_token or len(page_token) == 0:
                break

        return users_list

    async def share(self) -> None:
        pool = get_connection_pool()

        share_req = request.Request(
            share=request.Share(
                acl=request.ACL(
                    object_path=self.parent_path,
                    owner_email=self.owner,
                    actions=self.entries,
                )
            )
        )

        resp = await pool.send_and_receive(share_req)

        if not resp.HasField("share") or resp.share.status != response.Status.SUCCESS:
            raise RuntimeError("Failed to share object")

        self.entries.clear()

    async def update_share(self) -> None:
        pool = get_connection_pool()

        req = request.Request(
            updateShare=request.UpdateShare(
                acl=request.ACL(
                    object_path=self.parent_path,
                    owner_email=self.owner,
                    actions=self.entries,
                )
            )
        )

        resp = await pool.send_and_receive(req)

        if not resp.HasField("updateShare") or resp.updateShare.status != response.Status.SUCCESS:
            raise RuntimeError("Failed to update share")

        self.entries.clear()

    async def list_shares(self) -> List[Entry]:
        pool = get_connection_pool()

        req = request.Request(
            listShares=request.ListShares(object_path=self.parent_path)
        )

        resp = await pool.send_and_receive(req)

        # if not resp.HasField("listShares") or resp.listShares.status != response.Status.SUCCESS:
        #     raise RuntimeError("Failed to list shares")

        acl_bytes = resp.listShares.acl

        if not isinstance(acl_bytes, bytes):
            return []

        decoded_acl = request.ACL()
        decoded_acl.ParseFromString(acl_bytes)

        entries = []

        for action in decoded_acl.actions:
            entry = Entry(
                action=(
                    "ALLOW" if action.action == request.Action.ALLOW
                    else "DENY" if action.action == request.Action.DENY
                    else "UNKNOWN"
                ),
                ops=self.get_operation_from_id(list(action.op_ids)),
                subject_type=(
                    "USER" if action.subject_type == request.SubjectType.USER
                    else "TEAM" if action.subject_type == request.SubjectType.TEAM
                    else "UNKNOWN"
                ),
                subject=action.subject,
            )
            entries.append(entry)

        return entries

    async def unshare(self) -> None:
        pool = get_connection_pool()

        req = request.Request(
            unshare=request.Unshare(object_path=self.parent_path)
        )

        resp = await pool.send_and_receive(req)

        if not resp.HasField("unshare") or resp.unshare.status != response.Status.SUCCESS:
            raise RuntimeError("Failed to unshare object")
