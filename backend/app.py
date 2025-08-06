from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .models import QueryRequest, QueryResponse
from .flow_nodes import run_text_to_sql
from .settings import DB_PATH, MAX_DEBUG_ATTEMPTS

app = FastAPI(title="Text-to-SQL Service", version="0.1.0")

# Enable CORS so the browser can perform preflight OPTIONS and actual requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Consider restricting to known origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.api_route("/health", methods=["GET", "OPTIONS"])
async def health():
    return {"status": "ok"}


@app.post("/query", response_model=QueryResponse)
async def query(req: QueryRequest):
    db_path = req.db_path or DB_PATH
    max_attempts = req.max_debug_attempts if req.max_debug_attempts is not None else MAX_DEBUG_ATTEMPTS
    include_schema = bool(getattr(req, "include_schema", False))
    try:
        res = run_text_to_sql(
            req.natural_query,
            db_path=db_path,
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
            schema=res.get("schema"),
        )
    else:
        return QueryResponse(
            ok=False,
            result=None,
            error=res.get("err"),
            generated_sql=res.get("sql"),
            attempts=res.get("attempts"),
            schema=res.get("schema"),
        )
