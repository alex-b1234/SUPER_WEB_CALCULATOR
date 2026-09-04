from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

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

    try:
        number = ""
        result = 0
        operation = '+'
        for ch in expression+' ':
            if ch not in allowed_chars:
                return {"error": "Недопустимые символы"}
            if ch in "0123456789.":
                number += ch
            else:
                if operation == '+':
                    result += float(number)
                if operation == '-':
                    result -= float(number)
                if operation == '*':
                    result *= float(number)
                if operation == '/':
                    result /= float(number)
                operation = ch
                number = ""

        return {"result": result}
    except ZeroDivisionError:
        return {"error": "Деление на ноль"}
    except Exception as e:
        return {"error": str(e)}