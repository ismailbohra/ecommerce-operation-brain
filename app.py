import streamlit as st
import asyncio
import uuid
from datetime import datetime, timedelta
from db import Database, seed_database
from vectorstore import seed_vectors
from graph import create_workflow, run_query, resume_with_actions
from logger import log

st.set_page_config(page_title="ecomx", page_icon="🦉", layout="wide")


def run_async(coro):
    return asyncio.run(coro)


@st.cache_resource
def init_system():
    log.info("Initializing system...")
    run_async(seed_database())
    seed_vectors()
    workflow = create_workflow()
    log.info("System initialized")
    return workflow


def get_dashboard_metrics():
    db = Database()
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)

    sales = run_async(db.get_sales(week_ago.isoformat(), today.isoformat()))
    out_of_stock = run_async(db.get_out_of_stock())
    low_stock = run_async(db.get_low_stock())
    tickets = run_async(db.get_open_tickets())
    campaigns = run_async(db.get_campaigns())

    return {
        "revenue": sum(s["revenue"] or 0 for s in sales) if sales else 0,
        "orders": sum(s["orders"] or 0 for s in sales) if sales else 0,
        "out_of_stock": len(out_of_stock),
        "low_stock": len(low_stock),
        "open_tickets": len(tickets),
        "high_priority": len([t for t in tickets if t["priority"] == "high"]),
        "campaigns": len(campaigns),
        "ad_spend": sum(c["spent"] or 0 for c in campaigns) if campaigns else 0,
    }


def render_sidebar():
    st.header("📊 Dashboard")
    m = get_dashboard_metrics()

    st.subheader("Sales (7d)")
    col1, col2 = st.columns(2)
    col1.metric("Revenue", f"${m['revenue']:,.0f}")
    col2.metric("Orders", m["orders"])

    st.subheader("Inventory")
    col1, col2 = st.columns(2)
    col1.metric("Out of Stock", m["out_of_stock"], delta_color="inverse")
    col2.metric("Low Stock", m["low_stock"], delta_color="inverse")

    st.subheader("Support")
    col1, col2 = st.columns(2)
    col1.metric("Open Tickets", m["open_tickets"])
    col2.metric("High Priority", m["high_priority"], delta_color="inverse")

    st.subheader("Marketing")
    col1, col2 = st.columns(2)
    col1.metric("Campaigns", m["campaigns"])
    col2.metric("Ad Spend", f"${m['ad_spend']:,.0f}")

    st.divider()

    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_actions = None
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()


def render_action_approval(actions: list[dict], workflow):
    st.warning("⚠️ Actions require your approval")

    selected = []
    for action in actions:
        col1, col2 = st.columns([0.05, 0.95])
        with col1:
            if st.checkbox(" ", key=f"action_{action['id']}"):
                selected.append(action["id"])
        with col2:
            st.markdown(f"**{action['description']}**")
            st.caption(f"Reason: {action['reason']}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Execute Selected", type="primary", use_container_width=True):
            if selected:
                result = resume_with_actions(
                    workflow, st.session_state.thread_id, selected
                )
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": "**Executed:**\n"
                        + "\n".join(result.get("action_results", [])),
                    }
                )
                st.session_state.pending_actions = None
                st.rerun()

    with col2:
        if st.button("❌ Reject All", use_container_width=True):
            st.session_state.messages.append(
                {"role": "assistant", "content": "Actions rejected by user."}
            )
            st.session_state.pending_actions = None
            st.rerun()


def main():
    workflow = init_system()

    # Session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "pending_actions" not in st.session_state:
        st.session_state.pending_actions = None
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())

    # Sidebar
    with st.sidebar:
        render_sidebar()

    st.title("🦉 ecomx")

    # ✅ CHAT CONTAINER (SCROLL SAFE)
    chat_container = st.container(height=600)

    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if "agents" in msg and msg["agents"]:
                    st.caption(f"Consulted: {', '.join(msg['agents'])}")

    # Pending actions (HITL)
    if st.session_state.pending_actions:
        render_action_approval(st.session_state.pending_actions, workflow)
        return

    # Chat input
    if query := st.chat_input("Ask about your business..."):
        st.session_state.messages.append({"role": "user", "content": query})

        with chat_container:
            with st.chat_message("user"):
                st.markdown(query)

            with st.chat_message("assistant"):
                with st.spinner("Analyzing..."):
                    result = run_query(
                        workflow,
                        query,
                        st.session_state.thread_id,
                        st.session_state.messages,
                    )

                st.markdown(result["response"])

                if result.get("agents_to_call"):
                    st.caption(f"Consulted: {', '.join(result['agents_to_call'])}")

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": result["response"],
                "agents": result.get("agents_to_call", []),
            }
        )

        if result.get("proposed_actions"):
            st.session_state.pending_actions = result["proposed_actions"]
            st.rerun()


if __name__ == "__main__":
    main()
