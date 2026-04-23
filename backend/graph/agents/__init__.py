from .sales import SalesAgent
from .inventory import InventoryAgent
from .support import SupportAgent
from .marketing import MarketingAgent
from .memory import MemoryAgent

AGENTS = {
    "sales": SalesAgent(),
    "inventory": InventoryAgent(),
    "support": SupportAgent(),
    "marketing": MarketingAgent(),
    "memory": MemoryAgent(),
}

__all__ = [
    "SalesAgent",
    "InventoryAgent",
    "SupportAgent",
    "MarketingAgent",
    "MemoryAgent",
    "AGENTS",
]
