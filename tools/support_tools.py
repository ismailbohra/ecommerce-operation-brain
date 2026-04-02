import asyncio
from langchain_core.tools import tool
from database import Database
from vectorstore import VectorStore


def get_support_tools():
    db = Database()

    @tool
    def get_open_tickets() -> str:
        """Get all currently open support tickets."""

        async def _run():
            data = await db.get_open_tickets()
            if not data:
                return "No open tickets. All issues resolved!"

            result = f"Open Tickets ({len(data)}):\n"
            for row in data:
                result += f"  [{row['priority'].upper()}] {row['subject']} - {row['category']}\n"
            return result

        return asyncio.run(_run())

    @tool
    def get_tickets_by_category() -> str:
        """Get ticket counts grouped by category."""

        async def _run():
            data = await db.get_tickets_by_category()
            if not data:
                return "No tickets found."

            result = "Tickets by Category:\n"
            for row in data:
                result += f"  {row['category']}: {row['count']} total ({row['open_count']} open)\n"
            return result

        return asyncio.run(_run())

    @tool
    def get_recent_complaints(days: int = 7) -> str:
        """Get recent support tickets from the last N days."""

        async def _run():
            data = await db.get_recent_tickets(days)
            if not data:
                return f"No tickets in the last {days} days."

            result = f"Recent Tickets (Last {days} days): {len(data)} total\n"
            high_priority = [t for t in data if t["priority"] == "high"]
            if high_priority:
                result += f"\nHigh Priority Issues:\n"
                for row in high_priority:
                    result += f"  - {row['subject']}: {row['description'][:50]}...\n"
            return result

        return asyncio.run(_run())

    @tool
    def search_similar_issues(issue_description: str) -> str:
        """Search for similar past support tickets based on description."""
        vs = VectorStore()
        results = vs.search_similar_tickets(issue_description, limit=3)
        if not results:
            return "No similar issues found."

        result = "Similar Past Issues:\n"
        for r in results:
            result += (
                f"  [{r['score']:.2f}] {r['subject']}: {r['description'][:60]}...\n"
            )
        return result

    @tool
    def get_complaint_summary() -> str:
        """Get a summary of current complaint status and trends."""

        async def _run():
            open_tickets = await db.get_open_tickets()
            by_category = await db.get_tickets_by_category()

            high_priority = len([t for t in open_tickets if t["priority"] == "high"])

            result = f"Support Summary:\n"
            result += f"  Open Tickets: {len(open_tickets)}\n"
            result += f"  High Priority: {high_priority}\n"
            result += f"\nBy Category:\n"
            for cat in by_category:
                result += f"  {cat['category']}: {cat['open_count']} open\n"
            return result

        return asyncio.run(_run())

    return [
        get_open_tickets,
        get_tickets_by_category,
        get_recent_complaints,
        search_similar_issues,
        get_complaint_summary,
    ]
