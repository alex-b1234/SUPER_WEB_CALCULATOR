import pytest
from fastapi.testclient import TestClient
from main import app
from shunting_yard import tokenize, shunting_yard, calculate_expression

client = TestClient(app)

class TestApi:
    def test_calculator(self):
        response = client.post(
            "/api/calculate",
            json={"expression":"(1+2)*3-4/8+5.6+9^7"}
        )
        assert response.json() == {
            "result": '4782983.0999999996'
        } and response.status_code == 200

    def test_index(self):
        response = client.get(
            "/"
        )
        assert response.status_code == 200

    @pytest.mark.parametrize("error_json, error_code, error_message", [
        ({}, 400, "ПОЛЕ EXPRESSION ОТСУТСТВУЕТ"),
        ((), 400, "НЕКОРРЕКТНЫЙ ЗАПРОС"),
        ("{\"a\": 2, \"b\": 3, \"op\": \"+\"", 400, "НЕКОРРЕКТНЫЙ ЗАПРОС"),
        ({"expression":""}, 400, "ПОЛЕ EXPRESSION ОТСУТСТВУЕТ"),
        ({"expression":"1+"}, 400, "НЕКОРРЕКТНОЕ ВЫРАЖЕНИЕ"),
        ({"expression":"2(3+)"}, 400, "НЕКОРРЕКТНОЕ ВЫРАЖЕНИЕ"),
        ({"expression":"2 3 +"}, 400, "НЕКОРРЕКТНОЕ ВЫРАЖЕНИЕ"),
        ({"expression":"2/0"}, 400, "НЕЛЬЗЯ ДЕЛИТЬ НА НОЛЬ"),
        ({"expression":"абвгд"}, 400, "НЕДОПУСТИМЫЙ СИМВОЛ: а"),
        ({"expression":"(-3)^0.2"}, 400, "КОМПЛЕКСНЫЕ ЧИСЛА НЕ ПОДДЕРЖИВАЮТСЯ"),
    ])
    def test_errors(self, error_json, error_code, error_message):
        response = client.post(
            "/api/calculate",
            json=error_json
        )
        assert response.json() == {
            "error": {
                "code": error_code,
                "message": error_message
            }
        } and response.status_code == error_code

class TestTokenize:
    def test_simple(self):
        assert tokenize("2+3") == [2.0, '+', 3.0]

    def test_negative_number(self):
        assert tokenize("-2+3") == ['u-', 2.0, '+', 3.0]

    def test_many_same_digits(self):
        # Токенизатор должен увидеть это как одно число
        tokens = tokenize("999999999999999+1")
        assert len(tokens) == 3
        assert tokens[0] == 999_999_999_999_999.0

class TestShuntingYard:
    def test_basic_precedence(self):
        tokens = tokenize("2+3*4")
        rpn = shunting_yard(tokens)
        # Ожидаем: 2 3 4 * +
        assert rpn == [2.0, 3.0, 4.0, '*', '+']

    def test_parentheses(self):
        tokens = tokenize("(2+3)*4")
        rpn = shunting_yard(tokens)
        assert rpn == [2.0, 3.0, '+', 4.0, '*']

    def test_exponent_right_assoc(self):
        tokens = tokenize("2^3^2")
        rpn = shunting_yard(tokens)
        # 2^(3^2) = 2^9, а не (2^3)^2
        assert rpn == [2.0, 3.0, 2.0, '^', '^']

class TestCalculate:
    @pytest.mark.parametrize("expr,expected", [
        ("20+15", 35),
        ("2+2+2", 6),
        ("0.2+0.2", 0.4),
        ("-5+5", 0),
        ("15-5", 10),
        ("-4-5", -9),
        ("2+2*2", 6),
        ("4*0", 0),
        ("15*19", 285),
        ("0.5*0.5", 0.25),
        ("-2*-10", 20),
        ("5/2", 2.5),
        ("0/6", 0),
        ("150/15", 10),
        ("2+6/2", 5),
        ("-10/2", -5),
        ("4^3", 64),
        ("0^0", 1),
        ("2^-3", 0.125),
        ("-5^2", -25),
        ("(-5)^2", 25),
        ("5+21*8-29*(2+2)-4^2^2*2+1000", 545)
    ])
    def test_valid_expressions(self, expr, expected):
        res = calculate_expression(expr)
        assert res == expected

    def test_huge_number_rejected(self):
        # Число из 16 цифр — уже слишком много
        expr = "1111111111111111+1"
        with pytest.raises(OverflowError):
            calculate_expression(expr)

    def test_huge_exponent_rejected(self):
        expr = "2^100"
        with pytest.raises(OverflowError):
            calculate_expression(expr)

    def test_huge_expression_rejected(self):
        # Всё выражение длиннее лимита
        expr = "1111111111+1111111111+1111111111+1111111111+1111111111+1111111111+11111111111111"
        with pytest.raises(OverflowError):
            calculate_expression(expr)

    def test_division_by_zero(self):
        expr = "5/0"
        with pytest.raises(ZeroDivisionError):
            calculate_expression(expr)

    def test_mismatched_parentheses(self):
        expr = "(2+3"
        tokens = tokenize(expr)
        with pytest.raises(ValueError):
            shunting_yard(tokens)
