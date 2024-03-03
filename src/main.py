from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from src.configurations.database import create_db_and_tables, delete_db_and_tables, global_init
from src.routers import v1_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    global_init()
    await create_db_and_tables()

    yield

    await delete_db_and_tables()


def create_application():
    return FastAPI(
        title="Book Library App / Cherepashchuk A version.",
        description="Educational application for MTS Shad group.",
        version="1.0.0",
        responses={404: {"description": "Not Found!"}},
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
    )


app = create_application()


def _configure():
    app.include_router(v1_router)


_configure()
