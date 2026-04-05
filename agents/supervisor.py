from pathlib import Path
from typing import TypedDict
from config import Config, get_llm
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import SystemMessage, HumanMessage

from .sales_agent import SalesAgent
from .support_agent import SupportAgent
from .inventory_agent import InventoryAgent
from .marketing_agent import MarketingAgent
from .memory_agent import MemoryAgent


PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def load_prompt(filename: str) -> str:
    return (PROMPTS_DIR / filename).read_text(encoding="utf-8")


class SupervisorState(TypedDict):
    query: str
    chat_history: str
    query_type: str
    agents_to_call: list[str]
    agent_outputs: dict[str, str]
    final_response: str


class Supervisor:

    def __init__(self):
        self.llm = get_llm(Config.MODEL_SUPERVISOR)
        self.prompt = load_prompt("supervisor.md")
        self.agents = {
            "sales": SalesAgent(),
            "inventory": InventoryAgent(),
            "support": SupportAgent(),
            "marketing": MarketingAgent(),
            "memory": MemoryAgent(),
        }
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(SupervisorState)
        graph.add_node("classify", self._classify_query)
        graph.add_node("router", self._route_query)
        graph.add_node("call_agents", self._call_agents)
        graph.add_node("synthesize", self._synthesize_response)
        graph.add_edge(START, "classify")
        graph.add_edge("classify", "router")
        graph.add_edge("router", "call_agents")
        graph.add_edge("call_agents", "synthesize")
        graph.add_edge("synthesize", END)
        return graph.compile()

    def _classify_query(self, state: SupervisorState) -> SupervisorState:
        query_lower = state["query"].lower()

        simple_keywords = [
            "list",
            "show",
            "what is",
            "how many",
            "count",
            "status",
            "current",
        ]
        complex_keywords = [
            "why",
            "analyze",
            "compare",
            "explain",
            "what happened",
            "root cause",
            "recommend",
            "should",
            "fix",
            "do with",
        ]

        is_simple = any(kw in query_lower for kw in simple_keywords)
        is_complex = any(kw in query_lower for kw in complex_keywords)

        state["query_type"] = "complex" if is_complex and not is_simple else "simple"
        return state

    def _route_query(self, state: SupervisorState) -> SupervisorState:
        # Include chat history for context
        context = ""
        if state["chat_history"]:
            context = f"\nRecent conversation:\n{state['chat_history']}\n"

        routing_prompt = f"""{context}
Current query: {state["query"]}

{load_prompt("route_prompt.md").format(state["query"])}"""

        response = self.llm.invoke(
            [
                SystemMessage(
                    content="You are a routing assistant. Return only agent names or 'none'."
                ),
                HumanMessage(content=routing_prompt),
            ]
        )
        content = response.content.lower().strip()

        if content == "none":
            state["agents_to_call"] = []
            return state

        agents = [a.strip() for a in content.split(",")]
        agents = [a for a in agents if a in self.agents]
        state["agents_to_call"] = agents
        return state

    def _call_agents(self, state: SupervisorState) -> SupervisorState:
        # Include chat history in agent queries for context
        query_with_context = state["query"]
        if state["chat_history"]:
            query_with_context = f"Context from conversation:\n{state['chat_history']}\n\nCurrent question: {state['query']}"

        outputs = {}
        for agent_name in state["agents_to_call"]:
            agent = self.agents[agent_name]
            response = agent.invoke(query_with_context)
            outputs[agent_name] = response
        state["agent_outputs"] = outputs
        return state

    def _synthesize_response(self, state: SupervisorState) -> SupervisorState:
        agent_findings = "\n\n".join(
            [
                f"[{name.upper()}]: {output}"
                for name, output in state["agent_outputs"].items()
            ]
        )

        # Include chat history for context
        context = ""
        if state["chat_history"]:
            context = f"Recent conversation:\n{state['chat_history']}\n\n"

        if state["query_type"] == "simple":
            synthesis_prompt = f"""{context}User Query: {state["query"]}

Agent Findings:
{agent_findings}

Provide a SHORT, DIRECT answer. Use conversation context to understand references like "this", "that", "it"."""
        else:
            synthesis_prompt = f"""{context}{load_prompt("synthesis_prompt.md").format(state["query"], agent_findings)}

Use conversation context to understand references like "this", "that", "it"."""

        response = self.llm.invoke(
            [SystemMessage(content=self.prompt), HumanMessage(content=synthesis_prompt)]
        )
        state["final_response"] = response.content
        return state

    def invoke(self, query: str, chat_history: list[dict] = None) -> dict:
        # Format chat history
        history_str = ""
        if chat_history:
            recent = chat_history[-6:]  # Last 3 exchanges
            history_str = "\n".join(
                [
                    f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content'][:200]}"
                    for m in recent
                ]
            )

        initial_state = SupervisorState(
            query=query,
            chat_history=history_str,
            query_type="simple",
            agents_to_call=[],
            agent_outputs={},
            final_response="",
        )
        result = self.graph.invoke(initial_state)
        return {
            "query": query,
            "agents_consulted": result["agents_to_call"],
            "findings": result["agent_outputs"],
            "response": result["final_response"],
        }
