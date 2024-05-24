from aiofile import async_open
from fastapi import APIRouter, UploadFile

from tasks.tasks import process_img

router = APIRouter(prefix="/images", tags=["загрузка картинок"])


@router.post("")
async def add_hotel_image(name: int, file_to_upload: UploadFile):
    path = f"static/image/{name}.webp"
    async with async_open(path, "wb+") as file_object:
        file = await file_to_upload.read()
        await file_object.write(file)
    process_img.delay(path)
