from datetime import date

from hotels.rooms.dao import RoomDAO
from hotels.rooms.schemas import RoomsInHotel
from hotels.router import router


@router.get("/{hotel_id}/rooms")
async def find_all(hotel_id: int, date_from: date, date_to: date) -> list[RoomsInHotel]:
    return await RoomDAO.find_all(hotel_id, date_from, date_to)
