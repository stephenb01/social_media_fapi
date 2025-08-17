import logging
from  typing import Annotated 
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from social_media_fapi.database import database, user_table
from social_media_fapi.models.user import UserIn
from social_media_fapi.security import get_password_hash, get_user, authenticate_user, create_access_token

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


@router.post("/token")
async def login(user: UserIn):
    user = await authenticate_user(user.email, user.password)
    # Add the following to allow the API to work with the OAuth2PasswordRequestForm
    # async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    #     user = await authenticate_user(form_data.username, form_data.password)
    access_token = create_access_token(user.email)
    return {"access_token": access_token, "token_type": "bearer"}