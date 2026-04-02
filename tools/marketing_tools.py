import asyncio
from langchain_core.tools import tool
from database import Database


def get_marketing_tools():
    db = Database()

    @tool
    def get_active_campaigns() -> str:
        """Get all currently active marketing campaigns."""

        async def _run():
            data = await db.get_active_campaigns()
            if not data:
                return "No active campaigns."

            result = f"Active Campaigns ({len(data)}):\n"
            for row in data:
                budget_used = (
                    (row["spent"] / row["budget"] * 100) if row["budget"] > 0 else 0
                )
                result += f"  {row['name']} ({row['channel']}): ${row['spent']:.0f}/${row['budget']:.0f} ({budget_used:.0f}% used)\n"
            return result

        return asyncio.run(_run())

    @tool
    def get_campaign_performance() -> str:
        """Get performance metrics for all active campaigns."""

        async def _run():
            data = await db.get_campaign_performance()
            if not data:
                return "No campaign performance data available."

            result = "Campaign Performance:\n"
            for row in data:
                result += f"\n  {row['name']} ({row['channel']}):\n"
                result += f"    Impressions: {row['impressions']:,}\n"
                result += f"    Clicks: {row['clicks']:,} (CTR: {row['ctr']}%)\n"
                result += f"    Conversions: {row['conversions']} (Conv Rate: {row['conversion_rate']}%)\n"
            return result

        return asyncio.run(_run())

    @tool
    def get_underperforming_campaigns(min_ctr: float = 2.0) -> str:
        """Get campaigns with CTR below threshold (default 2%)."""

        async def _run():
            data = await db.get_campaign_performance()
            underperforming = [c for c in data if c["ctr"] < min_ctr]

            if not underperforming:
                return f"All campaigns are performing above {min_ctr}% CTR."

            result = f"Underperforming Campaigns (CTR < {min_ctr}%):\n"
            for row in underperforming:
                result += f"  ⚠️ {row['name']}: CTR={row['ctr']}%, Conv={row['conversion_rate']}%\n"
            return result

        return asyncio.run(_run())

    @tool
    def get_campaign_roi() -> str:
        """Calculate ROI for each campaign based on spend and conversions."""

        async def _run():
            data = await db.get_campaign_performance()
            if not data:
                return "No campaign data available."

            result = "Campaign ROI Analysis:\n"
            for row in data:
                cost_per_conv = (
                    row["spent"] / row["conversions"]
                    if row["conversions"] > 0
                    else float("inf")
                )
                result += f"  {row['name']}: ${cost_per_conv:.2f} per conversion\n"
            return result

        return asyncio.run(_run())

    @tool
    def get_marketing_summary() -> str:
        """Get overall marketing performance summary."""

        async def _run():
            data = await db.get_campaign_performance()
            if not data:
                return "No marketing data available."

            total_spend = sum(c["spent"] for c in data)
            total_conversions = sum(c["conversions"] for c in data)
            total_clicks = sum(c["clicks"] for c in data)
            total_impressions = sum(c["impressions"] for c in data)

            avg_ctr = (
                (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            )
            avg_conv = (
                (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
            )

            result = "Marketing Summary:\n"
            result += f"  Active Campaigns: {len(data)}\n"
            result += f"  Total Spend: ${total_spend:,.2f}\n"
            result += f"  Total Impressions: {total_impressions:,}\n"
            result += f"  Total Clicks: {total_clicks:,}\n"
            result += f"  Total Conversions: {total_conversions}\n"
            result += f"  Average CTR: {avg_ctr:.2f}%\n"
            result += f"  Average Conv Rate: {avg_conv:.2f}%\n"
            return result

        return asyncio.run(_run())

    return [
        get_active_campaigns,
        get_campaign_performance,
        get_underperforming_campaigns,
        get_campaign_roi,
        get_marketing_summary,
    ]
