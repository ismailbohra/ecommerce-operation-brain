from config import get_sales_llm
from graph.prompts import AGENT_PROMPTS
from graph.tools import SALES_TOOLS
from .base import BaseAgent


class SalesAgent(BaseAgent):
    name = "sales"

    def get_llm(self):
        return get_sales_llm()

    def get_prompt(self) -> str:
        return AGENT_PROMPTS["sales"]

    def get_tools(self) -> list:
        return SALES_TOOLS
