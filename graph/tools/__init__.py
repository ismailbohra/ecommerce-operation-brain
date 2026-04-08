from .sales import SALES_TOOLS
from .inventory import INVENTORY_TOOLS
from .support import SUPPORT_TOOLS
from .marketing import MARKETING_TOOLS
from .memory import MEMORY_TOOLS

ALL_TOOLS = (
    SALES_TOOLS + INVENTORY_TOOLS + SUPPORT_TOOLS + MARKETING_TOOLS + MEMORY_TOOLS
)

__all__ = [
    "SALES_TOOLS",
    "INVENTORY_TOOLS",
    "SUPPORT_TOOLS",
    "MARKETING_TOOLS",
    "MEMORY_TOOLS",
    "ALL_TOOLS",
]
