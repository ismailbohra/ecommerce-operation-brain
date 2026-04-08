from config import get_marketing_llm
from graph.prompts import AGENT_PROMPTS
from graph.tools import MARKETING_TOOLS
from .base import BaseAgent


class MarketingAgent(BaseAgent):
    name = "marketing"

    def get_llm(self):
        return get_marketing_llm()

    def get_prompt(self) -> str:
        return AGENT_PROMPTS["marketing"]

    def get_tools(self) -> list:
        return MARKETING_TOOLS
