from datetime import datetime
from .store import VectorStore
from logger import log


def seed_vectors():
    vs = VectorStore()
    vs.init_collections()

    if vs.count("incidents") > 0:
        log.info("VectorStore already seeded")
        return

    log.info("Seeding VectorStore...")
    seed_incidents(vs)
    seed_tickets(vs)
    seed_products(vs)
    log.info("VectorStore seeded successfully")


def seed_incidents(vs: VectorStore):
    today = datetime.now()

    incidents = [
        # Q4 - Holiday Season
        {
            "id": 1,
            "type": "sales_drop",
            "description": "Black Friday server crash caused 2-hour outage during peak traffic",
            "root_cause": "Traffic 10x normal capacity, auto-scaling too slow, database connections exhausted",
            "action_taken": "Emergency manual scaling, activated CDN, implemented queue system for checkout",
            "outcome": "Recovered in 2 hours, lost estimated $45,000, implemented pre-scaling for events",
            "quarter": "Q4",
        },
        {
            "id": 2,
            "type": "stockout",
            "description": "Top 5 products sold out by December 15, two weeks before Christmas",
            "root_cause": "Underestimated holiday demand by 40%, supplier lead times longer than expected",
            "action_taken": "Air freight emergency restock at 3x cost, implemented pre-order system",
            "outcome": "Captured 60% of demand via backorders, lost $30,000, implemented safety stock policy",
            "quarter": "Q4",
        },
        {
            "id": 3,
            "type": "support_spike",
            "description": "Support tickets increased 400% first week of January from holiday returns",
            "root_cause": "High gift return rate, unclear return policy, understaffed support team",
            "action_taken": "Hired 10 temp support staff, automated return labels, extended response hours",
            "outcome": "Cleared backlog in 10 days, CSAT dropped to 3.2 then recovered to 4.1",
            "quarter": "Q4",
        },
        {
            "id": 4,
            "type": "campaign_failure",
            "description": "Black Friday promotional email had only 0.2% open rate vs expected 15%",
            "root_cause": "Sent at 3 AM wrong timezone, subject line triggered spam filters",
            "action_taken": "Resent with new subject line at optimal time, A/B tested variations",
            "outcome": "Resend achieved 18% open rate, implemented timezone checks and spam testing",
            "quarter": "Q4",
        },
        {
            "id": 5,
            "type": "sales_drop",
            "description": "Cyber Monday sales 25% below target despite increased ad spend",
            "root_cause": "Competitor offered deeper discounts, our deals leaked early reducing urgency",
            "action_taken": "Added flash deals hourly, increased discount depth, extended sale 24 hours",
            "outcome": "Recovered 15% of gap, implemented deal embargo and competitive monitoring",
            "quarter": "Q4",
        },
        # Q1 - Post Holiday
        {
            "id": 6,
            "type": "sales_drop",
            "description": "January sales 45% below forecast for first two weeks",
            "root_cause": "Post-holiday consumer fatigue, aggressive competitor clearance sales",
            "action_taken": "Launched flash sale with 30% off winter items, email campaign to gift card holders",
            "outcome": "Recovered 20% of gap, learned to set lower Q1 forecasts",
            "quarter": "Q1",
        },
        {
            "id": 7,
            "type": "pricing_error",
            "description": "Smart Watch listed at $19.99 instead of $199.99 for 3 hours",
            "root_cause": "Bulk price upload CSV had decimal error, no validation caught it",
            "action_taken": "Honored 50 orders at $180 loss each, implemented price change validation",
            "outcome": "Lost $9,000, prevented future errors with min/max price rules",
            "quarter": "Q1",
        },
        {
            "id": 8,
            "type": "stockout",
            "description": "Protein Powder unavailable for 3 weeks due to supplier issue",
            "root_cause": "Contamination found at supplier facility, entire batch rejected",
            "action_taken": "Emergency supplier switch, customer communication, substitute recommendations",
            "outcome": "Lost $15,000 in sales, diversified to 2 suppliers for key products",
            "quarter": "Q1",
        },
        {
            "id": 9,
            "type": "support_spike",
            "description": "Payment disputes increased 300% in February",
            "root_cause": "Fraud ring targeted site with stolen cards, chargebacks hit",
            "action_taken": "Implemented additional fraud checks, 3D Secure, velocity limits",
            "outcome": "Fraud reduced 90%, some legitimate orders declined initially",
            "quarter": "Q1",
        },
        # Q2 - Spring/Summer
        {
            "id": 10,
            "type": "campaign_failure",
            "description": "Spring social media campaign had 0.3% CTR and zero conversions",
            "root_cause": "Wrong audience targeting (age 55+ for fitness products), poor creative",
            "action_taken": "Rebuilt campaign with proper targeting, new lifestyle creative",
            "outcome": "Retry achieved 2.1% CTR and 1.8% conversion, documented targeting rules",
            "quarter": "Q2",
        },
        {
            "id": 11,
            "type": "support_spike",
            "description": "200+ tickets about checkout failures in one afternoon",
            "root_cause": "Payment SDK update broke iOS checkout flow",
            "action_taken": "Rolled back SDK, deployed hotfix, refunded failed orders automatically",
            "outcome": "Fixed in 4 hours, 15 customers churned, implemented SDK testing protocol",
            "quarter": "Q2",
        },
        {
            "id": 12,
            "type": "sales_drop",
            "description": "Memorial Day weekend sales 30% below last year",
            "root_cause": "Started promotion too late, competitor had week-long head start",
            "action_taken": "Extended sale 2 extra days, added doorbusters, increased ad spend 50%",
            "outcome": "Recovered partially, implemented holiday calendar with earlier start dates",
            "quarter": "Q2",
        },
        {
            "id": 13,
            "type": "stockout",
            "description": "Sunglasses sold out during heat wave, missed $20k in sales",
            "root_cause": "Weather-driven demand spike not anticipated",
            "action_taken": "Express reorder, added weather-based demand forecasting",
            "outcome": "3 weeks stockout, implemented weather API integration for forecasting",
            "quarter": "Q2",
        },
        # Q3 - Back to School
        {
            "id": 14,
            "type": "stockout",
            "description": "Laptop Backpack and Running Shoes sold out during back-to-school rush",
            "root_cause": "Underestimated back-to-school demand, relied on last year's lower numbers",
            "action_taken": "Express reorder at premium shipping, pre-order waitlist",
            "outcome": "Lost estimated $25,000, implemented demand forecasting model",
            "quarter": "Q3",
        },
        {
            "id": 15,
            "type": "campaign_failure",
            "description": "Paid $15,000 for influencer campaign with 0.1% engagement",
            "root_cause": "Influencer had 80% fake followers, inadequate vetting",
            "action_taken": "Terminated contract, disputed payment, implemented verification process",
            "outcome": "Recovered $10,000, now require follower audit before partnerships",
            "quarter": "Q3",
        },
        {
            "id": 16,
            "type": "sales_drop",
            "description": "Labor Day weekend site slowdown caused 40% cart abandonment",
            "root_cause": "Database connection pool exhausted under load",
            "action_taken": "Emergency database optimization, increased connection pool, added caching",
            "outcome": "Fixed in 3 hours, lost estimated $12,000, scheduled load testing",
            "quarter": "Q3",
        },
        {
            "id": 17,
            "type": "support_spike",
            "description": "Shipping delay complaints spiked 200% over two weeks",
            "root_cause": "Major carrier had regional delays due to hurricane",
            "action_taken": "Proactive delay emails, offered shipping refunds, alternative carrier for urgent",
            "outcome": "Reduced ticket volume 40% through proactive communication",
            "quarter": "Q3",
        },
        # Recent Q4
        {
            "id": 18,
            "type": "stockout",
            "description": "Wireless Headphones sold out in 6 hours after TikTok viral video",
            "root_cause": "Unexpected viral social media mention caused 20x normal demand",
            "action_taken": "Implemented pre-order system within hours, social media monitoring alerts",
            "outcome": "Captured 70% of demand via pre-orders, restocked in 5 days",
            "quarter": "Q4",
        },
        {
            "id": 19,
            "type": "campaign_failure",
            "description": "Weekly newsletter failed to send, missing 50k subscriber touchpoint",
            "root_cause": "Email service provider had 4-hour outage",
            "action_taken": "Resent next day with apology, evaluated backup ESP",
            "outcome": "15% lower engagement on resend, implemented ESP redundancy",
            "quarter": "Q4",
        },
        {
            "id": 20,
            "type": "sales_drop",
            "description": "Yesterday's sales dropped 65% compared to typical day",
            "root_cause": "Multiple factors: 3 products out of stock, social campaign underperforming, competitor sale",
            "action_taken": "Investigation ongoing, emergency restock initiated, campaign paused for review",
            "outcome": "Pending resolution",
            "quarter": "Q4",
        },
        # Additional pattern incidents
        {
            "id": 21,
            "type": "sales_drop",
            "description": "Weekend sales consistently 20% lower in Q2",
            "root_cause": "Competitor running weekend-only flash sales",
            "action_taken": "Implemented our own weekend deals, increased weekend ad spend",
            "outcome": "Recovered weekend performance to within 5% of weekdays",
            "quarter": "Q2",
        },
        {
            "id": 22,
            "type": "campaign_failure",
            "description": "Retargeting ads showing to already-converted customers",
            "root_cause": "Pixel not firing on order confirmation, audience not excluding buyers",
            "action_taken": "Fixed pixel, rebuilt audiences with proper exclusions",
            "outcome": "Reduced wasted ad spend by $3,000/month, improved ROAS 40%",
            "quarter": "Q3",
        },
        {
            "id": 23,
            "type": "support_spike",
            "description": "Product quality complaints increased 150% for Winter Jacket",
            "root_cause": "Manufacturing defect in zipper batch",
            "action_taken": "Recall affected batch, automatic replacement offers, supplier audit",
            "outcome": "Resolved 95% of complaints, switched zipper supplier",
            "quarter": "Q4",
        },
        {
            "id": 24,
            "type": "pricing_error",
            "description": "Discount code stacked with sale price, items sold at 60% off",
            "root_cause": "Promo rules didn't exclude sale items",
            "action_taken": "Fixed promo logic, honored existing orders",
            "outcome": "Lost $5,000 margin, implemented promo rule testing",
            "quarter": "Q2",
        },
        {
            "id": 25,
            "type": "stockout",
            "description": "Running Shoes size 10 specifically sold out for 2 weeks",
            "root_cause": "Size distribution forecast wrong, size 10 is most popular",
            "action_taken": "Adjusted size distribution in orders, size-specific alerts",
            "outcome": "Implemented size-level inventory tracking and alerts",
            "quarter": "Q3",
        },
    ]

    for inc in incidents:
        vs.add_incident(
            incident_id=inc["id"],
            incident_type=inc["type"],
            description=inc["description"],
            root_cause=inc["root_cause"],
            action_taken=inc["action_taken"],
            outcome=inc["outcome"],
        )

    log.debug(f"Added {len(incidents)} incidents to VectorStore")


