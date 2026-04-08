from langchain_core.messages import SystemMessage, HumanMessage
from config import get_supervisor_llm, get_action_llm
from .state import AgentState
from .prompts import ROUTER_PROMPT, SYNTHESIS_PROMPT, ACTION_PROMPT
from .agents import AGENTS
from .actions import build_action_context, parse_actions, execute_action

VALID_AGENTS = {"sales", "inventory", "support", "marketing", "memory"}


def router_node(state: AgentState) -> AgentState:
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
    else:
        agents = [a.strip() for a in response.split(",") if a.strip() in VALID_AGENTS]
        state["agents_to_call"] = agents or ["sales", "memory"]
        state["direct_response"] = False

    return state


def execute_agents_node(state: AgentState) -> AgentState:
    outputs = {}
    for agent_name in state["agents_to_call"]:
        if agent_name in AGENTS:
            outputs[agent_name] = AGENTS[agent_name].run(state["query"])
    state["agent_outputs"] = outputs
    return state


def synthesis_node(state: AgentState) -> AgentState:
    llm = get_supervisor_llm()
    query = state["query"]
    outputs = state["agent_outputs"]

    if outputs:
        findings = "\n\n---\n\n".join(
            [f"## {k.upper()} Agent\n\n{v}" for k, v in outputs.items()]
        )
        content = f"Context:\n{state['chat_history']}\n\nUser Question: {query}\n\n# Agent Findings\n\n{findings}"
    else:
        content = f"Context:\n{state['chat_history']}\n\nUser Question: {query}"

    messages = [
        SystemMessage(content=SYNTHESIS_PROMPT),
        HumanMessage(content=content),
    ]

    response = llm.invoke(messages).content
    state["synthesis"] = response
    state["response"] = response
    return state


def action_node(state: AgentState) -> AgentState:
    llm = get_action_llm()
    context = build_action_context(state["query"], state["synthesis"])

    messages = [
        SystemMessage(content=ACTION_PROMPT),
        HumanMessage(content=context),
    ]

    response = llm.invoke(messages)
    state["proposed_actions"] = parse_actions(response.content)
    return state


def execute_actions_node(state: AgentState) -> AgentState:
    approved_ids = state.get("approved_action_ids", [])
    actions = state.get("proposed_actions", [])
    results = []

    for action in actions:
        if action["id"] in approved_ids:
            try:
                results.append(execute_action(action))
            except Exception as e:
                results.append(f"✗ Failed: {action.get('description')} - {str(e)}")

    state["action_results"] = results
    return state
