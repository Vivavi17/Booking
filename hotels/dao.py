from sqlalchemy import and_, column, func, or_, select

from booking.models import Bookings
from dao.base import BaseDAO
from database import async_session_maker
from hotels.models import Hotels
from hotels.rooms.models import Rooms


class HotelDAO(BaseDAO):
    model = Hotels

    @classmethod
    async def find_by_locate_date(cls, locate, date_from, date_to):
        async with async_session_maker() as session:
            left_quantity = (
                select(Rooms.hotel_id, func.count().label("lefter"))
                .select_from(Rooms)
                .join(Bookings, Bookings.room_id == Rooms.id)
                .where(
                    or_(
                        and_(
                            Bookings.date_from >= date_from,
                            Bookings.date_from <= date_to,
                        ),
                        and_(
                            Bookings.date_from <= date_from,
                            Bookings.date_to > date_from,
                        ),
                    )
                )
                .group_by(Rooms.hotel_id)
                .cte("left_quantity")
            )

            get_hotels = (
                select(
                    Hotels.id,
                    Hotels.name,
                    Hotels.location,
                    Hotels.services,
                    Hotels.rooms_quantity,
                    Hotels.image_id,
                    (
                        Hotels.rooms_quantity - func.coalesce(left_quantity.c.lefter, 0)
                    ).label("rooms_left"),
                )
                .select_from(Hotels)
                .join(
                    left_quantity, left_quantity.c.hotel_id == Hotels.id, isouter=True
                )
                .where(
                    (Hotels.rooms_quantity - func.coalesce(left_quantity.c.lefter, 0))
                    > 0
                )
                .where(Hotels.location.ilike(f"%{locate}%"))
            )
            result = await session.execute(get_hotels)
            return result.mappings().all()
