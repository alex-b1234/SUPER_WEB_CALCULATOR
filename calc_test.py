import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.mark.parametrize("a, b, expected_result", [
    (1, 2, 3),
    (5, 5, 10),
    (0, 0, 0),
    (20, 15, 35),
])

def test_add(a, b, expected_result):
    response = client.post(
        "/api/calculate",
        json={"expression":f'{a}+{b}'}
    )
    assert response.json() == {
        "result":expected_result
    }

@pytest.mark.parametrize("a, b, expected_result", [
    (5, 2, 3),
    (15, 5, 10),
    (0, 0, 0),
    (6, 15, -9),
    (0, 3, -3),
    (4, 4, 0),
])

def test_sub(a, b, expected_result):
    response = client.post(
        "/api/calculate",
        json={"expression":f'{a}-{b}'}
    )
    assert response.json() == {
        "result":expected_result
    }

@pytest.mark.parametrize("a, b, expected_result", [
    (1, 1, 1),
    (2, 2, 4),
    (3, 4, 12),
    (0, 3, 0),
    (4, 0, 0),
    (0, 0, 0),
    (15, 19, 285),
])

def test_multi(a, b, expected_result):
    response = client.post(
        "/api/calculate",
        json={"expression":f'{a}*{b}'}
    )
    assert response.json() == {
        "result":expected_result
    }

@pytest.mark.parametrize("a, b, expected_result", [
    (6, 2, 3),
    (5, 2, 2.5),
    (1, 1, 1),
    (3, 1, 3),
    (0, 6, 0),
    (150, 15, 10),
])

def test_division(a, b, expected_result):
    response = client.post(
        "/api/calculate",
        json={"expression":f'{a}/{b}'}
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

@pytest.mark.parametrize("a, b, expected_result", [
    (2, 2, 4),
    (3, 2, 9),
    (4, 3, 64),
    (3, 0, 1),
    (0, 0, 1),
    (12, 11, 743008370688),
])

def test_pow(a, b, expected_result):
    response = client.post(
        "/api/calculate",
        json={"expression":f'{a}^{b}'}
    )
    assert response.json() == {
        "result":expected_result
    }

@pytest.mark.parametrize("expression, expected_result", [
    ("1+1+1", 3),
    ("2+2+2", 6),
    ("2+2*2", 6),
    ("2+6/2", 5),
    ("7*9/21", 3),
    ("1+2^3*5", 41),
    ("5+21*8-29*(2+2)-4^2^2*2+1000", 545),
])

def test_several_operations(expression, expected_result):
    response = client.post(
        "/api/calculate",
        json={"expression":expression}
    )
    assert response.json() == {
        "result":expected_result
    }