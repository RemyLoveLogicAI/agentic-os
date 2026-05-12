from typing import Annotated, Optional
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    workspace_id: str
    session_id: str
    task: str
    cost_usd: float
    turn_count: int
    memory_artifacts: list
    last_compaction: Optional[str]
    error: Optional[str]
