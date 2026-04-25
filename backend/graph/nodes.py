from datetime import datetime

from config import get_action_llm, get_supervisor_llm
from langchain_core.messages import HumanMessage, SystemMessage
from logger import log

from .actions import build_action_context, execute_action, parse_actions
from .agents import AGENTS
from .events import emit
from .prompts import ACTION_PROMPT, ROUTER_PROMPT, SYNTHESIS_PROMPT
from .state import AgentState

VALID_AGENTS = {"sales", "inventory", "support", "marketing", "memory"}


def router_node(state: AgentState) -> AgentState:
    log.info("Router: analyzing query")
    emit("router_start")
    llm = get_supervisor_llm()

    messages = [
        SystemMessage(content=ROUTER_PROMPT),
        HumanMessage(
            content=f"Context:\n{state['chat_history']}\n\nQuery: {state['query']}"
        ),
    ]

    response = llm.invoke(messages).content.strip().lower()

    if response in ("none", "none."):
        state["agents_to_call"] = []
        state["agent_outputs"] = {}
        state["direct_response"] = True
        log.info("Router: no agents needed")
        emit("router_done", agents=[])
    else:
        agents = [a.strip() for a in response.split(",") if a.strip() in VALID_AGENTS]
        state["agents_to_call"] = agents or ["sales", "memory"]
        state["direct_response"] = False
        log.info(f"Router: calling agents {state['agents_to_call']}")
        emit("router_done", agents=state["agents_to_call"])

    return state


def _make_agent_node(agent_name: str):
    def node(state: AgentState) -> dict:
        log.info(f"Agent [{agent_name}]: executing")
        emit("agent_start", name=agent_name)
        result = AGENTS[agent_name].run(state["query"])
        log.info(f"Agent [{agent_name}]: completed")
        emit("agent_done", name=agent_name)
        return {"agent_outputs": {agent_name: result}}

    node.__name__ = f"{agent_name}_agent_node"
    return node


sales_agent_node = _make_agent_node("sales")
inventory_agent_node = _make_agent_node("inventory")
support_agent_node = _make_agent_node("support")
marketing_agent_node = _make_agent_node("marketing")
memory_agent_node = _make_agent_node("memory")


def synthesis_node(state: AgentState) -> AgentState:
    log.info("Synthesis: Analyzing findings")
    emit("synthesis_start")
    llm = get_supervisor_llm()
    query = state["query"]
    outputs = state["agent_outputs"]

    today = datetime.now().strftime("%Y-%m-%d")

    if outputs:
        findings = "\n\n---\n\n".join(
            [f"## {k.upper()} Agent\n\n{v}" for k, v in outputs.items()]
        )
        content = f"Context:\n{state['chat_history']}\n\nUser Question: {query}\n\n# Agent Findings\n\n{findings}"
    else:
        content = f"Context:\n{state['chat_history']}\n\nUser Question: {query}"

    messages = [
        SystemMessage(content=f"Today's date is {today}.\n\n{SYNTHESIS_PROMPT}"),
        HumanMessage(content=content),
    ]

    response = llm.invoke(messages).content
    state["synthesis"] = response
    state["response"] = response
    log.info("Synthesis: completed")
    emit("synthesis_done")
    return state


def action_node(state: AgentState) -> AgentState:
    log.info("Action: analyzing for actions")
    emit("action_start")
    llm = get_action_llm()
    context = build_action_context(state["query"], state["synthesis"])

    messages = [
        SystemMessage(content=ACTION_PROMPT),
        HumanMessage(content=context),
    ]

    response = llm.invoke(messages)
    state["proposed_actions"] = parse_actions(response.content)
    log.info(f"Action: found {len(state['proposed_actions'])} proposed actions")
    emit("action_done", count=len(state["proposed_actions"]))
    return state


def execute_actions_node(state: AgentState) -> AgentState:
    approved_ids = state.get("approved_action_ids", [])
    actions = state.get("proposed_actions", [])
    results = []
    log.info(f"Execute: running {len(approved_ids)} approved actions")
    for action in actions:
        if action["id"] in approved_ids:
            try:
                results.append(execute_action(action))
                log.info(f"Execute: {action['type']} - success")
            except Exception as e:
                results.append(f"✗ Failed: {action.get('description')} - {str(e)}")
                log.error(f"Execute: {action['type']} - failed: {e}")

    state["action_results"] = results
    return state
