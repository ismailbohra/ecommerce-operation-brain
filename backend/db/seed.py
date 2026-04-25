import asyncio
import random
from datetime import datetime, timedelta

from logger import log

from .database import Database

random.seed(42)

# ---------------------------------------------------------------------------
# Schema — all table definitions and migrations live here.
# asyncpg does not support multi-statement queries via the extended protocol,
# so each statement is executed separately.
# ---------------------------------------------------------------------------
_SCHEMA_STATEMENTS = [
    """CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT,
    price REAL,
    description TEXT,
    original_price REAL,
    discount_percent REAL DEFAULT 0
)""",
    """CREATE TABLE IF NOT EXISTS inventory (
    product_id INTEGER PRIMARY KEY,
    stock INTEGER DEFAULT 0,
    reorder_level INTEGER DEFAULT 10
)""",
    """CREATE TABLE IF NOT EXISTS sales (
    id SERIAL PRIMARY KEY,
    product_id INTEGER,
    quantity INTEGER,
    amount REAL,
    sale_date TEXT,
    region TEXT
)""",
    """CREATE TABLE IF NOT EXISTS tickets (
    id SERIAL PRIMARY KEY,
    subject TEXT,
    description TEXT,
    category TEXT,
    priority TEXT DEFAULT 'medium',
    status TEXT DEFAULT 'open',
    created_at TIMESTAMPTZ DEFAULT NOW()
)""",
    """CREATE TABLE IF NOT EXISTS campaigns (
    id SERIAL PRIMARY KEY,
    name TEXT,
    channel TEXT,
    budget REAL,
    spent REAL DEFAULT 0,
    status TEXT DEFAULT 'active',
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0
)""",
    """CREATE TABLE IF NOT EXISTS incidents (
    id SERIAL PRIMARY KEY,
    type TEXT,
    description TEXT,
    root_cause TEXT,
    action_taken TEXT,
    outcome TEXT,
    occurred_at TIMESTAMPTZ
)""",
    """CREATE TABLE IF NOT EXISTS chat_sessions (
    id UUID PRIMARY KEY,
    title TEXT NOT NULL DEFAULT 'New Chat',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
)""",
    """CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role TEXT NOT NULL,
    content TEXT NOT NULL DEFAULT '',
    agents JSONB DEFAULT '[]',
    actions JSONB DEFAULT NULL,
    action_results JSONB DEFAULT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
)""",
]


async def _create_schema(db: Database):
    pool = await db._get_pool()
    async with pool.acquire() as conn:
        for stmt in _SCHEMA_STATEMENTS:
            await conn.execute(stmt)
    log.info("Schema ready")


async def _count(db: Database, table: str) -> int:
    rows = await db._fetch(f"SELECT COUNT(*) as cnt FROM {table}")
    return rows[0]["cnt"] if rows else 0


