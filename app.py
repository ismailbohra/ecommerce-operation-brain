import streamlit as st
import asyncio
from agents import Supervisor
from database import Database, seed_database
from vectorstore import seed_vector_store
from actions import ActionManager
from datetime import datetime, timedelta

st.set_page_config(
    page_title="E-commerce Operations Brain", page_icon="🧠", layout="wide"
)


@st.cache_resource
def init_system():
    asyncio.run(seed_database())
    asyncio.run(seed_vector_store())
    return Supervisor(), ActionManager()


@st.cache_data(ttl=60)
def get_dashboard_metrics():
    db = Database()

    async def fetch_metrics():
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)

        sales = await db.get_sales_summary(week_ago.isoformat(), today.isoformat())
        total_revenue = sum(s["revenue"] for s in sales) if sales else 0
        total_orders = sum(s["total_orders"] for s in sales) if sales else 0

        low_stock = await db.get_low_stock_products()
        out_of_stock = await db.get_out_of_stock_products()

        open_tickets = await db.get_open_tickets()
        high_priority = len([t for t in open_tickets if t["priority"] == "high"])

        campaigns = await db.get_active_campaigns()
        total_spend = sum(c["spent"] for c in campaigns) if campaigns else 0

        return {
            "revenue": total_revenue,
            "orders": total_orders,
            "out_of_stock": len(out_of_stock),
            "low_stock": len(low_stock),
            "open_tickets": len(open_tickets),
            "high_priority": high_priority,
            "active_campaigns": len(campaigns),
            "ad_spend": total_spend,
        }

    return asyncio.run(fetch_metrics())


def render_agent_badges(agents: list[str]):
    if not agents:
        return
    colors = {
        "sales": "🟢",
        "inventory": "🟠",
        "support": "🔵",
        "marketing": "🟣",
        "memory": "⚪",
    }
    badges = " ".join([f"{colors.get(a, '⚫')} {a.upper()}" for a in agents])
    st.caption(f"Agents consulted: {badges}")


def render_findings(findings: dict[str, str]):
    if not findings:
        return
    with st.expander("📋 Agent Findings", expanded=False):
        for agent, finding in findings.items():
            st.markdown(f"**{agent.upper()}**")
            st.text(finding[:500] + "..." if len(finding) > 500 else finding)
            st.divider()


def render_sidebar_dashboard():
    metrics = get_dashboard_metrics()

    st.header("📊 Dashboard")

    st.subheader("💰 Sales (7 days)")
    col1, col2 = st.columns(2)
    col1.metric("Revenue", f"${metrics['revenue']:,.0f}")
    col2.metric("Orders", metrics["orders"])

    st.divider()

    st.subheader("📦 Inventory")
    col1, col2 = st.columns(2)
    col1.metric("Out of Stock", metrics["out_of_stock"], delta_color="inverse")
    col2.metric("Low Stock", metrics["low_stock"], delta_color="inverse")

    if metrics["out_of_stock"] > 0:
        st.warning(f"⚠️ {metrics['out_of_stock']} need restocking!")

    st.divider()

    st.subheader("🎫 Support")
    col1, col2 = st.columns(2)
    col1.metric("Open Tickets", metrics["open_tickets"])
    col2.metric("High Priority", metrics["high_priority"], delta_color="inverse")

    st.divider()

    st.subheader("📣 Marketing")
    col1, col2 = st.columns(2)
    col1.metric("Campaigns", metrics["active_campaigns"])
    col2.metric("Ad Spend", f"${metrics['ad_spend']:,.0f}")

    st.divider()

    if st.button("🔄 Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_actions = []
        st.rerun()


def render_action_panel(action_manager: ActionManager):
    """Render action selection UI."""
    st.warning("⚠️ **Actions require your approval:**")

    actions = st.session_state.pending_actions
    selected = []

    for i, action in enumerate(actions):
        if st.checkbox(action.description, key=f"action_{i}", value=True):
            selected.append(action)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Execute Selected", type="primary", use_container_width=True):
            if not selected:
                st.error("No actions selected!")
                return

            results = []
            for action in selected:
                result = action_manager.execute_action(action)
                results.append(result)

            result_text = "\n".join(results)
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": f"**Executed Actions:**\n\n{result_text}",
                    "agents": [],
                    "findings": {},
                }
            )
            st.session_state.pending_actions = []
            st.cache_data.clear()
            st.rerun()

    with col2:
        if st.button("❌ Cancel", use_container_width=True):
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": "Actions cancelled.",
                    "agents": [],
                    "findings": {},
                }
            )
            st.session_state.pending_actions = []
            st.rerun()


