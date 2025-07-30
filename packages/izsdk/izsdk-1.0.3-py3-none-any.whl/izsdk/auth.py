import os
from typing import Union

from .request_pb2 import (
    Request,
    SignIn,
    AddPin,
    GetUser
)

from .connectionPool import check_and_throw, get_connection_pool
from .user import User
from .organization import Organization
from .iz_uuid import generate_uuid
import random


async def sign_in_with_password(email: str, password: str, totp: str) -> Union[User, Organization]:
    sign_in = SignIn(email=email, password=password, totp=totp)
    sign_in_req = Request(signIn=sign_in)

    pool = get_connection_pool()
    sign_in_resp = await pool.send_and_receive(sign_in_req)

    if sign_in_resp.signIn.status != 0:
        raise Exception(sign_in_resp.signIn.message or "Sign-in failed")

    if not sign_in_resp.signIn.email:
        raise Exception("No email in response for SignIn with password")
    
    pool.set_email(sign_in_resp.signIn.email)
    pin = str(random.randint(100000,999999))
    await send_add_pin(email,pin)

    return await get_user_or_org(sign_in_resp.signIn.email)


async def sign_in_with_token(token: bytes, pin: str) -> Union[User, Organization]:
    req = Request(
        signIn=SignIn(email="", pin=pin, data=token)
    )

    pool = get_connection_pool()
    res = await pool.send_and_receive(req)
    if res.signIn.status != 0:
        raise Exception(res.signIn.message or "Sign-in failed")

    if not res.signIn.email:
        raise Exception("No email in response for SignIn with password")

    check_and_throw(res)
    pool.set_pin(pin,token)
    pool.set_email(res.signIn.email)

    return await get_user_or_org(res.signIn.email)


async def send_add_pin(email: str, pin: str) -> bytes:
    add_pin = AddPin(email=email, pin=pin)
    req = Request(addPin=add_pin)

    pool = get_connection_pool()
    res = await pool.send_and_receive(req)

    if res.addPin.status != 0 or not res.addPin.data:
        raise Exception(res.addPin.message or "Failed to add pin")
    
    pool.set_pin(pin,res.addPin.data)
    return res.addPin.data


async def get_user_or_org(email: str) -> Union[User, Organization]:
    get_user = GetUser(email=email)
    req = Request(getUser=get_user)

    pool = get_connection_pool()
    res = await pool.send_and_receive(req)

    user = res.getUser.user
    if not user:
        raise Exception("No user data in response")

    if user.HasField("userObj"):
        u = user.userObj
        return User(
            email=email,
            totp_uri="",
            first_name=u.firstname or "",
            last_name=u.lastname or "",
            organization=u.organization or "",
            phone=u.phone or "",
            address=u.address or "",
            plan=u.plan or 0,
            location=u.location or ""
        )

    if user.HasField("organizationObj"):
        o = user.organizationObj
        return Organization(
            email=email,
            name=o.name or "",
            totp_uri="",
            phone=o.phone or "",
            address=o.address or "",
            tax_id=o.tax_id or "",
            vat_id=o.vat_id or "",
            reg_id=o.registration_id or "",
            org_id=o.organization_id or b""
        )

    raise Exception("Unrecognized user structure")


async def load_token_from_file(file_path: str = None) -> bytes:
    resolved_path = file_path or os.path.join(os.path.expanduser("~"), ".iz-token")
    if not os.path.exists(resolved_path):
        raise FileNotFoundError(f"Token file not found: {resolved_path}")

    return await _read_file_async(resolved_path)


async def _read_file_async(path: str) -> bytes:
    # In actual async environments, use aiofiles or equivalent
    with open(path, "rb") as f:
        return f.read()


def create_token_sign_in_request(pin: str, token: bytes) -> Request:
    return Request(
        id=generate_uuid(),
        signIn=SignIn(
            pin=pin,
            data=token
        )
    )