async def seed_database():
    db = Database()
    await db.init()          # pool only
    await _create_schema(db) # schema creation + migrations

    seeded_any = False

    if await _count(db, "products") == 0:
        await seed_products(db)
        await seed_inventory(db)
        await seed_sales(db)
        seeded_any = True

    if await _count(db, "tickets") == 0:
        await seed_tickets(db)
        seeded_any = True

    if await _count(db, "campaigns") == 0:
        await seed_campaigns(db)
        seeded_any = True

    if await _count(db, "incidents") == 0:
        await seed_incidents(db)
        seeded_any = True

    if seeded_any:
        log.info("Database seeded successfully")
    else:
        log.info("Database already seeded")


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
        (16, "Gaming Keyboard", "Electronics", 89.99, "Mechanical gaming keyboard with RGB backlight"),
        (17, "Resistance Bands", "Fitness", 19.99, "Set of 5 resistance bands for strength training"),
        (18, "Travel Pillow", "Accessories", 24.99, "Memory foam neck pillow for travel"),
        (19, "Denim Jeans", "Clothing", 69.99, "Classic straight-fit denim jeans"),
        (20, "Electric Toothbrush", "Home", 49.99, "Sonic electric toothbrush with 3 cleaning modes"),
        (21, "Portable Charger", "Electronics", 39.99, "20000mAh power bank with fast charging"),
        (22, "Canvas Sneakers", "Footwear", 59.99, "Classic canvas low-top sneakers"),
        (23, "Kitchen Scale", "Home", 22.99, "Digital kitchen scale with 5kg capacity"),
        (24, "Foam Roller", "Fitness", 34.99, "High-density foam roller for muscle recovery"),
        (25, "Crossbody Bag", "Accessories", 49.99, "Compact crossbody bag with adjustable strap"),
        (26, "Hoodie", "Clothing", 54.99, "Fleece pullover hoodie with kangaroo pocket"),
        (27, "Wireless Earbuds", "Electronics", 149.99, "True wireless earbuds with ANC and 8hr battery"),
        (28, "Trail Running Shoes", "Footwear", 139.99, "Grippy trail running shoes with rock plate"),
        (29, "Blender", "Home", 79.99, "Personal blender for smoothies and protein shakes"),
        (30, "Compression Socks", "Fitness", 14.99, "Graduated compression socks for running and travel"),
    ]
    for p in products:
        await db._execute(
            "INSERT INTO products (id, name, category, price, description) VALUES ($1, $2, $3, $4, $5)",
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
        (16, 45, 15),  # OK - Gaming Keyboard
        (17, 0, 20),  # OUT OF STOCK - Resistance Bands
        (18, 78, 10),  # OK - Travel Pillow
        (19, 30, 15),  # OK - Denim Jeans
        (20, 12, 15),  # LOW - Electric Toothbrush
        (21, 90, 20),  # OK - Portable Charger
        (22, 25, 15),  # OK - Canvas Sneakers
        (23, 150, 20),  # OK - Kitchen Scale
        (24, 18, 10),  # OK - Foam Roller
        (25, 4, 12),  # LOW - Crossbody Bag
        (26, 55, 20),  # OK - Hoodie
        (27, 0, 15),  # OUT OF STOCK - Wireless Earbuds
        (28, 9, 12),  # LOW - Trail Running Shoes
        (29, 40, 10),  # OK - Blender
        (30, 200, 30),  # OK - Compression Socks
    ]
    for i in inventory:
        await db._execute(
            "INSERT INTO inventory (product_id, stock, reorder_level) VALUES ($1, $2, $3)",
            i,
        )
        log.debug(f"Added {len(inventory)} inventory records")


