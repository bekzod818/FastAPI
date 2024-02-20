import fastapi
import uvicorn

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


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
