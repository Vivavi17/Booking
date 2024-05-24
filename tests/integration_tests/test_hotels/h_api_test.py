import pytest
from httpx import AsyncClient


@pytest.mark.parametrize(
    "location,date_from,date_to,status_code",
    [
        ("Алтай", "2023-06-06", "2023-06-07", 200),
        ("Коми", "2023-06-06", "2023-06-05", 400),
        ("Сириус", "2023-06-06", "2023-07-07", 400),
    ],
)
async def test_get(location, date_from, date_to, status_code, ac: AsyncClient):
    hotels = await ac.get(
        f"/v1/hotels/{location}",
        params={"location": location, "date_from": date_from, "date_to": date_to},
    )
    assert hotels.status_code == status_code
