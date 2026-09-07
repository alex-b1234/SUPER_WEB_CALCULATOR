import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.mark.parametrize("expression, expected_result", [
    ("1+2", 3),
    ("5+5", 10),
    ("0+0", 0),
    ("20+15", 35),
    ("1+1+1", 3),
    ("2+2+2", 6),
    ("0.5+0.5", 1),
    ("0.2+0.2", 0.4),

    ("5-2", 3),
    ("15-5", 10),
    ("0-0", 0),
    ("6-15", -9),
    ("0-3", -3),
    ("4-4", 0),

    ("2+2*2", 6),
    ("1*1", 1),
    ("2*2", 4),
    ("3*4", 12),
    ("0*3", 0),
    ("4*0", 0),
    ("0*0", 0),
    ("15*19", 285),
    ("0.5*0.5", 0.25),

    ("6/2", 3),
    ("5/2", 2.5),
    ("1/1", 1),
    ("3/1", 3),
    ("0/6", 0),
    ("150/15", 10),
    ("2+6/2", 5),

    ("2^2", 4),
    ("3^2", 9),
    ("4^3", 64),
    ("3^0", 1),
    ("0^0", 1),
    ("12^11", 743008370688),
    ("7*9/21", 3),
    ("1+2^3*5", 41),
    ("5+21*8-29*(2+2)-4^2^2*2+1000", 545),
])

def test_calculator(expression, expected_result):
    response = client.post(
        "/api/calculate",
        json={"expression":expression}
    )
    assert response.json() == {
        "result":expected_result
    }

def test_zero_division():
    response = client.post(
            "/api/calculate",
            json={"expression":'2/0'}
        )
    assert response.json() == {
            "error":"Деление на ноль"
        }