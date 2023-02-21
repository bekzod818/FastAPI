from enum import Enum

from fastapi import FastAPI

app = FastAPI(
    title="Path Parameters"
)


class ModelName(str, Enum):
    alexnet = "alexnet"


@app.get('/')
async def get_index():
    return {"message": "Hello FastAPI!"}


@app.get("/users")
async def read_users():
    return ["Rick", "Morty"]


@app.get('/users/me')
async def get_user():
    return {"user": "The current user"}


@app.get('/users/{user_id}')
async def get_user_by_id(user_id: int):
    return {"user": f"The {user_id}-User"}
