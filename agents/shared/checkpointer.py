import os

from langgraph.checkpoint.memory import MemorySaver

try:
    import boto3
    from langgraph.checkpoint.dynamodb import DynamoDBSaver
    _HAS_DYNAMO = True
except ImportError:
    _HAS_DYNAMO = False


def get_checkpointer():
    """Return the best available checkpointer based on CHECKPOINT_BACKEND env var."""
    backend = os.getenv("CHECKPOINT_BACKEND", "memory")

    if backend == "dynamodb" and _HAS_DYNAMO:
        table = os.getenv("LANGGRAPH_CHECKPOINT_TABLE", "lovelogic-checkpoints")
        region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        return DynamoDBSaver(
            table_name=table,
            boto3_client=boto3.client("dynamodb", region_name=region),
        )

    return MemorySaver()
