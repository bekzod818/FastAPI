from fastapi import FastAPI


app = FastAPI()

fake_items_db = [
    {
        "item_name": "Foo" 
    },
    {
        "item_name": "Bar"
    },
    {
        "item_name": "Buz"
    }
]

@app.get('/items')  # /items/?skip=1&limit=3
async def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]


@app.get('/users/{user_id}/items/{item_id}')  # users/1/items/2?q=hello&short=true
async def read_user_item(user_id: int, item_id: int, q: str | None = None, short: bool = False):
    data = {"item_id": item_id, "owner_id": user_id}
    if q:
        data.update({"q": q})
    if not short:
        data.update({"description": "This is an amazing item that has a long description"})
    return data


@app.get('/items/{item_id}')  # /items/foo-item?needy=sooooneedy
async def get_item_by_id(item_id: int, need: str, skip: int = 0, limit: int | None = None):
    return {"item_id": item_id, "need": need, "skip": skip, "limit": limit}
