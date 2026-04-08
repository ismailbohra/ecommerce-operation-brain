from langchain_core.tools import tool
from db import Database

db = Database()


def _run_async(coro):
    import asyncio

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as pool:
                return pool.submit(asyncio.run, coro).result()
        return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)


@tool
def get_inventory_status() -> str:
    """Get current inventory status for all products including stock levels and reorder points."""
    inventory = _run_async(db.get_inventory())

    if not inventory:
        return "No inventory data available"

    critical = []
    low = []
    ok = []

    for item in inventory:
        stock = item["stock"]
        reorder = item["reorder_level"]
        entry = (
            f"{item['name']} (ID: {item['id']}): {stock} units (reorder at {reorder})"
        )

        if stock == 0:
            critical.append(entry)
        elif stock <= reorder:
            low.append(entry)
        else:
            ok.append(entry)

    lines = [
        "Inventory Status:",
        "",
        f"CRITICAL - Out of Stock ({len(critical)}):",
    ]
    lines.extend([f"  ❌ {item}" for item in critical] or ["  None"])

    lines.extend(["", f"LOW - Below Reorder Level ({len(low)}):"])
    lines.extend([f"  ⚠️ {item}" for item in low] or ["  None"])

    lines.extend(["", f"OK - Adequate Stock ({len(ok)}):"])
    lines.extend([f"  ✓ {item}" for item in ok] or ["  None"])

    return "\n".join(lines)


@tool
def get_out_of_stock_products() -> str:
    """Get list of products that are currently out of stock (zero inventory)."""
    products = _run_async(db.get_out_of_stock())

    if not products:
        return "No products are currently out of stock."

    lines = [f"Out of Stock Products ({len(products)}):"]
    for p in products:
        lines.append(f"  ❌ {p['name']} (ID: {p['id']})")

    return "\n".join(lines)


@tool
def get_low_stock_products() -> str:
    """Get list of products with stock at or below reorder level but not zero."""
    products = _run_async(db.get_low_stock())

    if not products:
        return "No products are currently low on stock."

    lines = [f"Low Stock Products ({len(products)}):"]
    for p in products:
        lines.append(f"  ⚠️ {p['name']} (ID: {p['id']}): {p['stock']} units remaining")

    return "\n".join(lines)


@tool
def get_product_inventory(product_id: int) -> str:
    """Get inventory details for a specific product.

    Args:
        product_id: The product ID to look up.
    """
    inventory = _run_async(db.get_inventory())

    for item in inventory:
        if item["id"] == product_id:
            stock = item["stock"]
            reorder = item["reorder_level"]
            status = (
                "OUT OF STOCK" if stock == 0 else "LOW" if stock <= reorder else "OK"
            )

            return (
                f"Product: {item['name']} (ID: {product_id})\n"
                f"Current Stock: {stock} units\n"
                f"Reorder Level: {reorder} units\n"
                f"Status: {status}"
            )

    return f"Product ID {product_id} not found in inventory."


@tool
def check_stock_for_products(product_ids: list[int]) -> str:
    """Check stock status for multiple products at once.

    Args:
        product_ids: List of product IDs to check.
    """
    inventory = _run_async(db.get_inventory())
    inv_map = {item["id"]: item for item in inventory}

    lines = ["Stock Check Results:", ""]
    for pid in product_ids:
        if pid in inv_map:
            item = inv_map[pid]
            stock = item["stock"]
            status = (
                "❌ OUT"
                if stock == 0
                else "⚠️ LOW" if stock <= item["reorder_level"] else "✓ OK"
            )
            lines.append(f"  {status} {item['name']} (ID: {pid}): {stock} units")
        else:
            lines.append(f"  ❓ Product ID {pid}: Not found")

    return "\n".join(lines)


INVENTORY_TOOLS = [
    get_inventory_status,
    get_out_of_stock_products,
    get_low_stock_products,
    get_product_inventory,
    check_stock_for_products,
]
