from langchain_core.messages import HumanMessage
from langchain.agents import create_agent
from config import get_llm


class BaseAgent:
    name: str = "base"
    model: str = "gpt-4o"
    system_prompt: str = "You are a helpful assistant."

    def __init__(self):
        self.llm = get_llm(self.model)
        self.tools = self._get_tools()
        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=self.system_prompt,
        )

    def _get_tools(self) -> list:
        return []

    def invoke(self, query: str) -> str:
        result = self.agent.invoke({"messages": [HumanMessage(content=query)]})
        return result["messages"][-1].content
