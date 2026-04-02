import asyncio
from langchain_core.tools import tool
from database import Database


def get_inventory_tools():
    db = Database()

    @tool
    def get_inventory_status() -> str:
        """Get current inventory status for all products."""

        async def _run():
            data = await db.get_inventory_status()
            if not data:
                return "No inventory data found."

            result = "Inventory Status:\n"
            for row in data:
                status = (
                    "⚠️ LOW" if row["stock_quantity"] <= row["reorder_level"] else "✓"
                )
                if row["stock_quantity"] == 0:
                    status = "❌ OUT"
                result += f"  {row['name']}: {row['stock_quantity']} units {status}\n"
            return result

        return asyncio.run(_run())

    @tool
    def get_low_stock_products() -> str:
        """Get products that are low on stock (at or below reorder level)."""

        async def _run():
            data = await db.get_low_stock_products()
            if not data:
                return "No low stock products found. All inventory levels are healthy."

            result = f"Low Stock Alert ({len(data)} products):\n"
            for row in data:
                result += f"  {row['name']}: {row['stock_quantity']} units (reorder at {row['reorder_level']})\n"
            return result

        return asyncio.run(_run())

    @tool
    def get_out_of_stock_products() -> str:
        """Get products that are completely out of stock."""

        async def _run():
            data = await db.get_out_of_stock_products()
            if not data:
                return "No out-of-stock products. All products are available."

            result = f"Out of Stock ({len(data)} products):\n"
            for row in data:
                result += f"  ❌ {row['name']} ({row['category']})\n"
            return result

        return asyncio.run(_run())

    @tool
    def check_product_stock(product_name: str) -> str:
        """Check stock level for a specific product by name."""

        async def _run():
            data = await db.get_inventory_status()
            for row in data:
                if product_name.lower() in row["name"].lower():
                    status = (
                        "Available" if row["stock_quantity"] > 0 else "Out of Stock"
                    )
                    return f"{row['name']}: {row['stock_quantity']} units - {status}"
            return f"Product '{product_name}' not found in inventory."

        return asyncio.run(_run())

    @tool
    def get_restock_recommendations() -> str:
        """Get recommendations for products that need restocking."""

        async def _run():
            data = await db.get_low_stock_products()
            if not data:
                return "No restocking needed at this time."

            result = "Restock Recommendations:\n"
            for row in data:
                suggested_qty = row["reorder_level"] * 3
                result += f"  {row['name']}: Order {suggested_qty} units (current: {row['stock_quantity']})\n"
            return result

        return asyncio.run(_run())

    return [
        get_inventory_status,
        get_low_stock_products,
        get_out_of_stock_products,
        check_product_stock,
        get_restock_recommendations,
    ]
