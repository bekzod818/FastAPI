from enum import Enum

from fastapi import FastAPI

app = FastAPI(title="Path Parameters")


class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


@app.get("/")
async def get_index():
    return {"message": "Hello FastAPI!"}


@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model": model_name, "message": "Deep Learning FTW!"}
    if model_name.value == "resnet":
        return {"model": model_name, "message": "LeCNN all the images"}
    return {"model": model_name, "message": "Have some residuals!"}


@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}


@app.get("/users")
async def read_users():
    return ["Rick", "Morty"]


@app.get("/users/me")
async def get_user():
    return {"user": "The current user"}


@app.get("/users/{user_id}")
async def get_user_by_id(user_id: int):
    return {"user": f"The {user_id}-User"}
