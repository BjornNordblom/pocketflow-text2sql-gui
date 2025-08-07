from __future__ import annotations

from typing import Any, Dict, Optional

from .db_adapters import get_adapter_for, normalize_to_url
from .deps import call_llm


class Node:
    """
    Minimal Node base compatible with the PocketFlow-style prep/exec/post lifecycle.
    """

    def __init__(self) -> None:
        self._next: Optional["Node"] = None
        self._branches: Dict[str, "Node"] = {}

    def prep(self, shared: Dict[str, Any]) -> Any:
        return None

    def exec(self, prep_res: Any) -> Any:
        return None

    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> Optional[str]:
        return None


def link(a: Node, b: Node) -> None:
    a._next = b


def branch(a: Node, tag: str, b: Node) -> None:
    a._branches[tag] = b


class Flow:
    def __init__(self, start: Node) -> None:
        self.start = start

    def run(self, shared: Dict[str, Any]) -> None:
        node: Optional[Node] = self.start
        while node is not None:
            prep_res = node.prep(shared)
            exec_res = node.exec(prep_res)
            route = node.post(shared, prep_res, exec_res)

            # Branching: if post() returns a tag that matches a branch, follow it
            if route is not None and route in node._branches:
                node = node._branches[route]
                continue

            # Default: proceed to the next node
            node = node._next


class GetSchema(Node):
    def prep(self, shared: Dict[str, Any]) -> str:
        return shared["db_url"]

    def exec(self, db_url_or_path: str) -> str:
        url = normalize_to_url(db_url_or_path)
        adapter = get_adapter_for(url)
        return adapter.get_schema(url)

    def post(self, shared: Dict[str, Any], _: Any, schema: str) -> None:
        shared["schema"] = schema
        return None


class GenerateSQL(Node):
    def prep(self, shared: Dict[str, Any]) -> tuple[str, str]:
        return shared["natural_query"], shared["schema"]

    def exec(self, inputs: tuple[str, str]) -> str:
        nl_query, schema = inputs
        prompt = f"Given schema:\n{schema}\n\nGenerate SQLite query for: {nl_query}\nSQL:"
        try:
            return call_llm(prompt).strip()
        except NotImplementedError:
            # Propagate so FastAPI can return 501
            raise

    def post(self, shared: Dict[str, Any], _: Any, sql: str) -> None:
        shared["generated_sql"] = sql
        return None


class ExecuteSQL(Node):
    def prep(self, shared: Dict[str, Any]) -> tuple[str, str]:
        return shared["db_url"], shared["generated_sql"]

    def exec(self, inputs: tuple[str, str]) -> Dict[str, Any]:
        db_url_or_path, sql = inputs
        try:
            url = normalize_to_url(db_url_or_path)
            adapter = get_adapter_for(url)
            data = adapter.execute(url, sql)
            return {"ok": True, "data": data}
        except NotImplementedError:
            # Bubble up so FastAPI can map to 501 in the route handler
            raise
        except Exception as e:
            return {"ok": False, "err": str(e)}

    def post(self, shared: Dict[str, Any], _: Any, res: Dict[str, Any]) -> Optional[str]:
        if res.get("ok"):
            shared["final_result"] = res["data"]
            return None
        else:
            shared["err"] = res.get("err")
            shared["debug_attempts"] = shared.get("debug_attempts", 0) + 1
            if shared["debug_attempts"] >= shared.get("max_debug_attempts", 3):
                shared["final_error"] = res.get("err")
                return None
            else:
                return "error_retry"


class DebugSQL(Node):
    def prep(self, shared: Dict[str, Any]) -> tuple[str, str, str, str]:
        return (
            shared["natural_query"],
            shared["schema"],
            shared["generated_sql"],
            shared["err"],
        )

    def exec(self, inputs: tuple[str, str, str, str]) -> str:
        nq, schema, bad_sql, err = inputs
        prompt = f"""Original Question: {nq}
Schema:
{schema}

Failed SQL:
{bad_sql}

Error: {err}

Provide the corrected SQLite query:
SQL:
"""
        try:
            return call_llm(prompt).strip()
        except NotImplementedError:
            # Propagate so FastAPI can return 501
            raise

    def post(self, shared: Dict[str, Any], _: Any, fixed_sql: str) -> None:
        shared["generated_sql"] = fixed_sql
        shared.pop("err", None)
        return None


def build_text_to_sql_flow() -> Flow:
    get_schema = GetSchema()
    gen_sql = GenerateSQL()
    exec_sql = ExecuteSQL()
    debug_sql = DebugSQL()

    # Wire default path
    link(get_schema, gen_sql)
    link(gen_sql, exec_sql)

    # Branch on failure
    branch(exec_sql, "error_retry", debug_sql)
    link(debug_sql, exec_sql)

    return Flow(start=get_schema)


def run_text_to_sql(
    natural_query: str,
    db_url: str,
    max_debug_attempts: int,
    include_schema: bool = False,
) -> Dict[str, Any]:
    shared: Dict[str, Any] = {
        "db_url": db_url,
        "natural_query": natural_query,
        "max_debug_attempts": max_debug_attempts,
    }

    flow = build_text_to_sql_flow()
    flow.run(shared)

    result_ok = "final_result" in shared
    attempts = shared.get("debug_attempts", 0)
    return {
        "ok": result_ok,
        "data": shared.get("final_result") if result_ok else None,
        "err": None if result_ok else (shared.get("final_error") or shared.get("err")),
        "sql": shared.get("generated_sql"),
        "attempts": attempts,
        "schema": shared.get("schema") if include_schema else None,
    }
