from datetime import date

from pydantic import BaseModel


# Объявляем параметр user_id с типом `str`
# и получаем поддержку проверки типов данных редактора (IDE) внутри функции
def main(user_id: str):
    return user_id


# Модель Pydantic - ещё один пример создания
class User(BaseModel):
    id: int = 1
    name: str
    age: int
    joined: date


my_user: User = User(id=2, name="John Doe", age=18, joined="2020-01-30")


second_user_data = {
    "id": 4,
    "name": "Mary",
    "age": 22,
    "joined": "2018-11-30",
}

my_second_user: User = User(**second_user_data)
