from pydantic import BaseModel


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
