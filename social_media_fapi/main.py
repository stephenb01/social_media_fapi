import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from social_media_fapi.database import database
from social_media_fapi.logging_conf import configure_logging
from social_media_fapi.routers.post import router as post_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    await database.connect()
    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan)


app.include_router(post_router)
