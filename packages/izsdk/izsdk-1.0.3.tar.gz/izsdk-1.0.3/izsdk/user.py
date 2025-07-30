from typing import Optional
from .request_pb2 import Request, VerifyUser, InitiatePayment, VerifyPayment, RemoveUser
from .connectionPool import get_connection_pool


class User:
    def __init__(
        self,
        email: str,
        totp_uri: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        organization: Optional[str] = None,
        phone: Optional[str] = None,
        address: Optional[str] = None,
        plan: Optional[int] = None,
        location: Optional[str] = None
    ):
        self.email = email
        self.totp_uri = totp_uri
        self.first_name = first_name
        self.last_name = last_name
        self.organization = organization
        self.phone = phone
        self.address = address
        self.plan = plan
        self.location = location

    async def remove(self):
        pool = get_connection_pool()

        req = Request(
            removeUser=RemoveUser(
                email=self.email,
                organization=self.organization or ""
            )
        )

        resp = await pool.send_and_receive(req)
        remove_resp = resp.removeUser

        if remove_resp.status != 0:
            raise Exception(remove_resp.message or "Failed to remove user")
