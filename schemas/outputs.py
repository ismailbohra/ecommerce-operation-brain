from pydantic import BaseModel, Field


class SalesOutput(BaseModel):
    summary: str = Field(description="Brief 1-2 sentence summary")
    total_revenue: float = Field(description="Total revenue in dollars")
    total_orders: int = Field(description="Total number of orders")
    trend: str = Field(description="up, down, or stable")
    key_insight: str = Field(description="Most important finding")
    action_needed: bool = Field(description="Whether action is required")


class InventoryOutput(BaseModel):
    summary: str = Field(description="Brief 1-2 sentence summary")
    out_of_stock_count: int = Field(description="Number of out-of-stock products")
    low_stock_count: int = Field(description="Number of low-stock products")
    critical_items: list[str] = Field(description="List of critical product names")
    action_needed: bool = Field(description="Whether restocking is required")


class SupportOutput(BaseModel):
    summary: str = Field(description="Brief 1-2 sentence summary")
    open_tickets: int = Field(description="Number of open tickets")
    high_priority_count: int = Field(description="Number of high priority tickets")
    top_issue: str = Field(description="Most common issue category")
    action_needed: bool = Field(description="Whether immediate action is required")


class MarketingOutput(BaseModel):
    summary: str = Field(description="Brief 1-2 sentence summary")
    active_campaigns: int = Field(description="Number of active campaigns")
    total_spend: float = Field(description="Total marketing spend")
    avg_ctr: float = Field(description="Average click-through rate percentage")
    underperforming: list[str] = Field(
        description="List of underperforming campaign names"
    )
    action_needed: bool = Field(description="Whether optimization is required")
