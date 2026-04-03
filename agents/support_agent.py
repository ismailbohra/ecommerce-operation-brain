from .base import BaseAgent
from tools import get_support_tools
from schemas import SupportOutput
from config import Config


class SupportAgent(BaseAgent):
    name = "support"
    model = Config.MODEL_SUPPORT
    prompt_file = "support_agent.md"
    output_schema = SupportOutput

    def _get_tools(self) -> list:
        return get_support_tools()
