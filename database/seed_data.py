import asyncio
import random
from datetime import datetime, timedelta
from .db import Database


async def seed_database():
    db = Database()
    await db.init_schema()

    # Check if already seeded
    products = await db.fetch_all("SELECT COUNT(*) as count FROM products")
    if products[0]["count"] > 0:
        print("Database already seeded")
        return

    # Seed products
    products_data = [
        (
            "Wireless Headphones",
            "Electronics",
            79.99,
            "Premium wireless headphones with noise cancellation",
        ),
        (
            "Smart Watch Pro",
            "Electronics",
            199.99,
            "Advanced fitness tracking smartwatch",
        ),
        ("Laptop Stand", "Accessories", 45.99, "Ergonomic aluminum laptop stand"),
        ("USB-C Hub", "Accessories", 35.99, "7-in-1 USB-C hub with HDMI"),
        (
            "Mechanical Keyboard",
            "Electronics",
            129.99,
            "RGB mechanical gaming keyboard",
        ),
        ("Wireless Mouse", "Accessories", 29.99, "Ergonomic wireless mouse"),
        ("Monitor Light Bar", "Accessories", 49.99, "LED monitor light bar"),
        ("Webcam HD", "Electronics", 89.99, "1080p HD webcam with microphone"),
        ("Phone Stand", "Accessories", 19.99, "Adjustable phone stand"),
        ("Power Bank", "Electronics", 39.99, "20000mAh portable power bank"),
        ("Bluetooth Speaker", "Electronics", 59.99, "Portable waterproof speaker"),
        ("Cable Organizer", "Accessories", 12.99, "Desktop cable management kit"),
    ]

    for name, category, price, desc in products_data:
        await db.execute(
            "INSERT INTO products (name, category, price, description) VALUES (?, ?, ?, ?)",
            (name, category, price, desc),
        )

    # Seed inventory
    for i in range(1, 13):
        stock = random.randint(0, 100)
        if i in [2, 5]:  # Make some products low/out of stock
            stock = random.randint(0, 5)
        await db.execute(
            "INSERT INTO inventory (product_id, stock_quantity, reorder_level) VALUES (?, ?, ?)",
            (i, stock, 10),
        )

    # Seed sales for last 30 days
    regions = ["North", "South", "East", "West"]
    today = datetime.now().date()

    for day_offset in range(30):
        sale_date = today - timedelta(days=day_offset)

        # Simulate lower sales on certain days
        if day_offset == 1:  # Yesterday - bad day
            num_sales = random.randint(5, 15)
        elif sale_date.weekday() >= 5:  # Weekends
            num_sales = random.randint(20, 40)
        else:
            num_sales = random.randint(30, 60)

        for _ in range(num_sales):
            product_id = random.randint(1, 12)
            quantity = random.randint(1, 5)

            price_row = await db.fetch_one(
                "SELECT price FROM products WHERE id = ?", (product_id,)
            )
            unit_price = price_row["price"]
            total = unit_price * quantity
            region = random.choice(regions)

            await db.execute(
                """
                INSERT INTO sales (product_id, quantity, unit_price, total_amount, sale_date, region)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    product_id,
                    quantity,
                    unit_price,
                    total,
                    sale_date.isoformat(),
                    region,
                ),
            )

    # Seed support tickets
    ticket_templates = [
        (
            "Order not received",
            "My order #12345 has not arrived after 2 weeks",
            "shipping",
            "high",
        ),
        (
            "Defective product",
            "The headphones I received are not working",
            "product_quality",
            "high",
        ),
        (
            "Refund request",
            "I want to return and get refund for my purchase",
            "refund",
            "medium",
        ),
        (
            "Wrong item received",
            "I ordered a keyboard but received a mouse",
            "shipping",
            "high",
        ),
        ("Payment issue", "I was charged twice for my order", "billing", "high"),
        (
            "Product inquiry",
            "What is the warranty period for Smart Watch?",
            "inquiry",
            "low",
        ),
        (
            "Discount code not working",
            "The promo code SAVE20 is not applying",
            "billing",
            "medium",
        ),
        (
            "Delivery delay",
            "My express shipping order is delayed",
            "shipping",
            "medium",
        ),
        (
            "Product damaged",
            "The package arrived with damaged contents",
            "product_quality",
            "high",
        ),
        (
            "Cancel order",
            "I want to cancel my pending order",
            "order_management",
            "medium",
        ),
    ]

    for subject, desc, category, priority in ticket_templates:
        status = random.choice(["open", "open", "open", "resolved"])
        await db.execute(
            """
            INSERT INTO support_tickets (subject, description, category, status, priority)
            VALUES (?, ?, ?, ?, ?)
        """,
            (subject, desc, category, status, priority),
        )

    # Seed marketing campaigns
    campaigns_data = [
        (
            "Summer Sale 2025",
            "email",
            5000,
            3500,
            "2025-01-01",
            "active",
            50000,
            2500,
            150,
        ),
        (
            "Social Media Push",
            "social",
            3000,
            2800,
            "2025-01-10",
            "active",
            80000,
            1600,
            80,
        ),
        (
            "Google Ads - Electronics",
            "search",
            4000,
            3900,
            "2025-01-05",
            "active",
            30000,
            1800,
            120,
        ),
        (
            "Retargeting Campaign",
            "display",
            2000,
            1500,
            "2025-01-15",
            "active",
            40000,
            800,
            40,
        ),
        (
            "Influencer Collab",
            "social",
            6000,
            6000,
            "2024-12-01",
            "completed",
            100000,
            5000,
            200,
        ),
    ]

    for (
        name,
        channel,
        budget,
        spent,
        start,
        status,
        imp,
        clicks,
        conv,
    ) in campaigns_data:
        await db.execute(
            """
            INSERT INTO marketing_campaigns 
            (name, channel, budget, spent, start_date, status, impressions, clicks, conversions)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (name, channel, budget, spent, start, status, imp, clicks, conv),
        )

    # Seed past incidents
    incidents_data = [
        (
            "sales_drop",
            "Sales dropped 40% on Black Friday due to website crash",
            "Server overload during peak traffic",
            "Scaled up servers and implemented caching",
            "Sales recovered within 2 hours, total loss ~$15000",
        ),
        (
            "inventory_stockout",
            "Top 3 products went out of stock during holiday sale",
            "Demand forecasting underestimated holiday surge",
            "Emergency restock from backup supplier, implemented safety stock policy",
            "Lost approximately 200 orders, policy change prevented future occurrences",
        ),
        (
            "campaign_failure",
            "Email campaign had 0% open rate",
            "Email subject line triggered spam filters",
            "Resent with modified subject, updated email templates",
            "Second send achieved 25% open rate",
        ),
    ]

    for inc_type, desc, cause, action, outcome in incidents_data:
        await db.execute(
            """
            INSERT INTO past_incidents (incident_type, description, root_cause, action_taken, outcome)
            VALUES (?, ?, ?, ?, ?)
        """,
            (inc_type, desc, cause, action, outcome),
        )

    print("Database seeded successfully!")


if __name__ == "__main__":
    asyncio.run(seed_database())
