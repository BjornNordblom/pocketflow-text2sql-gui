from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .models import QueryRequest, QueryResponse
from .flow_nodes import run_text_to_sql
from .settings import DB_PATH, MAX_DEBUG_ATTEMPTS, OPENROUTER_API_KEY, OPENROUTER_MODEL
from .db_adapters import get_adapter_for, normalize_to_url

app = FastAPI(title="Text-to-SQL Service", version="0.1.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def validate_llm_env():
    # In tests, we allow missing API key because deps.call_llm is monkeypatched.
    import os
    if not OPENROUTER_API_KEY:
        # Only warn instead of raising, so endpoints work in tests/offline.
        print("[startup] Warning: OPENROUTER_API_KEY is not set. LLM calls will fail unless monkeypatched.")
    else:
        # Log selected model
        print(f"[startup] OpenRouter model: {OPENROUTER_MODEL}")


@app.api_route("/health", methods=["GET", "OPTIONS"])
async def health():
    try:
        url = normalize_to_url(DB_PATH)
        # Use sqlite:// form (not sqlite:////...)
        if isinstance(url, str) and url.startswith("sqlite:"):
            # Strip extra slashes
            rest = url[len("sqlite:"):]
            rest_no_slashes = rest.lstrip("/")
            url = f"sqlite://{rest_no_slashes}"
    except Exception:
        url = None
    return {"status": "ok", "db_url": url}


@app.api_route("/schema", methods=["GET", "OPTIONS"])
async def schema(db_path: str | None = None, db_url: str | None = None):
    raw = db_url or db_path or DB_PATH
    try:
        url = normalize_to_url(raw)
        adapter = get_adapter_for(url)
        schema_text = adapter.get_schema(url)
        # Use sqlite:// form (not sqlite:////...)
        if isinstance(url, str) and url.startswith("sqlite:"):
            # Strip extra slashes
            rest = url[len("sqlite:"):]
            rest_no_slashes = rest.lstrip("/")
            url = f"sqlite://{rest_no_slashes}"
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "ok": True,
        "db_url": url,
        "schema": schema_text,
        "has_tables": bool(schema_text.strip()),
        "db_path": url,
    }


@app.post("/query", response_model=QueryResponse)
async def query(req: QueryRequest):
    raw = (req.db_url or req.db_path or DB_PATH)
    db_url = normalize_to_url(raw)
    max_attempts = req.max_debug_attempts if req.max_debug_attempts is not None else MAX_DEBUG_ATTEMPTS
    include_schema = bool(getattr(req, "include_schema", False))
    try:
        res = run_text_to_sql(
            req.natural_query,
            db_url=db_url,
            max_debug_attempts=max_attempts,
            include_schema=include_schema,
        )
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if res["ok"]:
        return QueryResponse(
            ok=True,
            result=res.get("data"),
            error=None,
            generated_sql=res.get("sql"),
            attempts=res.get("attempts"),
            db_schema=res.get("schema"),
            db_url=db_url,
        )
    else:
        return QueryResponse(
            ok=False,
            result=None,
            error=res.get("err"),
            generated_sql=res.get("sql"),
            attempts=res.get("attempts"),
            db_schema=res.get("schema"),
            db_url=db_url,
        )
