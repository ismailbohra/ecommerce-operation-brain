import json
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent
from config import get_llm
from pathlib import Path
from pydantic import BaseModel

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def load_prompt(filename: str) -> str:
    filepath = PROMPTS_DIR / filename
    return filepath.read_text(encoding="utf-8")


class BaseAgent:
    name: str = "base"
    model: str = None
    prompt_file: str = None

    def __init__(self):
        self.llm = get_llm(self.model)
        self.tools = self._get_tools()
        self.prompt = self._load_prompt()
        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=self.prompt,
        )

    def _load_prompt(self) -> str:
        if self.prompt_file:
            return load_prompt(self.prompt_file)
        return "You are a helpful assistant."

    def _get_tools(self) -> list:
        return []

    def invoke(self, query: str) -> str:
        response = self.agent.invoke({"messages": [HumanMessage(content=query)]})
        return response["messages"][-1].content
