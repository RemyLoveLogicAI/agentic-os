"""
Checkpoint factory: returns the right LangGraph checkpointer based on the
deployment environment. Supports DynamoDB (serverless), Postgres (VMs),
and SQLite (local dev).
"""

import os


def get_checkpointer():
    """Return a LangGraph checkpointer configured for the current environment."""
    backend = os.environ.get("CHECKPOINT_BACKEND", "sqlite")

    if backend == "dynamodb":
        from langgraph.checkpoint.dynamodb import DynamoDBSaver
        return DynamoDBSaver(
            table_name=os.environ.get("CHECKPOINT_TABLE", "lovelogic-checkpoints"),
            region_name=os.environ.get("AWS_REGION", "us-east-1"),
        )

    if backend == "postgres":
        from langgraph.checkpoint.postgres import PostgresSaver
        return PostgresSaver.from_conn_string(os.environ["DATABASE_URL"])

    # Default: SQLite for local dev
    from langgraph.checkpoint.sqlite import SqliteSaver
    db_path = os.environ.get("SQLITE_CHECKPOINT_PATH", "state/checkpoints.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    return SqliteSaver.from_conn_string(db_path)
