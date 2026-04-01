import asyncio
from database import Database, seed_database


async def test_database():
    # Seed the database
    await seed_database()

    db = Database()

    print("\n=== Testing Database Queries ===\n")

    # Test sales queries
    print("1. Sales Summary (last 7 days):")
    from datetime import datetime, timedelta

    end_date = datetime.now().date().isoformat()
    start_date = (datetime.now().date() - timedelta(days=7)).isoformat()
    sales = await db.get_sales_summary(start_date, end_date)
    for row in sales:
        print(
            f"   {row['sale_date']}: ${row['revenue']:.2f} ({row['total_orders']} orders)"
        )

    # Test inventory
    print("\n2. Low Stock Products:")
    low_stock = await db.get_low_stock_products()
    for item in low_stock:
        print(
            f"   {item['name']}: {item['stock_quantity']} units (reorder at {item['reorder_level']})"
        )

    # Test support tickets
    print("\n3. Open Support Tickets:")
    tickets = await db.get_open_tickets()
    for ticket in tickets[:5]:
        print(f"   [{ticket['priority']}] {ticket['subject']}")

    # Test marketing
    print("\n4. Active Campaigns:")
    campaigns = await db.get_campaign_performance()
    for camp in campaigns:
        print(f"   {camp['name']}: CTR={camp['ctr']}%, Conv={camp['conversion_rate']}%")

    # Test past incidents
    print("\n5. Past Incidents:")
    incidents = await db.get_past_incidents()
    for inc in incidents:
        print(f"   [{inc['incident_type']}] {inc['description'][:50]}...")

    print("\n=== Phase 1 Tests Completed ===")


if __name__ == "__main__":
    asyncio.run(test_database())
