import asyncio
from datetime import datetime, timedelta
import random
from .database import Database


async def seed_database():
    db = Database()
    await db.init()

    existing = await db._fetch("SELECT COUNT(*) as cnt FROM products")
    if existing and existing[0]["cnt"] > 0:
        return

    # Products
    products = [
        (
            1,
            "Wireless Headphones",
            "Electronics",
            79.99,
            "Premium Bluetooth headphones with noise cancellation",
        ),
        (
            2,
            "Running Shoes",
            "Footwear",
            129.99,
            "Lightweight running shoes with cushioned sole",
        ),
        (
            3,
            "Winter Jacket",
            "Clothing",
            149.99,
            "Waterproof insulated jacket for cold weather",
        ),
        (4, "Yoga Mat", "Fitness", 29.99, "Non-slip eco-friendly yoga mat"),
        (
            5,
            "Laptop Backpack",
            "Accessories",
            59.99,
            "Water-resistant backpack with laptop compartment",
        ),
        (
            6,
            "Smart Watch",
            "Electronics",
            199.99,
            "Fitness tracker with heart rate monitor",
        ),
        (7, "Coffee Maker", "Home", 89.99, "Programmable drip coffee maker"),
        (8, "Desk Lamp", "Home", 34.99, "LED desk lamp with adjustable brightness"),
    ]
    for p in products:
        await db._execute(
            "INSERT INTO products (id, name, category, price, description) VALUES (?, ?, ?, ?, ?)",
            p,
        )

    # Inventory - some critical issues for demo
    inventory = [
        (1, 0, 10),  # OUT OF STOCK
        (2, 5, 10),  # LOW
        (3, 50, 10),  # OK
        (4, 0, 10),  # OUT OF STOCK
        (5, 100, 10),  # OK
        (6, 3, 10),  # LOW
        (7, 25, 10),  # OK
        (8, 8, 10),  # LOW
    ]
    for i in inventory:
        await db._execute(
            "INSERT INTO inventory (product_id, stock, reorder_level) VALUES (?, ?, ?)",
            i,
        )

    # Sales - last 30 days with realistic patterns
    today = datetime.now().date()
    for i in range(30):
        date = today - timedelta(days=i)

        # Yesterday and day before have lower sales (for "why did sales drop" demo)
        if i == 1:
            num_sales = random.randint(3, 5)  # Very low
        elif i == 2:
            num_sales = random.randint(5, 8)  # Low
        elif date.weekday() >= 5:  # Weekends
            num_sales = random.randint(15, 25)
        else:
            num_sales = random.randint(10, 18)

        for _ in range(num_sales):
            product_id = random.randint(1, 8)
            quantity = random.choices([1, 2, 3], [60, 30, 10])[0]
            price = products[product_id - 1][3]
            region = random.choice(["North", "South", "East", "West"])
            await db._execute(
                "INSERT INTO sales (product_id, quantity, amount, sale_date, region) VALUES (?, ?, ?, ?, ?)",
                (product_id, quantity, price * quantity, date.isoformat(), region),
            )

    # Support Tickets - mix of priorities
    tickets = [
        (
            "Order not delivered",
            "Order #12345 hasn't arrived after 10 days",
            "shipping",
            "high",
        ),
        ("Wrong item received", "Got blue variant instead of red", "order", "medium"),
        ("Refund request", "Want refund for damaged Winter Jacket", "refund", "high"),
        (
            "App crashes on checkout",
            "App closes when I try to pay",
            "technical",
            "high",
        ),
        (
            "Discount code expired",
            "SAVE20 says invalid but should work",
            "billing",
            "low",
        ),
        (
            "Size exchange needed",
            "Running shoes too small, need size up",
            "order",
            "medium",
        ),
        (
            "Missing item in order",
            "Only received 2 of 3 items ordered",
            "shipping",
            "high",
        ),
    ]
    for t in tickets:
        await db._execute(
            "INSERT INTO tickets (subject, description, category, priority, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
            t,
        )

    # Marketing Campaigns - some underperforming
    campaigns = [
        (
            "Summer Electronics",
            "email",
            5000,
            3500,
            "active",
            50000,
            1500,
            75,
        ),  # Good: 3% CTR
        (
            "Social Promo",
            "social",
            3000,
            2800,
            "active",
            100000,
            800,
            15,
        ),  # Bad: 0.8% CTR
        ("Search Ads", "search", 4000, 2000, "active", 30000, 900, 45),  # Good: 3% CTR
        (
            "Influencer Push",
            "social",
            8000,
            7500,
            "active",
            200000,
            2000,
            20,
        ),  # Bad: 1% CTR
        (
            "Retargeting",
            "display",
            2000,
            1800,
            "active",
            40000,
            1200,
            60,
        ),  # Good: 3% CTR
    ]
    for c in campaigns:
        await db._execute(
            "INSERT INTO campaigns (name, channel, budget, spent, status, impressions, clicks, conversions) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            c,
        )

    # Historical Incidents - for memory agent
    incidents = [
        (
            "sales_drop",
            "Sales dropped 40% during Black Friday",
            "Server overload from traffic spike",
            "Scaled up infrastructure, added caching",
            "Sales recovered within 4 hours",
        ),
        (
            "stockout",
            "Top 3 products out of stock during holidays",
            "Underestimated demand",
            "Emergency restock, set up low-stock alerts",
            "Lost ~$25,000, implemented safety stock",
        ),
        (
            "campaign_failure",
            "Email campaign had 0.3% CTR",
            "Poor subject line, wrong segment",
            "A/B tested new copy, refined targeting",
            "Follow-up achieved 4.2% CTR",
        ),
        (
            "support_spike",
            "Tickets increased 300% in one day",
            "Shipping carrier delays",
            "Proactive email, extra support staff",
            "Volume reduced 50% in 48 hours",
        ),
        (
            "sales_drop",
            "Weekend sales 50% lower than usual",
            "Competitor flash sale",
            "Counter-promotion with email blast",
            "Recovered 70% of expected sales",
        ),
    ]
    for inc in incidents:
        await db._execute(
            "INSERT INTO incidents (type, description, root_cause, action_taken, outcome, occurred_at) VALUES (?, ?, ?, ?, ?, datetime('now', '-30 days'))",
            inc,
        )

    print("✅ Database seeded")


if __name__ == "__main__":
    asyncio.run(seed_database())
