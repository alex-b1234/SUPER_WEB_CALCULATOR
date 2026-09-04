from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from shunting_yard import calculate_expression

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/calculate")
async def calculate(request: Request):
    try:
        data = await request.json()
    except Exception:
        return {"error": "Некорректный JSON"}

    expression = data.get("expression", "")
    if not expression:
        return {"error": "Поле expression отсутствует"}

    try:
        result = calculate_expression(expression)
        return {"result": result}
    except ZeroDivisionError:
        return {"error": "Деление на ноль"}
    except Exception as e:
        return {"error": str(e)}