from fastapi import FastAPI

app = FastAPI()


@app.post("/user/")
def post_user(username: str):
    return {"username": username}


@app.get("/user/{user_id}/")
def index(user_id: int):
    return {'key': f'Hello {user_id}-user. Welcome to FastAPI'}
