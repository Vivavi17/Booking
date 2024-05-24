import asyncio
import json
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import insert

from booking.models import Bookings
from config import settings
from database import Base, async_session_maker, engine
from hotels.models import Hotels
from hotels.rooms.models import Rooms
from main import app as app_fastapi
from users.models import Users


@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    assert settings.MODE == "TEST"
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

    def open_mock(model: str):
        with open(f"tests/mock_{model}.json", encoding="utf-8") as file:
            return json.load(file)

    hotels = open_mock("hotels")
    rooms = open_mock("rooms")
    users = open_mock("users")
    bookings = open_mock("bookings")
    for booking in bookings:
        booking["date_from"] = datetime.strptime(booking["date_from"], "%Y-%m-%d")
        booking["date_to"] = datetime.strptime(booking["date_to"], "%Y-%m-%d")

    async with async_session_maker() as session:
        for Model, values in [
            (Hotels, hotels),
            (Rooms, rooms),
            (Users, users),
            (Bookings, bookings),
        ]:
            query = insert(Model).values(values)
            await session.execute(query)

        await session.commit()


# @pytest.fixture(scope="session")
# def event_loop():
#     policy = asyncio.get_event_loop_policy()
#     loop = policy.new_event_loop()
#     yield loop
#     loop.close()


@pytest.fixture()
async def ac():
    async with AsyncClient(app=app_fastapi, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="session")
async def auth_ac():
    async with AsyncClient(app=app_fastapi, base_url="http://test") as ac:
        await ac.post(
            "/v1/users/login", json={"email": "test@test.com", "password": "test"}
        )
        assert ac.cookies["access_token"]
        yield ac


@pytest.fixture()
async def session():
    async with async_session_maker() as session:
        yield session
