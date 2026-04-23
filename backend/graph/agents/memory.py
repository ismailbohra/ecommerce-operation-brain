from config import get_memory_llm
from graph.prompts import AGENT_PROMPTS
from graph.tools import MEMORY_TOOLS
from .base import BaseAgent


class MemoryAgent(BaseAgent):
    name = "memory"

    def get_llm(self):
        return get_memory_llm()

    def get_prompt(self) -> str:
        return AGENT_PROMPTS["memory"]

    def get_tools(self) -> list:
        return MEMORY_TOOLS
