from fastapi import FastAPI, Request, Response, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from .shunting_yard import calculate_expression

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
app = FastAPI()
templates = Jinja2Templates(directory=TEMPLATES_DIR)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/calculate")
async def calculate(request: Request, response: Response):
    try:
        data = await request.json()
    except Exception:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": {"code": response.status_code, "message": "Некорректный JSON"}}

    expression = data.get("expression", "")
    if not expression:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": {"code": response.status_code, "message": "Поле expression отсутствует"}}

    try:
        result = calculate_expression(expression)
        return {"result": result}
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": {"code": response.status_code, "message": str(e)}}