from typing import List, Tuple, Union, Optional
import re
from . import request_pb2 as request
from .connectionPool import get_connection_pool
from .tableUser import TableUser
from .user import User
from .organization import Organization
from .auth import get_user_or_org
from .cache import global_cache

class ManageUser:
    @staticmethod
    def verify_email(email: str) -> bool:
        email_regex = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
        return re.match(email_regex, email) is not None

    @staticmethod
    def cleaned_email_string(email_string: str) -> List[str]:
        return email_string.strip().split(",")

    @staticmethod
    async def invite_users(email_string: str) -> Tuple[List[str], List[str], List[str]]:
        user_emails, statuses, messages = [], [], []
        emails = ManageUser.cleaned_email_string(email_string)

        for email in emails:
            if not ManageUser.verify_email(email):
                user_emails.append(email)
                statuses.append("Failed")
                messages.append("Invalid Email")
                continue

            invite_user = request.InviteUser(email=email)
            req = request.Request(inviteUser=invite_user)
            pool = get_connection_pool()
            resp = await pool.send_and_receive(req)

            user_emails.append(email)
            if not resp or resp.inviteUser.status != 0:
                statuses.append("Failed")
                messages.append(getattr(resp.inviteUser, 'message', "Failed to Invite"))
            else:
                statuses.append("Success")
                messages.append(getattr(resp.inviteUser, 'message', "Invite Success"))

        return (user_emails, statuses, messages)

    @staticmethod
    async def update_user(email_of_user: str, roles: List[str], teams: List[str]) -> bool:
        req_data = request.SetRolesTeamsToUser(
            emailOfUser=email_of_user,
            name_of_roles=roles or None,
            name_of_teams=teams or None
        )
        req = request.Request(setRolesTeamsToUser=req_data)
        pool = get_connection_pool()
        resp = await pool.send_and_receive(req)

        if not resp or resp.setRolesTeamsToUser.status != 0:
            raise Exception(getattr(resp.setRolesTeamsToUser, 'message', f"Error while updating {email_of_user}"))
        return True

    @staticmethod
    async def get_profile_pic() -> bytes:
        return b""  # TODO: Implement this

    @staticmethod
    async def set_profile_pic(profile_pic: bytes, profile_pic_name: str):
        pass  # TODO: Implement this

    @staticmethod
    async def list_users() -> List[TableUser]:
        pool = get_connection_pool()
        users_list = []
        page_token = None

        while True:
            req = request.Request(
                listUsers=request.ListUsers(page_token_list_user=page_token, page_size=20 if not page_token else None)
            )
            resp = await pool.send_and_receive(req)
            result = resp.listUsers

            if not result or result.status != 0:
                raise Exception(f"Failed to list users ({result.status})")

            for user in result.users:
                if user.email != pool.get_email():
                    users_list.append(TableUser(user.email, user.roles_of_user, user.teams_of_user))

            page_token = result.page_token_list_user if result.page_token_list_user else None
            if not page_token:
                break

        return users_list

    async def remove_users(self, emails: List[str]):
        pass  # TODO: Implement this

    @staticmethod
    async def change_password_with_old_password(old_password: str, new_password: str):
        req = request.Request(
            changePassword=request.ChangePassword(email="not@used.in", oldPassword=old_password, newPassword=new_password)
        )
        pool = get_connection_pool()
        resp = await pool.send_and_receive(req)

        if not resp or resp.changePassword.status != 0:
            raise Exception(getattr(resp.changePassword, 'message', "Failed to change password (old password)"))

    @staticmethod
    async def change_password_with_token(email: str, token: bytes, new_password: str):
        req = request.Request(
            changePassword=request.ChangePassword(email=email, token=token, newPassword=new_password)
        )
        pool = get_connection_pool()
        resp = await pool.send_and_receive(req)

        if not resp or resp.changePassword.status != 0:
            raise Exception(getattr(resp.changePassword, 'message', "Failed to change password (token)"))
        
        pool.set_email(resp.changePassword.email)

    @staticmethod
    async def reset_password(email: str):
        req = request.Request(passwordReset=request.PasswordReset(email=email))
        pool = get_connection_pool()
        resp = await pool.send_and_receive(req)

        if not resp or resp.passwordReset.status != 0:
            raise Exception(getattr(resp.passwordReset, 'message', "Failed to reset password"))

    @staticmethod
    async def reset_totp() -> str:
        req = request.Request(resetTOTP=request.ResetTOTP())
        pool = get_connection_pool()
        resp = await pool.send_and_receive(req)

        if not resp or resp.resetTOTP.status != 0 or not resp.resetTOTP.totpUri:
            raise Exception("Failed to reset TOTP or retrieve TOTP URI")

        return resp.resetTOTP.totpUri

    @staticmethod
    async def get_user_details(email: Optional[str] = None) -> Union[User, Organization]:
        pool = get_connection_pool()
        email_to_get = email or pool.get_email()
        return await get_user_or_org(email_to_get)

    @staticmethod
    async def set_user_details(first_name: str, last_name: str, phone: str, address: str, location: str):
        user_info = await ManageUser.get_user_details()
        if isinstance(user_info, User):
            profile = request.UserProfile(
                firstname=first_name,
                lastname=last_name,
                phone=phone,
                address=address,
                location=location
            )
            pool = get_connection_pool()
            meta = request.UserProfileMeta(userObj=profile)
            req = request.Request(setUser=request.SetUser(email= pool.get_email(), usermeta=meta))
            resp = await get_connection_pool().send_and_receive(req)
            if not resp or resp.setUser.status != 0:
                raise Exception("Failed to set user details")

            email_key = pool.get_email() + "UserDetails"
            global_cache.delete(email_key, None)
            await ManageUser.get_user_details()
        else:
            raise Exception("User details can only be set for User type, not Organization")

    @staticmethod
    async def set_organization_details(phone: str, address: str, tax_id: str, vat_id: str, registration_number: str):
        org_info = await ManageUser.get_user_details()
        if isinstance(org_info, Organization):
            profile = request.OrganizationProfile(
                phone=phone,
                address=address,
                tax_id=tax_id,
                vat_id=vat_id,
                registration_id=registration_number
            )
            pool = get_connection_pool()
            meta = request.UserProfileMeta(organizationObj=profile)
            req = request.Request(setUser=request.SetUser(email=pool.get_email(), usermeta=meta))
            resp = await pool.send_and_receive(req)
            if not resp or resp.setUser.status != 0:
                raise Exception("Failed to set organization details")

            email_key = pool.get_email() + "UserDetails"
            # global_cache.delete(email_key, None)
            await ManageUser.get_user_details()
        else:
            raise Exception("Organization details can only be set for Organization type, not User")

