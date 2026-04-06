import asyncio
import json
import re
from langchain_core.tools import tool
from database import Database


def get_action_tools():

    @tool
    def restock_product(product_id: int, quantity: int) -> str:
        """Restock a product by adding quantity to inventory."""
        return _exec_restock(product_id, quantity)

    @tool
    def pause_campaign(campaign_id: int) -> str:
        """Pause a marketing campaign."""
        return _exec_pause_campaign(campaign_id)

    @tool
    def create_support_ticket(
        subject: str, description: str, category: str, priority: str = "medium"
    ) -> str:
        """Create a new support ticket."""
        return _exec_create_ticket(subject, description, category, priority)

    @tool
    def resolve_ticket(ticket_id: int, resolution: str) -> str:
        """Resolve a support ticket."""
        return _exec_resolve_ticket(ticket_id, resolution)

    @tool
    def apply_discount(product_id: int, discount_percent: float) -> str:
        """Apply a discount to a product."""
        return _exec_apply_discount(product_id, discount_percent)

    return [
        restock_product,
        pause_campaign,
        create_support_ticket,
        resolve_ticket,
        apply_discount,
    ]


def execute_actions_directly(proposals: str) -> list[str]:
    """Parse and execute action proposals directly."""
    results = []

    tools = {
        "restock_product": _exec_restock,
        "pause_campaign": _exec_pause_campaign,
        "create_support_ticket": _exec_create_ticket,
        "resolve_ticket": _exec_resolve_ticket,
        "apply_discount": _exec_apply_discount,
    }

    # Pattern 1: Strict format - action: X, params: {JSON}
    pattern1 = r"action:\s*(\w+)\s*\n\s*params:\s*(\{[^}]+\})"
    matches = re.findall(pattern1, proposals, re.IGNORECASE)

    # Pattern 2: Flexible - action: X ... params: {JSON} (any text between)
    if not matches:
        pattern2 = r"action:\s*(\w+).*?params:\s*(\{[^}]+\})"
        matches = re.findall(pattern2, proposals, re.DOTALL | re.IGNORECASE)

    # Pattern 3: Find any JSON with product_id or campaign_id
    if not matches:
        json_pattern = r'\{[^{}]*"product_id"[^{}]*\}|\{[^{}]*"campaign_id"[^{}]*\}'
        json_matches = re.findall(json_pattern, proposals)
        for json_str in json_matches:
            try:
                params = json.loads(json_str)
                if "product_id" in params and "quantity" in params:
                    matches.append(("restock_product", json_str))
                elif "campaign_id" in params:
                    matches.append(("pause_campaign", json_str))
            except:
                pass

    for action_name, params_str in matches:
        action_name = action_name.strip().lower()
        try:
            # Clean params string
            params_str = params_str.replace("'", '"')
            params = json.loads(params_str)

            if action_name in tools:
                result = tools[action_name](**params)
                results.append(result)
            else:
                results.append(f"❌ Unknown action: {action_name}")
        except Exception as e:
            results.append(f"❌ Error executing {action_name}: {str(e)}")

    if not results:
        # Last resort: Try to find product names and match to IDs
        results.append(
            "❌ Could not parse actions. Please try again with specific product IDs."
        )

    return results


def _exec_restock(product_id: int, quantity: int) -> str:
    db = Database()

    async def _run():
        # Get product info
        product = await db.fetch_one(
            "SELECT name FROM products WHERE id = ?", (product_id,)
        )
        if not product:
            return f"❌ Product ID {product_id} not found."

        # Get current stock
        inventory = await db.fetch_one(
            "SELECT stock_quantity FROM inventory WHERE product_id = ?", (product_id,)
        )

        old_qty = inventory["stock_quantity"] if inventory else 0
        new_qty = old_qty + quantity

        await db.update_stock(product_id, new_qty)
        return f"✅ Restocked '{product['name']}': {old_qty} → {new_qty} units (+{quantity})"

    return asyncio.run(_run())


def _exec_pause_campaign(campaign_id: int) -> str:
    db = Database()

    async def _run():
        result = await db.fetch_one(
            "SELECT name, status FROM marketing_campaigns WHERE id = ?", (campaign_id,)
        )
        if not result:
            return f"❌ Campaign ID {campaign_id} not found."

        await db.pause_campaign(campaign_id)
        return f"✅ Paused campaign '{result['name']}'"

    return asyncio.run(_run())


def _exec_create_ticket(
    subject: str, description: str, category: str, priority: str = "medium"
) -> str:
    db = Database()

    async def _run():
        await db.create_ticket(subject, description, category, priority)
        return f"✅ Created {priority} priority ticket: '{subject}'"

    return asyncio.run(_run())


def _exec_resolve_ticket(ticket_id: int, resolution: str = "") -> str:
    db = Database()

    async def _run():
        await db.execute(
            "UPDATE support_tickets SET status = 'resolved', resolved_at = CURRENT_TIMESTAMP WHERE id = ?",
            (ticket_id,),
        )
        return f"✅ Resolved ticket ID {ticket_id}"

    return asyncio.run(_run())


def _exec_apply_discount(product_id: int, discount_percent: float) -> str:
    db = Database()

    async def _run():
        result = await db.fetch_one(
            "SELECT name, price FROM products WHERE id = ?", (product_id,)
        )
        if not result:
            return f"❌ Product ID {product_id} not found."

        old_price = result["price"]
        new_price = round(old_price * (1 - discount_percent / 100), 2)
        await db.execute(
            "UPDATE products SET price = ? WHERE id = ?", (new_price, product_id)
        )
        return f"✅ Applied {discount_percent}% discount on '{result['name']}': ${old_price} → ${new_price}"

    return asyncio.run(_run())
