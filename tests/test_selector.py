from app.main import select_tool


def test_select_tool_weather():
    assert select_tool("What's the weather like today in Paris?") == "weather"


def test_select_tool_math():
    assert select_tool("What is 42 * 7?") == "math"


def test_select_tool_llm():
    assert select_tool("Who is the president of France?") == "llm"
