from datetime import datetime, timedelta
from langchain_core.tools import tool
from db import Database
from vectorstore import VectorStore

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
def search_similar_incidents(query: str, limit: int = 5) -> str:
    """Search for historically similar incidents using semantic search.

    Args:
        query: Description of the current situation to find similar past incidents.
        limit: Maximum number of results to return. Defaults to 5.
    """
    vs = VectorStore()
    results = vs.search_incidents(query, limit=limit)

    if not results:
        return "No similar incidents found in history."

    lines = [f"Similar Historical Incidents ({len(results)} found):", ""]

    for i, inc in enumerate(results, 1):
        score = inc.get("score", 0)
        lines.append(f"{i}. [{inc['incident_type'].upper()}] (Relevance: {score:.0%})")
        lines.append(f"   What happened: {inc['description']}")
        lines.append(f"   Root cause: {inc['root_cause']}")
        lines.append(f"   Action taken: {inc['action_taken']}")
        lines.append(f"   Outcome: {inc['outcome']}")
        lines.append("")

    return "\n".join(lines)


@tool
def search_incidents_by_type(
    incident_type: str, query: str = "", limit: int = 5
) -> str:
    """Search for past incidents of a specific type.

    Args:
        incident_type: Type of incident (sales_drop, stockout, campaign_failure, support_spike, pricing_error).
        query: Optional query to filter results. If empty, returns most relevant for the type.
        limit: Maximum number of results. Defaults to 5.
    """
    vs = VectorStore()

    search_query = query if query else f"{incident_type} incident"
    results = vs.search_incidents_by_type(search_query, incident_type, limit=limit)

    if not results:
        return f"No incidents of type '{incident_type}' found."

    lines = [f"Past {incident_type.upper()} Incidents ({len(results)} found):", ""]

    for i, inc in enumerate(results, 1):
        lines.append(f"{i}. {inc['description']}")
        lines.append(f"   Cause: {inc['root_cause']}")
        lines.append(f"   Action: {inc['action_taken']}")
        lines.append(f"   Result: {inc['outcome']}")
        lines.append("")

    return "\n".join(lines)


@tool
def get_recent_incidents(days: int = 30, incident_type: str = None) -> str:
    """Get recent incidents from the database.

    Args:
        days: Number of days to look back. Defaults to 30.
        incident_type: Optional filter by type (sales_drop, stockout, campaign_failure, support_spike).
    """
    incidents = _run_async(db.get_incidents(incident_type))

    if not incidents:
        type_filter = f" of type '{incident_type}'" if incident_type else ""
        return f"No incidents{type_filter} found."

    cutoff = datetime.now() - timedelta(days=days)

    recent = []
    for inc in incidents:
        try:
            inc_date = datetime.fromisoformat(inc["occurred_at"].replace("Z", "+00:00"))
            if inc_date >= cutoff:
                recent.append(inc)
        except:
            recent.append(inc)

    if not recent:
        return f"No incidents in the last {days} days."

    lines = [f"Recent Incidents (Last {days} Days):", ""]

    for inc in recent[:10]:
        lines.append(f"• [{inc['type'].upper()}] {inc['description']}")
        lines.append(f"  Date: {inc['occurred_at']}")
        lines.append(f"  Cause: {inc['root_cause']}")
        lines.append(f"  Action: {inc['action_taken']}")
        lines.append("")

    return "\n".join(lines)


@tool
def search_resolved_tickets(query: str, limit: int = 5) -> str:
    """Search resolved tickets for similar issues and their resolutions.

    Args:
        query: Description of the issue to find similar resolved tickets.
        limit: Maximum results to return. Defaults to 5.
    """
    vs = VectorStore()
    results = vs.search_tickets(query, limit=limit)

    if not results:
        return "No similar resolved tickets found."

    lines = [f"Similar Resolved Tickets ({len(results)} found):", ""]

    for i, t in enumerate(results, 1):
        score = t.get("score", 0)
        lines.append(
            f"{i}. [{t['category'].upper()}] {t['subject']} (Relevance: {score:.0%})"
        )
        lines.append(f"   Issue: {t['description']}")
        lines.append(f"   Resolution: {t['resolution']}")
        lines.append("")

    return "\n".join(lines)


@tool
def get_incident_patterns(incident_type: str = None) -> str:
    """Analyze patterns in historical incidents.

    Args:
        incident_type: Optional filter by type. If not provided, analyzes all types.
    """
    incidents = _run_async(db.get_incidents(incident_type))

    if not incidents:
        return "No incidents available for pattern analysis."

    type_counts = {}
    for inc in incidents:
        t = inc["type"]
        type_counts[t] = type_counts.get(t, 0) + 1

    lines = ["Incident Pattern Analysis:", ""]

    lines.append("Frequency by Type:")
    for t, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        lines.append(f"  {t}: {count} occurrences")

    lines.append("")
    lines.append("Common Root Causes:")

    causes = {}
    for inc in incidents:
        cause = inc["root_cause"][:50]
        causes[cause] = causes.get(cause, 0) + 1

    for cause, count in sorted(causes.items(), key=lambda x: -x[1])[:5]:
        lines.append(f"  • {cause}... ({count}x)")

    return "\n".join(lines)


MEMORY_TOOLS = [
    search_similar_incidents,
    search_incidents_by_type,
    get_recent_incidents,
    search_resolved_tickets,
    get_incident_patterns,
]
