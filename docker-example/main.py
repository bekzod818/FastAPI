from os import environ as env

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def get_details():
    return {"details": f"Hello World! Secret Key: {env['SECRET_KEY']}"}
