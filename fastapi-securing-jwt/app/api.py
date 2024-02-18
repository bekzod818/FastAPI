from fastapi import FastAPI

from .model import PostSchema

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
