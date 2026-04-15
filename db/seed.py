import asyncio
import random
from datetime import datetime, timedelta
from .database import Database
from logger import log

random.seed(42)


async def seed_database():
    db = Database()
    await db.init()

    existing = await db._fetch("SELECT COUNT(*) as cnt FROM products")
    if existing and existing[0]["cnt"] > 0:
        log.info("Database already seeded")
        return

    await seed_products(db)
    await seed_inventory(db)
    await seed_sales(db)
    await seed_tickets(db)
    await seed_campaigns(db)
    await seed_incidents(db)

    log.info("Database seeded successfully")


async def seed_products(db: Database):
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
        (9, "Bluetooth Speaker", "Electronics", 49.99, "Portable waterproof speaker"),
        (10, "Running Shorts", "Clothing", 34.99, "Quick-dry athletic shorts"),
        (11, "Protein Powder", "Fitness", 44.99, "Whey protein isolate 2lb"),
        (12, "Wireless Mouse", "Electronics", 29.99, "Ergonomic wireless mouse"),
        (13, "Water Bottle", "Fitness", 24.99, "Insulated stainless steel bottle"),
        (14, "Sunglasses", "Accessories", 89.99, "Polarized UV protection sunglasses"),
        (15, "Hiking Boots", "Footwear", 159.99, "Waterproof trail hiking boots"),
    ]
    for p in products:
        await db._execute(
            "INSERT INTO products (id, name, category, price, description) VALUES (?, ?, ?, ?, ?)",
            p,
        )
    log.debug(f"Added {len(products)} products")


async def seed_inventory(db: Database):
    inventory = [
        (1, 0, 15),  # OUT OF STOCK - Wireless Headphones
        (2, 8, 20),  # LOW - Running Shoes
        (3, 45, 15),  # OK - Winter Jacket
        (4, 0, 10),  # OUT OF STOCK - Yoga Mat
        (5, 120, 20),  # OK - Laptop Backpack
        (6, 5, 15),  # LOW - Smart Watch
        (7, 35, 10),  # OK - Coffee Maker
        (8, 12, 15),  # LOW - Desk Lamp
        (9, 60, 20),  # OK - Bluetooth Speaker
        (10, 3, 25),  # LOW - Running Shorts
        (11, 0, 30),  # OUT OF STOCK - Protein Powder
        (12, 85, 15),  # OK - Wireless Mouse
        (13, 200, 25),  # OK - Water Bottle
        (14, 15, 10),  # OK - Sunglasses
        (15, 7, 12),  # LOW - Hiking Boots
    ]
    for i in inventory:
        await db._execute(
            "INSERT INTO inventory (product_id, stock, reorder_level) VALUES (?, ?, ?)",
            i,
        )
        log.debug(f"Added {len(inventory)} inventory records")


