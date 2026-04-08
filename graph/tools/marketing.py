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
def get_active_campaigns() -> str:
    """Get all currently active marketing campaigns with performance metrics."""
    campaigns = _run_async(db.get_campaigns())

    if not campaigns:
        return "No active campaigns."

    lines = [f"Active Marketing Campaigns ({len(campaigns)}):", ""]

    total_budget = sum(c["budget"] for c in campaigns)
    total_spent = sum(c["spent"] for c in campaigns)

    for c in campaigns:
        ctr = c["ctr"] or 0
        conv = c["conv_rate"] or 0
        status = "❌ POOR" if ctr < 1 else "⚠️ WATCH" if ctr < 2 else "✓ GOOD"

        lines.append(f"{status} {c['name']} (ID: {c['id']})")
        lines.append(f"  Channel: {c['channel']}")
        lines.append(
            f"  Budget: ${c['spent']:,.0f} / ${c['budget']:,.0f} ({c['spent']/c['budget']*100:.0f}% used)"
        )
        lines.append(
            f"  Impressions: {c['impressions']:,} | Clicks: {c['clicks']:,} | Conversions: {c['conversions']}"
        )
        lines.append(f"  CTR: {ctr:.2f}% | Conversion Rate: {conv:.2f}%")
        lines.append("")

    lines.append(f"Total Budget: ${total_budget:,.0f}")
    lines.append(f"Total Spent: ${total_spent:,.0f}")

    return "\n".join(lines)


@tool
def get_campaign_details(campaign_id: int) -> str:
    """Get detailed information about a specific campaign.

    Args:
        campaign_id: The campaign ID to look up.
    """
    campaigns = _run_async(db.get_campaigns())

    for c in campaigns:
        if c["id"] == campaign_id:
            ctr = c["ctr"] or 0
            conv = c["conv_rate"] or 0
            cpc = c["spent"] / c["clicks"] if c["clicks"] > 0 else 0
            cpa = c["spent"] / c["conversions"] if c["conversions"] > 0 else 0

            return (
                f"Campaign: {c['name']} (ID: {campaign_id})\n"
                f"Channel: {c['channel']}\n"
                f"Status: {c['status']}\n"
                f"\nBudget:\n"
                f"  Total: ${c['budget']:,.0f}\n"
                f"  Spent: ${c['spent']:,.0f}\n"
                f"  Remaining: ${c['budget'] - c['spent']:,.0f}\n"
                f"\nPerformance:\n"
                f"  Impressions: {c['impressions']:,}\n"
                f"  Clicks: {c['clicks']:,}\n"
                f"  Conversions: {c['conversions']}\n"
                f"  CTR: {ctr:.2f}%\n"
                f"  Conversion Rate: {conv:.2f}%\n"
                f"  Cost Per Click: ${cpc:.2f}\n"
                f"  Cost Per Acquisition: ${cpa:.2f}"
            )

    return f"Campaign ID {campaign_id} not found."


@tool
def get_campaigns_by_channel(channel: str) -> str:
    """Get all campaigns for a specific channel.

    Args:
        channel: Channel to filter by (email, social, search, display).
    """
    campaigns = _run_async(db.get_campaigns())
    filtered = [c for c in campaigns if c["channel"].lower() == channel.lower()]

    if not filtered:
        return f"No active campaigns on {channel} channel."

    lines = [f"Campaigns on {channel.upper()} ({len(filtered)}):", ""]

    for c in filtered:
        ctr = c["ctr"] or 0
        lines.append(f"• {c['name']} (ID: {c['id']})")
        lines.append(
            f"  Spent: ${c['spent']:,.0f} | CTR: {ctr:.2f}% | Conversions: {c['conversions']}"
        )

    return "\n".join(lines)


@tool
def get_underperforming_campaigns(ctr_threshold: float = 1.0) -> str:
    """Get campaigns performing below a CTR threshold.

    Args:
        ctr_threshold: Minimum acceptable CTR percentage. Defaults to 1.0%.
    """
    campaigns = _run_async(db.get_campaigns())
    poor = [c for c in campaigns if (c["ctr"] or 0) < ctr_threshold]

    if not poor:
        return f"No campaigns below {ctr_threshold}% CTR threshold."

    lines = [f"Underperforming Campaigns (CTR < {ctr_threshold}%):", ""]

    total_wasted = 0
    for c in sorted(poor, key=lambda x: x["ctr"] or 0):
        ctr = c["ctr"] or 0
        lines.append(f"❌ {c['name']} (ID: {c['id']})")
        lines.append(
            f"   Channel: {c['channel']} | CTR: {ctr:.2f}% | Spent: ${c['spent']:,.0f}"
        )
        total_wasted += c["spent"]

    lines.append(f"\nTotal spent on underperforming: ${total_wasted:,.0f}")

    return "\n".join(lines)


@tool
def get_campaign_roi_analysis() -> str:
    """Analyze ROI across all active campaigns."""
    campaigns = _run_async(db.get_campaigns())

    if not campaigns:
        return "No campaigns to analyze."

    lines = ["Campaign ROI Analysis:", ""]

    # Assume average order value of $75 for ROI calculation
    avg_order_value = 75

    for c in sorted(
        campaigns,
        key=lambda x: x["conversions"] * avg_order_value - x["spent"],
        reverse=True,
    ):
        revenue_est = c["conversions"] * avg_order_value
        roi = ((revenue_est - c["spent"]) / c["spent"] * 100) if c["spent"] > 0 else 0

        status = "✓" if roi > 50 else "⚠️" if roi > 0 else "❌"

        lines.append(f"{status} {c['name']} (ID: {c['id']})")
        lines.append(
            f"   Spent: ${c['spent']:,.0f} | Est. Revenue: ${revenue_est:,.0f} | ROI: {roi:.0f}%"
        )

    return "\n".join(lines)


MARKETING_TOOLS = [
    get_active_campaigns,
    get_campaign_details,
    get_campaigns_by_channel,
    get_underperforming_campaigns,
    get_campaign_roi_analysis,
]
