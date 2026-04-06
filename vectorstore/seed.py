from .store import VectorStore


def seed_vectors():
    vs = VectorStore()
    vs.init_collections()

    # Check if already seeded
    if vs.count("incidents") > 0:
        print("Vector store already seeded")
        return

    # Historical incidents for memory agent
    incidents = [
        {
            "id": 1,
            "type": "sales_drop",
            "description": "Sales dropped 40% during Black Friday due to website issues",
            "root_cause": "Server overload from traffic spike",
            "action_taken": "Scaled up infrastructure, added caching layer",
            "outcome": "Sales recovered within 4 hours, lost ~$15,000",
        },
        {
            "id": 2,
            "type": "sales_drop",
            "description": "Sudden 30% sales decline mid-week",
            "root_cause": "Payment gateway outage",
            "action_taken": "Switched to backup payment provider",
            "outcome": "Recovered same day, minimal impact",
        },
        {
            "id": 3,
            "type": "stockout",
            "description": "Top 3 products ran out of stock during holiday season",
            "root_cause": "Underestimated demand, slow supplier response",
            "action_taken": "Emergency restock via air freight, set up alerts",
            "outcome": "Lost ~$25,000 in sales, implemented safety stock policy",
        },
        {
            "id": 4,
            "type": "stockout",
            "description": "Viral product sold out in 2 hours",
            "root_cause": "Social media spike, no inventory buffer",
            "action_taken": "Pre-order system implemented, supplier fast-track",
            "outcome": "Captured 60% of demand via pre-orders",
        },
        {
            "id": 5,
            "type": "campaign_failure",
            "description": "Email campaign had 0.3% CTR vs expected 3%",
            "root_cause": "Poor subject line, wrong audience segment",
            "action_taken": "A/B tested new copy, refined segmentation",
            "outcome": "Follow-up campaign achieved 4.2% CTR",
        },
        {
            "id": 6,
            "type": "campaign_failure",
            "description": "Social media ad spend with zero conversions",
            "root_cause": "Wrong targeting, landing page mismatch",
            "action_taken": "Paused campaign, rebuilt targeting, new landing page",
            "outcome": "Relaunch achieved 2.5% conversion rate",
        },
        {
            "id": 7,
            "type": "support_spike",
            "description": "Support tickets increased 300% in one day",
            "root_cause": "Shipping delay from carrier issues",
            "action_taken": "Proactive email to affected customers, extra support staff",
            "outcome": "Reduced ticket volume by 50% within 48 hours",
        },
        {
            "id": 8,
            "type": "support_spike",
            "description": "Complaints about product quality spiked",
            "root_cause": "Bad batch from supplier",
            "action_taken": "Recall batch, automatic refunds, supplier audit",
            "outcome": "Customer satisfaction recovered, switched suppliers",
        },
        {
            "id": 9,
            "type": "pricing_error",
            "description": "Product listed at $10 instead of $100",
            "root_cause": "Manual entry error during bulk update",
            "action_taken": "Honored orders, implemented validation rules",
            "outcome": "Cost $5,000, prevented future errors",
        },
        {
            "id": 10,
            "type": "sales_drop",
            "description": "Weekend sales 50% lower than usual",
            "root_cause": "Competitor flash sale drew traffic away",
            "action_taken": "Launched counter-promotion with email blast",
            "outcome": "Recovered 70% of expected sales",
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

    print(f"✓ Added {len(incidents)} incidents to vector store")

    # Sample resolved tickets for similarity search
    tickets = [
        {
            "id": 101,
            "subject": "Order not delivered after 7 days",
            "description": "Customer waiting for order #12345, no tracking update",
            "category": "shipping",
            "resolution": "Contacted carrier, expedited reshipment, offered discount",
        },
        {
            "id": 102,
            "subject": "Wrong item in package",
            "description": "Received blue shirt instead of red",
            "category": "order",
            "resolution": "Sent correct item express, let customer keep wrong item",
        },
        {
            "id": 103,
            "subject": "Refund not processed",
            "description": "Returned item 2 weeks ago, no refund yet",
            "category": "refund",
            "resolution": "Expedited refund, added store credit as apology",
        },
        {
            "id": 104,
            "subject": "Discount code not working",
            "description": "Code SAVE20 gives error at checkout",
            "category": "technical",
            "resolution": "Fixed code configuration, manually applied discount",
        },
        {
            "id": 105,
            "subject": "Product arrived damaged",
            "description": "Box was crushed, item broken inside",
            "category": "shipping",
            "resolution": "Full refund + replacement sent, filed carrier claim",
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

    print(f"✓ Added {len(tickets)} tickets to vector store")

    # Products for semantic search
    products = [
        (
            1,
            "Wireless Headphones",
            "Electronics",
            "Premium Bluetooth headphones with noise cancellation, 30hr battery",
        ),
        (
            2,
            "Running Shoes",
            "Footwear",
            "Lightweight running shoes with cushioned sole for marathon training",
        ),
        (
            3,
            "Winter Jacket",
            "Clothing",
            "Waterproof insulated jacket for cold weather, -20°C rated",
        ),
        (
            4,
            "Yoga Mat",
            "Fitness",
            "Non-slip eco-friendly yoga mat, 6mm thick with carrying strap",
        ),
        (
            5,
            "Laptop Backpack",
            "Accessories",
            "Water-resistant backpack with padded laptop compartment, USB port",
        ),
    ]

    for p in products:
        vs.add_product(product_id=p[0], name=p[1], category=p[2], description=p[3])

    print(f"✓ Added {len(products)} products to vector store")
    print("✅ Vector store seeded!")


if __name__ == "__main__":
    seed_vectors()
