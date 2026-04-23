from config import get_support_llm
from graph.prompts import AGENT_PROMPTS
from graph.tools import SUPPORT_TOOLS
from .base import BaseAgent


class SupportAgent(BaseAgent):
    name = "support"

    def get_llm(self):
        return get_support_llm()

    def get_prompt(self) -> str:
        return AGENT_PROMPTS["support"]

    def get_tools(self) -> list:
        return SUPPORT_TOOLS
