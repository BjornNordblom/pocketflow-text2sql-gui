from pocketflow import Flow, Node
from nodes import GetSchema, GenerateSQL, ExecuteSQL, DebugSQL

def create_text_to_sql_flow():
    """Create the text-to-SQL workflow with a debug loop."""
    get_schema_node = GetSchema()
    generate_sql_node = GenerateSQL()
    execute_sql_node = ExecuteSQL()
    debug_sql_node = DebugSQL()

    # Main path and debug loop
    get_schema_node >> generate_sql_node >> execute_sql_node
    execute_sql_node - "error_retry" >> debug_sql_node
    debug_sql_node >> execute_sql_node

    text_to_sql_flow = Flow(start=get_schema_node)
    return text_to_sql_flow
