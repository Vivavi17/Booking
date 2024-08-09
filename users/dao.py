from datetime import date, datetime, timedelta

from sqlalchemy import and_, delete, func, insert, or_, select
from sqlalchemy.orm import selectinload

from booking.models import Bookings
from dao.base import BaseDAO
from database import async_session_maker
from hotels.models import Hotels
from hotels.rooms.models import Rooms
from users.models import Users
from users.schemas import SBookingUser


class UsersDAO(BaseDAO):
    model = Users

    @classmethod
    async def find_booking_by_day(cls, days_left: int, today: date = datetime.now()):
        date_from = (today + timedelta(days=days_left)).date()
        async with async_session_maker() as session:
            query = (
                select(Users.email, Hotels.name, Bookings.date_from)
                .select_from(Users)
                .join(Bookings, Bookings.user_id == Users.id, isouter=True)
                .filter_by(date_from=date_from)
                .join(Rooms, Rooms.id == Bookings.user_id, isouter=True)
                .join(Hotels, Hotels.id == Rooms.hotel_id, isouter=True)
            )
            result = await session.execute(query)
        return result.mappings().all()
