import logging

from fastapi import APIRouter, HTTPException, status

from social_media_fapi.database import database, user_table
from social_media_fapi.models.user import UserIn
from social_media_fapi.security import get_password_hash, get_user

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("/register", status_code=201)
async def register(user: UserIn):
    if await get_user(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with that email already exists",
        )

    hashed_password = get_password_hash(user.password)
    query = user_table.insert().values(email=user.email, password=hashed_password)

    logger.debug(query)

    await database.execute(query)
    return {"detail": "User created."}
