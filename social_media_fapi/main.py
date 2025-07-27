import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.exception_handlers import http_exception_handler
from asgi_correlation_id import CorrelationIdMiddleware

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
app.add_middleware(CorrelationIdMiddleware)


app.include_router(post_router)

@app.exception_handler(HTTPException)
async def http_exception_handle_logger(request, exc):
    logger.error(f"HTTPException: {exc.status_code} {exc.detail}")
    return await http_exception_handler(request, exc)