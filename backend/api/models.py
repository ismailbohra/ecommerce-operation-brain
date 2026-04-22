from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str
    agents: Optional[list[str]] = None


class ChatRequest(BaseModel):
    query: str
    thread_id: str
    chat_history: list[ChatMessage] = Field(default_factory=list)


class ProposedAction(BaseModel):
    id: str
    type: str
    description: str = ""
    reason: str = ""
    params: dict[str, Any] = Field(default_factory=dict)


class ChatResponse(BaseModel):
    response: str
    agents_consulted: list[str] = Field(default_factory=list)
    proposed_actions: list[ProposedAction] = Field(default_factory=list)
    thread_id: str


class ActionApprovalRequest(BaseModel):
    thread_id: str
    approved_action_ids: list[str]


class ActionApprovalResponse(BaseModel):
    action_results: list[str] = Field(default_factory=list)


class SalesMetrics(BaseModel):
    revenue: float
    orders: int


class InventoryMetrics(BaseModel):
    out_of_stock: int
    low_stock: int


class SupportMetrics(BaseModel):
    open_tickets: int
    high_priority: int


class MarketingMetrics(BaseModel):
    campaigns: int
    ad_spend: float


class MetricsResponse(BaseModel):
    sales: SalesMetrics
    inventory: InventoryMetrics
    support: SupportMetrics
    marketing: MarketingMetrics
