from sqladmin import ModelView

from booking.models import Bookings
from hotels.models import Hotels
from hotels.rooms.models import Rooms
from users.models import Users


class UserAdmin(ModelView, model=Users):
    column_list = [Users.id, Users.email]
    can_delete = False
    column_details_exclude_list = [Users.hashed_password]
    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid fa-address-card"


class BookingsAdmin(ModelView, model=Bookings):
    column_list = [c.name for c in Bookings.__table__.c] + [
        Bookings.user,
        Bookings.room,
    ]
    name = "Бронирование"
    name_plural = "Бронирования"
    icon = "fa-solid fa-calendar-days"


class HotelsAdmin(ModelView, model=Hotels):
    column_list = [c.name for c in Hotels.__table__.c] + [Hotels.rooms]
    name = "Отель"
    name_plural = "Отели"
    icon = "fa-solid fa-hotel"


class RoomsAdmin(ModelView, model=Rooms):
    column_list = [c.name for c in Rooms.__table__.c] + [Rooms.hotel, Rooms.bookings]
    name = "Комната"
    name_plural = "Комнаты"
    icon = "fa-solid fa-door-closed"
