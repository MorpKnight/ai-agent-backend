from __future__ import annotations

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str = Field(..., description="Natural language user query")


class QueryResponse(BaseModel):
    query: str
    tool_used: str
    result: str
