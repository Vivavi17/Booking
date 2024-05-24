from datetime import date

from pydantic import BaseModel, EmailStr


class SUsersAuth(BaseModel):
    email: EmailStr
    password: str


class SBookingUser(BaseModel):
    email: EmailStr
    name: str
    date_from: date
