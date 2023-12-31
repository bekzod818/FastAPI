from fastapi import FastAPI, status
from pydantic import BaseModel, field_validator


class Item(BaseModel):
    name: str
    description: str = None
    price: int

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "name": "Learn Pydantic v2",
                    "description": "Test description here",
                    "price": 1,
                }
            ]
        }

    @field_validator("price")
    def price_must_be_positive(cls, value):
        if value <= 0:
            raise ValueError("The price must be positive")
        return value


app = FastAPI()


@app.post("/items", status_code=status.HTTP_201_CREATED)
async def create_item(item: Item):
    item_dict = item.model_dump()
    return {"item": item_dict}
