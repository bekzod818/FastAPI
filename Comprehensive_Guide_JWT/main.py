import fastapi
import uvicorn
from db_initializer import get_db
from fastapi import Body, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from schemas.users import CreateUserSchema, UserSchema
from services.db import users as user_db_services

from models import users as user_model
from sqlalchemy.orm import Session

app = fastapi.FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@app.post("/login", response_model=dict)
def login(
    payload: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_db)
):
    """Processes user's authentication and returns a token
    on successful authentication.

    request body:

    - username: Unique identifier for a user e.g email,
                phone number, name

    - password:
    """
    try:
        user: user_model.User = user_db_services.get_user(
            session=session, email=payload.username
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user credentials"
        )

    is_validated: bool = user.validate_password(payload.password)
    if not is_validated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user credentials"
        )

    return user.generate_token()


@app.post("/signup", response_model=UserSchema)
def sign_up(payload: CreateUserSchema = Body(), session: Session = Depends(get_db)):
    """Processes request to register user account."""
    payload.hashed_password = user_model.User.hash_password(payload.hashed_password)
    return user_db_services.create_user(session, user=payload)


@app.get("/profile/{id}", response_model=UserSchema)
def get_profile(
    id: int, token: str = Depends(oauth2_scheme), session: Session = Depends(get_db)
):
    """Processes request to retrieve user profile by id"""
    print(token)
    return user_db_services.get_user_by_id(session=session, id=id)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
