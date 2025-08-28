import logging

# from  typing import Annotated
from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, status

from social_media_fapi import tasks

# from fastapi.security import OAuth2PasswordRequestForm
from social_media_fapi.database import database, user_table
from social_media_fapi.models.user import UserIn
from social_media_fapi.security import (
    authenticate_user,
    create_access_token,
    create_confirmation_token,
    get_password_hash,
    get_subject_for_token_type,
    get_user,
)

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("/register", status_code=201)
async def register(user: UserIn, background_tasks: BackgroundTasks, request: Request):
    if await get_user(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with that email already exists",
        )

    hashed_password = get_password_hash(user.password)
    query = user_table.insert().values(email=user.email, password=hashed_password)

    logger.debug(query)

    await database.execute(query)
    # Adding a background task here allows the email to be sent later because it can be really slow.
    # The routine can then finish and move onto the next task.
    # There are others, such as RQ worker and celery when you have a computational expensive process as they have a separate process/server.
    background_tasks.add_task(
        tasks.send_user_registration_email,
        user.email,
        confirmation_url=request.url_for(
            "confirm_email", token=create_confirmation_token(user.email)
        ),
    )
    return {
        "detail": "User created. Please confirm your email",
        "confirmation_url": request.url_for(
            "confirm_email", token=create_confirmation_token(user.email)
        ),
    }


@router.post("/token")
async def login(user: UserIn):
    user = await authenticate_user(user.email, user.password)
    # Add the following to allow the API to work with the OAuth2PasswordRequestForm
    # async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    #     user = await authenticate_user(form_data.username, form_data.password)
    access_token = create_access_token(user.email)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/confirm/{token}")
async def confirm_email(token: str):
    email = get_subject_for_token_type(token, "confirmation")
    query = (
        user_table.update().where(user_table.c.email == email).values(confirmed=True)
    )

    logger.debug(query)

    await database.execute(query)
    return {"detail": "User confirmed"}
