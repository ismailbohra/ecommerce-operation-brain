from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    query: str
    chat_history: Annotated[list, add_messages]

    # Router
    agents_to_call: list[str]
    direct_response: bool

    # Agent responses
    agent_outputs: dict[str, str]

    # Synthesis
    synthesis: str

    # Actions
    proposed_actions: list[dict]
    approved_action_ids: list[str]

    # Results
    response: str
    action_results: list[str]
