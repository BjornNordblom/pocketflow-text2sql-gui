from __future__ import annotations

from typing import List, Optional, Any
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    natural_query: str = Field(..., min_length=1)
    max_debug_attempts: Optional[int] = Field(None, ge=0, le=10)
    db_path: Optional[str] = None
    include_schema: Optional[bool] = False


class QueryResponse(BaseModel):
    ok: bool
    result: Optional[List[Any]] = None
    error: Optional[str] = None
    generated_sql: Optional[str] = None
    attempts: Optional[int] = None
    schema: Optional[str] = None
