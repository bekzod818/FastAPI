from enum import Enum

from fastapi import FastAPI

app = FastAPI()


class Product(str, Enum):
    carrot = "carrot"
    cucumber = "cucumber"
    apple = "apple"
    orange = "orange"


@app.get("/")
async def get_data():
    return {"message": "Some useful data for you!"}


@app.get("/items/{item_id}")
async def get_item_detail(item_id: int):
    return {"item_id": item_id}


@app.get("/users/me")
async def get_me():
    return {"user": "The current user"}


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id}


@app.get("/products/{product}")
async def get_product(product: Product):
    if product == Product.carrot:
        return {"product": "This is a carrot. It's my favorite vegetable!"}
    else:
        return {"product": f"This is a {product.name}"}


@app.get("/file/{file_path:path}")
async def get_file_path(file_path: str):
    return {"file_path": file_path}
