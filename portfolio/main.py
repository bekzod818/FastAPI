import os

import aiohttp
from environs import Env
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

env = Env()
env.read_env()  # read .env file, if it exists
# required variables
BOT_TOKEN = env.str("BOT_TOKEN")  # => 'sloria'
CHAT_ID = env.int("CHAT_ID")  # => raises error if not set


app = FastAPI()

# Get the absolute path of the current script
current_script_path = os.path.abspath(__file__)

# Get the base directory (parent directory of the script)
base_dir = os.path.dirname(current_script_path)

app.mount("/static", StaticFiles(directory=f"{base_dir}/static"), name="static")

templates = Jinja2Templates(directory="templates")


async def send_message(message):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"text": message, "chat_id": CHAT_ID},
        ) as response:
            return await response.json()


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/", response_class=HTMLResponse)
async def post_root(request: Request):
    response = await request.form()
    name = response.get("name")
    email = response.get("email")
    message = f"Received Request\n\nName: {name}\nEmail: {email}"
    await send_message(message=message)
    return templates.TemplateResponse("index.html", {"request": request})
