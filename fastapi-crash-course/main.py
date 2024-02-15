from contextlib import asynccontextmanager

import uvicorn
from database import create_tables
from fastapi import FastAPI
from router import router as tasks_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # await delete_tables()
    # print("Deleted tables from database ...")
    await create_tables()
    print("Connected to database ...")
    yield
    print("Closed ...")


app = FastAPI(lifespan=lifespan)
app.include_router(tasks_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
