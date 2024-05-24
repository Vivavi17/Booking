import codecs
import csv
import time
from contextlib import asynccontextmanager
from typing import Literal

import sentry_sdk
import uvicorn
from fastapi import BackgroundTasks, FastAPI, Request, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_versioning import VersionedFastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from redis import asyncio as aioredis
from sqladmin import Admin

from admin.auth import authentication_backend
from admin.views import BookingsAdmin, HotelsAdmin, RoomsAdmin, UserAdmin
from booking.router import router as router_bookings
from config import settings
from dao.base import BaseDAO
from database import engine
from hotels.rooms.router import router  # noqa
from hotels.router import router as router_hotels
from images.router import router as router_image
from logger import logger
from pages.router import router as router_pages
from prometheus_r.router import router as router_prometheus
from users.router import router as router_users

sentry_sdk.init(
    dsn="https://fe973fa0811386223a9025259045a0c6@o4507282918670336.ingest.us.sentry.io/4507282925355008",
    enable_tracing=True,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = aioredis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
        encoding="utf8",
        decode_responses=True,
    )
    FastAPICache.init(RedisBackend(redis), prefix="cache")
    logger.info("Service started")

    yield
    logger.info("Service exited")


app = FastAPI(lifespan=lifespan)

app.include_router(router_users)
app.include_router(router_bookings)
app.include_router(router_hotels)
app.include_router(router_pages)
app.include_router(router_image)
app.include_router(router_prometheus)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.post("/import/{table_name}", status_code=201)
async def import_csv(
    table_name: Literal["bookings", "rooms", "hotels", "users"],
    file: UploadFile,
    background_tasks: BackgroundTasks,
):
    csvReader = csv.DictReader(codecs.iterdecode(file.file, "utf-8"), delimiter=";")
    background_tasks.add_task(file.file.close)
    return await BaseDAO.add_by_csv(table_name, csvReader)


@app.get("/sentry-debug")
async def trigger_error():
    division_by_zero = 1 / 0


app = VersionedFastAPI(app, version_format="{major}", prefix_format="/v{major}")

instrumentator = Instrumentator(
    should_group_status_codes=False, excluded_handlers=[".*admin.*", "/metrics"]
)
instrumentator.instrument(app).expose(app)

app.mount("/static", StaticFiles(directory="static"), "static")

admin = Admin(app, engine, authentication_backend=authentication_backend)
admin.add_view(UserAdmin)
admin.add_view(BookingsAdmin)
admin.add_view(HotelsAdmin)
admin.add_view(RoomsAdmin)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    # logger.info(
    #     "Request executions time", extra={"process_time": round(process_time, 4)}
    # )
    return response


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
