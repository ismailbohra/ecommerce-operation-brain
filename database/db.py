import aiosqlite
import os
from datetime import datetime, timedelta
from config import Config


class Database:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or Config.DB_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    async def init_schema(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.executescript(
                """
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    price REAL NOT NULL,
                    description TEXT
                );
                
                CREATE TABLE IF NOT EXISTS inventory (
                    id INTEGER PRIMARY KEY,
                    product_id INTEGER NOT NULL,
                    stock_quantity INTEGER NOT NULL,
                    reorder_level INTEGER DEFAULT 10,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products(id)
                );
                
                CREATE TABLE IF NOT EXISTS sales (
                    id INTEGER PRIMARY KEY,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    unit_price REAL NOT NULL,
                    total_amount REAL NOT NULL,
                    sale_date DATE NOT NULL,
                    region TEXT,
                    FOREIGN KEY (product_id) REFERENCES products(id)
                );
                
                CREATE TABLE IF NOT EXISTS support_tickets (
                    id INTEGER PRIMARY KEY,
                    customer_id INTEGER,
                    subject TEXT NOT NULL,
                    description TEXT NOT NULL,
                    category TEXT NOT NULL,
                    status TEXT DEFAULT 'open',
                    priority TEXT DEFAULT 'medium',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    resolved_at TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS marketing_campaigns (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    channel TEXT NOT NULL,
                    budget REAL NOT NULL,
                    spent REAL DEFAULT 0,
                    start_date DATE NOT NULL,
                    end_date DATE,
                    status TEXT DEFAULT 'active',
                    impressions INTEGER DEFAULT 0,
                    clicks INTEGER DEFAULT 0,
                    conversions INTEGER DEFAULT 0
                );
                
                CREATE TABLE IF NOT EXISTS past_incidents (
                    id INTEGER PRIMARY KEY,
                    incident_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    root_cause TEXT,
                    action_taken TEXT,
                    outcome TEXT,
                    occurred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """
            )
            await db.commit()

    async def execute(self, query: str, params: tuple = ()):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(query, params)
            await db.commit()

    async def fetch_all(self, query: str, params: tuple = ()):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(query, params)
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def fetch_one(self, query: str, params: tuple = ()):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(query, params)
            row = await cursor.fetchone()
            return dict(row) if row else None

    # Sales queries
    async def get_sales_by_date(self, date: str):
        return await self.fetch_all("SELECT * FROM sales WHERE sale_date = ?", (date,))

    async def get_sales_summary(self, start_date: str, end_date: str):
        return await self.fetch_all(
            """
            SELECT sale_date, 
                   SUM(total_amount) as revenue,
                   SUM(quantity) as total_orders,
                   COUNT(DISTINCT product_id) as products_sold
            FROM sales 
            WHERE sale_date BETWEEN ? AND ?
            GROUP BY sale_date
            ORDER BY sale_date
        """,
            (start_date, end_date),
        )

    async def get_top_products_by_revenue(
        self, start_date: str, end_date: str, limit: int = 5
    ):
        return await self.fetch_all(
            """
            SELECT p.name, p.category, 
                   SUM(s.total_amount) as revenue,
                   SUM(s.quantity) as units_sold
            FROM sales s
            JOIN products p ON s.product_id = p.id
            WHERE s.sale_date BETWEEN ? AND ?
            GROUP BY p.id
            ORDER BY revenue DESC
            LIMIT ?
        """,
            (start_date, end_date, limit),
        )

    async def get_sales_by_region(self, start_date: str, end_date: str):
        return await self.fetch_all(
            """
            SELECT region, 
                   SUM(total_amount) as revenue,
                   SUM(quantity) as orders
            FROM sales 
            WHERE sale_date BETWEEN ? AND ?
            GROUP BY region
        """,
            (start_date, end_date),
        )

    # Inventory queries
    async def get_inventory_status(self):
        return await self.fetch_all(
            """
            SELECT p.id, p.name, p.category, i.stock_quantity, 
                   i.reorder_level, i.last_updated
            FROM inventory i
            JOIN products p ON i.product_id = p.id
            ORDER BY i.stock_quantity ASC
        """
        )

    async def get_low_stock_products(self):
        return await self.fetch_all(
            """
            SELECT p.id, p.name, p.category, i.stock_quantity, i.reorder_level
            FROM inventory i
            JOIN products p ON i.product_id = p.id
            WHERE i.stock_quantity <= i.reorder_level
        """
        )

    async def get_out_of_stock_products(self):
        return await self.fetch_all(
            """
            SELECT p.id, p.name, p.category
            FROM inventory i
            JOIN products p ON i.product_id = p.id
            WHERE i.stock_quantity = 0
        """
        )

    async def update_stock(self, product_id: int, quantity: int):
        await self.execute(
            """
            UPDATE inventory 
            SET stock_quantity = ?, last_updated = CURRENT_TIMESTAMP
            WHERE product_id = ?
        """,
            (quantity, product_id),
        )

    # Support queries
    async def get_open_tickets(self):
        return await self.fetch_all(
            "SELECT * FROM support_tickets WHERE status = 'open' ORDER BY created_at DESC"
        )

    async def get_tickets_by_category(self):
        return await self.fetch_all(
            """
            SELECT category, COUNT(*) as count, 
                   SUM(CASE WHEN status = 'open' THEN 1 ELSE 0 END) as open_count
            FROM support_tickets
            GROUP BY category
        """
        )

    async def get_recent_tickets(self, days: int = 7):
        return await self.fetch_all(
            """
            SELECT * FROM support_tickets 
            WHERE created_at >= datetime('now', ?)
            ORDER BY created_at DESC
        """,
            (f"-{days} days",),
        )

    async def create_ticket(
        self, subject: str, description: str, category: str, priority: str = "medium"
    ):
        await self.execute(
            """
            INSERT INTO support_tickets (subject, description, category, priority)
            VALUES (?, ?, ?, ?)
        """,
            (subject, description, category, priority),
        )

    # Marketing queries
    async def get_active_campaigns(self):
        return await self.fetch_all(
            "SELECT * FROM marketing_campaigns WHERE status = 'active'"
        )

    async def get_campaign_performance(self):
        return await self.fetch_all(
            """
            SELECT name, channel, budget, spent, 
                   impressions, clicks, conversions,
                   CASE WHEN impressions > 0 THEN ROUND(clicks * 100.0 / impressions, 2) ELSE 0 END as ctr,
                   CASE WHEN clicks > 0 THEN ROUND(conversions * 100.0 / clicks, 2) ELSE 0 END as conversion_rate
            FROM marketing_campaigns
            WHERE status = 'active'
        """
        )

    async def pause_campaign(self, campaign_id: int):
        await self.execute(
            "UPDATE marketing_campaigns SET status = 'paused' WHERE id = ?",
            (campaign_id,),
        )

    # Past incidents
    async def get_past_incidents(self, incident_type: str = None):
        if incident_type:
            return await self.fetch_all(
                "SELECT * FROM past_incidents WHERE incident_type = ? ORDER BY occurred_at DESC",
                (incident_type,),
            )
        return await self.fetch_all(
            "SELECT * FROM past_incidents ORDER BY occurred_at DESC"
        )

    async def add_incident(
        self,
        incident_type: str,
        description: str,
        root_cause: str,
        action_taken: str,
        outcome: str,
    ):
        await self.execute(
            """
            INSERT INTO past_incidents (incident_type, description, root_cause, action_taken, outcome)
            VALUES (?, ?, ?, ?, ?)
        """,
            (incident_type, description, root_cause, action_taken, outcome),
        )
