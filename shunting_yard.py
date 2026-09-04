import re
import operator

PRECEDENCE = {
    '+': 1,
    '-': 1,
    '*': 2,
    '/': 2,
    '^': 3,
}

RIGHT_ASSOC = {'^'}

OPS = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv,
    '^': operator.pow,
}

def tokenize(expr: str):
    """Разбивает строку на токены: числа, операторы, скобки."""
    token_pattern = r'\s*(?:(\d+(?:\.\d+)?)|([+\-*/^()]))\s*'
    tokens = []
    pos = 0
    while pos < len(expr):
        m = re.match(token_pattern, expr[pos:])
        if not m:
            raise ValueError(f"Недопустимый символ в позиции {pos}: {expr[pos]}")
        num, op = m.groups()
        if num is not None:
            tokens.append(float(num) if '.' in num else int(num))
        elif op is not None:
            tokens.append(op)
        pos += m.end()
    return tokens

def shunting_yard(tokens):
    """Преобразует инфиксные токены в постфиксные (RPN)."""
    output = []
    stack = []

    for token in tokens:
        if isinstance(token, (int, float)):
            output.append(token)
        elif token in OPS:
            while stack and stack[-1] in OPS:
                top = stack[-1]
                if ((token not in RIGHT_ASSOC and PRECEDENCE[token] <= PRECEDENCE[top]) or
                    (token in RIGHT_ASSOC and PRECEDENCE[token] < PRECEDENCE[top])):
                    output.append(stack.pop())
                else:
                    break
            stack.append(token)
        elif token == '(':
            stack.append(token)
        elif token == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            if not stack:
                raise ValueError("Несбалансированные скобки")
            stack.pop()
        else:
            raise ValueError(f"Неизвестный токен: {token}")

    while stack:
        top = stack.pop()
        if top in '()':
            raise ValueError("Несбалансированные скобки")
        output.append(top)

    return output

def eval_rpn(rpn):
    """Вычисляет постфиксное выражение (RPN) безопасно, без eval."""
    stack = []
    for token in rpn:
        if isinstance(token, (int, float)):
            stack.append(token)
        elif token in OPS:
            if len(stack) < 2:
                raise ValueError("Некорректное выражение")
            b = stack.pop()
            a = stack.pop()
            if token == '/' and b == 0:
                raise ZeroDivisionError("Деление на ноль")
            res = OPS[token](a, b)
            stack.append(res)
        else:
            raise ValueError(f"Неизвестный токен в RPN: {token}")
    if len(stack) != 1:
        raise ValueError("Некорректное выражение")
    return stack[0]

def calculate_expression(expr: str) -> float:
    """Главная функция: парсит, конвертирует, считает."""
    tokens = tokenize(expr)
    rpn = shunting_yard(tokens)
    return eval_rpn(rpn)
