import streamlit as st
import asyncio
from agents import Supervisor
from database import Database, seed_database
from vectorstore import seed_vector_store
from datetime import datetime, timedelta

st.set_page_config(
    page_title="E-commerce Operation Brains", page_icon="ECOMX", layout="wide"
)


@st.cache_resource
def init_system():
    asyncio.run(seed_database())
    asyncio.run(seed_vector_store())
    return Supervisor()


@st.cache_data(ttl=60)
def get_dashboard_metrics():
    db = Database()

    async def fetch_metrics():
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)

        # Sales metrics
        sales = await db.get_sales_summary(week_ago.isoformat(), today.isoformat())
        total_revenue = sum(s["revenue"] for s in sales) if sales else 0
        total_orders = sum(s["total_orders"] for s in sales) if sales else 0

        # Inventory metrics
        low_stock = await db.get_low_stock_products()
        out_of_stock = await db.get_out_of_stock_products()

        # Support metrics
        open_tickets = await db.get_open_tickets()
        high_priority = len([t for t in open_tickets if t["priority"] == "high"])

        # Marketing metrics
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

    # Sales
    st.subheader("💰 Sales (7 days)")
    col1, col2 = st.columns(2)
    col1.metric("Revenue", f"${metrics['revenue']:,.0f}")
    col2.metric("Orders", metrics["orders"])

    st.divider()

    # Inventory
    st.subheader("📦 Inventory")
    col1, col2 = st.columns(2)
    col1.metric("Out of Stock", metrics["out_of_stock"], delta_color="inverse")
    col2.metric("Low Stock", metrics["low_stock"], delta_color="inverse")

    if metrics["out_of_stock"] > 0:
        st.warning(f"⚠️ {metrics['out_of_stock']} products need restocking!")

    st.divider()

    # Support
    st.subheader("🎫 Support")
    col1, col2 = st.columns(2)
    col1.metric("Open Tickets", metrics["open_tickets"])
    col2.metric("High Priority", metrics["high_priority"], delta_color="inverse")

    if metrics["high_priority"] > 0:
        st.error(f"🔴 {metrics['high_priority']} high priority tickets!")

    st.divider()

    # Marketing
    st.subheader("📣 Marketing")
    col1, col2 = st.columns(2)
    col1.metric("Campaigns", metrics["active_campaigns"])
    col2.metric("Ad Spend", f"${metrics['ad_spend']:,.0f}")

    st.divider()

    # Actions
    if st.button("🔄 Refresh Dashboard", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


def main():
    st.title("🧠 E-commerce Operations Brain")
    st.caption(
        "Ask questions about sales, inventory, support, marketing, or past incidents"
    )

    # Initialize
    supervisor = init_system()

    # Session state for chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Sidebar Dashboard
    with st.sidebar:
        render_sidebar_dashboard()

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and "agents" in msg:
                render_agent_badges(msg["agents"])
                render_findings(msg.get("findings", {}))

    # Chat input
    if query := st.chat_input("Ask about your business operations..."):
        # Display user message
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        # Get response with chat history
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                result = supervisor.invoke(
                    query, st.session_state.messages
                )  # Pass history

            st.markdown(result["response"])
            render_agent_badges(result["agents_consulted"])
            render_findings(result["findings"])

        # Save to history
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
