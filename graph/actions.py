import json
import uuid
import asyncio
from db import Database

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


def build_action_context(query: str, synthesis: str) -> str:
    # ctx = fetch_action_context()
    return f"""
## User Request
{query}

## Analysis Summary
{synthesis}
"""


def parse_actions(content: str) -> list[dict]:
    try:
        content = content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        start = content.find("[")
        end = content.rfind("]") + 1
        if start == -1 or end == 0:
            return []

        actions = json.loads(content[start:end])
        for action in actions:
            action["id"] = str(uuid.uuid4())[:8]
        return actions
    except:
        return []


def execute_action(action: dict) -> str:
    action_type = action.get("type")
    params = action.get("params", {})

    handlers = {
        "restock": _handle_restock,
        "pause_campaign": _handle_pause_campaign,
        "discount": _handle_discount,
        "create_ticket": _handle_create_ticket,
        "resolve_ticket": _handle_resolve_ticket,
    }

    handler = handlers.get(action_type)
    if handler:
        return handler(params)
    return f"⚠ Unknown action: {action_type}"


def _handle_restock(params: dict) -> str:
    run_async(db.update_stock(params["product_id"], params.get("quantity", 50)))
    return f"✓ Restocked {params.get('name', 'product')} with {params.get('quantity', 50)} units"


def _handle_pause_campaign(params: dict) -> str:
    run_async(db.pause_campaign(params["campaign_id"]))
    return f"✓ Paused campaign: {params.get('name', 'campaign')}"


def _handle_discount(params: dict) -> str:
    run_async(db.apply_discount(params["product_id"], params.get("percent", 10)))
    return f"✓ Applied {params.get('percent', 10)}% discount to {params.get('name', 'product')}"


def _handle_create_ticket(params: dict) -> str:
    run_async(
        db.create_ticket(
            params.get("subject", "New Ticket"),
            params.get("description", ""),
            params.get("category", "general"),
            params.get("priority", "medium"),
        )
    )
    return f"✓ Created ticket: {params.get('subject', 'New Ticket')}"


def _handle_resolve_ticket(params: dict) -> str:
    run_async(db.resolve_ticket(params["ticket_id"]))
    return f"✓ Resolved ticket #{params['ticket_id']}"
