import smtplib
from pathlib import Path

from PIL import Image
from pydantic import EmailStr

from config import settings
from tasks.celery_app import celery_app
from tasks.email_templates import create_conformation_message


@celery_app.task
def process_img(path: str):
    img_path = Path(path)
    img = Image.open(img_path)
    img_resize_1000x500 = img.resize((1000, 500))
    img_resize_200x100 = img.resize((200, 100))
    img_resize_1000x500.save(f"static/image/resize_1000x500{img_path.name}")
    img_resize_200x100.save(f"static/image/resize_200x100{img_path.name}")


@celery_app.task
def send_message(data: dict, emai_to: EmailStr):
    emai_to_mok = settings.SMTP_USER
    message_content = create_conformation_message(data, emai_to)
    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(message_content)
