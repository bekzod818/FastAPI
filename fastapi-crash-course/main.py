from contextlib import asynccontextmanager
from typing import Annotated

import uvicorn
from database import create_tables, drop_tables
from fastapi import Depends, FastAPI
from pydantic import BaseModel


@asynccontextmanager
async def lifespan(app: FastAPI):
    await drop_tables()
    print("Baza tozalandi")
    await create_tables()
    print("Bazada jadvallar yangidan yaratildi")
    yield
    print("O'chirildi")


app = FastAPI(lifespan=lifespan)
tasks = []


class STaskAdd(BaseModel):
    name: str
    description: str | None = None


class STask(STaskAdd):
    id: int


@app.get("/")
async def get_data():
    task = STask(name="Learn FastAPI")
    return {"data": task}


@app.post("/tasks")
async def create_task(task: Annotated[STaskAdd, Depends()]):
    tasks.append(task)
    return {"ok": True}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
