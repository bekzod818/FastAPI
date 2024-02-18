from pydantic import BaseModel, EmailStr


class PostSchema(BaseModel):
    id: int | None = None
    title: str
    content: str

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Securing FastAPI applications with JWT.",
                "content": "In this tutorial, you'll learn how to secure your application by enabling authentication "
                "using JWT. We'll be using PyJWT to sign, encode and decode JWT tokens....",
            }
        }


class UserSchema(BaseModel):
    fullname: str
    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "fullname": "John Doe",
                "email": "john_doe@gmail.com",
                "password": "weakpassword",
            }
        }


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {"email": "john_doe@gmail.com", "password": "weakpassword"}
        }
