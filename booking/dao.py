from datetime import date

from sqlalchemy import and_, delete, func, insert, or_, select
from sqlalchemy.exc import SQLAlchemyError

from booking.models import Bookings
from dao.base import BaseDAO
from database import async_session_maker
from exceptions import RoomFullyBooked
from hotels.rooms.models import Rooms
from logger import logger


class BookingDAO(BaseDAO):
    model = Bookings

    @classmethod
    async def add(cls, room_id: int, date_from: date, date_to: date, user_id: int):
        async with async_session_maker() as session:
            booked_rooms = (
                select(Bookings)
                .where(
                    and_(
                        Bookings.room_id == room_id,
                        or_(
                            and_(
                                Bookings.date_from >= date_from,
                                Bookings.date_from <= date_to,
                            ),
                            and_(
                                Bookings.date_from <= date_from,
                                Bookings.date_to > date_from,
                            ),
                        ),
                    )
                )
                .cte("booked_rooms")
            )

            get_rooms_left = (
                select(
                    (
                        Rooms.quantity
                        - func.count(booked_rooms.c.room_id).filter(
                            booked_rooms.c.room_id.is_not(None)
                        )
                    ).label("rooms_left")
                )
                .select_from(Rooms)
                .join(booked_rooms, booked_rooms.c.room_id == Rooms.id, isouter=True)
                .where(Rooms.id == room_id)
                .group_by(Rooms.quantity, booked_rooms.c.room_id)
            )

            rooms_left = await session.execute(get_rooms_left)
            rooms_left: int = rooms_left.scalar()

            if not rooms_left:
                raise RoomFullyBooked
            try:
                room_price = select(Rooms.price).filter_by(id=room_id)
                price = await session.execute(room_price)
                price: int = price.scalar()

                add_booking = (
                    insert(Bookings)
                    .values(
                        room_id=room_id,
                        user_id=user_id,
                        date_from=date_from,
                        date_to=date_to,
                        price=price,
                    )
                    .returning(
                        Bookings.id,
                        Bookings.user_id,
                        Bookings.room_id,
                        Bookings.date_from,
                        Bookings.date_to,
                    )
                )
                new_booking = await session.execute(add_booking)
                await session.commit()
                return new_booking.mappings().one()
            except Exception as e:
                msg = f"{['Unknown', 'Database'][isinstance(e, SQLAlchemyError)]} Exc: Cannot add booking"
                extra = {
                    "room_id": room_id,
                    "date_from": date_from,
                    "date_to": date_to,
                    "user_id": user_id,
                }
                logger.error(msg, extra=extra, exc_info=True)

    @classmethod
    async def find_all(cls, user_id: int):
        async with async_session_maker() as session:
            query = (
                select(
                    Bookings.id,
                    Bookings.room_id,
                    Bookings.user_id,
                    Bookings.date_from,
                    Bookings.date_to,
                    Bookings.price,
                    Bookings.total_cost,
                    Bookings.total_days,
                    Rooms.image_id,
                    Rooms.name,
                    Rooms.description,
                    Rooms.services,
                )
                .select_from(Bookings)
                .filter_by(user_id=user_id)
                .join(Rooms, Bookings.room_id == Rooms.id, isouter=True)
            )
            result = await session.execute(query)
        return result.mappings().all()

    @classmethod
    async def del_row(cls, booking_id, user_id):
        async with async_session_maker() as session:
            query = (
                delete(cls.model)
                .where(cls.model.id == booking_id)
                .where(cls.model.user_id == user_id)
            )
            await session.execute(query)
            await session.commit()
