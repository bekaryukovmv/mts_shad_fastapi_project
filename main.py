from fastapi import FastAPI, Response, status
from fastapi.responses import ORJSONResponse
from icecream import ic
from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError

COUNTER = 0  # Каунтер имитирующий присвоение id в базе данных


# Само приложение fastApi. именно оно запускается сервером и служит точкой входа
# в нем можно указать разные параметры для сваггера и для ручек (эндпоинтов).
app = FastAPI(
    title="Book Library App",
    description="Учебное приложение для группы MTS Shad",
    version="0.0.1",
    responses={404: {"description": "Not Found!"}},
    default_response_class=ORJSONResponse,  # Подключаем быстрый сериализатор
)


# симулируем хранилище данных. Просто сохраняем объекты в память, в словаре.
fake_storage = {}


# Базовый класс "Книги", содержащий поля, которые есть во всех классах-наследниках.
class BaseBook(BaseModel):
    title: str
    author: str
    year: int


# Класс для валидации входящих данных. Не содержит id так как его присваивает БД.
class IncomingBook(BaseBook):
    year: int = 2024  # Пример присваивания дефолтного значения
    count_pages: int = Field(
        alias="pages",
        default=300,
    )  # Пример использования тонкой настройки полей. Передачи в них метаинформации.

    @field_validator("year")  # Валидатор, проверяет что дата не слишком древняя
    @staticmethod
    def validate_year(val: int):
        if val < 1900:
            raise PydanticCustomError("Validation error", "Year is wrong!")
        return val


# Класс, валидирующий исходящие данные. Он уже содержит id
class ReturnedBook(BaseBook):
    id: int
    count_pages: int


# Класс для возврата массива объектов "Книга"
class ReturnedAllBooks(BaseModel):
    books: list[ReturnedBook]


# Просто пример ручки и того, как ее можно исключить из схемы сваггера
@app.get("/", include_in_schema=False)
async def main():
    return "Hello World!"


# Ручка для создания записи о книге в БД. Возвращает созданную книгу.
@app.post("/books/", response_model=ReturnedBook)  # Прописываем модель ответа
async def create_book(book: IncomingBook):  # прописываем модель валидирующую входные данные
    global COUNTER  # счетчик ИД нашей фейковой БД
    # TODO запись в БД
    # это - бизнес логика. Обрабатываем данные, сохраняем, преобразуем и т.д.
    new_book = {
        "id": COUNTER,
        "title": book.title,
        "author": book.author,
        "year": book.year,
        "count_pages": book.count_pages,
    }
    fake_storage[COUNTER] = new_book
    COUNTER += 1

    # return new_book  # Так можно просто вернуть объект
    return ORJSONResponse(
        new_book,
        status_code=status.HTTP_201_CREATED,
    )  # Возвращаем объект в формате Json с нужным нам статус-кодом, обработанный нужным сериализатором.


# Ручка, возвращающая все книги
@app.get("/books/", response_model=ReturnedAllBooks)
async def get_all_books():
    # Хотим видеть формат:
    # books: [{"id": 1, "title": "Blabla", ...}, {"id": 2, ...}]
    books = list(fake_storage.values())
    return {"books": books}


# Ручка для получения книги по ее ИД
@app.get("/books/{book_id}", response_model=ReturnedBook)
async def get_book(book_id: int):
    return fake_storage[book_id]


# Ручка для удаления книги
@app.delete("/books/{book_id}")
async def delete_book(book_id: int):
    deleted_book = fake_storage.pop(book_id, -1)
    # print("*****************", deleted_book)
    ic(deleted_book)  # Красивая и информативная замена для print. Полезна при отладке.
    return Response(status_code=status.HTTP_204_NO_CONTENT)  # Response может вернуть текст и метаданные.


# Ручка для обновления данных о книге
@app.put("/books/{book_id}")
async def update_book(book_id: int, book: ReturnedBook):
    # Оператор "морж", позволяющий одновременно и присвоить значение и проверить его.
    if _ := fake_storage.get(book_id, None):
        fake_storage[book_id] = book

    return fake_storage[book_id]