async def seed_sales(db: Database):
    today = datetime.now().date()
    products = list(range(1, 16))
    prices = {
        1: 79.99,
        2: 129.99,
        3: 149.99,
        4: 29.99,
        5: 59.99,
        6: 199.99,
        7: 89.99,
        8: 34.99,
        9: 49.99,
        10: 34.99,
        11: 44.99,
        12: 29.99,
        13: 24.99,
        14: 89.99,
        15: 159.99,
    }
    regions = ["North", "South", "East", "West"]

    # Seasonal multipliers by month
    seasonal = {
        1: 0.7,  # Jan - post-holiday slump
        2: 0.75,  # Feb
        3: 0.85,  # Mar - recovery
        4: 0.9,  # Apr
        5: 0.95,  # May
        6: 1.0,  # Jun
        7: 0.9,  # Jul - summer lull
        8: 1.1,  # Aug - back to school
        9: 1.0,  # Sep
        10: 1.1,  # Oct - pre-holiday
        11: 1.4,  # Nov - Black Friday
        12: 1.5,  # Dec - Holiday peak
    }

    # Product seasonality
    product_seasonal = {
        3: {11: 1.8, 12: 2.0, 1: 1.5, 2: 1.3},  # Winter Jacket
        2: {3: 1.3, 4: 1.4, 5: 1.5, 9: 1.3},  # Running Shoes
        14: {5: 1.5, 6: 1.8, 7: 1.8, 8: 1.5},  # Sunglasses
        15: {4: 1.3, 5: 1.5, 6: 1.4, 9: 1.3},  # Hiking Boots
    }

    # Anomaly days (sales drops/spikes)
    anomalies = {}
    for _ in range(20):
        day_offset = random.randint(7, 365)
        anomaly_date = today - timedelta(days=day_offset)
        anomalies[anomaly_date] = random.choice([0.3, 0.4, 0.5, 1.5, 1.8, 2.0])

    # Stockout periods (no sales for specific products)
    stockouts = {
        1: [(30, 35), (120, 125), (250, 255)],  # Wireless Headphones
        4: [(45, 50), (180, 185)],  # Yoga Mat
        11: [(60, 68), (200, 210)],  # Protein Powder
        6: [(90, 95)],  # Smart Watch
    }

    sales_count = 0
    for days_ago in range(365):
        date = today - timedelta(days=days_ago)
        month = date.month
        weekday = date.weekday()

        # Base orders
        base_orders = 12 if weekday < 5 else 18
        base_orders = int(base_orders * seasonal.get(month, 1.0))

        # Apply anomaly
        if date in anomalies:
            base_orders = int(base_orders * anomalies[date])

        # Yesterday specific drop for demo
        if days_ago == 1:
            base_orders = int(base_orders * 0.35)
        elif days_ago == 2:
            base_orders = int(base_orders * 0.5)

        for _ in range(base_orders):
            product_id = random.choices(
                products,
                weights=[15, 12, 10, 8, 10, 8, 7, 6, 9, 7, 10, 8, 12, 6, 5],
            )[0]

            # Check stockout
            is_stockout = False
            for start, end in stockouts.get(product_id, []):
                if start <= days_ago <= end:
                    is_stockout = True
                    break
            if is_stockout:
                continue

            # Product seasonality
            prod_mult = product_seasonal.get(product_id, {}).get(month, 1.0)

            quantity = random.choices([1, 2, 3, 4], [55, 30, 12, 3])[0]
            price = prices[product_id] * prod_mult
            region = random.choices(regions, [30, 25, 25, 20])[0]

            await db._execute(
                "INSERT INTO sales (product_id, quantity, amount, sale_date, region) VALUES (?, ?, ?, ?, ?)",
                (product_id, quantity, price * quantity, date.isoformat(), region),
            )
            sales_count += 1

    log.debug(f"Added {sales_count} sales records")


async def seed_tickets(db: Database):
    today = datetime.now()
    categories = ["shipping", "order", "refund", "technical", "billing", "product"]
    priorities = ["high", "medium", "low"]

    ticket_templates = [
        (
            "Order not delivered",
            "Order #{order} hasn't arrived after {days} days",
            "shipping",
            "high",
        ),
        (
            "Wrong item received",
            "Received {wrong} instead of {right}",
            "order",
            "medium",
        ),
        (
            "Refund not processed",
            "Returned item {days} days ago, no refund yet",
            "refund",
            "high",
        ),
        (
            "App crashes on checkout",
            "App closes when trying to pay",
            "technical",
            "high",
        ),
        (
            "Discount code invalid",
            "Code {code} gives error at checkout",
            "billing",
            "low",
        ),
        (
            "Size exchange needed",
            "{product} too {size}, need exchange",
            "order",
            "medium",
        ),
        (
            "Missing item in order",
            "Only received {received} of {total} items",
            "shipping",
            "high",
        ),
        ("Product quality issue", "{product} arrived {issue}", "product", "medium"),
        ("Payment failed", "Card charged but order not confirmed", "billing", "high"),
        (
            "Tracking not updating",
            "No tracking update for {days} days",
            "shipping",
            "medium",
        ),
        (
            "Wrong size delivered",
            "Ordered {ordered} but received {received}",
            "order",
            "medium",
        ),
        (
            "Damaged packaging",
            "Box was {damage}, worried about item",
            "shipping",
            "low",
        ),
        ("Cancel order request", "Need to cancel order #{order}", "order", "medium"),
        (
            "Price match request",
            "Found {product} cheaper at {competitor}",
            "billing",
            "low",
        ),
        ("Account login issue", "Cannot log in to account", "technical", "medium"),
    ]

    products = [
        "Wireless Headphones",
        "Running Shoes",
        "Winter Jacket",
        "Smart Watch",
        "Yoga Mat",
    ]
    codes = ["SAVE20", "WELCOME10", "FLASH50", "SUMMER25"]
    issues = ["damaged", "defective", "different from photos", "not working"]
    sizes = ["small", "large", "tight", "loose"]

    # Generate open tickets (recent)
    open_tickets = []
    for i in range(15):
        template = random.choice(ticket_templates)
        subject = template[0]
        desc = template[1].format(
            order=random.randint(10000, 99999),
            days=random.randint(3, 14),
            wrong=random.choice(products),
            right=random.choice(products),
            code=random.choice(codes),
            product=random.choice(products),
            size=random.choice(sizes),
            received=random.randint(1, 2),
            total=random.randint(3, 5),
            issue=random.choice(issues),
            ordered="M",
            damage=random.choice(["crushed", "wet", "torn"]),
            competitor=random.choice(["Amazon", "Walmart", "Target"]),
        )
        created = today - timedelta(hours=random.randint(1, 72))
        open_tickets.append(
            (subject, desc, template[2], template[3], "open", created.isoformat())
        )

    for t in open_tickets:
        await db._execute(
            "INSERT INTO tickets (subject, description, category, priority, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            t,
        )

    # Generate resolved tickets (historical)
    resolved_count = 0
    for days_ago in range(365):
        date = today - timedelta(days=days_ago)
        month = date.month

        # More tickets during holiday season
        base_tickets = 3 if month in [11, 12, 1] else 2
        num_tickets = random.randint(1, base_tickets)

        for _ in range(num_tickets):
            template = random.choice(ticket_templates)
            subject = template[0]
            desc = template[1].format(
                order=random.randint(10000, 99999),
                days=random.randint(3, 14),
                wrong=random.choice(products),
                right=random.choice(products),
                code=random.choice(codes),
                product=random.choice(products),
                size=random.choice(sizes),
                received=random.randint(1, 2),
                total=random.randint(3, 5),
                issue=random.choice(issues),
                ordered="M",
                damage=random.choice(["crushed", "wet", "torn"]),
                competitor=random.choice(["Amazon", "Walmart", "Target"]),
            )
            await db._execute(
                "INSERT INTO tickets (subject, description, category, priority, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (subject, desc, template[2], template[3], "resolved", date.isoformat()),
            )
            resolved_count += 1

    log.debug(f"Added {len(open_tickets)} open + {resolved_count} resolved tickets")


