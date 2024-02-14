from contextlib import asynccontextmanager

import uvicorn
from database import create_tables, delete_tables
from fastapi import FastAPI
from router import router as tasks_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await delete_tables()
    print("Baza tozalandi")
    await create_tables()
    print("Bazada jadvallar yangidan yaratildi")
    yield
    print("O'chirildi")


app = FastAPI(lifespan=lifespan)
app.include_router(tasks_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
