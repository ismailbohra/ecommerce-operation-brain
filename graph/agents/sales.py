from config import get_sales_llm
from graph.prompts import AGENT_PROMPTS
from graph.data_fetchers import fetch_sales_data
from graph.formatters import format_sales, format_products, format_regions
from .base import BaseAgent


class SalesAgent(BaseAgent):
    name = "sales"

    def get_llm(self):
        return get_sales_llm()

    def get_prompt(self) -> str:
        return AGENT_PROMPTS["sales"]

    def fetch_data(self, query: str) -> dict:
        return fetch_sales_data()

    def format_data(self, data: dict) -> str:
        return f"""
## Sales Data (Last 7 Days)

Daily Summary:
{format_sales(data['sales'])}

Top Products:
{format_products(data['top_products'])}

By Region:
{format_regions(data['regions'])}
"""
