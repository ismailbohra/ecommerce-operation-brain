def format_sales(sales: list) -> str:
    if not sales:
        return "No sales data"
    lines = []
    for s in sales:
        rev = s["revenue"] or 0
        orders = s["orders"] or 0
        lines.append(f"- {s['sale_date']}: ${rev:,.2f} ({orders} orders)")
    return "\n".join(lines)


def format_products(products: list) -> str:
    if not products:
        return "No product data"
    lines = []
    for i, p in enumerate(products, 1):
        rev = p["revenue"] or 0
        units = p["units"] or 0
        lines.append(f"{i}. {p['name']}: ${rev:,.2f} ({units} units)")
    return "\n".join(lines)


def format_regions(regions: list) -> str:
    if not regions:
        return "No regional data"
    return "\n".join([f"- {r['region']}: ${r['revenue'] or 0:,.2f}" for r in regions])


def format_out_of_stock(products: list) -> str:
    if not products:
        return "None"
    return "\n".join([f"- {p['name']} (ID: {p['id']})" for p in products])


def format_low_stock(products: list) -> str:
    if not products:
        return "None"
    return "\n".join(
        [f"- {p['name']}: {p['stock']} units (ID: {p['id']})" for p in products]
    )


def format_inventory(items: list) -> str:
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


def format_tickets(tickets: list) -> str:
    if not tickets:
        return "No open tickets"
    lines = []
    for t in tickets[:10]:
        icon = (
            "🔴"
            if t["priority"] == "high"
            else "🟡" if t["priority"] == "medium" else "🟢"
        )
        lines.append(f"{icon} [{t['priority'].upper()}] {t['subject']} (ID: {t['id']})")
    return "\n".join(lines)


def format_ticket_summary(summary: list) -> str:
    if not summary:
        return "No summary"
    return "\n".join(
        [f"- {s['category']} ({s['priority']}): {s['count']}" for s in summary]
    )


def format_campaigns(campaigns: list) -> str:
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


def format_similar_incidents(incidents: list) -> str:
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


def format_db_incidents(incidents: list) -> str:
    if not incidents:
        return "No incidents"
    return "\n".join(
        [f"- [{inc['type']}] {inc['description'][:60]}..." for inc in incidents[:5]]
    )
