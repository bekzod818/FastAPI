from fastapi import FastAPI, Query
from pydantic import Required


app = FastAPI()


@app.get('/items/')
async def read_items(
        q: str | None = Query(
            default=None, 
            min_length=3, 
            max_length=50, 
            title="Query string",
            description="Query string for the items to search in the database that have a good match",
            alias="item-query",
            deprecated=True,
            )  # regex="^fixedquery$"
    ):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


@app.get("/item/")
async def read_item(q: str | None = Query(default=..., min_length=3, max_length=20), text: str = Query(default=Required, min_length=3)):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}], "text": text}
    if q:
        results.update({"q": q})
    return results


@app.get('/items/list/')
async def get_items_list(items: list[str] | None = Query(default=["foo", "bar"])):
    return {"items": items}


@app.get('/hidden/item/')
async def get_hidden_item(hidden_query: str | None = Query(default=None, include_in_schema=False)):
    if hidden_query:
        return {"hidden_query": hidden_query}
    else:
        return {"hidden_query": "Not Found"}
