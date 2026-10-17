import operator
import re

PRECEDENCE = {
    '+': 1,
    '-': 1,
    '*': 2,
    '/': 2,
    '^': 3,
    'u-': 3
}

RIGHT_ASSOC = {'^', 'u-'}

OPS = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv,
    '^': operator.pow,
    'u-': None
}

MAX_LEN = 70
MAX_DIGITS = 15
MAX_POW = 15
MAX_EXP = 15
MAX_BASE = 100000    # макс. основание степени
MAX_RESULT = 1e12    # макс. результат операции


def validate_expression(expr: str) -> None:
    if len(expr) > MAX_LEN:
        raise OverflowError(f"МАКС. СИМВОЛОВ В ВЫРАЖЕНИИ: {MAX_LEN}")
    if re.search(r'\d\(', expr) or re.search(r'[+\-*/^]\)', expr):
        raise ValueError("НЕКОРРЕКТНОЕ ВЫРАЖЕНИЕ")
    if '()' in expr:
        raise ValueError("НЕКОРРЕКТНОЕ ВЫРАЖЕНИЕ")

def tokenize(expr: str):
    tokens = []
    i = 0
    n = len(expr)

    number_pattern = re.compile(r"""
        (?:
            \d+(?:\.\d*)?
            | \.\d+
        )
        (?:[eE][+-]?\d+)?
    """, re.VERBOSE)

    while i < n:
        ch = expr[i]
        if ch.isspace():
            i += 1
            continue
        match = number_pattern.match(expr, i)
        if match:
            num_str = match.group(0)
            try:
                num = float(num_str)
            except ValueError:
                raise ValueError(f"НЕКОРРЕКТНОЕ ЧИСЛО: {num_str}")
            digits_only = re.sub(r'[^\d]', '', num_str)
            if len(digits_only) > MAX_DIGITS:
                raise OverflowError(f"МАКС. ЦИФР В ЧИСЛЕ: {MAX_DIGITS}")
            exp_match = re.search(r'[eE]([+-]?\d+)', num_str)
            if exp_match:
                exp_value = int(exp_match.group(1))
                if abs(exp_value) > MAX_EXP:
                    raise OverflowError(
                        f"МАКС. ЭКСПОНЕНТА: {MAX_EXP}"
                    )
            tokens.append(num)
            i = match.end()
            continue
        if ch == '-':
            is_unary = (
                len(tokens) == 0 or
                (isinstance(tokens[-1], str) and tokens[-1] in OPS) or
                tokens[-1] == '(' or
                tokens[-1] == 'u-'
            )
            if is_unary:
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
        raise ValueError(f"НЕДОПУСТИМЫЙ СИМВОЛ: {ch}")
    return tokens

def shunting_yard(tokens):
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
            if not stack or stack[-1] != '(':
                raise ValueError("НЕСБАЛАНСИРОВАННЫЕ СКОБКИ")
            stack.pop()
        else:
            raise ValueError(f"НЕИЗВЕСТНЫЙ ТОКЕН: {token}")
    while stack:
        top = stack.pop()
        if top in '()':
            raise ValueError("НЕСБАЛАНСИРОВАННЫЕ СКОБКИ")
        output.append(top)
    return output

def eval_rpn(rpn):
    stack = []
    for token in rpn:
        if isinstance(token, (int, float)):
            stack.append(token)
        elif token == 'u-':
            if not stack:
                raise ValueError("НЕКОРРЕКТНОЕ ВЫРАЖЕНИЕ")
            stack.append(-stack.pop())
        elif token in OPS:
            if len(stack) < 2:
                raise ValueError("НЕКОРРЕКТНОЕ ВЫРАЖЕНИЕ")
            b = stack.pop()
            a = stack.pop()
            if token == '/' and b == 0:
                raise ZeroDivisionError("НЕЛЬЗЯ ДЕЛИТЬ НА НОЛЬ")
            if token == '^':
                if abs(b) > MAX_POW:
                    raise OverflowError(f"МАКС. ЗНАЧЕНИЕ СТЕПЕНИ: {MAX_POW}")
                if abs(a) > MAX_BASE:
                    raise OverflowError(f"РЕЗУЛЬТАТ СЛИШКОМ БОЛЬШОЙ")
                if a < 0 and b % 1 != 0:
                    raise ValueError("КОМПЛЕКСНЫЕ ЧИСЛА НЕ ПОДДЕРЖИВАЮТСЯ")
            res = OPS[token](a, b)
            stack.append(res)
        else:
            raise ValueError(f"НЕИЗВЕСТНЫЙ ТОКЕН: {token}")
    if len(stack) != 1:
        raise ValueError("НЕКОРРЕКТНОЕ ВЫРАЖЕНИЕ")
    return stack[0]

def calculate_expression(expr: str) -> float:
    validate_expression(expr)
    tokens = tokenize(expr)
    rpn = shunting_yard(tokens)
    return eval_rpn(rpn)
