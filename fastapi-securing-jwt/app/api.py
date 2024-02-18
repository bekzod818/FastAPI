from fastapi import Body, FastAPI

from .auth.auth_handler import signJWT
from .model import PostSchema, UserLoginSchema, UserSchema

app = FastAPI()

posts = [{"id": 1, "title": "Pancake", "content": "Lorem Ipsum ..."}]

users = []


@app.get("/", tags=["root"])
async def read_root() -> dict:
    return {"message": "Welcome to your blog!"}


@app.get("/posts", tags=["posts"])
async def get_posts() -> dict:
    return {"data": posts}


@app.get("/posts/{id}", tags=["posts"])
async def get_single_post(id: int) -> dict:
    if id > len(posts):
        return {"error": "No such post with the supplied ID."}

    for post in posts:
        if post["id"] == id:
            return {"data": post}


@app.post("/posts", tags=["posts"])
async def add_post(post: PostSchema) -> dict:
    post.id = len(posts) + 1
    posts.append(post.dict())
    return {"data": "post added."}


@app.post("/user/signup", tags=["user"])
async def create_user(user: UserSchema = Body(...)):
    """
    In a production environment, make sure to hash your password using bcrypt or passlib before saving the user to the database.
    """
    users.append(user)  # replace with db call, making sure to hash the password first
    return signJWT(user.email)


def check_user(data: UserLoginSchema):
    for user in users:
        if user.email == data.email and user.password == data.password:
            return True
    return False


@app.post("/user/login", tags=["user"])
async def user_login(user: UserLoginSchema = Body(...)):
    if check_user(user):
        return signJWT(user.email)
    return {"error": "Wrong login details!"}
