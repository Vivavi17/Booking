from datetime import UTC, datetime

from fastapi import Depends, Request
from jose import JWTError, jwt

from config import settings
from exceptions import IncorrectTokenFormatException, TokenAbsentException
from users.dao import UsersDAO


def get_curr_token(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise TokenAbsentException
    return token


async def curr_user(token: str = Depends(get_curr_token)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, settings.ALGORITHM)
    except JWTError:
        raise IncorrectTokenFormatException
    user_id: str = payload.get("sub")
    if not user_id:
        raise IncorrectTokenFormatException
    user = await UsersDAO.find_by_id(int(user_id))
    if not user:
        raise IncorrectTokenFormatException
    return user
