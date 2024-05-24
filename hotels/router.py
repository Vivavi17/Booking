import asyncio
from datetime import date

from fastapi import APIRouter
from fastapi_cache.decorator import cache

from exceptions import CannotBookHotelForLongPeriod, DateFromCannotBeAfterDateTo
from hotels.dao import HotelDAO
from hotels.schemas import Hotel

router = APIRouter(prefix="/hotels", tags=["Отели и номера"])


@router.get("/id/{hotel_id}")
async def find_by_id(hotel_id: int) -> Hotel:
    return await HotelDAO.find_by_id(hotel_id)


@router.get("/{location}")
@cache(expire=30)
async def find_by_locate_date(
    location: str, date_from: date, date_to: date
) -> list[Hotel]:
    if date_to <= date_from:
        raise DateFromCannotBeAfterDateTo
    if (date_to - date_from).days > 30:
        raise CannotBookHotelForLongPeriod
    # await asyncio.sleep(3)
    return await HotelDAO.find_by_locate_date(location, date_from, date_to)
