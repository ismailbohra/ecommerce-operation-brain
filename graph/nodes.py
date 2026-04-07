import asyncio
import uuid
from datetime import datetime, timedelta
from langchain_core.messages import SystemMessage, HumanMessage
from config import (
    get_supervisor_llm,
    get_sales_llm,
    get_inventory_llm,
    get_support_llm,
    get_marketing_llm,
    get_memory_llm,
    get_action_llm,
)
from db import Database
from vectorstore import VectorStore
from .state import AgentState
from .prompts import ROUTER_PROMPT, SYNTHESIS_PROMPT, ACTION_PROMPT, AGENT_PROMPTS

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


# ============ ROUTER NODE ============
def router_node(state: AgentState) -> AgentState:
    llm = get_supervisor_llm()
    query = state["query"]

    messages = [
        SystemMessage(content=ROUTER_PROMPT),
        HumanMessage(content=f"Context:\n{state['chat_history']}\n\nQuery: {query}"),
    ]

    response = llm.invoke(messages)
    content = response.content.strip().lower()

    # Handle "none" case - simple query, no agents needed
    if content == "none" or content == "none.":
        state["agents_to_call"] = []
        state["agent_outputs"] = {}
        state["direct_response"] = True
        return state

    valid_agents = {"sales", "inventory", "support", "marketing", "memory"}
    agents = [a.strip() for a in content.split(",") if a.strip() in valid_agents]

    # Fallback if parsing failed but wasn't "none"
    if not agents:
        agents = ["sales", "memory"]

    state["agents_to_call"] = agents
    state["direct_response"] = False
    return state


# ============ SALES AGENT ============
def sales_agent(state: AgentState) -> str:
    llm = get_sales_llm()

    end = datetime.now().date()
    start = end - timedelta(days=7)

    sales = run_async(db.get_sales(start.isoformat(), end.isoformat()))
    top = run_async(db.get_top_products(start.isoformat(), end.isoformat()))
    regions = run_async(db.get_sales_by_region(start.isoformat(), end.isoformat()))

    data = f"""
## Sales Data (Last 7 Days)

Daily Summary:
{_format_sales(sales)}

Top Products:
{_format_products(top)}

By Region:
{_format_regions(regions)}
"""

    messages = [
        SystemMessage(content=AGENT_PROMPTS["sales"]),
        HumanMessage(content=f"{data}\n\nUser Query: {state['query']}"),
    ]

    return llm.invoke(messages).content


def _format_sales(sales: list) -> str:
    if not sales:
        return "No sales data"
    lines = []
    for s in sales:
        rev = s["revenue"] or 0
        orders = s["orders"] or 0
        lines.append(f"- {s['sale_date']}: ${rev:,.2f} ({orders} orders)")
    return "\n".join(lines)


def _format_products(products: list) -> str:
    if not products:
        return "No product data"
    lines = []
    for i, p in enumerate(products, 1):
        rev = p["revenue"] or 0
        units = p["units"] or 0
        lines.append(f"{i}. {p['name']}: ${rev:,.2f} ({units} units)")
    return "\n".join(lines)


def _format_regions(regions: list) -> str:
    if not regions:
        return "No regional data"
    lines = []
    for r in regions:
        rev = r["revenue"] or 0
        lines.append(f"- {r['region']}: ${rev:,.2f}")
    return "\n".join(lines)


# ============ INVENTORY AGENT ============
def inventory_agent(state: AgentState) -> str:
    llm = get_inventory_llm()

    inventory = run_async(db.get_inventory())
    out_of_stock = run_async(db.get_out_of_stock())
    low_stock = run_async(db.get_low_stock())

    data = f"""
## Inventory Data

Out of Stock ({len(out_of_stock)}):
{_format_out_of_stock(out_of_stock)}

Low Stock ({len(low_stock)}):
{_format_low_stock(low_stock)}

All Products:
{_format_inventory(inventory)}
"""

    messages = [
        SystemMessage(content=AGENT_PROMPTS["inventory"]),
        HumanMessage(content=f"{data}\n\nUser Query: {state['query']}"),
    ]

    return llm.invoke(messages).content


def _format_out_of_stock(products: list) -> str:
    if not products:
        return "None"
    return "\n".join([f"- {p['name']} (ID: {p['id']})" for p in products])


def _format_low_stock(products: list) -> str:
    if not products:
        return "None"
    return "\n".join(
        [f"- {p['name']}: {p['stock']} units (ID: {p['id']})" for p in products]
    )


