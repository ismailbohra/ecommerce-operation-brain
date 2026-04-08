import asyncio
from datetime import datetime, timedelta
from db import Database
from vectorstore import VectorStore

db = Database()


def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as pool:
                return pool.submit(asyncio.run, coro).result()
        return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)


def get_date_range(days: int = 7) -> tuple[str, str]:
    end = datetime.now().date()
    start = end - timedelta(days=days)
    return start.isoformat(), end.isoformat()


# Sales data
def fetch_sales_data(days: int = 7) -> dict:
    start, end = get_date_range(days)
    return {
        "sales": run_async(db.get_sales(start, end)),
        "top_products": run_async(db.get_top_products(start, end)),
        "regions": run_async(db.get_sales_by_region(start, end)),
    }


# Inventory data
def fetch_inventory_data() -> dict:
    return {
        "inventory": run_async(db.get_inventory()),
        "out_of_stock": run_async(db.get_out_of_stock()),
        "low_stock": run_async(db.get_low_stock()),
    }


# Support data
def fetch_support_data() -> dict:
    return {
        "tickets": run_async(db.get_open_tickets()),
        "summary": run_async(db.get_ticket_summary()),
    }


# Marketing data
def fetch_marketing_data() -> dict:
    return {"campaigns": run_async(db.get_campaigns())}


# Memory data
def fetch_memory_data(query: str) -> dict:
    vs = VectorStore()
    incident_type = detect_incident_type(query)

    return {
        "similar": vs.search_incidents(query, limit=5),
        "type_specific": (
            vs.search_incidents_by_type(query, incident_type, limit=3)
            if incident_type
            else []
        ),
        "incident_type": incident_type,
        "db_incidents": run_async(db.get_incidents()),
    }


def detect_incident_type(query: str) -> str | None:
    q = query.lower()
    mapping = {
        "sales_drop": ["sales", "revenue", "drop"],
        "stockout": ["stock", "inventory"],
        "campaign_failure": ["campaign", "marketing", "ctr"],
        "support_spike": ["ticket", "support"],
    }
    for incident_type, keywords in mapping.items():
        if any(k in q for k in keywords):
            return incident_type
    return None


# Action context data
def fetch_action_context() -> dict:
    return {
        "out_of_stock": run_async(db.get_out_of_stock()),
        "low_stock": run_async(db.get_low_stock()),
        "campaigns": run_async(db.get_campaigns()),
        "tickets": run_async(db.get_open_tickets()),
    }
