import asyncio
from database import Database, seed_database
from vectorstore import VectorStore, seed_vector_store


async def test_vector_store():
    # Ensure database is seeded first
    await seed_database()

    # Seed vector store (force=True for in-memory)
    await seed_vector_store(force=True)

    vs = VectorStore()

    print("\n=== Testing Vector Store ===\n")

    # Test product search
    print("1. Product Search: 'wireless audio device'")
    results = vs.search_products("wireless audio device", limit=3)
    for r in results:
        print(f"   [{r['score']:.3f}] {r['name']} - {r['category']}")

    print("\n2. Product Search: 'computer accessories for desk'")
    results = vs.search_products("computer accessories for desk", limit=3)
    for r in results:
        print(f"   [{r['score']:.3f}] {r['name']} - {r['category']}")

    # Test ticket search
    print("\n3. Similar Tickets: 'my package never arrived'")
    results = vs.search_similar_tickets("my package never arrived", limit=3)
    for r in results:
        print(f"   [{r['score']:.3f}] {r['subject']}")

    print("\n4. Similar Tickets: 'want my money back'")
    results = vs.search_similar_tickets("want my money back", limit=3)
    for r in results:
        print(f"   [{r['score']:.3f}] {r['subject']}")

    # Test incident search - KEY FOR MEMORY RECALL
    print("\n5. Past Incidents: 'sales dropped significantly'")
    results = vs.search_similar_incidents("sales dropped significantly", limit=3)
    for r in results:
        print(f"   [{r['score']:.3f}] {r['description'][:60]}...")
        print(f"      Action: {r['action_taken'][:50]}...")

    print("\n6. Past Incidents: 'products out of stock'")
    results = vs.search_similar_incidents("products out of stock", limit=3)
    for r in results:
        print(f"   [{r['score']:.3f}] {r['description'][:60]}...")
        print(f"      Action: {r['action_taken'][:50]}...")

    print("\n7. Past Incidents by Type: 'revenue decline' (type=sales_drop)")
    results = vs.search_incidents_by_type("revenue decline", "sales_drop", limit=3)
    for r in results:
        print(f"   [{r['score']:.3f}] {r['description'][:60]}...")

    # Collection stats
    print("\n8. Collection Statistics:")
    for collection in ["products", "support_tickets", "past_incidents"]:
        count = vs.get_collection_count(collection)
        print(f"   {collection}: {count} vectors")

    print("\n=== Phase 2 Tests Completed ===")


if __name__ == "__main__":
    asyncio.run(test_vector_store())
