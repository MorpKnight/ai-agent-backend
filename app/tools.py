import requests
import os
from langchain.tools import tool

@tool
def weather_tool(city: str) -> str:
    api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    if not api_key:
        return "Error: OpenWeatherMap API key not found."
    
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": api_key, "units": "metric"}
    
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        main = data['main']
        weather_desc = data['weather'][0]['description']
        temp = main['temp']
        return f"The weather in {city} is currently {weather_desc} with a temperature of {temp}°C."
    else:
        return f"Error: Could not retrieve weather for {city}. Status code: {response.status_code}"

@tool
def math_tool(expression: str) -> str:
    try:
        result = eval(expression, {"__builtins__": None}, {})
        return str(result)
    except Exception as e:
        return f"Error: Invalid math expression. Details: {e}"