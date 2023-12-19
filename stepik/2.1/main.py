from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def get_index_page(request: Request):
    return templates.TemplateResponse(name="index.html", context={"request": request})


# http://127.0.0.1:8000/calculate?num1=2&num2=4
@app.post("/calculate")
async def calculate_expressions_by_query(num1: int, num2: int):
    return {"result": num1 + num2}

# http://127.0.0.1:8000/calculate/{num1}/{num2}
@app.post("/calculate/{num1}/{num2}")
async def calculate_expressions_by_args(num1: int, num2: int):
    return {"result": num1 + num2}
