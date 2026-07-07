from typing import TypedDict, Optional


class AgentState(TypedDict, total=False):
    query: str
    intent: str          # which specialist agent should handle this
    db_context: str       # grounded facts pulled from the database
    raw_data_summary: str
    reply: str
    agent_name: str
    error: Optional[str]
