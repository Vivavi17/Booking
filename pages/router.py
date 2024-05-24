from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from hotels.router import find_by_locate_date

router = APIRouter(prefix="/pages", tags=["фронтенд"])

templates = Jinja2Templates(directory="templates")


@router.get("")
async def get_hotels_pages(request: Request, hotels=Depends(find_by_locate_date)):
    return templates.TemplateResponse(
        name="hotels.html", context={"request": request, "hotels": hotels}
    )
