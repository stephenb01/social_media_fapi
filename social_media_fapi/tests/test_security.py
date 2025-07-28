import pytest
from social_media_fapi import security

@pytest.mark.anyio
async def test_get_user(registered_user: dict):
    user = await security.get_user(registered_user["email"])

    assert user.email == registered_user["email"]

    
@pytest.mark.anyio
async def test_get_user_not_found():
    user = await security.get_user('test1@example.com')

    assert user is None

    