def detect_action_request(query: str) -> str | None:
    """Detect if query is requesting an action."""
    query_lower = query.lower()

    # Inventory actions
    inventory_keywords = [
        "fix inventory",
        "restock",
        "fix stock",
        "refill stock",
        "update inventory",
        "add stock",
    ]
    if any(kw in query_lower for kw in inventory_keywords):
        return "inventory"

    # Marketing actions
    marketing_keywords = [
        "pause campaign",
        "stop campaign",
        "fix marketing",
        "disable campaign",
        "turn off campaign",
    ]
    if any(kw in query_lower for kw in marketing_keywords):
        return "marketing"

    # Support actions
    support_keywords = [
        "resolve ticket",
        "fix ticket",
        "close ticket",
        "resolve support",
        "fix support",
        "resolve them",
        "close them",
        "mark resolved",
        "resolve all",
    ]
    if any(kw in query_lower for kw in support_keywords):
        return "support"

    # Flexible: "resolve" + "ticket" anywhere
    if "resolve" in query_lower and "ticket" in query_lower:
        return "support"

    if "close" in query_lower and "ticket" in query_lower:
        return "support"

    return None


def main():
    st.title("🧠 E-commerce Operations Brain")
    st.caption(
        "Ask questions about sales, inventory, support, marketing, or past incidents"
    )

    supervisor, action_manager = init_system()

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "pending_actions" not in st.session_state:
        st.session_state.pending_actions = []

    with st.sidebar:
        render_sidebar_dashboard()

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant":
                render_agent_badges(msg.get("agents", []))
                render_findings(msg.get("findings", {}))

    # Handle pending actions
    if st.session_state.pending_actions:
        render_action_panel(action_manager)
        return

    # Chat input
    if query := st.chat_input("Ask about your business operations..."):
        st.session_state.messages.append({"role": "user", "content": query})

        with st.chat_message("user"):
            st.markdown(query)

        # Check if this is an action request
        action_type = detect_action_request(query)

        if action_type:
            # Get proposed actions directly
            if action_type == "inventory":
                actions = action_manager.get_inventory_actions()
            elif action_type == "marketing":
                actions = action_manager.get_marketing_actions()
            elif action_type == "support":
                actions = action_manager.get_support_actions()
            else:
                actions = []

            if actions:
                with st.chat_message("assistant"):
                    st.markdown(f"Found **{len(actions)}** actions to review:")

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": f"Found **{len(actions)}** actions to review:",
                        "agents": [],
                        "findings": {},
                    }
                )

                st.session_state.pending_actions = actions
                st.rerun()
            else:
                with st.chat_message("assistant"):
                    st.success("✅ No issues found. Everything looks good!")
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": "✅ No issues found. Everything looks good!",
                        "agents": [],
                        "findings": {},
                    }
                )
        else:
            # Regular query
            with st.chat_message("assistant"):
                with st.spinner("Analyzing..."):
                    result = supervisor.invoke(query, st.session_state.messages)
                st.markdown(result["response"])
                render_agent_badges(result["agents_consulted"])
                render_findings(result["findings"])

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": result["response"],
                    "agents": result["agents_consulted"],
                    "findings": result["findings"],
                }
            )


if __name__ == "__main__":
    main()
