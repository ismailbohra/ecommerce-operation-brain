from concurrent.futures import ThreadPoolExecutor, as_completed
from langchain_core.messages import SystemMessage, HumanMessage
from config import get_supervisor_llm, get_action_llm, get_callbacks
from .state import AgentState
from .prompts import ROUTER_PROMPT, SYNTHESIS_PROMPT, ACTION_PROMPT
from .agents import AGENTS
from .actions import build_action_context, parse_actions, execute_action
from logger import log

VALID_AGENTS = {"sales", "inventory", "support", "marketing", "memory"}


def router_node(state: AgentState) -> AgentState:
    log.info("Router: analyzing query")
    llm = get_supervisor_llm()
    callbacks = get_callbacks()

    messages = [
        SystemMessage(content=ROUTER_PROMPT),
        HumanMessage(
            content=f"Context:\n{state['chat_history']}\n\nQuery: {state['query']}"
        ),
    ]

    response = (
        llm.invoke(messages, config={"callbacks": callbacks}).content.strip().lower()
    )

    if response in ("none", "none."):
        state["agents_to_call"] = []
        state["agent_outputs"] = {}
        state["direct_response"] = True
        log.info("Router: no agents needed")
    else:
        agents = [a.strip() for a in response.split(",") if a.strip() in VALID_AGENTS]
        state["agents_to_call"] = agents or ["sales", "memory"]
        state["direct_response"] = False
        log.info(f"Router: calling agents {state['agents_to_call']}")

    return state


def _run_agent(agent_name: str, query: str) -> tuple[str, str]:
    log.info(f"Agent [{agent_name}]: executing")
    return agent_name, AGENTS[agent_name].run(query)


def execute_agents_node(state: AgentState) -> AgentState:
    agents_to_call = [a for a in state["agents_to_call"] if a in AGENTS]

    if not agents_to_call:
        state["agent_outputs"] = {}
        return state

    outputs = {}
    with ThreadPoolExecutor(max_workers=len(agents_to_call)) as executor:
        futures = {
            executor.submit(_run_agent, name, state["query"]): name
            for name in agents_to_call
        }
        for future in as_completed(futures):
            name, result = future.result()
            outputs[name] = result
            log.info(f"Agent [{name}]: completed")

    state["agent_outputs"] = outputs
    return state


def synthesis_node(state: AgentState) -> AgentState:
    log.info("Synthesis: Analyzing findings")
    llm = get_supervisor_llm()
    callbacks = get_callbacks()
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

    response = llm.invoke(messages, config={"callbacks": callbacks}).content
    state["synthesis"] = response
    state["response"] = response
    log.info("Synthesis: completed")
    return state


def action_node(state: AgentState) -> AgentState:
    log.info("Action: analyzing for actions")
    llm = get_action_llm()
    callbacks = get_callbacks()
    context = build_action_context(state["query"], state["synthesis"])

    messages = [
        SystemMessage(content=ACTION_PROMPT),
        HumanMessage(content=context),
    ]

    response = llm.invoke(messages, config={"callbacks": callbacks})
    state["proposed_actions"] = parse_actions(response.content)
    log.info(f"Action: found {len(state['proposed_actions'])} proposed actions")
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
