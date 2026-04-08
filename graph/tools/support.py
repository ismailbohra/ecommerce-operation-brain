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
def get_open_tickets() -> str:
    """Get all currently open support tickets sorted by priority."""
    tickets = _run_async(db.get_open_tickets())

    if not tickets:
        return "No open support tickets."

    high = [t for t in tickets if t["priority"] == "high"]
    medium = [t for t in tickets if t["priority"] == "medium"]
    low = [t for t in tickets if t["priority"] == "low"]

    lines = [f"Open Support Tickets ({len(tickets)} total):", ""]

    lines.append(f"HIGH Priority ({len(high)}):")
    for t in high:
        lines.append(f"  🔴 [{t['id']}] {t['subject']} ({t['category']})")
    if not high:
        lines.append("  None")

    lines.append(f"\nMEDIUM Priority ({len(medium)}):")
    for t in medium:
        lines.append(f"  🟡 [{t['id']}] {t['subject']} ({t['category']})")
    if not medium:
        lines.append("  None")

    lines.append(f"\nLOW Priority ({len(low)}):")
    for t in low:
        lines.append(f"  🟢 [{t['id']}] {t['subject']} ({t['category']})")
    if not low:
        lines.append("  None")

    return "\n".join(lines)


@tool
def get_ticket_summary() -> str:
    """Get summary of open tickets grouped by category and priority."""
    summary = _run_async(db.get_ticket_summary())

    if not summary:
        return "No ticket summary available."

    lines = ["Ticket Summary by Category:", ""]

    by_category = {}
    for s in summary:
        cat = s["category"]
        if cat not in by_category:
            by_category[cat] = {"high": 0, "medium": 0, "low": 0, "total": 0}
        by_category[cat][s["priority"]] = s["count"]
        by_category[cat]["total"] += s["count"]

    for cat, counts in sorted(by_category.items(), key=lambda x: -x[1]["total"]):
        lines.append(f"{cat.upper()}: {counts['total']} tickets")
        lines.append(
            f"  High: {counts['high']} | Medium: {counts['medium']} | Low: {counts['low']}"
        )

    return "\n".join(lines)


@tool
def get_ticket_details(ticket_id: int) -> str:
    """Get full details of a specific support ticket.

    Args:
        ticket_id: The ticket ID to look up.
    """
    tickets = _run_async(db.get_open_tickets())

    for t in tickets:
        if t["id"] == ticket_id:
            return (
                f"Ticket #{t['id']}\n"
                f"Subject: {t['subject']}\n"
                f"Category: {t['category']}\n"
                f"Priority: {t['priority'].upper()}\n"
                f"Status: {t['status']}\n"
                f"Created: {t['created_at']}\n"
                f"\nDescription:\n{t['description']}"
            )

    return f"Ticket #{ticket_id} not found or not open."


@tool
def get_tickets_by_category(category: str) -> str:
    """Get all open tickets for a specific category.

    Args:
        category: Category to filter by (shipping, order, refund, technical, billing, product).
    """
    tickets = _run_async(db.get_open_tickets())
    filtered = [t for t in tickets if t["category"].lower() == category.lower()]

    if not filtered:
        return f"No open tickets in category '{category}'."

    lines = [f"Open Tickets - {category.upper()} ({len(filtered)}):", ""]
    for t in filtered:
        icon = (
            "🔴"
            if t["priority"] == "high"
            else "🟡" if t["priority"] == "medium" else "🟢"
        )
        lines.append(f"{icon} [{t['id']}] {t['subject']}")
        lines.append(f"    {t['description'][:100]}...")

    return "\n".join(lines)


@tool
def get_ticket_trends(start_date: str = None, end_date: str = None) -> str:
    """Get ticket creation trends over a date range.

    Args:
        start_date: Start date in YYYY-MM-DD format. Defaults to 7 days ago.
        end_date: End date in YYYY-MM-DD format. Defaults to today.
    """
    start = _parse_date(start_date, default_days_ago=7)
    end = _parse_date(end_date, default_days_ago=0)

    stats = _run_async(db.get_ticket_stats(start, end))

    if not stats:
        return f"No ticket data available for {start} to {end}."

    lines = [f"Ticket Trends ({start} to {end}):", ""]

    total = sum(s["count"] for s in stats)
    lines.append(f"Total Tickets Created: {total}")
    lines.append("")
    lines.append("Daily Breakdown:")

    for s in sorted(stats, key=lambda x: x["date"], reverse=True):
        lines.append(f"  {s['date']}: {s['count']} tickets")

    return "\n".join(lines)


SUPPORT_TOOLS = [
    get_open_tickets,
    get_ticket_summary,
    get_ticket_details,
    get_tickets_by_category,
    get_ticket_trends,
]
