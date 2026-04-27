from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages


def _merge_outputs(left: dict, right: dict) -> dict:
    return {**left, **right}


class AgentState(TypedDict):
    query: str
    chat_history: Annotated[list, add_messages]

    # Router
    agents_to_call: list[str]
    direct_response: bool

    # Agent responses (merged across parallel subagent nodes)
    agent_outputs: Annotated[dict[str, str], _merge_outputs]

    # Synthesis
    synthesis: str

    # Actions
    proposed_actions: list[dict]
    approved_action_ids: list[str]

    # Results
    response: str
    action_results: list[str]
