import pytest
from httpx import AsyncClient


@pytest.mark.parametrize(
    "room_id,date_from,date_to,booked_rooms,status_code",
    *[
        [(4, "2030-05-01", "2030-05-15", i, 201) for i in range(3, 11)]
        + [(4, "2030-05-01", "2030-05-15", 10, 409)] * 2
    ],
)
async def test_add_booking_and_get_bookings(
    room_id, date_from, date_to, booked_rooms, status_code, auth_ac: AsyncClient
):
    response = await auth_ac.post(
        "/v1/bookings",
        params={"room_id": room_id, "date_from": date_from, "date_to": date_to},
    )
    assert response.status_code == status_code

    response = await auth_ac.get("/v1/bookings")
    assert len(response.json()) == booked_rooms


async def test_get_bookings_and_del(auth_ac: AsyncClient):
    response = await auth_ac.get("/v1/bookings")
    for dict_ in response.json():
        remove_booking = await auth_ac.delete(
            f'/v1/bookings/{dict_["id"]}', params={"booking_id": dict_["id"]}
        )
        assert remove_booking.status_code == 204
    response = await auth_ac.get("/v1/bookings")
    assert len(response.json()) == 0
