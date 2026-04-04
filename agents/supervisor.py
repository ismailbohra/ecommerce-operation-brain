from pathlib import Path
from typing import TypedDict
from config import Config, get_llm
from agents import SalesAgent, SupportAgent, InventoryAgent, MarketingAgent, MemoryAgent
from langgraph.graph import StateGraph, START, END
from langchain.messages import SystemMessage, HumanMessage


PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def load_prompt(filename: str) -> str:
    return (PROMPTS_DIR / filename).read_text(encoding="utf-8")


class SupervisorState(TypedDict):
    query: str
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
        # Add nodes
        graph.add_node("router", self._route_query)
        graph.add_node("call_agents", self._call_agents)
        graph.add_node("synthesize", self._synthesize_response)
        # Add edges
        graph.add_edge(START, "router")
        graph.add_edge("router", "call_agents")
        graph.add_edge("call_agents", "synthesize")
        graph.add_edge("synthesize", END)
        return graph.compile()

    # Router Agent
    def _route_query(self, state: SupervisorState) -> SupervisorState:
        query = state["query"].lower()
        routing_prompt = load_prompt("route_prompt.md").format(query)
        response = self.llm.invoke(
            [
                SystemMessage(
                    content="You are a routing assistant. Return only agent names."
                ),
                HumanMessage(content=routing_prompt),
            ]
        )
        content = response.content.lower().split(",")
        agents = [c.strip() for c in content]
        agents = [a for a in agents if a in self.agents]
        if not agents:
            agents = ["sales"]
        state["agents_to_call"] = agents
        return state

    # Agent Invoker
    def _call_agents(self, state: SupervisorState) -> SupervisorState:
        outputs = {}
        for agent_name in state["agents_to_call"]:
            agent = self.agents[agent_name]
            response = agent.invoke(state["query"])
            outputs[agent_name] = response
        state["agent_outputs"] = outputs
        return state

    # Synthesize Agent
    def _synthesize_response(self, state: SupervisorState) -> SupervisorState:
        agent_findings = state["agent_outputs"].items()
        agent_findings = [
            f"[{name.upper()}]: {output}" for name, output in agent_findings
        ]
        agent_findings = "\n\n".join(agent_findings)
        query = state["query"]
        synthesis_prompt = load_prompt("synthesis_prompt.md").format(
            query, agent_findings
        )
        response = self.llm.invoke(
            [SystemMessage(content=self.prompt), HumanMessage(content=synthesis_prompt)]
        )
        state["final_response"] = response.content
        return state

    def invoke(self, query: str) -> dict:
        initial_state = SupervisorState(
            query=query, agents_to_call=[], agent_outputs={}, final_response=""
        )
        result = self.graph.invoke(initial_state)
        return {
            "query": query,
            "agents_consulted": result["agents_to_call"],
            "findings": result["agent_outputs"],
            "response": result["final_response"],
        }
