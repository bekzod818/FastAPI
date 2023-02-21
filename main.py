from fastapi import FastAPI
from fastapi.responses import Response, PlainTextResponse, HTMLResponse

app = FastAPI(
    title="FastAPI Example Title"
)

fake_users = [
    {"id": 1, "role": "admin", "name": "Bob"},
    {"id": 2, "role": "investor", "name": "John"},
    {"id": 3, "role": "trader", "name": "Lucy"}
]

fake_trades = [
    {"id": 1, "user_id": 1, "currency": "BTC", "side": "buy", "price": 123, "amount": 2.34},
    {"id": 2, "user_id": 2, "currency": "ETC", "side": "sell", "price": 345, "amount": 5.67}
]


@app.get("/")
async def root():
    return {"message": "Hello, FastAPI!"}


@app.get('/{item_id}')
async def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}


@app.post("/user/{user_id}")
async def post_user(user_id: int, new_name: str):
    current_user = list(filter(lambda user: user.get('id') == user_id, fake_users))[0]
    current_user["name"] = new_name
    return {"data": current_user, "status": 200}


@app.get("/user/{user_id}")
async def index(user_id: int):
    return [user for user in fake_users if user.get('id') == user_id]


@app.get("/trades")
async def get_trades(limit: int = 1, offset: int = 0):
    return fake_trades[offset:][:limit]


@app.get('/json')
async def return_json():
    return {"response": "This is JSON response"}


@app.get('/text', response_class=PlainTextResponse)
async def return_text():
    return "This is a simple TEXT response!"


@app.get('/html')
async def return_html(response: HTMLResponse):
    content = "<html><body><h1>Hello FastAPI, this is a HTML template!</h1></body></html>"
    return HTMLResponse(content=content, status_code=200)


@app.get('/csv')
async def return_csv():
    content = "Name, Age\nJohn Doe, 25\nGeorge Bob, 30"
    return Response(content=content, media_type="text/csv")
