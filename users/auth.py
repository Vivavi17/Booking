from datetime import UTC, datetime, timedelta

from jose import jwt
from passlib.context import CryptContext
from pydantic import EmailStr

from config import settings
from users.dao import UsersDAO

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_pwd(password: str, hashed_pwd: str) -> bool:
    return pwd_context.verify(password, hashed_pwd)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, settings.ALGORITHM)
    return encoded_jwt


async def authentication_user(email: EmailStr, password: str):
    user = await UsersDAO.find_one_or_none(email=email)
    if user and verify_pwd(password, user.hashed_password):
        return user
