import logging
from contextlib import AsyncExitStack, asynccontextmanager

from fastapi import FastAPI

logger = logging.getLogger(__file__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncExitStack() as _:
        await startup_event(app)
        yield
        await shutdown(app)


async def startup_event(app: FastAPI):
    logger.info("startup")


async def shutdown(app: FastAPI):
    logger.info("shutdown")
