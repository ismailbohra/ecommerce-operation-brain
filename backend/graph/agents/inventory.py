from config import get_inventory_llm
from graph.prompts import AGENT_PROMPTS
from graph.tools import INVENTORY_TOOLS
from .base import BaseAgent


class InventoryAgent(BaseAgent):
    name = "inventory"

    def get_llm(self):
        return get_inventory_llm()

    def get_prompt(self) -> str:
        return AGENT_PROMPTS["inventory"]

    def get_tools(self) -> list:
        return INVENTORY_TOOLS
