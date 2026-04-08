from config import get_support_llm
from graph.prompts import AGENT_PROMPTS
from graph.data_fetchers import fetch_support_data
from graph.formatters import format_tickets, format_ticket_summary
from .base import BaseAgent


class SupportAgent(BaseAgent):
    name = "support"

    def get_llm(self):
        return get_support_llm()

    def get_prompt(self) -> str:
        return AGENT_PROMPTS["support"]

    def fetch_data(self, query: str) -> dict:
        return fetch_support_data()

    def format_data(self, data: dict) -> str:
        return f"""
## Support Data

Open Tickets ({len(data['tickets'])}):
{format_tickets(data['tickets'])}

By Category/Priority:
{format_ticket_summary(data['summary'])}
"""