async def seed_campaigns(db: Database):
    today = datetime.now().date()

    # Active campaigns
    active_campaigns = [
        ("Summer Electronics Sale", "email", 5000, 3500, "active", 50000, 1500, 75),
        ("Social Media Push", "social", 3000, 2800, "active", 100000, 800, 15),
        ("Google Search Ads", "search", 4000, 2000, "active", 30000, 900, 45),
        ("Influencer Campaign", "social", 8000, 7500, "active", 200000, 2000, 20),
        ("Retargeting Display", "display", 2000, 1800, "active", 40000, 1200, 60),
        ("Email Newsletter", "email", 1500, 1200, "active", 25000, 750, 40),
    ]

    for c in active_campaigns:
        await db._execute(
            "INSERT INTO campaigns (name, channel, budget, spent, status, impressions, clicks, conversions) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            c,
        )

    # Historical campaigns (completed)
    historical_campaigns = [
        # Q4 last year
        ("Black Friday Blitz", "email", 15000, 15000, "completed", 500000, 25000, 2500),
        ("Holiday Social", "social", 10000, 10000, "completed", 800000, 16000, 800),
        ("Cyber Monday Search", "search", 8000, 8000, "completed", 120000, 6000, 900),
        ("December Push", "display", 5000, 5000, "completed", 200000, 4000, 200),
        # Q1
        ("New Year Sale", "email", 6000, 6000, "completed", 150000, 6000, 450),
        ("Winter Clearance", "social", 4000, 4000, "completed", 180000, 3600, 180),
        ("Valentine's Promo", "email", 3000, 3000, "completed", 80000, 3200, 320),
        # Q2
        ("Spring Collection", "social", 5000, 5000, "completed", 220000, 5500, 330),
        ("Mother's Day Special", "email", 4000, 4000, "completed", 100000, 4500, 400),
        ("Summer Preview", "display", 3500, 3500, "completed", 150000, 3000, 150),
        # Q3
        ("Back to School", "search", 7000, 7000, "completed", 180000, 9000, 720),
        ("Labor Day Sale", "email", 5000, 5000, "completed", 120000, 5400, 432),
        ("Fall Fashion", "social", 4500, 4500, "completed", 200000, 4000, 200),
    ]

    for c in historical_campaigns:
        await db._execute(
            "INSERT INTO campaigns (name, channel, budget, spent, status, impressions, clicks, conversions) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            c,
        )

    log.debug(
        f"Added {len(active_campaigns)} active + {len(historical_campaigns)} historical campaigns"
    )


