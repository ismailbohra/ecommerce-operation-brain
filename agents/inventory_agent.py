from .base import BaseAgent
from tools import get_inventory_tools
from config import Config


class InventoryAgent(BaseAgent):
    name = "inventory"
    model = Config.MODEL_INVENTORY
    prompt_file = "inventory_agent.md"

    def _get_tools(self) -> list:
        return get_inventory_tools()
