import asyncio
from datetime import datetime, timedelta

from fastapi import APIRouter

from db import Database

from ..models import (
    InventoryMetrics,
    MarketingMetrics,
    MetricsResponse,
    SalesMetrics,
    SupportMetrics,
)

router = APIRouter()


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics() -> MetricsResponse:
    db = Database()
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)

    sales, out_of_stock, low_stock, tickets, campaigns = await asyncio.gather(
        db.get_sales(week_ago.isoformat(), today.isoformat()),
        db.get_out_of_stock(),
        db.get_low_stock(),
        db.get_open_tickets(),
        db.get_campaigns(),
    )

    revenue = sum((s.get("revenue") or 0) for s in (sales or []))
    orders = sum((s.get("orders") or 0) for s in (sales or []))
    ad_spend = sum((c.get("spent") or 0) for c in (campaigns or []))
    high_priority = len([t for t in tickets if t.get("priority") == "high"])

    return MetricsResponse(
        sales=SalesMetrics(revenue=float(revenue), orders=int(orders)),
        inventory=InventoryMetrics(
            out_of_stock=len(out_of_stock), low_stock=len(low_stock)
        ),
        support=SupportMetrics(open_tickets=len(tickets), high_priority=high_priority),
        marketing=MarketingMetrics(campaigns=len(campaigns), ad_spend=float(ad_spend)),
    )
