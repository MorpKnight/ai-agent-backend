import os
import re
import requests


def weather_tool(city: str) -> str:
    """Fetch the current weather for a given city via OpenWeatherMap API."""
    api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    if not api_key:
        return "Error: OpenWeatherMap API key not found."

    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": api_key, "units": "metric"}

    try:
        response = requests.get(base_url, params=params, timeout=10)
    except Exception as e:
        return f"Error: Weather request failed. Details: {e}"

    if response.status_code == 200:
        data = response.json()
        try:
            main = data["main"]
            weather_desc = data["weather"][0]["description"]
            temp = main["temp"]
        except Exception:
            return "Error: Unexpected weather API response format."
        ascii_deg = os.getenv("WEATHER_ASCII_DEGREES", "").lower() in ("1", "true", "yes", "on")
        unit = "°C" if not ascii_deg else " deg C"
        return f"It's {round(temp)}{unit} and {weather_desc} in {city}."
    elif response.status_code == 404:
        return f"Error: City '{city}' not found."
    else:
        return f"Error: Could not retrieve weather for {city}. Status code: {response.status_code}"


def math_tool(expression: str) -> str:
    """Evaluate a basic mathematical expression safely, with phrase support.

    Supports:
    - Operators: + - * / % and parentheses
    - Phrases: 'square root of N', 'sqrt(N)', 'cubic/cube root of N',
      'N to the power of M', 'power of'
    """
    expr = expression.strip().lower()

    # Handle phrase-based math first
    try:
        # square root / sqrt
        m = re.search(r"(square\s+root|sqrt)\s*(of)?\s*([0-9]+(?:\.[0-9]+)?)", expr)
        if m:
            n = float(m.group(3))
            return str(n ** 0.5)

        # cube/cubic root
        m = re.search(r"(cube|cubic)\s+root\s*(of)?\s*([0-9]+(?:\.[0-9]+)?)", expr)
        if m:
            n = float(m.group(3))
            return str(n ** (1/3))

        # power expressions: 'x to the power of y' or 'power of y'
        m = re.search(r"([0-9]+(?:\.[0-9]+)?)\s+(to\s+the\s+power\s+of|\^)\s*([0-9]+(?:\.[0-9]+)?)", expr)
        if m:
            base = float(m.group(1))
            exp = float(m.group(3))
            return str(base ** exp)

        m = re.search(r"(power\s+of)\s*([0-9]+(?:\.[0-9]+)?)\s*(for\s*)?([0-9]+(?:\.[0-9]+)?)", expr)
        if m:
            exp = float(m.group(2))
            base = float(m.group(4))
            return str(base ** exp)
    except Exception:
        # fall through to safe eval
        pass

    # Safe eval for operator-based math
    try:
        allowed = set("0123456789+-*/(). %")
        if not set(expression).issubset(allowed):
            return "Error: Unsupported characters in expression."
        result = eval(expression, {"__builtins__": None}, {})
        return str(result)
    except Exception as e:
        return f"Error: Invalid math expression. Details: {e}"