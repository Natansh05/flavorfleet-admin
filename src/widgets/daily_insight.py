import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

def render_daily_insights(orders, order_items, foods, addons, order_addons, categories):
    st.set_page_config(page_title="📅 Daily Insights", layout="wide")
    st.title("📅 Daily Order Summary")

    if not orders:
        st.warning("No order data available.")
        return

    # Convert data
    orders_df = pd.DataFrame(orders)
    order_items_df = pd.DataFrame(order_items)
    addons_df = pd.DataFrame(order_addons)
    foods_df = pd.DataFrame(foods)
    addon_defs_df = pd.DataFrame(addons)
    categories_df = pd.DataFrame(categories)

    orders_df["created_at"] = pd.to_datetime(orders_df["created_at"], format="ISO8601")
    order_items_df["created_at"] = pd.to_datetime(order_items_df["created_at"], format="ISO8601")

    # Date selection
    unique_dates = sorted(orders_df["created_at"].dt.date.unique(), reverse=True)
    selected_date = st.date_input("Select Date", value=unique_dates[0], min_value=min(unique_dates), max_value=max(unique_dates))

    # Filter by selected date
    daily_orders = orders_df[orders_df["created_at"].dt.date == selected_date]
    daily_items = order_items_df[order_items_df["created_at"].dt.date == selected_date]
    daily_addons = addons_df[addons_df["order_item_id"].isin(daily_items["id"])] if not daily_items.empty else pd.DataFrame()

    st.subheader(f"📆 Summary for {selected_date.strftime('%A, %d %B %Y')}")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("📦 Total Orders", len(daily_orders))
    with col2:
        st.metric("💰 Total Revenue", f"₹ {daily_orders['amount'].sum():,.2f}")

    # Category Filter
    category_map = {row['id']: row['name'] for _, row in categories_df.iterrows()}
    selected_cat = st.selectbox("Filter by Category (optional)", ["All"] + list(category_map.values()))

    # Join food items for names
    if not daily_items.empty:
        daily_items = daily_items.merge(foods_df, left_on="food_item_id", right_on="id", suffixes=("", "_food"))
        if selected_cat != "All":
            cat_id = categories_df[categories_df.name == selected_cat].iloc[0].id
            daily_items = daily_items[daily_items["category_id"] == cat_id]

    # Table of Orders
    st.markdown("### 📋 Order Details")
    order_table = daily_orders[["id", "user_id", "amount", "created_at"]].sort_values("created_at")
    st.dataframe(order_table, use_container_width=True, hide_index=True)

    # Top Food Items
    st.markdown("### 🍽️ Food Items Ordered")
    if not daily_items.empty:
        food_summary = daily_items.groupby("name")["quantity"].sum().reset_index().sort_values(by="quantity", ascending=False)
        st.dataframe(food_summary, use_container_width=True, hide_index=True)
    else:
        st.info("No food items ordered on this day.")

    # Add-on Usage
    st.markdown("### 🧂 Add-ons Used")
    if not daily_addons.empty:
        daily_addons = daily_addons.merge(addon_defs_df, left_on="addon_id", right_on="id")
        addon_summary = daily_addons.groupby("name").size().reset_index(name="count").sort_values(by="count", ascending=False)
        st.dataframe(addon_summary, use_container_width=True, hide_index=True)
    else:
        st.info("No add-ons used on this day.")
