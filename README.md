# AI Agent Backend (Gemini Edition)

Small FastAPI app that routes a natural language query to one of three tools and returns a structured response:
- weather – uses OpenWeatherMap API
- math – evaluates a basic math expression
- llm – answers using Google Gemini

This project intentionally keeps the “agent” logic very simple with a tiny router. You can swap in LangChain or LangGraph later if desired.

## Requirements

- Python 3.10+
- API keys in a `.env` file:

```
GOOGLE_API_KEY=your_google_api_key
OPENWEATHERMAP_API_KEY=your_openweathermap_api_key
# optional override (defaults to gemini-flash-latest in code)
GEMINI_MODEL=gemini-flash-latest
# optional: return ASCII degrees in weather responses (avoids Windows PS 5.1 encoding issues)
WEATHER_ASCII_DEGREES=true
```

## Install and run (local)

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open http://localhost:8000/docs for Swagger UI.

## API

POST /query

Body:

```
{ "query": "What is 42 * 7?" }
```

Responses include:

```
{
	"query": "What is 42 * 7?",
	"tool_used": "math",
	"result": "294"
}
```

Examples:

- Weather

```
{
	"query": "What's the weather like today in Paris?"
}
```

```
{
	"query": "What's the weather like today in Paris?",
	"tool_used": "weather",
	"result": "It's 26°C and sunny in Paris."
}
```
- LLM

```
{
	"query": "Who is the president of France?"
}
```

```
{
	"query": "Who is the president of France?",
	"tool_used": "llm",
	"result": "The president of France is Emmanuel Macron."
}
```

- Math (natural phrase)

```
{
	"query": "Calculate cubic root of 1000?"
}
```

```
{
	"query": "Calculate cubic root of 1000?",
	"tool_used": "math",
	"result": "10.0"
}
```
## Docker

Build and run:

```
docker build -t ai-agent-backend .
docker run -p 8000:8000 --env-file .env ai-agent-backend
```

## Notes

- Math tool uses a very restricted eval and may not support advanced functions. For production, replace with a real parser.
- Weather tool requires a valid OpenWeatherMap API key.
- LLM tool requires a valid Google API key for Gemini.
