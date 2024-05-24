import json
from datetime import date
from io import BytesIO

from aiofile import async_open
from sqlalchemy import delete, insert, select, types

from database import Base, async_session_maker


class BaseDAO:
    model = None

    @classmethod
    async def find_all(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns).filter_by(**filter_by)
            result = await session.execute(query)
            return result.mappings().all()

    @classmethod
    async def find_one_or_none(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns).filter_by(**filter_by)
            result = await session.execute(query)
            return result.mappings().one_or_none()

    @classmethod
    async def find_by_id(cls, model_id: int):
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns).filter_by(id=model_id)
            result = await session.execute(query)
            return result.mappings().one_or_none()

    @classmethod
    async def add(cls, **data):
        async with async_session_maker() as session:
            query = insert(cls.model).values(**data)
            await session.execute(query)
            await session.commit()

    @classmethod
    async def add_by_csv(cls, table_name, rows):
        async with async_session_maker() as session:
            classes = {
                "bookings": {
                    "id": int,
                    "room_id": int,
                    "user_id": int,
                    "date_from": date,
                    "date_to": date,
                    "price": int,
                    "total_cost": int,
                    "total_days": int,
                },
                "rooms": {
                    "id": int,
                    "hotel_id": int,
                    "name": str,
                    "description": str,
                    "price": int,
                    "services": lambda s: json.loads(s.replace("'", '"')),
                    "quantity": int,
                    "image_id": int,
                },
                "hotels": {
                    "id": int,
                    "name": str,
                    "location": str,
                    "services": lambda s: json.loads(s.replace("'", '"')),
                    "rooms_quantity": int,
                    "image_id": int,
                },
                "users": {"id": int, "email": str, "hashed_password": str},
            }
            for row in rows:
                row = {
                    name: classes[table_name][name](value)
                    for name, value in row.items()
                }
                query = insert(Base.metadata.tables[table_name]).values(**row)
                await session.execute(query)
            await session.commit()
