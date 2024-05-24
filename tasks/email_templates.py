from datetime import date, datetime, timedelta
from email.message import EmailMessage

from pydantic import EmailStr

from config import settings


def create_conformation_message(booking: dict, email_to: EmailStr):
    email = EmailMessage()
    email["Subject"] = "Подтверждение бронирования"
    email["From"] = settings.SMTP_USER
    email["To"] = email_to
    email.set_content(
        f"""
        <h1>Подтвердите бронирование</h1>
        Вы забронировали отель с {booking['date_from']} по {booking["date_to"]}
        """,
        subtype="html",
    )
    return email


def create_notification_message(booking: dict):
    email = EmailMessage()
    email["Subject"] = "Напоминание о бронировании"
    email["From"] = settings.SMTP_USER
    email["To"] = booking["email"]
    email.set_content(
        f"""
        <h1>Напоминание о бронировании</h1>
        Напоминаем, Вы забронировали отель {booking['name']} на {booking['date_from']}.
        {['','Заселение уже завтра'][booking['date_from']==(datetime.now()+timedelta(days=1)).date()]}
        """,
        subtype="html",
    )
    return email
