from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import re

from langchain_google_genai import ChatGoogleGenerativeAI

from app.tools import weather_tool, math_tool


load_dotenv()

app = FastAPI(
    title="AI Agent Backend (Gemini Edition)",
    description="Routes natural language queries to the right tool (weather, math, or LLM).",
    version="1.0.0",
)


class QueryRequest(BaseModel):
    query: str


def pick_tool(query: str) -> str:
    """Very simple router to pick which tool to use based on the query text."""
    q = query.lower().strip()

    if "weather" in q or "temperature" in q or "forecast" in q:
        return "weather"

    math_pattern = re.compile(r"^\s*[\d\s()+\-*/%.]+\s*$")
    if math_pattern.match(q):
        return "math"

    if "what is" in q or "calculate" in q:
        if re.search(r"[0-9]", q) and re.search(r"[+\-*/%()]", q):
            return "math"

        phrase_markers = [
            "square root", "sqrt", "cube root", "cubic root", "to the power of", "^", "power of"
        ]
        if any(marker in q for marker in phrase_markers) and re.search(r"[0-9]", q):
            return "math"

    return "llm"


def extract_city(query: str) -> str | None:
    """Heuristic city extractor supporting 'in/at/on CITY' and 'City, Region'."""
    preposition_pat = re.compile(r"\b(in|at|on)\s+([A-Za-z0-9\s\-\.,]+)", re.IGNORECASE)
    last_match = None
    for m in preposition_pat.finditer(query):
        last_match = m
    if last_match:
        candidate = last_match.group(2)
        candidate = re.sub(r"[\?\.!]+$", "", candidate).strip()
        candidate = re.sub(r"\b(today|now|currently|right now)\b\.?$", "", candidate, flags=re.IGNORECASE).strip(
        )
        if candidate:
            return candidate

    comma_loc = re.search(r"([A-Za-z][A-Za-z\s\-]+,\s*[A-Za-z\s\-]+)", query)
    if comma_loc:
        return comma_loc.group(1).strip()

    match = re.search(r"in\s+([A-Za-z\s\-]+)\??$", query, flags=re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None


llm = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_MODEL", "gemini-flash-latest"),
    temperature=0,
)


@app.post("/query")
async def process_query(request: QueryRequest):
    query = request.query

    tool = pick_tool(query)

    if tool == "math":
        expr = query
        m = re.search(r"what is\s+(.+)", query, flags=re.IGNORECASE)
        if not m:
            m = re.search(r"calculate\s+(.+)", query, flags=re.IGNORECASE)
        if m:
            expr = m.group(1).strip()
        expr = re.sub(r"[\?\.!]+$", "", expr).replace(",", "").strip()
        result = math_tool(expr)
        return {"query": query, "tool_used": "math", "result": result}

    if tool == "weather":
        city = extract_city(query) or "San Francisco"
        result = weather_tool(city)
        return {"query": query, "tool_used": "weather", "result": result}

    try:
        ai_msg = llm.invoke(query)
        content = getattr(ai_msg, "content", None) or getattr(ai_msg, "text", None) or str(ai_msg)
    except Exception as e:
        content = f"Error calling LLM: {e}"
    return {"query": query, "tool_used": "llm", "result": content}


@app.get("/")
def health():
    return {"status": "ok"}