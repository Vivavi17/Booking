from sqlalchemy import and_, func, or_, select

from booking.models import Bookings
from dao.base import BaseDAO
from database import async_session_maker
from hotels.rooms.models import Rooms


class RoomDAO(BaseDAO):
    model = Rooms

    @classmethod
    async def find_all(cls, hotel_id, date_from, date_to):
        async with async_session_maker() as session:
            left_quantity = (
                select(Rooms.id, func.count().label("lefter"))
                .select_from(Rooms)
                .join(Bookings, Bookings.room_id == Rooms.id)
                .where(Rooms.hotel_id == hotel_id)
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
                .group_by(Rooms.id)
                .cte("left_quantity")
            )

            query = (
                select(
                    Rooms.id,
                    Rooms.hotel_id,
                    Rooms.name,
                    Rooms.description,
                    Rooms.services,
                    Rooms.price,
                    Rooms.quantity,
                    Rooms.image_id,
                    ((date_to - date_from).days * Rooms.price).label("total_cost"),
                    (Rooms.quantity - func.coalesce(left_quantity.c.lefter, 0)).label(
                        "rooms_left"
                    ),
                )
                .select_from(Rooms)
                .join(left_quantity, left_quantity.c.id == Rooms.id, isouter=True)
                .where(Rooms.hotel_id == hotel_id)
            )

            result = await session.execute(query)
            return result.mappings().all()
