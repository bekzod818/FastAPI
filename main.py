from fastapi import FastAPI
from fastapi.responses import Response, PlainTextResponse, HTMLResponse

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello, FastAPI!"}


@app.get('/{item_id}/')
async def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}


@app.post("/user/")
async def post_user(username: str):
    return {"username": username}


@app.get("/user/{user_id}/")
async def index(user_id: int):
    return {'key': f'Hello {user_id}-user. Welcome to FastAPI'}


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
