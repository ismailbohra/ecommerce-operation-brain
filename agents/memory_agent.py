from .base import BaseAgent
from tools import get_memory_tools
from config import Config


class MemoryAgent(BaseAgent):
    name = "memory"
    model = Config.MODEL_MEMORY
    prompt_file = "memory_agent.md"

    def _get_tools(self) -> list:
        return get_memory_tools()
