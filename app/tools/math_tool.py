from __future__ import annotations

import ast
import operator as op
from typing import Any


# Supported operators
OPS: dict[type[ast.AST], Any] = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Mod: op.mod,
    ast.Pow: op.pow,
    ast.USub: op.neg,
    ast.UAdd: op.pos,
}


def _eval(node: ast.AST) -> float:
    if isinstance(node, ast.Num):  # type: ignore[attr-defined]
        return node.n  # type: ignore[return-value]
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in OPS:
        left = _eval(node.left)
        right = _eval(node.right)
        return OPS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in OPS:
        operand = _eval(node.operand)
        return OPS[type(node.op)](operand)
    if isinstance(node, ast.Expression):
        return _eval(node.body)
    raise ValueError("Unsupported expression")


def _sanitize_to_expression(text: str) -> str:
    """Extract a math expression from arbitrary text by keeping allowed chars.

    - Keeps digits, operators, decimals, spaces, and parentheses.
    - Converts caret '^' to '**' for exponent.
    - Strips leading/trailing spaces.
    """
    allowed = set("0123456789+-*/%^(). ")
    expr = "".join(ch for ch in text if ch in allowed)
    expr = expr.replace("^", "**").strip()
    return expr


def evaluate_math_expression(text: str) -> str:
    """Safely evaluate a basic arithmetic expression from a query string.

    Supports +, -, *, /, %, ** and parentheses.
    """
    try:
        expr = _sanitize_to_expression(text)
        if not expr:
            raise ValueError("No math expression found")
        parsed = ast.parse(expr, mode="eval")
        result = _eval(parsed)
        # normalize float that are int-like
        if isinstance(result, float) and result.is_integer():
            return str(int(result))
        return str(result)
    except Exception as e:  # noqa: BLE001 - return error as string to caller
        raise ValueError(f"Invalid math expression: {e}")


def is_math_query(query: str) -> bool:
    # Heuristic: if the sanitized expression contains digits and any operator
    sanitized = _sanitize_to_expression(query)
    has_digit = any(c.isdigit() for c in sanitized)
    has_op = any(c in sanitized for c in "+-*/%^")
    keyword = any(kw in query.lower() for kw in ["plus", "minus", "times", "divided by"])
    return (has_digit and has_op) or keyword
