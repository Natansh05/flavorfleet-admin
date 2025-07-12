import streamlit as st
from src.supabase_client import supabase
import pandas as pd
import altair as alt
from ..widgets import monthly_summary
from ..widgets import weekday_analysis
from ..widgets import daily_insight

def fetch_all_data():
    return {
        "orders": supabase.table("orders").select("*").execute().data,
        "order_items": supabase.table("order_items").select("*").execute().data,
        "order_addons": supabase.table("order_item_addons").select("*").execute().data,
        "foods": supabase.table("foods").select("id, name").execute().data,
        "addons": supabase.table("addons").select("id, name").execute().data
    }


# Main Page
def show():
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.warning("🔒 Please login to access this page.")
        st.stop()

    st.set_page_config(page_title="📈 Analytics Dashboard", layout="wide")
    st.title("📊 FlavorFleet Analytics Dashboard")

    # Fetch all data
    data = fetch_all_data()
    orders = data["orders"]
    order_items = data["order_items"]
    order_addons = data["order_addons"]
    foods = data["foods"]
    addons = data["addons"]

    # Convert to DataFrames
    orders_df = pd.DataFrame(orders)
    order_items_df = pd.DataFrame(order_items)
    order_addons_df = pd.DataFrame(order_addons)
    foods_df = pd.DataFrame(foods)
    addons_df = pd.DataFrame(addons)

    # Preprocess timestamps
    if not orders_df.empty:
        orders_df["created_at"] = pd.to_datetime(orders_df["created_at"], format="ISO8601")
    if not order_items_df.empty:
        order_items_df["created_at"] = pd.to_datetime(order_items_df["created_at"], format="ISO8601")

    # ---------- Metrics ----------
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📦 Total Orders", len(orders_df))
    with col2:
        st.metric("💰 Total Revenue", f"₹ {orders_df['amount'].sum():,.2f}")
    with col3:
        st.metric("🧍 Unique Users", orders_df["user_id"].nunique())
    with col4:
        st.metric("🍽️ Total Items Sold", int(order_items_df["quantity"].sum()))

    st.markdown("---")

    # ---------- Expandable Sections ----------

    with st.expander("📆 Monthly Summary", expanded=False):
        monthly_summary.show()

    with st.expander("📅 Weekday Analysis", expanded=False):
        if not orders_df.empty:
            weekday_analysis.render_weekday_analysis(
                orders=orders,
                order_items=order_items,
                foods=foods,
                addons=addons,
                order_addons=order_addons
            )
        else:
            st.warning("No order data available for weekday analysis.")

    with st.expander("📅 Daily Insights", expanded=False):  
        if not orders_df.empty:
            daily_insight.render_daily_insights(
                orders=orders,
                order_items=order_items,
                foods=foods,
                addons=addons,
                order_addons=order_addons,
                categories=supabase.table("categories").select("*").execute().data
            )
        else:
            st.warning("No order data available for daily insights.")

    # Placeholder for future expansions
    with st.expander("🔍 More Insights (Coming Soon)", expanded=False):
        st.info("More analytical features will be added here in the future.")
