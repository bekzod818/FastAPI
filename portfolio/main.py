import os

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Get the absolute path of the current script
current_script_path = os.path.abspath(__file__)

# Get the base directory (parent directory of the script)
base_dir = os.path.dirname(current_script_path)

app.mount("/static", StaticFiles(directory=f"{base_dir}/static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
