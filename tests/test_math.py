from app.tools.math_tool import evaluate_math_expression, is_math_query


def test_basic_operations():
    assert evaluate_math_expression("2 + 2") == "4"
    assert evaluate_math_expression("6 * 7") == "42"
    assert evaluate_math_expression("10 / 2") == "5"
    assert evaluate_math_expression("2 ** 3") == "8"


def test_is_math_query():
    assert is_math_query("42 * 7")
    assert not is_math_query("what's the weather")