async def seed_incidents(db: Database):
    today = datetime.now()

    incidents = [
        # Q4 incidents
        (
            "sales_drop",
            "Black Friday server crash",
            "Traffic 10x normal, servers overwhelmed",
            "Emergency scaling, CDN activation, queue system",
            "Recovered in 2 hours, lost estimated $45,000",
            (today - timedelta(days=320)).isoformat(),
        ),
        (
            "stockout",
            "Holiday stockout crisis",
            "Top 5 products sold out by Dec 15",
            "Air freight emergency restock, pre-order system",
            "Captured 60% of demand via backorders, lost $30,000",
            (today - timedelta(days=300)).isoformat(),
        ),
        (
            "support_spike",
            "Post-holiday return tsunami",
            "Tickets increased 400% first week of January",
            "Temp staff hired, automated responses, extended hours",
            "Cleared backlog in 10 days, CSAT dropped to 3.2",
            (today - timedelta(days=280)).isoformat(),
        ),
        (
            "campaign_failure",
            "Holiday email disaster",
            "Black Friday email had 0.2% open rate",
            "Wrong send time, spam filter triggered",
            "Resent with new subject, achieved 18% open rate",
            (today - timedelta(days=315)).isoformat(),
        ),
        # Q1 incidents
        (
            "sales_drop",
            "January slump worse than expected",
            "Sales 45% below forecast for first 2 weeks",
            "Post-holiday fatigue, competitor promotions",
            "Flash sale recovered 20% of gap",
            (today - timedelta(days=260)).isoformat(),
        ),
        (
            "pricing_error",
            "Wrong price on Smart Watch",
            "Listed at $19.99 instead of $199.99",
            "Bulk upload CSV error",
            "Honored 50 orders at loss, added validation",
            (today - timedelta(days=240)).isoformat(),
        ),
        (
            "stockout",
            "Protein Powder shortage",
            "Supplier quality issue, batch rejected",
            "Contamination found in supplier facility",
            "Switched suppliers, 3 week gap in availability",
            (today - timedelta(days=220)).isoformat(),
        ),
        # Q2 incidents
        (
            "campaign_failure",
            "Spring social ads bombed",
            "Social campaign had 0.3% CTR, 0% conversions",
            "Wrong audience targeting, creative mismatch",
            "Rebuilt campaign, achieved 2.1% CTR on retry",
            (today - timedelta(days=180)).isoformat(),
        ),
        (
            "support_spike",
            "App bug caused ticket surge",
            "200+ tickets about checkout failure",
            "Payment SDK update broke iOS checkout",
            "Hotfix deployed in 4 hours, refunded failed orders",
            (today - timedelta(days=160)).isoformat(),
        ),
        (
            "sales_drop",
            "Memorial Day underperformance",
            "Sales 30% below last year's Memorial Day",
            "Competitor aggressive pricing, late promo start",
            "Extended sale 2 days, recovered partially",
            (today - timedelta(days=140)).isoformat(),
        ),
        # Q3 incidents
        (
            "stockout",
            "Back to school demand surge",
            "Laptop Backpack and Running Shoes sold out",
            "Underestimated back-to-school demand",
            "Express reorder, implemented demand forecasting",
            (today - timedelta(days=100)).isoformat(),
        ),
        (
            "campaign_failure",
            "Influencer campaign flop",
            "Paid $15,000 for influencer with fake followers",
            "Inadequate influencer vetting",
            "0.1% engagement, implemented verification process",
            (today - timedelta(days=85)).isoformat(),
        ),
        (
            "sales_drop",
            "Labor Day site slowdown",
            "Site slow, 40% cart abandonment",
            "Database connection pool exhausted",
            "Fixed in 3 hours, lost estimated $12,000",
            (today - timedelta(days=60)).isoformat(),
        ),
        # Recent incidents
        (
            "support_spike",
            "Shipping carrier delays",
            "Major carrier had regional delays",
            "Hurricane affected distribution center",
            "Proactive communication reduced tickets 40%",
            (today - timedelta(days=30)).isoformat(),
        ),
        (
            "stockout",
            "Wireless Headphones viral demand",
            "TikTok video caused 20x normal demand",
            "Viral social media mention",
            "Sold out in 6 hours, pre-orders captured 70%",
            (today - timedelta(days=14)).isoformat(),
        ),
        (
            "campaign_failure",
            "Email send failure",
            "Weekly newsletter not delivered",
            "Email service provider outage",
            "Resent next day, 15% lower engagement",
            (today - timedelta(days=7)).isoformat(),
        ),
        (
            "sales_drop",
            "Yesterday's sales anomaly",
            "Sales dropped 65% compared to typical day",
            "Multiple factors: inventory issues, campaign underperformance",
            "Investigation ongoing",
            (today - timedelta(days=1)).isoformat(),
        ),
    ]

    for inc in incidents:
        await db._execute(
            "INSERT INTO incidents (type, description, root_cause, action_taken, outcome, occurred_at) VALUES (?, ?, ?, ?, ?, ?)",
            inc,
        )

    log.debug(f"Added {len(incidents)} incidents")


if __name__ == "__main__":
    asyncio.run(seed_database())
