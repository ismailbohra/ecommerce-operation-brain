from __future__ import annotations

import asyncio

from langgraph.graph import END, START, StateGraph
from langgraph.types import Send
from logger import log

from .nodes import (
    action_node,
    execute_actions_node,
    inventory_agent_node,
    marketing_agent_node,
    memory_agent_node,
    router_node,
    sales_agent_node,
    support_agent_node,
    synthesis_node,
)
from .state import AgentState

_AGENT_NODES = {
    "sales": "sales_agent",
    "inventory": "inventory_agent",
    "support": "support_agent",
    "marketing": "marketing_agent",
    "memory": "memory_agent",
}


def dispatch_to_agents(state: AgentState):
    """Fan-out via Send to each selected agent node, or go direct to synthesis."""
    if state.get("direct_response", False):
        return "synthesis"
    agents = [a for a in state["agents_to_call"] if a in _AGENT_NODES]
    if not agents:
        return "synthesis"
    return [Send(_AGENT_NODES[name], state) for name in agents]


def should_propose_actions(state: AgentState) -> str:
    if state.get("proposed_actions"):
        return "has_actions"
    return "no_actions"


def create_workflow(checkpointer):
    log.info("Creating workflow graph")
    graph = StateGraph(AgentState)

    # Supervisor nodes
    graph.add_node("router", router_node)
    graph.add_node("synthesis", synthesis_node)
    graph.add_node("action", action_node)
    graph.add_node("execute", execute_actions_node)

    # Per-agent subagent nodes
    graph.add_node("sales_agent", sales_agent_node)
    graph.add_node("inventory_agent", inventory_agent_node)
    graph.add_node("support_agent", support_agent_node)
    graph.add_node("marketing_agent", marketing_agent_node)
    graph.add_node("memory_agent", memory_agent_node)

    # Define flow
    graph.add_edge(START, "router")

    # Router → direct synthesis OR fan-out to individual agent nodes via Send
    graph.add_conditional_edges(
        "router",
        dispatch_to_agents,
        [
            "synthesis",
            "sales_agent",
            "inventory_agent",
            "support_agent",
            "marketing_agent",
            "memory_agent",
        ],
    )

    # Each agent node → synthesis (fan-in: synthesis waits for all dispatched agents)
    for node_name in _AGENT_NODES.values():
        graph.add_edge(node_name, "synthesis")

    graph.add_edge("synthesis", "action")

    # Conditional: if actions proposed, go to execute (with HITL interrupt)
    graph.add_conditional_edges(
        "action", should_propose_actions, {"has_actions": "execute", "no_actions": END}
    )
    graph.add_edge("execute", END)

    # Compile with checkpointer for HITL
    log.info("Workflow graph created")
    return graph.compile(
        checkpointer=checkpointer,
        interrupt_before=["execute"],  # HITL: pause before execution
    )


def run_query(
    workflow,
    query: str,
    thread_id: str,
    chat_history: list = None,
    progress_queue: "asyncio.Queue | None" = None,
    progress_loop: "asyncio.AbstractEventLoop | None" = None,
):
    log.info(f"Running query: {query[:50]}...")

    # Bind the per-request queue so nodes can emit progress events.
    if progress_queue is not None and progress_loop is not None:
        from .events import bind_queue

        bind_queue(progress_queue, progress_loop)

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
    log.info("Query completed")
    return result


def resume_with_actions(workflow, thread_id: str, approved_ids: list[str]):
    log.info(f"Resuming with {len(approved_ids)} approved actions")
    config = {"configurable": {"thread_id": thread_id}}

    # Update state with approved actions and resume
    workflow.update_state(config, {"approved_action_ids": approved_ids})
    result = workflow.invoke(None, config)
    log.info("Actions executed")
    return result
