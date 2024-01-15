from fastapi import FastAPI

from . import endpoints
from .containers import Container


def create_app() -> FastAPI:
    container = Container()

    db = container.db()
    db.create_database()

    app = FastAPI()
    app.container = container
    app.include_router(router=endpoints.router)

    return app


app = create_app()
