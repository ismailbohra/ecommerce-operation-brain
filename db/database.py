import aiosqlite
import os
from config import Config

SCHEMA = """
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT,
    price REAL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS inventory (
    product_id INTEGER PRIMARY KEY,
    stock INTEGER DEFAULT 0,
    reorder_level INTEGER DEFAULT 10
);

CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY,
    product_id INTEGER,
    quantity INTEGER,
    amount REAL,
    sale_date TEXT,
    region TEXT
);

CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY,
    subject TEXT,
    description TEXT,
    category TEXT,
    priority TEXT DEFAULT 'medium',
    status TEXT DEFAULT 'open',
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS campaigns (
    id INTEGER PRIMARY KEY,
    name TEXT,
    channel TEXT,
    budget REAL,
    spent REAL DEFAULT 0,
    status TEXT DEFAULT 'active',
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS incidents (
    id INTEGER PRIMARY KEY,
    type TEXT,
    description TEXT,
    root_cause TEXT,
    action_taken TEXT,
    outcome TEXT,
    occurred_at TEXT
);
"""


class Database:
    def __init__(self):
        self.path = Config.DB_PATH
        os.makedirs(os.path.dirname(self.path), exist_ok=True)

    async def _execute(self, query: str, params: tuple = ()):
        async with aiosqlite.connect(self.path) as db:
            await db.execute(query, params)
            await db.commit()

    async def _fetch(self, query: str, params: tuple = ()) -> list[dict]:
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(query, params)
            return [dict(row) for row in await cursor.fetchall()]

    async def init(self):
        async with aiosqlite.connect(self.path) as db:
            await db.executescript(SCHEMA)
            await db.commit()

    # Sales / Products

    async def get_product(self, product_id: int) -> dict | None:
        results = await self._fetch(
            "SELECT * FROM products WHERE id = ?", (product_id,)
        )
        return results[0] if results else None

    async def get_all_products(self) -> list[dict]:
        return await self._fetch("SELECT * FROM products ORDER BY name")

    async def get_sales(self, start: str, end: str) -> list[dict]:
        return await self._fetch(
            "SELECT sale_date, SUM(amount) as revenue, SUM(quantity) as orders "
            "FROM sales WHERE sale_date BETWEEN ? AND ? GROUP BY sale_date",
            (start, end),
        )

    async def get_top_products(
        self, start: str, end: str, limit: int = 5
    ) -> list[dict]:
        return await self._fetch(
            "SELECT p.id, p.name, SUM(s.amount) as revenue, SUM(s.quantity) as units "
            "FROM sales s JOIN products p ON s.product_id = p.id "
            "WHERE s.sale_date BETWEEN ? AND ? GROUP BY p.id ORDER BY revenue DESC LIMIT ?",
            (start, end, limit),
        )

    async def get_sales_by_region(self, start: str, end: str) -> list[dict]:
        return await self._fetch(
            "SELECT region, SUM(amount) as revenue, SUM(quantity) as orders "
            "FROM sales WHERE sale_date BETWEEN ? AND ? GROUP BY region",
            (start, end),
        )

    async def get_product_sales(
        self, product_id: int, start: str, end: str
    ) -> list[dict]:
        return await self._fetch(
            "SELECT * FROM sales WHERE product_id = ? AND sale_date BETWEEN ? AND ? ORDER BY sale_date DESC",
            (product_id, start, end),
        )

    # Inventory
    async def get_inventory(self) -> list[dict]:
        return await self._fetch(
            "SELECT p.id, p.name, i.stock, i.reorder_level "
            "FROM inventory i JOIN products p ON i.product_id = p.id ORDER BY i.stock"
        )

    async def get_low_stock(self) -> list[dict]:
        return await self._fetch(
            "SELECT p.id, p.name, i.stock FROM inventory i "
            "JOIN products p ON i.product_id = p.id "
            "WHERE i.stock <= i.reorder_level AND i.stock > 0"
        )

    async def get_out_of_stock(self) -> list[dict]:
        return await self._fetch(
            "SELECT p.id, p.name FROM inventory i "
            "JOIN products p ON i.product_id = p.id WHERE i.stock = 0"
        )

    async def update_stock(self, product_id: int, quantity: int):
        await self._execute(
            "UPDATE inventory SET stock = stock + ? WHERE product_id = ?",
            (quantity, product_id),
        )

    # Tickets
    async def get_open_tickets(self) -> list[dict]:
        return await self._fetch(
            "SELECT * FROM tickets WHERE status = 'open' ORDER BY "
            "CASE priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END"
        )

    async def get_ticket_summary(self) -> list[dict]:
        return await self._fetch(
            "SELECT category, priority, COUNT(*) as count FROM tickets "
            "WHERE status = 'open' GROUP BY category, priority"
        )

    async def create_ticket(
        self, subject: str, description: str, category: str, priority: str
    ):
        await self._execute(
            "INSERT INTO tickets (subject, description, category, priority, created_at) "
            "VALUES (?, ?, ?, ?, datetime('now'))",
            (subject, description, category, priority),
        )

    async def resolve_ticket(self, ticket_id: int):
        await self._execute(
            "UPDATE tickets SET status = 'resolved' WHERE id = ?", (ticket_id,)
        )

    async def get_ticket_stats(self, start: str, end: str) -> list[dict]:
        return await self._fetch(
            "SELECT DATE(created_at) as date, COUNT(*) as count FROM tickets "
            "WHERE DATE(created_at) BETWEEN ? AND ? GROUP BY DATE(created_at)",
            (start, end),
        )

    # Campaigns
    async def get_campaigns(self) -> list[dict]:
        return await self._fetch(
            "SELECT *, ROUND(clicks * 100.0 / NULLIF(impressions, 0), 2) as ctr, "
            "ROUND(conversions * 100.0 / NULLIF(clicks, 0), 2) as conv_rate "
            "FROM campaigns WHERE status = 'active'"
        )

    async def pause_campaign(self, campaign_id: int):
        await self._execute(
            "UPDATE campaigns SET status = 'paused' WHERE id = ?", (campaign_id,)
        )

    # Incidents
    async def get_incidents(self, incident_type: str = None) -> list[dict]:
        if incident_type:
            return await self._fetch(
                "SELECT * FROM incidents WHERE type = ? ORDER BY occurred_at DESC",
                (incident_type,),
            )
        return await self._fetch("SELECT * FROM incidents ORDER BY occurred_at DESC")

    # Actions
    async def apply_discount(self, product_id: int, percent: float):
        before = await self._fetch(
            "SELECT price FROM products WHERE id = ?", (product_id,)
        )
        if not before:
            return

        old_price = before[0]["price"]
        new_price = old_price * (1 - percent / 100.0)

        await self._execute(
            "UPDATE products SET price = ? WHERE id = ?", (new_price, product_id)
        )
