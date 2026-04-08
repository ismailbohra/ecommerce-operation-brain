from config import get_marketing_llm
from graph.prompts import AGENT_PROMPTS
from graph.data_fetchers import fetch_marketing_data
from graph.formatters import format_campaigns
from .base import BaseAgent


class MarketingAgent(BaseAgent):
    name = "marketing"

    def get_llm(self):
        return get_marketing_llm()

    def get_prompt(self) -> str:
        return AGENT_PROMPTS["marketing"]

    def fetch_data(self, query: str) -> dict:
        return fetch_marketing_data()

    def format_data(self, data: dict) -> str:
        return f"""
## Marketing Data

Active Campaigns ({len(data['campaigns'])}):
{format_campaigns(data['campaigns'])}
"""
