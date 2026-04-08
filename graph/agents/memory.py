from config import get_memory_llm
from graph.prompts import AGENT_PROMPTS
from graph.data_fetchers import fetch_memory_data
from graph.formatters import format_similar_incidents, format_db_incidents
from .base import BaseAgent


class MemoryAgent(BaseAgent):
    name = "memory"

    def get_llm(self):
        return get_memory_llm()

    def get_prompt(self) -> str:
        return AGENT_PROMPTS["memory"]

    def fetch_data(self, query: str) -> dict:
        return fetch_memory_data(query)

    def format_data(self, data: dict) -> str:
        incident_type = data.get("incident_type")
        type_section = ""
        if incident_type and data["type_specific"]:
            type_section = f"""
Type-Specific ({incident_type}):
{format_similar_incidents(data['type_specific'])}
"""
        return f"""
## Historical Data

Similar Past Incidents (Vector Search):
{format_similar_incidents(data['similar'])}
{type_section}
Recent Incident Log:
{format_db_incidents(data['db_incidents'])}
"""
