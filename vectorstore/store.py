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
from logger import log


class VectorStore:
    _instance = None
    _client = None

    COLLECTIONS = {
        "incidents": 1536,
        "tickets": 1536,
        "products": 1536,
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        if VectorStore._client is None:
            VectorStore._client = self._create_client()
            atexit.register(self._cleanup)

        self.client = VectorStore._client
        self.embeddings = get_embeddings()
        self._initialized = True

    @classmethod
    def _cleanup(cls):
        try:
            if cls._client is not None:
                cls._client.close()
                cls._client = None
                cls._instance = None
        except:
            pass

    def _create_client(self) -> QdrantClient:
        mode = Config.QDRANT_MODE

        if mode == "memory":
            log.info("VectorStore: in-memory mode")
            return QdrantClient(":memory:")

        elif mode == "local":
            os.makedirs(Config.QDRANT_PATH, exist_ok=True)
            log.info(f"VectorStore: local at {Config.QDRANT_PATH}")
            try:
                return QdrantClient(path=Config.QDRANT_PATH)
            except RuntimeError:
                log.warning("Qdrant locked, falling back to memory")
                return QdrantClient(":memory:")

        else:
            log.info(
                f"VectorStore: server at {Config.QDRANT_HOST}:{Config.QDRANT_PORT}"
            )
            return QdrantClient(host=Config.QDRANT_HOST, port=Config.QDRANT_PORT)

    def _embed(self, text: str) -> list[float]:
        return self.embeddings.embed_query(text)

    def _embed_batch(self, texts: list[str]) -> list[list[float]]:
        return self.embeddings.embed_documents(texts)

    def init_collections(self):
        existing = [c.name for c in self.client.get_collections().collections]
        for name, dim in self.COLLECTIONS.items():
            if name not in existing:
                self.client.create_collection(
                    collection_name=name,
                    vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
                )
                log.debug(f"Created collection: {name}")
        log.info("VectorStore collections initialized")

    def _search(
        self,
        collection: str,
        query: str,
        limit: int = 5,
        filter_conditions: Filter = None,
    ) -> list[dict]:
        vector = self._embed(query)
        results = self.client.query_points(
            collection_name=collection,
            query=vector,
            limit=limit,
            query_filter=filter_conditions,
        )
        return [{"score": r.score, **r.payload} for r in results.points]

    # ============ INCIDENTS ============
    def add_incident(
        self,
        incident_id: int,
        incident_type: str,
        description: str,
        root_cause: str,
        action_taken: str,
        outcome: str,
    ):
        text = f"Type: {incident_type}. {description}. Cause: {root_cause}. Action: {action_taken}. Result: {outcome}"
        vector = self._embed(text)
        self.client.upsert(
            collection_name="incidents",
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

    def search_incidents(self, query: str, limit: int = 5) -> list[dict]:
        return self._search("incidents", query, limit)

    def search_incidents_by_type(
        self, query: str, incident_type: str, limit: int = 5
    ) -> list[dict]:
        filter_cond = Filter(
            must=[
                FieldCondition(
                    key="incident_type", match=MatchValue(value=incident_type)
                )
            ]
        )
        return self._search("incidents", query, limit, filter_cond)

    # ============ TICKETS ============
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
            collection_name="tickets",
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

    def search_tickets(self, query: str, limit: int = 5) -> list[dict]:
        return self._search("tickets", query, limit)

    def search_tickets_by_category(
        self, query: str, category: str, limit: int = 5
    ) -> list[dict]:
        filter_cond = Filter(
            must=[FieldCondition(key="category", match=MatchValue(value=category))]
        )
        return self._search("tickets", query, limit, filter_cond)

    # ============ PRODUCTS ============
    def add_product(self, product_id: int, name: str, category: str, description: str):
        text = f"Product: {name}. Category: {category}. {description}"
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
        return self._search("products", query, limit)

    # ============ UTILS ============
    def count(self, collection: str) -> int:
        try:
            return self.client.get_collection(collection).points_count
        except:
            return 0

    def reset(self):
        for name in self.COLLECTIONS:
            try:
                self.client.delete_collection(name)
            except:
                pass
        self.init_collections()
