from .base import BaseAgent
from tools import get_sales_tools
from schemas import SalesOutput
from config import Config


class SalesAgent(BaseAgent):
    name = "sales"
    model = Config.MODEL_SALES
    prompt_file = "sales_agent.md"
    output_schema = SalesOutput

    def _get_tools(self) -> list:
        return get_sales_tools()
