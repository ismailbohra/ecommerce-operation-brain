from config import get_inventory_llm
from graph.prompts import AGENT_PROMPTS
from graph.data_fetchers import fetch_inventory_data
from graph.formatters import format_inventory, format_out_of_stock, format_low_stock
from .base import BaseAgent


class InventoryAgent(BaseAgent):
    name = "inventory"

    def get_llm(self):
        return get_inventory_llm()

    def get_prompt(self) -> str:
        return AGENT_PROMPTS["inventory"]

    def fetch_data(self, query: str) -> dict:
        return fetch_inventory_data()

    def format_data(self, data: dict) -> str:
        return f"""
## Inventory Data

Out of Stock ({len(data['out_of_stock'])}):
{format_out_of_stock(data['out_of_stock'])}

Low Stock ({len(data['low_stock'])}):
{format_low_stock(data['low_stock'])}

All Products:
{format_inventory(data['inventory'])}
"""