def seed_tickets(vs: VectorStore):
    tickets = [
        {
            "id": 101,
            "subject": "Order not delivered after 10 days",
            "description": "Customer waiting for order #12345, tracking shows delivered but not received",
            "category": "shipping",
            "resolution": "Contacted carrier, confirmed misdelivery, reshipped with signature required, $10 credit",
        },
        {
            "id": 102,
            "subject": "Wrong color item received",
            "description": "Ordered blue Winter Jacket but received black",
            "category": "order",
            "resolution": "Sent correct color express, let customer keep wrong item, apologized",
        },
        {
            "id": 103,
            "subject": "Refund pending for 2 weeks",
            "description": "Returned Running Shoes 14 days ago, refund not processed",
            "category": "refund",
            "resolution": "Found return stuck in processing, expedited refund + $15 credit for delay",
        },
        {
            "id": 104,
            "subject": "Discount code SAVE20 not working",
            "description": "Code gives 'invalid' error at checkout despite being within validity",
            "category": "technical",
            "resolution": "Code had typo in system, fixed and manually applied discount",
        },
        {
            "id": 105,
            "subject": "Product arrived damaged",
            "description": "Smart Watch screen cracked, box was intact",
            "category": "shipping",
            "resolution": "Full refund + replacement sent, filed carrier claim for packaging",
        },
        {
            "id": 106,
            "subject": "Size exchange for Running Shoes",
            "description": "Size 9 too small, need size 10",
            "category": "order",
            "resolution": "Sent size 10 express, prepaid return label for size 9",
        },
        {
            "id": 107,
            "subject": "App crashes during checkout",
            "description": "iOS app closes when tapping 'Pay Now' button",
            "category": "technical",
            "resolution": "Known issue with iOS 17.1, provided web checkout link, fix deployed next day",
        },
        {
            "id": 108,
            "subject": "Double charged for order",
            "description": "Card shows two charges for same order #54321",
            "category": "billing",
            "resolution": "Second charge was authorization hold, explained and confirmed it will drop off",
        },
        {
            "id": 109,
            "subject": "Order shows delivered but missing item",
            "description": "Package had 2 of 3 items, Yoga Mat missing",
            "category": "shipping",
            "resolution": "Warehouse confirmed short ship, sent Yoga Mat express with discount",
        },
        {
            "id": 110,
            "subject": "Cancel order request",
            "description": "Need to cancel order #67890 placed 2 hours ago",
            "category": "order",
            "resolution": "Order already shipped, arranged free return pickup, refunded immediately",
        },
        {
            "id": 111,
            "subject": "Product not as described",
            "description": "Laptop Backpack smaller than dimensions listed",
            "category": "product",
            "resolution": "Confirmed website dimension error, corrected listing, full refund offered",
        },
        {
            "id": 112,
            "subject": "Warranty claim for Wireless Headphones",
            "description": "Left earbud stopped working after 3 months",
            "category": "product",
            "resolution": "Within warranty, replacement sent, defective unit return requested",
        },
        {
            "id": 113,
            "subject": "Account shows wrong order history",
            "description": "Missing recent orders from account page",
            "category": "technical",
            "resolution": "Database sync issue, orders restored, monitoring added",
        },
        {
            "id": 114,
            "subject": "Price dropped after purchase",
            "description": "Bought Smart Watch yesterday, now $30 cheaper",
            "category": "billing",
            "resolution": "Applied price protection policy, refunded $30 difference",
        },
        {
            "id": 115,
            "subject": "International shipping taking too long",
            "description": "Order to Canada stuck in customs for 2 weeks",
            "category": "shipping",
            "resolution": "Contacted customs broker, expedited clearance, added tracking updates",
        },
    ]

    for t in tickets:
        vs.add_ticket(
            ticket_id=t["id"],
            subject=t["subject"],
            description=t["description"],
            category=t["category"],
            resolution=t["resolution"],
        )

    log.debug(f"Added {len(tickets)} tickets to VectorStore")


