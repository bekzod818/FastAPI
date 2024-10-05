from contextlib import asynccontextmanager

from fastapi import FastAPI
from src.database import close as db_close
from src.database import init as db_init
from src.speaking.router import router as speak_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db_init()
    yield
    await db_close()


app = FastAPI(lifespan=lifespan)

app.include_router(speak_router, prefix="/speaking", tags=["speaking"])
