import operator

PRECEDENCE = {
    '+': 1,
    '-': 1,
    '*': 2,
    '/': 2,
    'u-': 3,
    '^': 4,
}

RIGHT_ASSOC = {'^'}

OPS = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv,
    '^': operator.pow,
    'u-': None
}

def tokenize(expr: str):
    """Разбивает строку на токены: числа, операторы, скобки."""
    tokens = []
    i = 0
    n = len(expr)
    while i < n:
        ch = expr[i]
        if ch.isspace():
            i += 1
            continue
        if ch.isdigit() or ch == '.':
            start = i
            has_dot = (ch == '.')
            i += 1
            while i < n and (expr[i].isdigit() or (expr[i] == '.' and not has_dot)):
                if expr[i] == '.':
                    has_dot = True
                i += 1
            num_str = expr[start:i]
            tokens.append(float(num_str) if '.' in num_str else int(num_str))
            continue
        if ch in '-':
            is_unary = (
                len(tokens) == 0 or
                (isinstance(tokens[-1], str) and tokens[-1] in OPS) or
                tokens[-1] == '(' or
                tokens[-1] == 'u-'
            )
            if is_unary:
                if ch == '-':
                    tokens.append('u-')
                i += 1
                continue
            else:
                tokens.append(ch)
                i += 1
                continue
        if ch in OPS or ch in '()':
            tokens.append(ch)
            i += 1
            continue
        raise ValueError(f"Недопустимый символ: {ch}")
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
    """Вычисляет постфиксное выражение (RPN)"""
    stack = []
    for token in rpn:
        if isinstance(token, (int, float)):
            stack.append(token)
        elif token == 'u-':
            if not stack:
                raise ValueError("Некорректное выражение")
            stack.append(-stack.pop())
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