def seed_products(vs: VectorStore):
    products = [
        (
            1,
            "Wireless Headphones",
            "Electronics",
            "Premium Bluetooth headphones with active noise cancellation, 30-hour battery life, comfortable over-ear design",
        ),
        (
            2,
            "Running Shoes",
            "Footwear",
            "Lightweight running shoes with responsive cushioning, breathable mesh upper, ideal for marathon training",
        ),
        (
            3,
            "Winter Jacket",
            "Clothing",
            "Waterproof insulated jacket rated to -20°C, adjustable hood, multiple pockets, breathable membrane",
        ),
        (
            4,
            "Yoga Mat",
            "Fitness",
            "Non-slip eco-friendly TPE yoga mat, 6mm thick, includes carrying strap, antimicrobial surface",
        ),
        (
            5,
            "Laptop Backpack",
            "Accessories",
            "Water-resistant backpack with padded 15.6-inch laptop compartment, USB charging port, anti-theft pocket",
        ),
        (
            6,
            "Smart Watch",
            "Electronics",
            "Fitness tracker with heart rate monitor, GPS, sleep tracking, 7-day battery, water resistant to 50m",
        ),
        (
            7,
            "Coffee Maker",
            "Home",
            "Programmable 12-cup drip coffee maker with thermal carafe, auto shut-off, brew strength control",
        ),
        (
            8,
            "Desk Lamp",
            "Home",
            "LED desk lamp with adjustable brightness and color temperature, USB charging port, flexible neck",
        ),
        (
            9,
            "Bluetooth Speaker",
            "Electronics",
            "Portable waterproof speaker with 360° sound, 12-hour battery, IPX7 rating, built-in microphone",
        ),
        (
            10,
            "Running Shorts",
            "Clothing",
            "Quick-dry athletic shorts with built-in liner, zippered pocket, reflective details for visibility",
        ),
        (
            11,
            "Protein Powder",
            "Fitness",
            "Whey protein isolate 2lb, 25g protein per serving, low carb, available in chocolate and vanilla",
        ),
        (
            12,
            "Wireless Mouse",
            "Electronics",
            "Ergonomic wireless mouse with adjustable DPI, silent clicks, USB-C rechargeable, works on any surface",
        ),
        (
            13,
            "Water Bottle",
            "Fitness",
            "Insulated stainless steel bottle, keeps drinks cold 24hr or hot 12hr, leak-proof lid, BPA-free",
        ),
        (
            14,
            "Sunglasses",
            "Accessories",
            "Polarized UV400 protection sunglasses, lightweight frame, scratch-resistant lenses, includes case",
        ),
        (
            15,
            "Hiking Boots",
            "Footwear",
            "Waterproof trail hiking boots with Vibram sole, ankle support, breathable Gore-Tex lining",
        ),
    ]

    for p in products:
        vs.add_product(product_id=p[0], name=p[1], category=p[2], description=p[3])

    log.debug(f"Added {len(products)} products to VectorStore")


if __name__ == "__main__":
    seed_vectors()
