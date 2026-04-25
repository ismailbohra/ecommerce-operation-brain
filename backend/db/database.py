import json

import asyncpg

from config import Config
from logger import log


class Database:
    # Class-level pool shared across all instances (tools, actions, routes).
    _pool: asyncpg.Pool | None = None

    async def _get_pool(self) -> asyncpg.Pool:
        if Database._pool is None:
            raise RuntimeError("Database not initialised. Call await db.init() first.")
        return Database._pool

    async def _execute(self, query: str, params: tuple = ()):
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            await conn.execute(query, *params)

    async def _fetch(self, query: str, params: tuple = ()) -> list[dict]:
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
            return [dict(row) for row in rows]

    async def _fetchrow(self, query: str, params: tuple = ()) -> dict | None:
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(query, *params)
            return dict(row) if row else None

    async def init(self):
        if Database._pool is None:
            Database._pool = await asyncpg.create_pool(
                Config.DATABASE_URL, min_size=2, max_size=10
            )
        log.info("Database initialised")

    # ------------------------------------------------------------------ #
    # Sales / Products
    # ------------------------------------------------------------------ #

    async def get_product(self, product_id: int) -> dict | None:
        results = await self._fetch(
            "SELECT * FROM products WHERE id = $1", (product_id,)
        )
        return results[0] if results else None

    async def get_all_products(self) -> list[dict]:
        return await self._fetch("SELECT * FROM products ORDER BY name")

    async def get_sales(self, start: str, end: str) -> list[dict]:
        return await self._fetch(
            "SELECT sale_date, SUM(amount) as revenue, SUM(quantity) as orders "
            "FROM sales WHERE sale_date BETWEEN $1 AND $2 GROUP BY sale_date",
            (start, end),
        )

    async def get_top_products(
        self, start: str, end: str, limit: int = 5
    ) -> list[dict]:
        return await self._fetch(
            "SELECT p.id, p.name, SUM(s.amount) as revenue, SUM(s.quantity) as units "
            "FROM sales s JOIN products p ON s.product_id = p.id "
            "WHERE s.sale_date BETWEEN $1 AND $2 GROUP BY p.id, p.name ORDER BY revenue DESC LIMIT $3",
            (start, end, limit),
        )

    async def get_sales_by_region(self, start: str, end: str) -> list[dict]:
        return await self._fetch(
            "SELECT region, SUM(amount) as revenue, SUM(quantity) as orders "
            "FROM sales WHERE sale_date BETWEEN $1 AND $2 GROUP BY region",
            (start, end),
        )

    async def get_product_sales(
        self, product_id: int, start: str, end: str
    ) -> list[dict]:
        return await self._fetch(
            "SELECT * FROM sales WHERE product_id = $1 AND sale_date BETWEEN $2 AND $3 ORDER BY sale_date DESC",
            (product_id, start, end),
        )

    # ------------------------------------------------------------------ #
    # Inventory
    # ------------------------------------------------------------------ #

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
            "UPDATE inventory SET stock = stock + $1 WHERE product_id = $2",
            (quantity, product_id),
        )

    # ------------------------------------------------------------------ #
    # Tickets
    # ------------------------------------------------------------------ #

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
            "VALUES ($1, $2, $3, $4, NOW())",
            (subject, description, category, priority),
        )

    async def resolve_ticket(self, ticket_id: int):
        await self._execute(
            "UPDATE tickets SET status = 'resolved' WHERE id = $1", (ticket_id,)
        )

    async def get_ticket_stats(self, start: str, end: str) -> list[dict]:
        return await self._fetch(
            "SELECT created_at::date AS date, COUNT(*) as count FROM tickets "
            "WHERE created_at::date BETWEEN $1::date AND $2::date GROUP BY created_at::date",
            (start, end),
        )

    # ------------------------------------------------------------------ #
    # Campaigns
    # ------------------------------------------------------------------ #

    async def get_campaigns(self) -> list[dict]:
        return await self._fetch(
            "SELECT *, ROUND(CAST(clicks * 100.0 / NULLIF(impressions, 0) AS numeric), 2) as ctr, "
            "ROUND(CAST(conversions * 100.0 / NULLIF(clicks, 0) AS numeric), 2) as conv_rate "
            "FROM campaigns WHERE status = 'active'"
        )

    async def pause_campaign(self, campaign_id: int):
        await self._execute(
            "UPDATE campaigns SET status = 'paused' WHERE id = $1", (campaign_id,)
        )

    # ------------------------------------------------------------------ #
    # Incidents
    # ------------------------------------------------------------------ #

    async def get_incidents(self, incident_type: str = None) -> list[dict]:
        if incident_type:
            return await self._fetch(
                "SELECT * FROM incidents WHERE type = $1 ORDER BY occurred_at DESC",
                (incident_type,),
            )
        return await self._fetch("SELECT * FROM incidents ORDER BY occurred_at DESC")

    # ------------------------------------------------------------------ #
    # Actions
    # ------------------------------------------------------------------ #

    async def apply_discount(self, product_id: int, percent: float):
        before = await self._fetch(
            "SELECT price, original_price FROM products WHERE id = $1", (product_id,)
        )
        if not before:
            return
        row = before[0]
        # Preserve the original (pre-discount) price on the first discount only
        base_price = row["original_price"] if row["original_price"] is not None else row["price"]
        new_price = base_price * (1 - percent / 100.0)
        await self._execute(
            "UPDATE products SET price = $1, original_price = $2, discount_percent = $3 WHERE id = $4",
            (new_price, base_price, percent, product_id),
        )

    async def get_discounted_products(self) -> list[dict]:
        return await self._fetch(
            "SELECT id, name, category, price, original_price, discount_percent "
            "FROM products WHERE discount_percent > 0 ORDER BY discount_percent DESC"
        )

    # ------------------------------------------------------------------ #
    # Chat Sessions
    # ------------------------------------------------------------------ #

    async def session_exists(self, session_id: str) -> bool:
        row = await self._fetchrow(
            "SELECT id FROM chat_sessions WHERE id = $1", (session_id,)
        )
        return row is not None

    async def create_session(self, session_id: str, title: str = "New Chat") -> dict:
        row = await self._fetchrow(
            "INSERT INTO chat_sessions (id, title) VALUES ($1, $2) RETURNING *",
            (session_id, title),
        )
        return dict(row)

    async def get_sessions(self) -> list[dict]:
        return await self._fetch(
            "SELECT id, title, created_at, updated_at FROM chat_sessions ORDER BY updated_at DESC"
        )

    async def get_session(self, session_id: str) -> dict | None:
        return await self._fetchrow(
            "SELECT id, title, created_at, updated_at FROM chat_sessions WHERE id = $1",
            (session_id,),
        )

    async def update_session_title(self, session_id: str, title: str):
        await self._execute(
            "UPDATE chat_sessions SET title = $1 WHERE id = $2", (title, session_id)
        )

    async def update_session_timestamp(self, session_id: str):
        await self._execute(
            "UPDATE chat_sessions SET updated_at = NOW() WHERE id = $1", (session_id,)
        )

    async def delete_session(self, session_id: str):
        # ON DELETE CASCADE removes messages automatically
        await self._execute("DELETE FROM chat_sessions WHERE id = $1", (session_id,))

    # ------------------------------------------------------------------ #
    # Chat Messages
    # ------------------------------------------------------------------ #

    async def save_message(
        self,
        session_id: str,
        role: str,
        content: str,
        agents: list | None = None,
        actions: list | None = None,
        action_results: list | None = None,
    ) -> dict:
        import json as _json

        row = await self._fetchrow(
            "INSERT INTO chat_messages "
            "(session_id, role, content, agents, actions, action_results) "
            "VALUES ($1, $2, $3, $4, $5, $6) RETURNING *",
            (
                session_id,
                role,
                content,
                _json.dumps(agents or []),
                _json.dumps(actions) if actions is not None else None,
                _json.dumps(action_results) if action_results is not None else None,
            ),
        )
        return dict(row)

    async def get_messages(self, session_id: str) -> list[dict]:
        return await self._fetch(
            "SELECT * FROM chat_messages WHERE session_id = $1 ORDER BY created_at ASC",
            (session_id,),
        )
