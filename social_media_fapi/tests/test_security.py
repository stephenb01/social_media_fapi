import pytest
from jose import jwt

from social_media_fapi import security
from social_media_fapi.config import config


def test_access_token_expire_minutes():
    assert security.access_token_expire_minutes() == 30


def test_create_access_token():
    token = security.create_access_token("123")
    assert {"sub": "123"}.items() <= jwt.decode(
        token, key=config.SECRET_KEY, algorithms=[config.ALGORITHM]
    ).items()


def test_password_hashes():
    password = "password"
    assert security.verify_password(password, security.get_password_hash(password))


@pytest.mark.anyio
async def test_get_user(registered_user: dict):
    user = await security.get_user(registered_user["email"])

    assert user.email == registered_user["email"]


@pytest.mark.anyio
async def test_get_user_not_found():
    user = await security.get_user("test1@example.com")

    assert user is None


@pytest.mark.anyio
async def test_authenticate_user(registered_user: dict):
    user = await security.authenticate_user(
        registered_user["email"], registered_user["password"] 
    )
    assert user.email == registered_user["email"]

@pytest.mark.anyio
async def test_authenticate_user_not_found():
    # The with block ensures the exception is caught in pytest.raises
    with pytest.raises(security.HTTPException):
        await security.authenticate_user( "test@ex.com", "1234" )

@pytest.mark.anyio
async def test_authenticate_user_wrong_password(registered_user: dict):
    # The with block ensures the exception is caught in pytest.raises
    with pytest.raises(security.HTTPException):
        await security.authenticate_user( registered_user["email"], "wrong password" )