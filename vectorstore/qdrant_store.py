import os
import atexit
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)
from config import Config, get_embeddings


class VectorStore:
    COLLECTIONS = {
        "products": 1536,
        "support_tickets": 1536,
        "past_incidents": 1536,
    }

    _instance = None
    _client = None

    # Singleton pattern
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if VectorStore._client is None:
            VectorStore._client = self._create_client()
            atexit.register(self._cleanup)
        self.client = VectorStore._client
        self.embeddings = get_embeddings()

    # Tackle Closing exceptions
    @classmethod
    def _cleanup(cls):
        try:
            if cls._client is not None:
                cls._client.close()
                cls._client = None
        except:
            pass

    def _create_client(self):
        mode = Config.QDRANT_MODE

        if mode == "memory":
            print("Using in-memory Qdrant")
            return QdrantClient(":memory:")

        elif mode == "local":
            os.makedirs(Config.QDRANT_PATH, exist_ok=True)
            print(f"Using local Qdrant at {Config.QDRANT_PATH}")
            return QdrantClient(path=Config.QDRANT_PATH)

        else:
            print(
                f"Connecting to Qdrant server at {Config.QDRANT_HOST}:{Config.QDRANT_PORT}"
            )
            return QdrantClient(host=Config.QDRANT_HOST, port=Config.QDRANT_PORT)

    def init_collections(self):
        existing = [c.name for c in self.client.get_collections().collections]

        for name, dim in self.COLLECTIONS.items():
            if name not in existing:
                self.client.create_collection(
                    collection_name=name,
                    vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
                )
                print(f"Created collection: {name}")
            else:
                print(f"Collection exists: {name}")

    def _embed(self, text: str) -> list[float]:
        return self.embeddings.embed_query(text)

    def _embed_batch(self, texts: list[str]) -> list[list[float]]:
        return self.embeddings.embed_documents(texts)

    def _search(
        self,
        collection_name: str,
        query_vector: list[float],
        limit: int,
        query_filter: Filter = None,
    ) -> list[dict]:
        results = self.client.query_points(
            collection_name=collection_name,
            query=query_vector,
            limit=limit,
            query_filter=query_filter,
        )
        return [{"score": r.score, **r.payload} for r in results.points]

    def add_product(self, product_id: int, name: str, category: str, description: str):
        text = f"{name}. Category: {category}. {description}"
        vector = self._embed(text)

        self.client.upsert(
            collection_name="products",
            points=[
                PointStruct(
                    id=product_id,
                    vector=vector,
                    payload={
                        "product_id": product_id,
                        "name": name,
                        "category": category,
                        "description": description,
                    },
                )
            ],
        )

    def search_products(self, query: str, limit: int = 5) -> list[dict]:
        vector = self._embed(query)
        return self._search("products", vector, limit)

    def add_ticket(
        self,
        ticket_id: int,
        subject: str,
        description: str,
        category: str,
        resolution: str = None,
    ):
        text = f"Subject: {subject}. Issue: {description}. Category: {category}."
        if resolution:
            text += f" Resolution: {resolution}"

        vector = self._embed(text)

        self.client.upsert(
            collection_name="support_tickets",
            points=[
                PointStruct(
                    id=ticket_id,
                    vector=vector,
                    payload={
                        "ticket_id": ticket_id,
                        "subject": subject,
                        "description": description,
                        "category": category,
                        "resolution": resolution,
                    },
                )
            ],
        )

    def search_similar_tickets(self, query: str, limit: int = 5) -> list[dict]:
        vector = self._embed(query)
        return self._search("support_tickets", vector, limit)

    def search_tickets_by_category(
        self, query: str, category: str, limit: int = 5
    ) -> list[dict]:
        vector = self._embed(query)
        query_filter = Filter(
            must=[FieldCondition(key="category", match=MatchValue(value=category))]
        )
        return self._search("support_tickets", vector, limit, query_filter)

    def add_incident(
        self,
        incident_id: int,
        incident_type: str,
        description: str,
        root_cause: str,
        action_taken: str,
        outcome: str,
    ):
        text = f"Incident: {description}. Type: {incident_type}. Root cause: {root_cause}. Action: {action_taken}. Outcome: {outcome}"
        vector = self._embed(text)

        self.client.upsert(
            collection_name="past_incidents",
            points=[
                PointStruct(
                    id=incident_id,
                    vector=vector,
                    payload={
                        "incident_id": incident_id,
                        "incident_type": incident_type,
                        "description": description,
                        "root_cause": root_cause,
                        "action_taken": action_taken,
                        "outcome": outcome,
                    },
                )
            ],
        )

    def search_similar_incidents(self, query: str, limit: int = 5) -> list[dict]:
        vector = self._embed(query)
        return self._search("past_incidents", vector, limit)

    def search_incidents_by_type(
        self, query: str, incident_type: str, limit: int = 5
    ) -> list[dict]:
        vector = self._embed(query)
        query_filter = Filter(
            must=[
                FieldCondition(
                    key="incident_type", match=MatchValue(value=incident_type)
                )
            ]
        )
        return self._search("past_incidents", vector, limit, query_filter)

    def get_collection_count(self, collection_name: str) -> int:
        info = self.client.get_collection(collection_name)
        return info.points_count

    def delete_collection(self, collection_name: str):
        self.client.delete_collection(collection_name)

    def reset(self):
        for name in self.COLLECTIONS:
            try:
                self.client.delete_collection(name)
            except:
                pass
        self.init_collections()

    def close(self):
        self._cleanup()
