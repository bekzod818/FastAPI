from fastapi import FastAPI

from config.routes import router

app = FastAPI()
app.include_router(router=router)
