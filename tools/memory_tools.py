from langchain_core.tools import tool

# Database and VectoreStore are lazy-loaded here.

def get_memory_tools():

    @tool
    def recall_similar_incidents(description: str) -> str:
        """Search for similar past incidents based on description."""
        from vectorstore import VectorStore

        vs = VectorStore()
        results = vs.search_similar_incidents(description, limit=5)
        if not results:
            return "No similar past incidents found."
        output = f"Found {len(results)} similar past incidents:\n\n"
        for i, r in enumerate(results, 1):
            output += f"{i}. [{r['incident_type']}] {r['description']}\n"
            output += f"   Root Cause: {r['root_cause']}\n"
            output += f"   Action Taken: {r['action_taken']}\n"
            output += f"   Outcome: {r['outcome']}\n\n"
        return output

    @tool
    def recall_incidents_by_type(incident_type: str, description: str) -> str:
        """Search past incidents by type: sales_drop, inventory_stockout, support_spike, campaign_failure"""
        from vectorstore import VectorStore

        vs = VectorStore()
        results = vs.search_incidents_by_type(description, incident_type, limit=5)
        if not results:
            return f"No past incidents of type '{incident_type}' found."

        output = f"Found {len(results)} past '{incident_type}' incidents:\n\n"
        for i, r in enumerate(results, 1):
            output += f"{i}. {r['description']}\n"
            output += f"   Action: {r['action_taken']}\n"
            output += f"   Outcome: {r['outcome']}\n\n"
        return output

    @tool
    def get_past_actions_for_issue(issue: str) -> str:
        """Get actions taken for similar past issues."""
        from vectorstore import VectorStore

        vs = VectorStore()
        results = vs.search_similar_incidents(issue, limit=3)
        if not results:
            return "No historical actions found."

        output = "Past actions:\n\n"
        for i, r in enumerate(results, 1):
            output += f"{i}. {r['description'][:50]}...\n"
            output += f"   Action: {r['action_taken']}\n"
            output += f"   Result: {r['outcome']}\n\n"
        return output

    @tool
    def get_incident_history() -> str:
        """Get recent incident history."""
        import asyncio
        from database import Database

        db = Database()

        async def _run():
            results = await db.get_past_incidents()
            if not results:
                return "No incident history found."
            output = "Recent Incidents:\n\n"
            for r in results[:10]:
                output += f"[{r['incident_type']}] {r['description'][:60]}...\n"
            return output

        return asyncio.run(_run())

    return [
        recall_similar_incidents,
        recall_incidents_by_type,
        get_past_actions_for_issue,
        get_incident_history,
    ]
