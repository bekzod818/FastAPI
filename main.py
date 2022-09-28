from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    is_offer: Optional[bool] = None


@app.get('/')
async def read_root():
    return {"Hello": "World"}


@app.post('/items/')
async def create_item(item: Item):
    item_dict = item.dict()
    # print(item_dict)
    if item.is_offer:
        item_dict.update({'new_price': item.price + 5.99})
    return item_dict


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Optional[str] = None):
    return {'item_id': item_id, "q": q}


@app.put('/items/{item_id}')
async def update_item(item_id: int, item: Item):
    # return {'item_id': item_id, **item.dict()}
    return {'item_name': item.name, 'item_price': item.price, 'item_id': item_id}