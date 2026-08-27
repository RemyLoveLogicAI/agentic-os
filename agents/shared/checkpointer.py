import os

from langgraph.checkpoint.memory import MemorySaver

try:
    import boto3
    from langgraph_checkpoint_aws import DynamoDBSaver
    _HAS_DYNAMO = True
except ImportError:
    _HAS_DYNAMO = False


def get_checkpointer():
    """Return the best available checkpointer based on CHECKPOINT_BACKEND env var."""
    backend = os.getenv("CHECKPOINT_BACKEND", "memory")

    if backend == "dynamodb":
        if not _HAS_DYNAMO:
            raise RuntimeError(
                "CHECKPOINT_BACKEND=dynamodb but langgraph-checkpoint-aws is not installed. "
                "Run: pip install 'langgraph-checkpoint-aws>=2.0.0'"
            )
        table = os.getenv("LANGGRAPH_CHECKPOINT_TABLE", "lovelogic-checkpoints")
        region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        return DynamoDBSaver(
            table_name=table,
            boto3_client=boto3.client("dynamodb", region_name=region),
        )

    return MemorySaver()
