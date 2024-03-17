from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError

__all__ = ["IncomingSeller", "ReturnedAllSellers", "ReturnedSeller"]


# Базовый класс "Книги", содержащий поля, которые есть во всех классах-наследниках.
class BaseSeller(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str



# Класс для валидации входящих данных. Не содержит id так как его присваивает БД.
class IncomingSeller(BaseSeller):
    password: str = "default"  # Пример присваивания дефолтного значения
    email: str = Field(
        alias="e-mail",
        default="blank@blank.ru",
    )  # Пример использования тонкой настройки полей. Передачи в них метаинформации.

    @field_validator("first_name")  # Валидатор, проверяет что дата не слишком древняя
    @staticmethod
    def validate_fname(val: str):
        if len(val) < 2:
            raise PydanticCustomError("Validation error", "first_name is wrong!")
        return val


# Класс, валидирующий исходящие данные. Он уже содержит id, но не содержит password
class ReturnedSeller(BaseSeller):
    id: int
    first_name: str
    last_name: str
    email: str
    password: str ="*****"


# Класс для возврата массива объектов "Seller"
class ReturnedAllSellers(BaseModel):
    sellers: list[ReturnedSeller]
