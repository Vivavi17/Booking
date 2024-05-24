from datetime import datetime

import pytest

from booking.dao import BookingDAO


@pytest.mark.parametrize(
    "room_id,date_from,date_to,user_id", [(2, "2023-07-10", "2023-07-24", 1)]
)
async def test_add_and_find_by_id(room_id, date_from, date_to, user_id):
    new_booking = await BookingDAO.add(
        room_id,
        datetime.strptime(date_from, "%Y-%m-%d"),
        datetime.strptime(date_to, "%Y-%m-%d"),
        user_id,
    )
    assert new_booking.room_id == room_id
    assert new_booking.user_id == user_id

    find_by_id = await BookingDAO.find_by_id(new_booking.id)
    assert find_by_id


@pytest.mark.parametrize(
    "room_id,date_from,date_to,user_id", [(2, "2023-07-10", "2023-07-24", 1)]
)
async def test_CRUD_bookings(room_id, date_from, date_to, user_id):
    old_bookings = await BookingDAO.find_all(user_id)
    new_booking = await BookingDAO.add(
        room_id,
        datetime.strptime(date_from, "%Y-%m-%d"),
        datetime.strptime(date_to, "%Y-%m-%d"),
        user_id,
    )
    new_bookings = await BookingDAO.find_all(user_id)

    assert len(old_bookings) == len(new_bookings) - 1

    read_id = await BookingDAO.find_by_id(new_booking.id)
    assert read_id

    await BookingDAO.del_row(new_booking.id, user_id)
    read_id = await BookingDAO.find_by_id(new_booking.id)
    assert read_id == None
