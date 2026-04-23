from concurrent.futures import ThreadPoolExecutor, as_completed
from langchain_core.messages import SystemMessage, HumanMessage
from config import get_supervisor_llm, get_action_llm, get_callbacks
from .state import AgentState
from .prompts import ROUTER_PROMPT, SYNTHESIS_PROMPT, ACTION_PROMPT
from .agents import AGENTS
from .actions import build_action_context, parse_actions, execute_action
from .events import emit
from logger import log
from datetime import datetime

VALID_AGENTS = {"sales", "inventory", "support", "marketing", "memory"}


def router_node(state: AgentState) -> AgentState:
    log.info("Router: analyzing query")
    emit("router_start")
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
        emit("router_done", agents=[])
    else:
        agents = [a.strip() for a in response.split(",") if a.strip() in VALID_AGENTS]
        state["agents_to_call"] = agents or ["sales", "memory"]
        state["direct_response"] = False
        log.info(f"Router: calling agents {state['agents_to_call']}")
        emit("router_done", agents=state["agents_to_call"])

    return state


def _run_agent(
    agent_name: str,
    query: str,
    progress_queue=None,
    progress_loop=None,
) -> tuple[str, str]:
    log.info(f"Agent [{agent_name}]: executing")
    # Bind the queue in this worker thread so emit() works here too.
    if progress_queue is not None and progress_loop is not None:
        from .events import bind_queue
        bind_queue(progress_queue, progress_loop)
    emit("agent_start", name=agent_name)
    result = AGENTS[agent_name].run(query)
    log.info(f"Agent [{agent_name}]: completed")
    emit("agent_done", name=agent_name)
    return agent_name, result


def execute_agents_node(state: AgentState) -> AgentState:
    agents_to_call = [a for a in state["agents_to_call"] if a in AGENTS]

    if not agents_to_call:
        state["agent_outputs"] = {}
        return state

    # Capture the queue/loop from the current thread's context so worker threads
    # can emit per-agent progress events.
    from .events import _progress_queue, _progress_loop
    captured_queue = _progress_queue.get(None)
    captured_loop = _progress_loop.get(None)

    emit("agents_start", agents=agents_to_call)
    outputs = {}
    with ThreadPoolExecutor(max_workers=len(agents_to_call)) as executor:
        futures = {
            executor.submit(
                _run_agent, name, state["query"], captured_queue, captured_loop
            ): name
            for name in agents_to_call
        }
        for future in as_completed(futures):
            name, result = future.result()
            outputs[name] = result

    emit("agents_done")
    state["agent_outputs"] = outputs
    return state


def synthesis_node(state: AgentState) -> AgentState:
    log.info("Synthesis: Analyzing findings")
    emit("synthesis_start")
    llm = get_supervisor_llm()
    callbacks = get_callbacks()
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

    response = llm.invoke(messages, config={"callbacks": callbacks}).content
    state["synthesis"] = response
    state["response"] = response
    log.info("Synthesis: completed")
    emit("synthesis_done")
    return state


def action_node(state: AgentState) -> AgentState:
    log.info("Action: analyzing for actions")
    emit("action_start")
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
