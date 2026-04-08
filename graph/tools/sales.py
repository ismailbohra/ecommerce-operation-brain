from datetime import datetime, timedelta
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


def _parse_date(date_str: str | None, default_days_ago: int = 0) -> str:
    if date_str:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date().isoformat()
        except ValueError:
            pass
    return (datetime.now().date() - timedelta(days=default_days_ago)).isoformat()


@tool
def get_sales_summary(start_date: str = None, end_date: str = None) -> str:
    """Get daily sales summary (revenue and order count) for a date range.

    Args:
        start_date: Start date in YYYY-MM-DD format. Defaults to 7 days ago.
        end_date: End date in YYYY-MM-DD format. Defaults to today.
    """
    start = _parse_date(start_date, default_days_ago=7)
    end = _parse_date(end_date, default_days_ago=0)

    sales = _run_async(db.get_sales(start, end))

    if not sales:
        return f"No sales data found between {start} and {end}"

    total_revenue = sum(s["revenue"] or 0 for s in sales)
    total_orders = sum(s["orders"] or 0 for s in sales)

    lines = [
        f"Sales Summary ({start} to {end}):",
        f"Total Revenue: ${total_revenue:,.2f}",
        f"Total Orders: {total_orders}",
        "",
        "Daily Breakdown:",
    ]
    for s in sorted(sales, key=lambda x: x["sale_date"], reverse=True):
        lines.append(
            f"  {s['sale_date']}: ${s['revenue'] or 0:,.2f} ({s['orders'] or 0} orders)"
        )

    return "\n".join(lines)


@tool
def get_top_products(
    start_date: str = None, end_date: str = None, limit: int = 5
) -> str:
    """Get top selling products by revenue for a date range.

    Args:
        start_date: Start date in YYYY-MM-DD format. Defaults to 7 days ago.
        end_date: End date in YYYY-MM-DD format. Defaults to today.
        limit: Number of top products to return. Defaults to 5.
    """
    start = _parse_date(start_date, default_days_ago=7)
    end = _parse_date(end_date, default_days_ago=0)

    products = _run_async(db.get_top_products(start, end, limit))

    if not products:
        return f"No product sales data found between {start} and {end}"

    lines = [f"Top {limit} Products ({start} to {end}):", ""]
    for i, p in enumerate(products, 1):
        lines.append(f"{i}. {p['name']} (ID: {p['id']})")
        lines.append(
            f"   Revenue: ${p['revenue'] or 0:,.2f} | Units Sold: {p['units'] or 0}"
        )

    return "\n".join(lines)


@tool
def get_sales_by_region(start_date: str = None, end_date: str = None) -> str:
    """Get sales breakdown by region for a date range.

    Args:
        start_date: Start date in YYYY-MM-DD format. Defaults to 7 days ago.
        end_date: End date in YYYY-MM-DD format. Defaults to today.
    """
    start = _parse_date(start_date, default_days_ago=7)
    end = _parse_date(end_date, default_days_ago=0)

    regions = _run_async(db.get_sales_by_region(start, end))

    if not regions:
        return f"No regional sales data found between {start} and {end}"

    total = sum(r["revenue"] or 0 for r in regions)

    lines = [f"Sales by Region ({start} to {end}):", f"Total: ${total:,.2f}", ""]
    for r in sorted(regions, key=lambda x: x["revenue"] or 0, reverse=True):
        pct = ((r["revenue"] or 0) / total * 100) if total > 0 else 0
        lines.append(
            f"  {r['region']}: ${r['revenue'] or 0:,.2f} ({pct:.1f}%) - {r['orders'] or 0} orders"
        )

    return "\n".join(lines)


@tool
def compare_sales_periods(
    period1_start: str, period1_end: str, period2_start: str, period2_end: str
) -> str:
    """Compare sales between two time periods.

    Args:
        period1_start: Start date of first period (YYYY-MM-DD).
        period1_end: End date of first period (YYYY-MM-DD).
        period2_start: Start date of second period (YYYY-MM-DD).
        period2_end: End date of second period (YYYY-MM-DD).
    """
    p1_start = _parse_date(period1_start)
    p1_end = _parse_date(period1_end)
    p2_start = _parse_date(period2_start)
    p2_end = _parse_date(period2_end)

    sales1 = _run_async(db.get_sales(p1_start, p1_end))
    sales2 = _run_async(db.get_sales(p2_start, p2_end))

    rev1 = sum(s["revenue"] or 0 for s in sales1) if sales1 else 0
    rev2 = sum(s["revenue"] or 0 for s in sales2) if sales2 else 0
    ord1 = sum(s["orders"] or 0 for s in sales1) if sales1 else 0
    ord2 = sum(s["orders"] or 0 for s in sales2) if sales2 else 0

    rev_change = ((rev1 - rev2) / rev2 * 100) if rev2 > 0 else 0
    ord_change = ((ord1 - ord2) / ord2 * 100) if ord2 > 0 else 0

    lines = [
        "Sales Comparison:",
        "",
        f"Period 1 ({p1_start} to {p1_end}):",
        f"  Revenue: ${rev1:,.2f}",
        f"  Orders: {ord1}",
        "",
        f"Period 2 ({p2_start} to {p2_end}):",
        f"  Revenue: ${rev2:,.2f}",
        f"  Orders: {ord2}",
        "",
        "Change (Period 1 vs Period 2):",
        f"  Revenue: {rev_change:+.1f}%",
        f"  Orders: {ord_change:+.1f}%",
    ]

    return "\n".join(lines)


@tool
def get_sales_for_product(
    product_id: int, start_date: str = None, end_date: str = None
) -> str:
    """Get sales data for a specific product.

    Args:
        product_id: The product ID to look up.
        start_date: Start date in YYYY-MM-DD format. Defaults to 30 days ago.
        end_date: End date in YYYY-MM-DD format. Defaults to today.
    """
    start = _parse_date(start_date, default_days_ago=30)
    end = _parse_date(end_date, default_days_ago=0)

    sales = _run_async(db.get_product_sales(product_id, start, end))

    if not sales:
        return f"No sales found for product {product_id} between {start} and {end}"

    total_rev = sum(s["amount"] or 0 for s in sales)
    total_qty = sum(s["quantity"] or 0 for s in sales)

    lines = [
        f"Sales for Product ID {product_id} ({start} to {end}):",
        f"Total Revenue: ${total_rev:,.2f}",
        f"Total Units: {total_qty}",
        f"Number of Transactions: {len(sales)}",
    ]

    return "\n".join(lines)


SALES_TOOLS = [
    get_sales_summary,
    get_top_products,
    get_sales_by_region,
    compare_sales_periods,
    get_sales_for_product,
]
