from __future__ import annotations

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from app.schemas import QueryRequest, QueryResponse
from app.tools.math_tool import evaluate_math_expression, is_math_query
from app.tools.weather_tool import fetch_weather, is_weather_query
from app.tools.llm_tool import ask_llm, ask_llm_stream


app = FastAPI(title="AI Agent Router", version="0.1.0")


def select_tool(query: str) -> str:
    if is_weather_query(query):
        return "weather"
    if is_math_query(query):
        return "math"
    return "llm"


@app.post("/query", response_model=QueryResponse)
async def query_endpoint(payload: QueryRequest):
    tool = select_tool(payload.query)
    if tool == "weather":
        result = await fetch_weather(payload.query)
    elif tool == "math":
        try:
            result = evaluate_math_expression(payload.query)
        except ValueError as e:
            return JSONResponse(
                status_code=400,
                content={
                    "query": payload.query,
                    "tool_used": tool,
                    "result": str(e),
                },
            )
    else:
        result = await ask_llm(payload.query)

    return QueryResponse(query=payload.query, tool_used=tool, result=result)


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            data = await ws.receive_text()
            tool = select_tool(data)
            await ws.send_json({"query": data, "tool_used": tool, "result": ""})
            if tool == "weather":
                text = await fetch_weather(data)
                await ws.send_text(text)
            elif tool == "math":
                try:
                    text = evaluate_math_expression(data)
                except Exception as e:  # noqa: BLE001
                    text = str(e)
                await ws.send_text(text)
            else:
                async for chunk in ask_llm_stream(data):
                    await ws.send_text(chunk)
            await ws.send_text("[END]")
    except WebSocketDisconnect:
        return
