from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from configurations.database import create_db_and_tables, global_init
from routers import v1_router

# Само приложение fastApi. именно оно запускается сервером и служит точкой входа
# в нем можно указать разные параметры для сваггера и для ручек (эндпоинтов).
app = FastAPI(
    title="Book Library App",
    description="Учебное приложение для группы MTS Shad",
    version="0.0.1",
    responses={404: {"description": "Not Found!"}},
    default_response_class=ORJSONResponse,  # Подключаем быстрый сериализатор
)

app.include_router(v1_router)


@app.on_event("startup")
async def startup_event():
    global_init()
    await create_db_and_tables()