def _format_inventory(items: list) -> str:
    if not items:
        return "No inventory data"
    lines = []
    for item in items[:10]:
        status = (
            "❌"
            if item["stock"] == 0
            else "⚠️" if item["stock"] <= item["reorder_level"] else "✓"
        )
        lines.append(f"{status} {item['name']}: {item['stock']} units")
    return "\n".join(lines)


# ============ SUPPORT AGENT ============
def support_agent(state: AgentState) -> str:
    llm = get_support_llm()

    tickets = run_async(db.get_open_tickets())
    summary = run_async(db.get_ticket_summary())

    data = f"""
## Support Data

Open Tickets ({len(tickets)}):
{_format_tickets(tickets)}

By Category/Priority:
{_format_ticket_summary(summary)}
"""

    messages = [
        SystemMessage(content=AGENT_PROMPTS["support"]),
        HumanMessage(content=f"{data}\n\nUser Query: {state['query']}"),
    ]

    return llm.invoke(messages).content


def _format_tickets(tickets: list) -> str:
    if not tickets:
        return "No open tickets"
    lines = []
    for t in tickets[:10]:
        priority_icon = (
            "🔴"
            if t["priority"] == "high"
            else "🟡" if t["priority"] == "medium" else "🟢"
        )
        lines.append(
            f"{priority_icon} [{t['priority'].upper()}] {t['subject']} (ID: {t['id']})"
        )
    return "\n".join(lines)


def _format_ticket_summary(summary: list) -> str:
    if not summary:
        return "No summary"
    return "\n".join(
        [f"- {s['category']} ({s['priority']}): {s['count']}" for s in summary]
    )


# ============ MARKETING AGENT ============
def marketing_agent(state: AgentState) -> str:
    llm = get_marketing_llm()

    campaigns = run_async(db.get_campaigns())

    data = f"""
## Marketing Data

Active Campaigns ({len(campaigns)}):
{_format_campaigns(campaigns)}
"""

    messages = [
        SystemMessage(content=AGENT_PROMPTS["marketing"]),
        HumanMessage(content=f"{data}\n\nUser Query: {state['query']}"),
    ]

    return llm.invoke(messages).content


def _format_campaigns(campaigns: list) -> str:
    if not campaigns:
        return "No active campaigns"
    lines = []
    for c in campaigns:
        ctr = c["ctr"] or 0
        conv = c["conv_rate"] or 0
        status = "❌" if ctr < 1 else "⚠️" if ctr < 2 else "✓"
        lines.append(
            f"{status} {c['name']} ({c['channel']})\n"
            f"   Budget: ${c['spent']:,.0f}/${c['budget']:,.0f} | "
            f"CTR: {ctr:.1f}% | Conv: {conv:.1f}% | ID: {c['id']}"
        )
    return "\n".join(lines)


# ============ MEMORY AGENT ============
def memory_agent(state: AgentState) -> str:
    llm = get_memory_llm()
    vs = VectorStore()

    query = state["query"]

    # Vector search
    similar = vs.search_incidents(query, limit=5)

    # Type-specific search
    incident_type = _detect_incident_type(query)
    type_specific = []
    if incident_type:
        type_specific = vs.search_incidents_by_type(query, incident_type, limit=3)

    # DB incidents
    db_incidents = run_async(db.get_incidents())

    data = f"""
## Historical Data

Similar Past Incidents (Vector Search):
{_format_similar_incidents(similar)}

{f"Type-Specific ({incident_type}):" if incident_type else ""}
{_format_similar_incidents(type_specific) if type_specific else ""}

Recent Incident Log:
{_format_db_incidents(db_incidents)}
"""

    messages = [
        SystemMessage(content=AGENT_PROMPTS["memory"]),
        HumanMessage(content=f"{data}\n\nUser Query: {query}"),
    ]

    return llm.invoke(messages).content


def _detect_incident_type(query: str) -> str | None:
    q = query.lower()
    if any(k in q for k in ["sales", "revenue", "drop"]):
        return "sales_drop"
    if any(k in q for k in ["stock", "inventory"]):
        return "stockout"
    if any(k in q for k in ["campaign", "marketing", "ctr"]):
        return "campaign_failure"
    if any(k in q for k in ["ticket", "support"]):
        return "support_spike"
    return None


def _format_similar_incidents(incidents: list) -> str:
    if not incidents:
        return "None found"
    lines = []
    for i, inc in enumerate(incidents, 1):
        score = inc.get("score", 0)
        lines.append(
            f"{i}. [{inc['incident_type']}] {inc['description']}\n"
            f"   Cause: {inc['root_cause']}\n"
            f"   Action: {inc['action_taken']}\n"
            f"   Outcome: {inc['outcome']}\n"
            f"   Relevance: {score:.0%}"
        )
    return "\n".join(lines)


