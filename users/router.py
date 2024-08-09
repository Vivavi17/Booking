from fastapi import APIRouter, Depends, HTTPException, Response, status

from exceptions import UserAlreadyExistsException
from users.auth import authentication_user, create_access_token, get_password_hash
from users.dao import UsersDAO
from users.dependencies import curr_user
from users.models import Users
from users.schemas import SUsersAuth

router = APIRouter(prefix="/users", tags=["Аут и Пользователи"])


@router.post("/register", status_code=201)
async def register(data: SUsersAuth):
    existing_user = await UsersDAO.find_one_or_none(email=data.email)
    if existing_user:
        raise UserAlreadyExistsException
    hashed_pwd = get_password_hash(data.password)
    await UsersDAO.add(email=data.email, hashed_password=hashed_pwd)


@router.post("/login")
async def login(response: Response, data: SUsersAuth):
    user = await authentication_user(data.email, data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    access_token = create_access_token({"sub": str(user.id)})
    response.set_cookie("access_token", access_token, httponly=True)
    return {"access_token": access_token}


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")


@router.get("/me")
async def me(user: Users = Depends(curr_user)):
    return user
