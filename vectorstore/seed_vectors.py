import asyncio
from database import Database
from .qdrant_store import VectorStore


async def seed_vector_store(force: bool = False):
    db = Database()
    vs = VectorStore()

    # Initialize collections
    vs.init_collections()

    # Check if already seeded (skip for in-memory since it's always fresh)
    try:
        count = vs.get_collection_count("products")
        if count > 0 and not force:
            print("Vector store already seeded")
            return
    except:
        pass

    print("Seeding vector store...")

    # Seed products
    products = await db.fetch_all("SELECT * FROM products")
    for p in products:
        vs.add_product(p["id"], p["name"], p["category"], p["description"])
    print(f"Added {len(products)} products to vector store")

    # Seed support tickets
    tickets = await db.fetch_all("SELECT * FROM support_tickets")
    for t in tickets:
        vs.add_ticket(t["id"], t["subject"], t["description"], t["category"])
    print(f"Added {len(tickets)} tickets to vector store")

    # Seed past incidents
    incidents = await db.fetch_all("SELECT * FROM past_incidents")
    for i in incidents:
        vs.add_incident(
            i["id"],
            i["incident_type"],
            i["description"],
            i["root_cause"],
            i["action_taken"],
            i["outcome"],
        )
    print(f"Added {len(incidents)} incidents to vector store")

    # Add more detailed past incidents for better memory recall
    additional_incidents = [
        {
            "type": "sales_drop",
            "description": "Sales dropped 30% on a Tuesday due to payment gateway issues",
            "root_cause": "Payment provider had an outage affecting card transactions",
            "action": "Switched to backup payment provider, notified customers via email",
            "outcome": "Recovered within 4 hours, offered 10% discount to affected customers",
        },
        {
            "type": "sales_drop",
            "description": "Revenue declined 25% during a week in December",
            "root_cause": "Main competitor launched aggressive discount campaign",
            "action": "Launched flash sale with 15% off, increased ad spend",
            "outcome": "Recovered 80% of lost sales within 3 days",
        },
        {
            "type": "inventory_stockout",
            "description": "Wireless headphones went out of stock for 5 days",
            "root_cause": "Supplier delay due to shipping issues",
            "action": "Found alternative supplier, added backorder option",
            "outcome": "Lost ~50 sales, implemented dual-supplier strategy",
        },
        {
            "type": "support_spike",
            "description": "Customer complaints increased 200% after product update",
            "root_cause": "New firmware caused connectivity issues",
            "action": "Rolled back update, issued fix within 48 hours",
            "outcome": "Complaints normalized, offered free accessory to affected users",
        },
        {
            "type": "campaign_failure",
            "description": "Social media campaign had negative engagement",
            "root_cause": "Ad creative was perceived as insensitive",
            "action": "Pulled campaign immediately, issued apology",
            "outcome": "Brand sentiment recovered in 2 weeks after PR response",
        },
    ]

    base_id = len(incidents) + 1
    for idx, inc in enumerate(additional_incidents):
        vs.add_incident(
            base_id + idx,
            inc["type"],
            inc["description"],
            inc["root_cause"],
            inc["action"],
            inc["outcome"],
        )
    print(f"Added {len(additional_incidents)} additional incidents")

    print("Vector store seeded successfully!")


def seed_sync():
    asyncio.run(seed_vector_store())


if __name__ == "__main__":
    seed_sync()
