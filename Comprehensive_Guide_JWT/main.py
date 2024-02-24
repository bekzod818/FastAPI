import fastapi
import uvicorn
from db_initializer import get_db
from fastapi import Body, Depends
from schemas.users import CreateUserSchema, UserSchema
from services.db import users as user_db_services

from models import users as user_model
from sqlalchemy.orm import Session

app = fastapi.FastAPI()


@app.post("/login")
def login():
    """Processes user's authentication and returns a token
    on successful authentication.

    request body:

    - username: Unique identifier for a user e.g email,
                phone number, name

    - password:
    """
    return "ThisTokenIsFake"


@app.post("/signup", response_model=UserSchema)
def sign_up(payload: CreateUserSchema = Body(), session: Session = Depends(get_db)):
    """Processes request to register user account."""
    payload.hashed_password = user_model.User.hash_password(payload.hashed_password)
    return user_db_services.create_user(session, user=payload)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