async def seed_sales(db: Database):
    today = datetime.now().date()
    products = list(range(1, 31))
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
        16: 89.99,
        17: 19.99,
        18: 24.99,
        19: 69.99,
        20: 49.99,
        21: 39.99,
        22: 59.99,
        23: 22.99,
        24: 34.99,
        25: 49.99,
        26: 54.99,
        27: 149.99,
        28: 139.99,
        29: 79.99,
        30: 14.99,
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
        19: {3: 1.2, 9: 1.3, 10: 1.2},  # Denim Jeans
        26: {10: 1.3, 11: 1.5, 12: 1.4, 1: 1.2},  # Hoodie
        28: {4: 1.3, 5: 1.5, 6: 1.4, 9: 1.4},  # Trail Running Shoes
        18: {6: 1.3, 7: 1.5, 8: 1.4},  # Travel Pillow (summer travel)
    }

    # Anomaly days (sales drops/spikes) — spread across 2 years
    anomalies = {}
    for _ in range(40):
        day_offset = random.randint(7, 730)
        anomaly_date = today - timedelta(days=day_offset)
        anomalies[anomaly_date] = random.choice([0.3, 0.4, 0.5, 1.5, 1.8, 2.0])

    # Stockout periods (no sales for specific products) — 2 years
    stockouts = {
        1: [(30, 35), (120, 125), (250, 255), (400, 410), (560, 565)],  # Wireless Headphones
        4: [(45, 50), (180, 185), (390, 398)],  # Yoga Mat
        11: [(60, 68), (200, 210), (450, 462)],  # Protein Powder
        6: [(90, 95), (510, 518)],  # Smart Watch
        3: [(610, 622)],  # Winter Jacket
        14: [(480, 488)],  # Sunglasses
    }

    sales_count = 0
    for days_ago in range(730):
        date = today - timedelta(days=days_ago)
        month = date.month
        weekday = date.weekday()

        # Base orders — higher volume for richer analysis
        base_orders = 28 if weekday < 5 else 42
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
                weights=[15, 12, 10, 8, 10, 8, 7, 6, 9, 7, 10, 8, 12, 6, 5,
                         7, 9, 6, 8, 7, 10, 6, 5, 8, 6, 9, 11, 7, 6, 10],
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
                "INSERT INTO sales (product_id, quantity, amount, sale_date, region) VALUES ($1, $2, $3, $4, $5)",
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
    for i in range(40):
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
            (subject, desc, template[2], template[3], "open", created)
        )

    for t in open_tickets:
        await db._execute(
            "INSERT INTO tickets (subject, description, category, priority, status, created_at) VALUES ($1, $2, $3, $4, $5, $6)",
            t,
        )

    # Generate resolved tickets (historical)
    resolved_count = 0
    for days_ago in range(730):
        date = today - timedelta(days=days_ago)
        month = date.month

        # More tickets during holiday season
        base_tickets = 8 if month in [11, 12, 1] else 5
        num_tickets = random.randint(3, base_tickets)

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
                "INSERT INTO tickets (subject, description, category, priority, status, created_at) VALUES ($1, $2, $3, $4, $5, $6)",
                (subject, desc, template[2], template[3], "resolved", date),
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
        ("YouTube Pre-roll Ads", "video", 3500, 2100, "active", 75000, 1100, 55),
        ("Fitness Category Push", "search", 2500, 1400, "active", 22000, 660, 33),
        ("New Arrivals Email", "email", 1200, 900, "active", 18000, 540, 27),
    ]

    for c in active_campaigns:
        await db._execute(
            "INSERT INTO campaigns (name, channel, budget, spent, status, impressions, clicks, conversions) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)",
            c,
        )

    # Historical campaigns (completed — last year)
    historical_campaigns = [
        # Q4 last year
        ("Black Friday Blitz", "email", 15000, 15000, "completed", 500000, 25000, 2500),
        ("Holiday Social", "social", 10000, 10000, "completed", 800000, 16000, 800),
        ("Cyber Monday Search", "search", 8000, 8000, "completed", 120000, 6000, 900),
        ("December Push", "display", 5000, 5000, "completed", 200000, 4000, 200),
        ("Holiday YouTube", "video", 6000, 6000, "completed", 350000, 10500, 525),
        ("Gift Guide Email", "email", 3500, 3500, "completed", 90000, 4500, 360),
        # Q1
        ("New Year Sale", "email", 6000, 6000, "completed", 150000, 6000, 450),
        ("Winter Clearance", "social", 4000, 4000, "completed", 180000, 3600, 180),
        ("Valentine's Promo", "email", 3000, 3000, "completed", 80000, 3200, 320),
        ("January Search Boost", "search", 2500, 2500, "completed", 60000, 3000, 180),
        # Q2
        ("Spring Collection", "social", 5000, 5000, "completed", 220000, 5500, 330),
        ("Mother's Day Special", "email", 4000, 4000, "completed", 100000, 4500, 400),
        ("Summer Preview", "display", 3500, 3500, "completed", 150000, 3000, 150),
        ("Fitness Season Search", "search", 3000, 3000, "completed", 72000, 3600, 216),
        ("Spring YouTube", "video", 2800, 2800, "completed", 120000, 3600, 180),
        # Q3
        ("Back to School", "search", 7000, 7000, "completed", 180000, 9000, 720),
        ("Labor Day Sale", "email", 5000, 5000, "completed", 120000, 5400, 432),
        ("Fall Fashion", "social", 4500, 4500, "completed", 200000, 4000, 200),
        ("Back to School YouTube", "video", 4000, 4000, "completed", 160000, 4800, 384),
        ("August Display Retargeting", "display", 2200, 2200, "completed", 88000, 1760, 88),
    ]

    # Year 2 historical campaigns (two years ago)
    year2_campaigns = [
        # Q4 - two years ago
        ("Black Friday Early Access", "email", 14000, 14000, "completed", 460000, 23000, 2300),
        ("Holiday Social Blitz", "social", 9000, 9000, "completed", 750000, 15000, 750),
        ("Cyber Week Search", "search", 7500, 7500, "completed", 110000, 5500, 825),
        ("December Deals Display", "display", 4500, 4500, "completed", 185000, 3700, 185),
        ("Holiday Video Ads", "video", 5500, 5500, "completed", 310000, 9300, 465),
        ("Christmas Email Series", "email", 3200, 3200, "completed", 82000, 4100, 328),
        # Q1 - two years ago
        ("New Year Clearance", "email", 5500, 5500, "completed", 140000, 5600, 420),
        ("Winter Flash Sale", "social", 3500, 3500, "completed", 165000, 3300, 165),
        ("Valentine's Email Promo", "email", 2800, 2800, "completed", 75000, 3000, 300),
        ("Q1 Search Visibility", "search", 2200, 2200, "completed", 52000, 2600, 156),
        # Q2 - two years ago
        ("Spring Refresh Social", "social", 4800, 4800, "completed", 210000, 5250, 315),
        ("Mother's Day Email", "email", 3800, 3800, "completed", 95000, 4275, 380),
        ("Summer Kickoff Display", "display", 3200, 3200, "completed", 140000, 2800, 140),
        ("Spring Search Campaign", "search", 2700, 2700, "completed", 64000, 3200, 192),
        ("Fitness Spring Video", "video", 2400, 2400, "completed", 105000, 3150, 158),
        # Q3 - two years ago
        ("Back to School Search", "search", 6500, 6500, "completed", 168000, 8400, 672),
        ("Labor Day Email Blast", "email", 4700, 4700, "completed", 115000, 5175, 414),
        ("Fall Preview Social", "social", 4200, 4200, "completed", 190000, 3800, 190),
        ("Summer End Display", "display", 2000, 2000, "completed", 80000, 1600, 80),
        ("Back to School YouTube", "video", 3600, 3600, "completed", 145000, 4350, 348),
    ]

    for c in historical_campaigns + year2_campaigns:
        await db._execute(
            "INSERT INTO campaigns (name, channel, budget, spent, status, impressions, clicks, conversions) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)",
            c,
        )

    log.debug(
        f"Added {len(active_campaigns)} active + {len(historical_campaigns) + len(year2_campaigns)} historical campaigns"
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
            (today - timedelta(days=320)),
        ),
        (
            "stockout",
            "Holiday stockout crisis",
            "Top 5 products sold out by Dec 15",
            "Air freight emergency restock, pre-order system",
            "Captured 60% of demand via backorders, lost $30,000",
            (today - timedelta(days=300)),
        ),
        (
            "support_spike",
            "Post-holiday return tsunami",
            "Tickets increased 400% first week of January",
            "Temp staff hired, automated responses, extended hours",
            "Cleared backlog in 10 days, CSAT dropped to 3.2",
            (today - timedelta(days=280)),
        ),
        (
            "campaign_failure",
            "Holiday email disaster",
            "Black Friday email had 0.2% open rate",
            "Wrong send time, spam filter triggered",
            "Resent with new subject, achieved 18% open rate",
            (today - timedelta(days=315)),
        ),
        # Q1 incidents
        (
            "sales_drop",
            "January slump worse than expected",
            "Sales 45% below forecast for first 2 weeks",
            "Post-holiday fatigue, competitor promotions",
            "Flash sale recovered 20% of gap",
            (today - timedelta(days=260)),
        ),
        (
            "pricing_error",
            "Wrong price on Smart Watch",
            "Listed at $19.99 instead of $199.99",
            "Bulk upload CSV error",
            "Honored 50 orders at loss, added validation",
            (today - timedelta(days=240)),
        ),
        (
            "stockout",
            "Protein Powder shortage",
            "Supplier quality issue, batch rejected",
            "Contamination found in supplier facility",
            "Switched suppliers, 3 week gap in availability",
            (today - timedelta(days=220)),
        ),
        # Q2 incidents
        (
            "campaign_failure",
            "Spring social ads bombed",
            "Social campaign had 0.3% CTR, 0% conversions",
            "Wrong audience targeting, creative mismatch",
            "Rebuilt campaign, achieved 2.1% CTR on retry",
            (today - timedelta(days=180)),
        ),
        (
            "support_spike",
            "App bug caused ticket surge",
            "200+ tickets about checkout failure",
            "Payment SDK update broke iOS checkout",
            "Hotfix deployed in 4 hours, refunded failed orders",
            (today - timedelta(days=160)),
        ),
        (
            "sales_drop",
            "Memorial Day underperformance",
            "Sales 30% below last year's Memorial Day",
            "Competitor aggressive pricing, late promo start",
            "Extended sale 2 days, recovered partially",
            (today - timedelta(days=140)),
        ),
        # Q3 incidents
        (
            "stockout",
            "Back to school demand surge",
            "Laptop Backpack and Running Shoes sold out",
            "Underestimated back-to-school demand",
            "Express reorder, implemented demand forecasting",
            (today - timedelta(days=100)),
        ),
        (
            "campaign_failure",
            "Influencer campaign flop",
            "Paid $15,000 for influencer with fake followers",
            "Inadequate influencer vetting",
            "0.1% engagement, implemented verification process",
            (today - timedelta(days=85)),
        ),
        (
            "sales_drop",
            "Labor Day site slowdown",
            "Site slow, 40% cart abandonment",
            "Database connection pool exhausted",
            "Fixed in 3 hours, lost estimated $12,000",
            (today - timedelta(days=60)),
        ),
        # Recent incidents
        (
            "support_spike",
            "Shipping carrier delays",
            "Major carrier had regional delays",
            "Hurricane affected distribution center",
            "Proactive communication reduced tickets 40%",
            (today - timedelta(days=30)),
        ),
        (
            "stockout",
            "Wireless Headphones viral demand",
            "TikTok video caused 20x normal demand",
            "Viral social media mention",
            "Sold out in 6 hours, pre-orders captured 70%",
            (today - timedelta(days=14)),
        ),
        (
            "campaign_failure",
            "Email send failure",
            "Weekly newsletter not delivered",
            "Email service provider outage",
            "Resent next day, 15% lower engagement",
            (today - timedelta(days=7)),
        ),
        (
            "sales_drop",
            "Yesterday's sales anomaly",
            "Sales dropped 65% compared to typical day",
            "Multiple factors: inventory issues, campaign underperformance",
            "Investigation ongoing",
            (today - timedelta(days=1)),
        ),
        # Recent Q3/Q4 additional
        (
            "pricing_error",
            "Gaming Keyboard listed at $8.99",
            "Price field corrupted in product import",
            "Missing field validation in bulk upload tool",
            "Honored 12 orders; fixed upload validation; loss ~$1,000",
            (today - timedelta(days=45)),
        ),
        (
            "stockout",
            "Hoodie demand spike before winter",
            "Hoodies sold out 3 weeks ahead of forecast",
            "Early cold snap accelerated seasonal demand",
            "Air-freight restock; lost ~$8,000 in missed sales",
            (today - timedelta(days=20)),
        ),
        (
            "support_spike",
            "Delayed refunds backlog",
            "150 refund tickets unresolved over 5-day window",
            "Payment processor API timeout caused refund queue failure",
            "Bulk-processed refunds manually; cleared in 2 days",
            (today - timedelta(days=10)),
        ),
        # Year 2 - Q4 (two years ago)
        (
            "sales_drop",
            "Black Friday server degradation",
            "Site response times 5x normal during peak hours",
            "Insufficient pre-scaling before traffic surge",
            "Performance degraded but recovered; lost estimated $28,000",
            (today - timedelta(days=690)),
        ),
        (
            "stockout",
            "Pre-Christmas inventory gap",
            "Smart Watch and Wireless Headphones sold out Dec 18",
            "40% demand underestimate from prior year data",
            "Expedited restock via air freight; captured 50% of demand via waitlist",
            (today - timedelta(days=672)),
        ),
        (
            "support_spike",
            "Holiday returns surge",
            "Support tickets up 350% first two weeks of January",
            "High gift return volume, under-resourced team",
            "Cleared backlog in 12 days; introduced self-service returns portal",
            (today - timedelta(days=648)),
        ),
        (
            "campaign_failure",
            "Black Friday email poor open rate",
            "Promo email achieved only 1.1% open rate vs 15% target",
            "Subject line too generic, sent at suboptimal time",
            "Resend with personalized subject achieved 14% open rate",
            (today - timedelta(days=685)),
        ),
        # Year 2 - Q1
        (
            "sales_drop",
            "Q1 post-holiday slump",
            "Sales 38% below forecast for January",
            "Consumer spending fatigue after holiday period",
            "Flash clearance sale closed 18% of the gap",
            (today - timedelta(days=620)),
        ),
        (
            "pricing_error",
            "Yoga Mat priced at $2.99",
            "Decimal shift in CSV upload set price to $2.99 instead of $29.99",
            "Batch upload missing validation layer",
            "Honored 23 orders at a loss; added price bounds validation",
            (today - timedelta(days=603)),
        ),
        (
            "stockout",
            "Running Shoes size shortage Q1",
            "Sizes 9-10 out of stock for 2.5 weeks",
            "Size distribution model underweighted popular sizes",
            "Reordered correct size mix; implemented size-level inventory alerts",
            (today - timedelta(days=580)),
        ),
        # Year 2 - Q2
        (
            "campaign_failure",
            "Spring display ads zero conversions",
            "Display campaign spent $3,200 with 0 conversions over 2 weeks",
            "Landing page was broken on mobile, not caught before launch",
            "Fixed landing page, relaunched; achieved 1.4% conversion rate",
            (today - timedelta(days=540)),
        ),
        (
            "support_spike",
            "Duplicate order billing bug",
            "150+ tickets about duplicate charges in one week",
            "Payment gateway retry logic created double-charge on timeout",
            "Hotfix in 6 hours; all duplicate charges refunded with $5 credit",
            (today - timedelta(days=510)),
        ),
        (
            "sales_drop",
            "Mother's Day last-minute drop",
            "Sales 22% below forecast the week of Mother's Day",
            "Promo email sent too late, competitor dominated search ads",
            "Extending sale captured partial gap; adjusted campaign calendar",
            (today - timedelta(days=495)),
        ),
        # Year 2 - Q3
        (
            "stockout",
            "Summer sunglasses sellout",
            "Sunglasses sold out in first heat wave of summer",
            "No weather-linked demand signal in forecast model",
            "Lost an estimated $18,000; added weather API to demand model",
            (today - timedelta(days=450)),
        ),
        (
            "campaign_failure",
            "Retargeting ads wasted on existing buyers",
            "Retargeting campaign reached 60% already-converted users",
            "Purchase pixel mis-firing excluded buyers from exclusion list",
            "Fixed pixel logic; retargeting ROAS improved 35%",
            (today - timedelta(days=430)),
        ),
        (
            "sales_drop",
            "August site downtime",
            "4-hour site outage during back-to-school peak",
            "CDN provider had regional outage",
            "Switched to backup CDN; lost estimated $20,000; SLA credit obtained",
            (today - timedelta(days=400)),
        ),
        (
            "support_spike",
            "Shipping label error batch",
            "180 packages shipped with wrong labels due to warehouse system bug",
            "Address mapping error in warehouse management software update",
            "Reshipped affected orders; proactive emails reduced inbound tickets 50%",
            (today - timedelta(days=375)),
        ),
        # Year 2 additional incidents
        (
            "pricing_error",
            "Wireless Earbuds priced at $14.99",
            "New product listing had placeholder price",
            "Missing review step in product launch checklist",
            "Honored 8 orders; introduced mandatory pricing review",
            (today - timedelta(days=720)),
        ),
        (
            "sales_drop",
            "Summer mid-season slump",
            "Week-over-week decline of 28% with no clear cause",
            "Multiple small competitors launched simultaneous promotions",
            "Responded with flash sale; recovered 15% of gap",
            (today - timedelta(days=470)),
        ),
        (
            "support_spike",
            "App login failures for Google OAuth users",
            "300+ login-failure tickets over 3 days",
            "OAuth provider changed token format; app didn't handle it",
            "Emergency patch deployed in 8 hours; all affected users notified",
            (today - timedelta(days=530)),
        ),
        (
            "stockout",
            "Resistance Bands sellout post-New Year",
            "Out of stock within 2 weeks of January fitness rush",
            "New Year resolution demand vastly underestimated",
            "Restocked in 10 days; set up fitness-season demand buffer",
            (today - timedelta(days=635)),
        ),
        (
            "campaign_failure",
            "Video ad creative rejected by platform",
            "YouTube campaign paused for 5 days pending review",
            "Ad included before/after imagery flagged by policy",
            "Recreated compliant creative; lost 5 days of planned reach",
            (today - timedelta(days=555)),
        ),
    ]

    for inc in incidents:
        await db._execute(
            "INSERT INTO incidents (type, description, root_cause, action_taken, outcome, occurred_at) VALUES ($1, $2, $3, $4, $5, $6)",
            inc,
        )

    log.debug(f"Added {len(incidents)} incidents")


if __name__ == "__main__":
    asyncio.run(seed_database())
