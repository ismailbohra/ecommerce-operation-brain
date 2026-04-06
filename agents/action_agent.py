from .base import BaseAgent
from tools import get_action_tools, get_inventory_tools
from config import Config


class ActionAgent(BaseAgent):
    name = "action"
    model = Config.MODEL_SUPERVISOR
    prompt_file = "action_agent.md"

    def _get_tools(self) -> list:
        # Both action tools AND inventory lookup tools
        return get_action_tools() + get_inventory_tools()

    def propose(self, context: str) -> str:
        query = f"""Based on this context, propose specific actions to fix the issues.

Context:
{context}

Steps:
1. First, use get_out_of_stock_products or get_low_stock_products to find product IDs
2. Then propose actions with exact product IDs

Use this EXACT format for each action:

ACTION_PROPOSAL:
action: restock_product
params: {{"product_id": <id>, "quantity": <qty>}}
reason: <why>

DO NOT ask for product IDs - look them up yourself using tools."""
        return self.invoke(query)

    def execute(self, action_description: str) -> str:
        query = f"""Execute this approved action:
{action_description}

Use the appropriate tool to execute. Confirm completion."""
        return self.invoke(query)
