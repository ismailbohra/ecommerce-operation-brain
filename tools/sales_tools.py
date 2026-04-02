import asyncio
from datetime import datetime, timedelta
from langchain_core.tools import tool
from database import Database


def get_sales_tools():
    db = Database()

    @tool
    def get_sales_summary(days: int = 7) -> str:
        """Get sales summary for the last N days. Returns daily revenue and order counts."""

        async def _run():
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)
            data = await db.get_sales_summary(
                start_date.isoformat(), end_date.isoformat()
            )
            if not data:
                return "No sales data found for this period."

            result = f"Sales Summary (Last {days} days):\n"
            total_revenue = 0
            total_orders = 0
            for row in data:
                result += f"  {row['sale_date']}: ${row['revenue']:.2f} | {row['total_orders']} orders\n"
                total_revenue += row["revenue"]
                total_orders += row["total_orders"]
            result += f"\nTotal: ${total_revenue:.2f} | {total_orders} orders"
            return result

        return asyncio.run(_run())

    @tool
    def get_sales_for_date(date: str) -> str:
        """Get detailed sales for a specific date. Format: YYYY-MM-DD"""

        async def _run():
            data = await db.get_sales_by_date(date)
            if not data:
                return f"No sales found for {date}"

            total = sum(row["total_amount"] for row in data)
            return f"Sales on {date}: {len(data)} transactions, Total: ${total:.2f}"

        return asyncio.run(_run())

    @tool
    def get_top_products(days: int = 7, limit: int = 5) -> str:
        """Get top selling products by revenue for the last N days."""

        async def _run():
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)
            data = await db.get_top_products_by_revenue(
                start_date.isoformat(), end_date.isoformat(), limit
            )
            if not data:
                return "No product sales data found."

            result = f"Top {limit} Products (Last {days} days):\n"
            for i, row in enumerate(data, 1):
                result += f"  {i}. {row['name']} ({row['category']}): ${row['revenue']:.2f} | {row['units_sold']} units\n"
            return result

        return asyncio.run(_run())

    @tool
    def get_sales_by_region(days: int = 7) -> str:
        """Get sales breakdown by region for the last N days."""

        async def _run():
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)
            data = await db.get_sales_by_region(
                start_date.isoformat(), end_date.isoformat()
            )
            if not data:
                return "No regional sales data found."

            result = f"Sales by Region (Last {days} days):\n"
            for row in data:
                result += f"  {row['region']}: ${row['revenue']:.2f} | {row['orders']} orders\n"
            return result

        return asyncio.run(_run())

    @tool
    def compare_sales_periods(days_ago_start: int, days_ago_end: int) -> str:
        """Compare two time periods. E.g., compare_sales_periods(1, 1) for yesterday vs compare_sales_periods(8, 8) for same day last week."""

        async def _run():
            today = datetime.now().date()

            date1 = today - timedelta(days=days_ago_start)
            date2 = today - timedelta(days=days_ago_end)

            data1 = await db.get_sales_summary(date1.isoformat(), date1.isoformat())
            data2 = await db.get_sales_summary(date2.isoformat(), date2.isoformat())

            rev1 = data1[0]["revenue"] if data1 else 0
            rev2 = data2[0]["revenue"] if data2 else 0

            diff = rev1 - rev2
            pct = ((rev1 - rev2) / rev2 * 100) if rev2 > 0 else 0

            return f"Comparison:\n  {date1}: ${rev1:.2f}\n  {date2}: ${rev2:.2f}\n  Difference: ${diff:.2f} ({pct:+.1f}%)"

        return asyncio.run(_run())

    return [
        get_sales_summary,
        get_sales_for_date,
        get_top_products,
        get_sales_by_region,
        compare_sales_periods,
    ]