def _format_db_incidents(incidents: list) -> str:
    if not incidents:
        return "No incidents"
    lines = []
    for inc in incidents[:5]:
        lines.append(f"- [{inc['type']}] {inc['description'][:60]}...")
    return "\n".join(lines)


# ============ AGENT EXECUTOR ============
AGENT_MAP = {
    "sales": sales_agent,
    "inventory": inventory_agent,
    "support": support_agent,
    "marketing": marketing_agent,
    "memory": memory_agent,
}


def execute_agents_node(state: AgentState) -> AgentState:
    outputs = {}
    for agent_name in state["agents_to_call"]:
        if agent_name in AGENT_MAP:
            outputs[agent_name] = AGENT_MAP[agent_name](state)
    state["agent_outputs"] = outputs
    return state


# ============ SYNTHESIS NODE ============
def synthesis_node(state: AgentState) -> AgentState:
    llm = get_supervisor_llm()

    query = state["query"]
    outputs = state["agent_outputs"]

    if not outputs:
        messages = [
            SystemMessage(content=SYNTHESIS_PROMPT),
            HumanMessage(
                content=f"Context:\n{state["chat_history"]}\n\nUser Question: {query}"
            ),
        ]
    else:
        findings = "\n\n---\n\n".join(
            [f"## {k.upper()} Agent\n\n{v}" for k, v in outputs.items()]
        )

        messages = [
            SystemMessage(content=SYNTHESIS_PROMPT),
            HumanMessage(
                content=f"Context:\n{state["chat_history"]}\n\nUser Question: {query}\n\n# Agent Findings\n\n{findings}"
            ),
        ]

    response = llm.invoke(messages)
    state["synthesis"] = response.content
    state["response"] = response.content
    return state


# ============ ACTION NODE ============
def action_node(state: AgentState) -> AgentState:
    llm = get_action_llm()

    query = state["query"].lower()
    synthesis = state["synthesis"]

    # Get current state
    out_of_stock = run_async(db.get_out_of_stock())
    low_stock = run_async(db.get_low_stock())
    campaigns = run_async(db.get_campaigns())
    tickets = run_async(db.get_open_tickets())

    context = f"""
## Current System State

Out of Stock Products:
{_format_out_of_stock(out_of_stock)}

Low Stock Products:
{_format_low_stock(low_stock)}

Active Campaigns:
{_format_campaigns(campaigns)}

Open Tickets:
{_format_tickets(tickets)}

## User Request
{query}

## Analysis Summary
{synthesis}
"""

    messages = [
        SystemMessage(content=ACTION_PROMPT),
        HumanMessage(content=context),
    ]

    response = llm.invoke(messages)
    actions = _parse_actions(response.content)
    state["proposed_actions"] = actions
    return state


def _parse_actions(content: str) -> list[dict]:
    import json

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


# ============ EXECUTE NODE ============
def execute_actions_node(state: AgentState) -> AgentState:
    approved_ids = state.get("approved_action_ids", [])
    actions = state.get("proposed_actions", [])
    results = []

    for action in actions:
        if action["id"] not in approved_ids:
            continue

        try:
            action_type = action.get("type")
            params = action.get("params", {})

            if action_type == "restock":
                run_async(
                    db.update_stock(params["product_id"], params.get("quantity", 50))
                )
                results.append(
                    f"✓ Restocked {params.get('name', 'product')} with {params.get('quantity', 50)} units"
                )

            elif action_type == "pause_campaign":
                run_async(db.pause_campaign(params["campaign_id"]))
                results.append(f"✓ Paused campaign: {params.get('name', 'campaign')}")

            elif action_type == "discount":
                run_async(
                    db.apply_discount(params["product_id"], params.get("percent", 10))
                )
                results.append(
                    f"✓ Applied {params.get('percent', 10)}% discount to {params.get('name', 'product')}"
                )

            elif action_type == "create_ticket":
                run_async(
                    db.create_ticket(
                        params.get("subject", "New Ticket"),
                        params.get("description", ""),
                        params.get("category", "general"),
                        params.get("priority", "medium"),
                    )
                )
                results.append(
                    f"✓ Created ticket: {params.get('subject', 'New Ticket')}"
                )

            elif action_type == "resolve_ticket":
                run_async(db.resolve_ticket(params["ticket_id"]))
                results.append(f"✓ Resolved ticket #{params['ticket_id']}")

            else:
                results.append(f"⚠ Unknown action: {action_type}")

        except Exception as e:
            results.append(
                f"✗ Failed: {action.get('description', 'action')} - {str(e)}"
            )

    state["action_results"] = results
    return state
