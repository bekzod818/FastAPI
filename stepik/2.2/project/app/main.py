from fastapi import FastAPI
from models.users import User as SimpleUser
from models.users_2 import User as User2
from pydantic import BaseModel

app = FastAPI()


class User(BaseModel):
    username: str
    message: str


@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}


@app.get("/custom")
async def read_custom_message():
    return {"message": "This is a custom message!"}


@app.post("/register")
async def register_user(user: User):
    """тут мы можем с переменной user, которая в себе содержит объект класса User с соответствующими полями (и указанными типами), делать любую логику
    - например, мы можем сохранить информацию в базу данных
    - или передать их в другую функцию
    - или другое"""
    print(
        f"Мы получили от юзера {user.username} такое сообщение: {user.message}"
    )  # тут мы просто выведем полученные данные на экран в отформатированном варианте
    return user  # или можем вернуть обратно полученные данные, как символ того, что данные получили, или другая логика на ваш вкус


@app.post("/user")
async def add_user(user: SimpleUser):
    return user


@app.post("/user/2")
async def add_again_user(user: User2):
    return {"is_adult": user.age >= 18}
