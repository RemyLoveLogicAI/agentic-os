"""
Checkpoint factory: returns the right LangGraph checkpointer based on the
deployment environment. Supports DynamoDB (serverless), Postgres (VMs),
and SQLite (local dev).
"""

import os
import sqlite3


def get_checkpointer():
    """Return a LangGraph checkpointer configured for the current environment."""
    backend = os.environ.get("CHECKPOINT_BACKEND", "sqlite").strip().lower()

    if backend == "dynamodb":
        try:
            from langgraph_checkpoint_aws import DynamoDBSaver
        except ImportError:
            raise ImportError(
                "DynamoDB backend requires: pip install langgraph-checkpoint-aws"
            )
        return DynamoDBSaver(
            table_name=os.environ.get("CHECKPOINT_TABLE", "lovelogic-checkpoints"),
            region_name=os.environ.get("AWS_REGION", "us-east-1"),
        )

    if backend == "postgres":
        try:
            import psycopg
            from langgraph.checkpoint.postgres import PostgresSaver
        except ImportError:
            raise ImportError(
                "Postgres backend requires: pip install langgraph-checkpoint-postgres 'psycopg[binary]'"
            )
        conn = psycopg.connect(os.environ["DATABASE_URL"], autocommit=True)
        return PostgresSaver(conn)

    if backend != "sqlite":
        raise ValueError(
            f"Unsupported CHECKPOINT_BACKEND: {backend!r}. "
            "Valid options: 'sqlite', 'dynamodb', 'postgres'."
        )

    # Default: SQLite for local dev
    # Use sqlite3.connect directly to avoid the context-manager form of from_conn_string()
    from langgraph.checkpoint.sqlite import SqliteSaver
    db_path = os.environ.get("SQLITE_CHECKPOINT_PATH", "state/checkpoints.db")
    parent = os.path.dirname(db_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    return SqliteSaver(conn)
