# AI Agent Backend (Minimal Router)

A tiny FastAPI backend that routes a natural-language query to one of three tools:

- weather tool (OpenWeatherMap)
- math tool (safe arithmetic evaluator)
- LLM tool (OpenAI; mocked if no key)

It returns a structured JSON response with the tool used and the result.

## Setup

1) Create and activate a virtual environment (optional but recommended).

2) Install dependencies:

```powershell
pip install -r requirements.txt
```

3) Set environment variables (optional to enable external APIs):

- `OPENWEATHER_API_KEY` for OpenWeatherMap
- `OPENAI_API_KEY` for OpenAI
- `DEFAULT_CITY` (optional, defaults to "San Francisco")

Example in PowerShell:

```powershell
$env:OPENWEATHER_API_KEY = "your_openweather_key"
$env:OPENAI_API_KEY = "your_openai_key"
```

4) Run the server:

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API

POST `/query`

Request body:

```json
{
  "query": "What's the weather today in Paris?"
}
```

Response shape:

```json
{
  "query": "What's the weather today in Paris?",
  "tool_used": "weather",
  "result": "It's 26°C and sunny in Paris."
}
```

If no API keys are set, weather and llm responses are mocked with clearly labeled text.

### WebSocket `/ws`

Send a text message with your query. The server first sends a JSON frame announcing the selected tool, then streams text chunks of the result. A final `[END]` message marks completion.

## Examples

- Math

Request:

```json
{ "query": "42 * 7" }
```

Response:

```json
{ "query": "42 * 7", "tool_used": "math", "result": "294" }
```

- Weather (Paris)

Request:

```json
{ "query": "What's the weather like today in Paris?" }
```

Response (example):

```json
{ "query": "What's the weather like today in Paris?", "tool_used": "weather", "result": "It's 26°C and sunny in Paris." }
```

- LLM

Request:

```json
{ "query": "Who is the president of France?" }
```

Response (example):

```json
{ "query": "Who is the president of France?", "tool_used": "llm", "result": "The president of France is Emmanuel Macron." }
```

## Docker

Build and run with Docker:

```powershell
docker build -t ai-agent-backend .
# Optionally pass env vars
docker run -p 8000:8000 -e OPENWEATHER_API_KEY=$env:OPENWEATHER_API_KEY -e OPENAI_API_KEY=$env:OPENAI_API_KEY ai-agent-backend
```

## Tests

```powershell
pytest -q
```

## Notes

- The selector is heuristic: weather keywords outrank math; otherwise falls back to LLM.
- Weather city extraction is naive (looks for "in <City>"). You can extend it with proper NER if desired.
- LLM and weather tools gracefully degrade to mocked responses if no API keys are set.