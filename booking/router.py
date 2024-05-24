from datetime import date

from fastapi import APIRouter, Depends
from fastapi_versioning import version
from pydantic import EmailStr

from booking.dao import BookingDAO
from booking.schema import AddBooking, SBooking, UsersBookings
from database import async_session_maker
from exceptions import RoomCannotBeBooked
from tasks.tasks import send_message
from users.dependencies import curr_user
from users.models import Users

router = APIRouter(prefix="/bookings", tags=["Бронирование"])


@router.get("")
# @version(2)
async def get_bookings(user: Users = Depends(curr_user)) -> list[UsersBookings]:
    res = await BookingDAO.find_all(user_id=user.id)
    return res


@router.delete("/{booking_id}", status_code=204)
async def del_booking(booking_id: int, user: Users = Depends(curr_user)) -> None:
    return await BookingDAO.del_row(booking_id, user.id)


@router.post("", status_code=201)
@version(1, 0)
async def add_booking(
    room_id: int, date_from: date, date_to: date, user: Users = Depends(curr_user)
) -> AddBooking:
    new_booking = await BookingDAO.add(room_id, date_from, date_to, user_id=user.id)
    if not new_booking:
        raise RoomCannotBeBooked
    booking_dict = AddBooking.model_validate(new_booking).model_dump()
    send_message.delay(booking_dict, user.email)
    return new_booking
