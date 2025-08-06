# Text-to-SQL from Scratch (Using PocketFlow!)

*A beginner-friendly guide to turning plain-English questions into precise SQL queries, complete with automatic debugging, in just a few dozen lines of code.*

---

## Why Text-to-SQL?

- Databases hold answers, but SQL can be intimidating for non-experts.  
- Large-Language-Models (LLMs) can bridge the gap by translating natural language → SQL.  
- A smart workflow can even catch and fix its own SQL errors. :contentReference[oaicite:0]{index=0}  

---

## Learning goals

1. **Understand** the four key stages of a Text-to-SQL system  
2. **See** how PocketFlow’s minimal “Node + Flow + Shared Store” design makes those stages explicit  
3. **Build** a complete working prototype that you can adapt to your own database :contentReference[oaicite:1]{index=1}  

---

## 1 · How Text-to-SQL Works

| Stage | Role | Real-world analogy |
|-------|------|--------------------|
| **Schema discovery** | Ask DB for its tables/columns | “Map out the warehouse aisles” |
| **LLM generation**   | Turn question + schema → SQL | “Write the pick-list” |
| **Execution**        | Run SQL, fetch results       | “Walk the aisles and collect items” |
| **Auto-debug loop**  | On error, show message to LLM, retry | “Fix a wrong aisle number and try again” | :contentReference[oaicite:2]{index=2}  

---

## 2 · PocketFlow in 60 seconds

```python
class BaseNode:
    def prep(self, shared): ...
    def exec(self, prep_res): ...
    def post(self, shared, prep_res, exec_res): ...
````

* **Node** = one focused task
* **Flow** = orchestrator that moves from node ➜ node based on each `post()` return value
* **shared** = global dict every node can read/write ([DEV Community][1])

---

## 3 · Implementing the Nodes

### 3.1 GetSchema Node

```python
class GetSchema(Node):
    def prep(self, shared):
        return shared["db_path"]

    def exec(self, db_path):
        conn = sqlite3.connect(db_path)
        cur  = conn.cursor()
        cur.execute("SELECT sql FROM sqlite_master WHERE type='table';")
        schema = "\n".join(row[0] for row in cur.fetchall())
        conn.close()
        return schema

    def post(self, shared, _, schema):
        shared["schema"] = schema        # make it available downstream
```

### 3.2 GenerateSQL Node

```python
class GenerateSQL(Node):
    def prep(self, shared):
        return shared["natural_query"], shared["schema"]

    def exec(self, inputs):
        nl_query, schema = inputs
        prompt = f"Given schema:\n{schema}\n\nGenerate SQLite query for: {nl_query}\nSQL:"
        return call_llm(prompt).strip()

    def post(self, shared, _, sql):
        shared["generated_sql"] = sql
        shared["debug_attempts"] = 0
```

### 3.3 ExecuteSQL Node (with error hook)

```python
class ExecuteSQL(Node):
    def prep(self, shared):
        return shared["db_path"], shared["generated_sql"]

    def exec(self, inputs):
        db_path, sql = inputs
        try:
            conn = sqlite3.connect(db_path)
            cur  = conn.cursor()
            cur.execute(sql)
            data = cur.fetchall()
            conn.close()
            return {"ok": True, "data": data}
        except sqlite3.Error as e:
            if 'conn' in locals(): conn.close()
            return {"ok": False, "err": str(e)}

    def post(self, shared, _, res):
        if res["ok"]:
            shared["final_result"] = res["data"]
        else:
            shared["err"] = res["err"]
            shared["debug_attempts"] = shared.get("debug_attempts", 0) + 1
            if shared["debug_attempts"] >= shared.get("max_debug_attempts", 3):
                shared["final_error"] = res["err"]
            else:
                return "error_retry"        # tell Flow to branch
```

### 3.4 DebugSQL Node

```python
class DebugSQL(Node):
    def prep(self, shared):
        return (
            shared["natural_query"],
            shared["schema"],
            shared["generated_sql"],
            shared["err"]
        )

    def exec(self, inputs):
        nq, schema, bad_sql, err = inputs
        prompt = f"""
Original Question: {nq}
Schema:
{schema}

Failed SQL:
{bad_sql}

Error: {err}

Provide the corrected SQLite query:
SQL:
"""
        return call_llm(prompt).strip()

    def post(self, shared, _, fixed_sql):
        shared["generated_sql"] = fixed_sql
        shared.pop("err", None)            # clear error
```

---

## 4 · Wiring the Flow

```python
get_schema = GetSchema()
gen_sql    = GenerateSQL()
exec_sql   = ExecuteSQL()
debug_sql  = DebugSQL()

# default path
get_schema >> gen_sql >> exec_sql

# branch on failure
exec_sql - "error_retry" >> debug_sql
debug_sql >> exec_sql   # loop back after fix

text_to_sql_flow = Flow(start=get_schema)
```

Run it:

```python
shared = {
    "db_path": "example.db",
    "natural_query": "Show me total sales for June 2025",
    "max_debug_attempts": 3
}

text_to_sql_flow.run(shared)
print(shared.get("final_result") or shared.get("final_error"))
```

---

## 5 · Next steps

1. **Swap SQLite for your DB** – adapt the schema query & connection code.
2. **Tune the prompts** – include examples, enforce stricter output formatting.
3. **Add security** – whitelist tables/columns, parameterize queries to prevent injection.
4. **UI layer** – wrap the flow in a FastAPI or Streamlit app. ([DEV Community][1])

---

### ✨  Conclusion

PocketFlow shows that a resilient Text-to-SQL agent can fit in a single page of Python.
By structuring each concern in its own Node and letting the Flow handle happy-path *and* error-path routing, you get:

* 🔍 **Transparency** – it’s clear which step failed and why
* ♻️ **Reusability** – swap out nodes or loop logic without touching others
* ⚡ **Speed to MVP** – from idea to working prototype in an afternoon

Happy querying!
