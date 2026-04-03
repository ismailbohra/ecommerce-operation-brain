from .base import BaseAgent
from tools import get_marketing_tools
from schemas import MarketingOutput
from config import Config


class MarketingAgent(BaseAgent):
    name = "marketing"
    model = Config.MODEL_MARKETING
    prompt_file = "marketing_agent.md"
    output_schema = MarketingOutput

    def _get_tools(self) -> list:
        return get_marketing_tools()
