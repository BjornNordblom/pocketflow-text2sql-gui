from __future__ import annotations

from typing import List, Optional, Any
from pydantic import BaseModel, Field
from pydantic.config import ConfigDict


class QueryRequest(BaseModel):
    natural_query: str = Field(..., min_length=1)
    max_debug_attempts: Optional[int] = Field(None, ge=0, le=10)
    db_path: Optional[str] = None
    include_schema: Optional[bool] = False
    db_url: Optional[str] = None


class QueryResponse(BaseModel):
    ok: bool
    result: Optional[List[Any]] = None
    error: Optional[str] = None
    generated_sql: Optional[str] = None
    attempts: Optional[int] = None
    db_schema: Optional[str] = Field(default=None, alias="schema")
    db_url: Optional[str] = None

    model_config = ConfigDict(
        validate_by_name=True,   # allow population/validation by attribute name
        populate_by_name=True,   # allow population by attribute name as well
    )
