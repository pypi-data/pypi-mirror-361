from .request_pb2 import Request, VerifyOrganization, InitiatePayment, VerifyPayment, RemoveUser
from .connectionPool import get_connection_pool

class Organization:
    def __init__(
        self,
        email: str,
        name: str,
        totp_uri: str,
        phone: str,
        address: str,
        tax_id: str,
        vat_id: str,
        reg_id: str,
        org_id: bytes,
    ):
        self.email = email
        self.name = name
        self.totp_uri = totp_uri
        self.phone = phone
        self.address = address
        self.tax_id = tax_id
        self.vat_id = vat_id
        self.reg_id = reg_id
        self.org_id = org_id

    async def remove(self):
        pool = get_connection_pool()
        remove_user = RemoveUser(email=self.email, organization=self.name)
        req = Request(removeUser=remove_user)

        resp = await pool.send_and_receive(req)

        if resp.removeUser.status != 0:
            raise Exception(resp.removeUser.message or "Failed to remove user")
