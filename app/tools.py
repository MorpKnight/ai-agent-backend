import os
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
        return f"It's {round(temp)}°C and {weather_desc} in {city}."
    elif response.status_code == 404:
        return f"Error: City '{city}' not found."
    else:
        return f"Error: Could not retrieve weather for {city}. Status code: {response.status_code}"


def math_tool(expression: str) -> str:
    """Evaluate a basic mathematical expression safely."""
    # Very restricted evaluation using Python's eval with no builtins
    try:
        # Only allow digits, operators and parentheses
        allowed = set("0123456789+-*/(). %")
        if not set(expression).issubset(allowed):
            return "Error: Unsupported characters in expression."
        result = eval(expression, {"__builtins__": None}, {})
        return str(result)
    except Exception as e:
        return f"Error: Invalid math expression. Details: {e}"