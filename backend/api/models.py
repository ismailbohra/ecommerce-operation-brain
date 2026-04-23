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


# ------------------------------------------------------------------ #
# Sessions
# ------------------------------------------------------------------ #


class SessionListItem(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str


class SessionMessage(BaseModel):
    id: str
    role: str
    content: str
    agents: list[str] = Field(default_factory=list)
    actions: Optional[list[dict[str, Any]]] = None
    action_results: Optional[list[str]] = None
    created_at: str


class SessionDetail(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str
    messages: list[SessionMessage] = Field(default_factory=list)


class CreateSessionRequest(BaseModel):
    session_id: str
    title: str = "New Chat"


class RenameSessionRequest(BaseModel):
    title: str
