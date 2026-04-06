import asyncio
from dataclasses import dataclass
from database import Database


@dataclass
class ProposedAction:
    action_type: str
    description: str
    params: dict

    def to_dict(self):
        return {
            "action_type": self.action_type,
            "description": self.description,
            "params": self.params,
        }


class ActionManager:
    def __init__(self):
        self.db = Database()

    def get_inventory_actions(self) -> list[ProposedAction]:
        """Get proposed actions for inventory issues."""

        async def _run():
            actions = []

            out_of_stock = await self.db.get_out_of_stock_products()
            for p in out_of_stock:
                actions.append(
                    ProposedAction(
                        action_type="restock",
                        description=f"Restock '{p['name']}' (+50 units)",
                        params={"product_id": p["id"], "quantity": 50},
                    )
                )

            low_stock = await self.db.get_low_stock_products()
            for p in low_stock:
                if p["stock_quantity"] > 0:
                    actions.append(
                        ProposedAction(
                            action_type="restock",
                            description=f"Restock '{p['name']}' (+30 units, currently {p['stock_quantity']})",
                            params={"product_id": p["id"], "quantity": 30},
                        )
                    )

            return actions

        return asyncio.run(_run())

    def get_support_actions(self) -> list[ProposedAction]:
        """Get proposed actions for support tickets."""

        async def _run():
            actions = []

            tickets = await self.db.get_open_tickets()
            for t in tickets:
                priority_icon = "🔴" if t["priority"] == "high" else "🟡"
                actions.append(
                    ProposedAction(
                        action_type="resolve_ticket",
                        description=f"{priority_icon} [{t['priority'].upper()}] {t['subject']} (#{t['id']} - {t['category']})",
                        params={
                            "ticket_id": t["id"],
                            "subject": t["subject"],
                            "category": t["category"],
                        },
                    )
                )

            return actions

        return asyncio.run(_run())

    def get_marketing_actions(self) -> list[ProposedAction]:
        """Get proposed actions for marketing issues."""

        async def _run():
            actions = []
            campaigns = await self.db.get_campaign_performance()

            for c in campaigns:
                if c["ctr"] < 2.0:
                    actions.append(
                        ProposedAction(
                            action_type="pause_campaign",
                            description=f"Pause '{c['name']}' (CTR: {c['ctr']}%)",
                            params={"campaign_id": c.get("id", 0)},
                        )
                    )

            return actions

        return asyncio.run(_run())

    def execute_action(self, action: ProposedAction) -> str:
        """Execute a single action."""
        if action.action_type == "restock":
            return self._exec_restock(**action.params)
        elif action.action_type == "pause_campaign":
            return self._exec_pause_campaign(**action.params)
        elif action.action_type == "resolve_ticket":
            return self._exec_resolve_ticket(**action.params)
        else:
            return f"❌ Unknown action type: {action.action_type}"

    def _exec_restock(self, product_id: int, quantity: int) -> str:
        async def _run():
            product = await self.db.fetch_one(
                "SELECT name FROM products WHERE id = ?", (product_id,)
            )
            if not product:
                return f"❌ Product ID {product_id} not found."

            inventory = await self.db.fetch_one(
                "SELECT stock_quantity FROM inventory WHERE product_id = ?",
                (product_id,),
            )
            old_qty = inventory["stock_quantity"] if inventory else 0
            new_qty = old_qty + quantity

            await self.db.update_stock(product_id, new_qty)
            return f"✅ Restocked '{product['name']}': {old_qty} → {new_qty} units"

        return asyncio.run(_run())

    def _exec_pause_campaign(self, campaign_id: int) -> str:
        async def _run():
            result = await self.db.fetch_one(
                "SELECT name FROM marketing_campaigns WHERE id = ?", (campaign_id,)
            )
            if not result:
                return f"❌ Campaign ID {campaign_id} not found."

            await self.db.pause_campaign(campaign_id)
            return f"✅ Paused campaign '{result['name']}'"

        return asyncio.run(_run())

    def _exec_resolve_ticket(
        self, ticket_id: int, subject: str = "", category: str = ""
    ) -> str:
        async def _run():
            result = await self.db.fetch_one(
                "SELECT subject, status FROM support_tickets WHERE id = ?", (ticket_id,)
            )
            if not result:
                return f"❌ Ticket ID {ticket_id} not found."

            if result["status"] == "resolved":
                return f"⚠️ Ticket #{ticket_id} '{result['subject']}' already resolved."

            await self.db.execute(
                "UPDATE support_tickets SET status = 'resolved', resolved_at = CURRENT_TIMESTAMP WHERE id = ?",
                (ticket_id,),
            )
            return f"✅ Resolved ticket #{ticket_id}: '{result['subject']}'"

        return asyncio.run(_run())
