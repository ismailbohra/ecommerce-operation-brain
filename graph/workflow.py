from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from .state import AgentState
from .nodes import (
    router_node,
    execute_agents_node,
    synthesis_node,
    action_node,
    execute_actions_node,
)


def should_propose_actions(state: AgentState) -> str:
    if state.get("proposed_actions"):
        return "has_actions"
    return "no_actions"


def create_workflow():
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("router", router_node)
    graph.add_node("agents", execute_agents_node)
    graph.add_node("synthesis", synthesis_node)
    graph.add_node("action", action_node)
    graph.add_node("execute", execute_actions_node)

    # Define flow
    graph.add_edge(START, "router")
    graph.add_edge("router", "agents")
    graph.add_edge("agents", "synthesis")
    graph.add_edge("synthesis", "action")

    # Conditional: if actions proposed, go to execute (with HITL interrupt)
    graph.add_conditional_edges(
        "action", should_propose_actions, {"has_actions": "execute", "no_actions": END}
    )
    graph.add_edge("execute", END)

    # Compile with checkpointer for HITL
    checkpointer = MemorySaver()
    return graph.compile(
        checkpointer=checkpointer,
        interrupt_before=["execute"],  # HITL: pause before execution
    )


def run_query(workflow, query: str, thread_id: str, chat_history: list = None):
    config = {"configurable": {"thread_id": thread_id}}

    initial_state = {
        "query": query,
        "chat_history": chat_history or [],
        "agents_to_call": [],
        "agent_outputs": {},
        "synthesis": "",
        "proposed_actions": [],
        "approved_action_ids": [],
        "response": "",
        "action_results": [],
    }

    result = workflow.invoke(initial_state, config)
    return result


def resume_with_actions(workflow, thread_id: str, approved_ids: list[str]):
    config = {"configurable": {"thread_id": thread_id}}

    # Update state with approved actions and resume
    workflow.update_state(config, {"approved_action_ids": approved_ids})
    result = workflow.invoke(None, config)
    return result
