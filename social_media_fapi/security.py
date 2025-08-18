import datetime
import logging
from typing import Annotated, Literal

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, jwt
from passlib.context import CryptContext

from social_media_fapi.config import config
from social_media_fapi.database import database, user_table

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# This is used to extract the token from the request header.
pwd_context = CryptContext(schemes=["bcrypt"])

def create_credentials_exception(detail: str) ->HTTPException:
    return  HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail=detail,
    headers={"WWW-Authenticate": "Bearer"},
)


def access_token_expire_minutes() -> int:
    return 30

def confirm_token_expire_minutes() -> int:
    return 1440 # 24 hours


def create_access_token(email: str):
    logger.debug("Creating access token for user", extra={"email": email})
    # The access token will expire in 30 minutes.
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        minutes=access_token_expire_minutes()
    )

    # Now creating the payload of the jwt.
    # sub - The subject for the jwt or who the access token is for.
    # exp - the expiry time.
    # type - the type of token, in this case, access.
    jwt_data = {"sub": email, "exp": expire, 'type': 'access'}
    encoded_jwt = jwt.encode(
        jwt_data, key=config.SECRET_KEY, algorithm=config.ALGORITHM
    )
    return encoded_jwt

def create_confirmation_token(email: str):
    logger.debug("Creating confirmation token for email", extra={"email": email})
    # The confirmation token will expire in 24 hours.
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        minutes=confirm_token_expire_minutes()
    )

    # Now creating the payload of the jwt.
    # sub - The subject for the jwt or who the confirmation token is for.
    # exp - the expiry time.
    # type - the type of token, in this case, confirmation.
    jwt_data = {"sub": email, "exp": expire, 'type': 'confirmation'}
    encoded_jwt = jwt.encode(
        jwt_data, key=config.SECRET_KEY, algorithm=config.ALGORITHM
    )
    return encoded_jwt

def get_subject_for_token_type(token: str, type: Literal["access", "confirmation"]) -> str:
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])

    except ExpiredSignatureError as e:
        raise create_credentials_exception("Token has expired") from e
    except jwt.JWTError as e:
        raise create_credentials_exception("Invalid token") from e

    email: str = payload.get("sub")
    if email is None:
        raise create_credentials_exception("Token is missing the 'sub' field")

    token_type: str = payload.get("type")
    if token_type is None or token_type != type:
        raise create_credentials_exception(f"Token is not a valid {token_type} token, expected {type}")
    
    return email

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def get_user(email: str):
    logger.debug("Fetching user from the database", extra={"email": email})
    query = user_table.select().where(user_table.c.email == email)
    result = await database.fetch_one(query)
    if result:
        return result


async def authenticate_user(email: str, password: str):
    logger.debug("Authenticating user", extra={"email": email})
    user = await get_user(email)
    if not user:
        raise create_credentials_exception("Invalid email or pasword")
    if not verify_password(password, user.password):
        raise create_credentials_exception("Invalid email or password")
    return user

# Changed teh parameter from token: str to token: Annotated[str, Depends(oauth2_scheme)]
# This " Annotated[str, Depends(oauth2_scheme)]" means the value should be given to the paramter token is Depends(oauth2_scheme)
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    email = get_subject_for_token_type(token, "access")
    user = await get_user(email=email)
    if user is None:
        raise create_credentials_exception("Could not find user for this token")
    return user
