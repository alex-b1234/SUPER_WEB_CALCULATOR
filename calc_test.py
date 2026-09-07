import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.mark.parametrize("a, b, expected_sum", [
    (1, 2, 3),
    (5, 5, 10),
    (0, 0, 0),
])

def test_add(a, b, expected_sum):
    response = client.post(
        "/api/calculate",
        json={"expression":f'{a}+{b}'}
    )
    assert response.json() == {
        "result":expected_sum
    }