import asyncio
import smtplib

from fastapi import Depends

from config import settings
from tasks.celery_app import celery_app
from tasks.email_templates import create_notification_message
from users.dao import UsersDAO


async def get_data():
    await asyncio.sleep(5)


@celery_app.task(name="periodic_task")
def periodic_task():
    """Пример запуска асинхронной функции внутри celery таски"""
    print(12345)
    # asyncio.run(get_data())


@celery_app.task(name="notification_1_day")
def notification_1_day():
    bookings = asyncio.run(UsersDAO.find_booking_by_day(1))
    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        for booking in bookings:
            message_content = create_notification_message(booking)
            server.send_message(message_content)


@celery_app.task(name="notification_3_days")
def notification_3_days():
    bookings = asyncio.run(UsersDAO.find_booking_by_day(3))
    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        print(booking.__dict__)
        for booking in bookings:
            message_content = create_notification_message(booking)
            server.send_message(message_content)
