from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from simpleeval import simple_eval, NameNotDefined

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

    allowed_chars = set("0123456789+-*/(). ")
    if any(ch not in allowed_chars for ch in expression):
        return {"error": "Недопустимые символы"}

    try:
        # simple_eval специально создан для безопасного вычисления выражений
        result = simple_eval(expression)
        return {"result": result}
    except ZeroDivisionError:
        return {"error": "Деление на ноль"}
    except NameNotDefined:
        return {"error": "Запрещённая функция или переменная"}
    except Exception as e:
        return {"error": str(e)}
