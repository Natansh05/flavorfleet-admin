import streamlit as st
from src.supabase_client import supabase
import pandas as pd
import altair as alt
from datetime import datetime

# Fetching functions
def fetch_all():
    return {
        "orders": supabase.table("orders").select("*").execute().data,
        "order_items": supabase.table("order_items").select("*").execute().data,
        "addons": supabase.table("order_item_addons").select("*").execute().data,
        "foods": supabase.table("foods").select("id, name, category_id").execute().data,
        "categories": supabase.table("categories").select("id, name").execute().data,
        "addon_defs": supabase.table("addons").select("id, name").execute().data
    }

def show():
    st.set_page_config(page_title="📆 Monthly Summary", layout="wide")

    data = fetch_all()
    
    orders_df = pd.DataFrame(data["orders"])
    items_df = pd.DataFrame(data["order_items"])
    addons_df = pd.DataFrame(data["addons"])
    foods_df = pd.DataFrame(data["foods"])
    categories_df = pd.DataFrame(data["categories"])
    addon_defs_df = pd.DataFrame(data["addon_defs"])

    # Preprocess datetime
    for df in [orders_df, items_df]:
        if not df.empty:
            df["created_at"] = pd.to_datetime(df["created_at"], format="ISO8601")

    # Month selector
    if orders_df.empty:
        st.warning("No orders available.")
        return

    orders_df["month"] = orders_df["created_at"].dt.to_period("M")
    available_months = sorted(orders_df["month"].unique(), reverse=True)
    selected_month = st.selectbox("Select Month", available_months)

    # Filter data by month
    month_orders = orders_df[orders_df["month"] == selected_month]
    month_items = items_df[items_df["created_at"].dt.to_period("M") == selected_month]
    
    st.subheader(f"📊 Summary for {selected_month.strftime('%B %Y')}")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("💰 Monthly Revenue", f"₹ {month_orders['amount'].sum():,.2f}")
    with col2:
        st.metric("📦 Total Orders", len(month_orders))

    # Top Food Item
    st.markdown("---")
    st.subheader("🥇 Most Ordered Item")
    if not month_items.empty and not foods_df.empty:
        merged = month_items.merge(foods_df, left_on="food_item_id", right_on="id")
        top_item = merged.groupby("name")["quantity"].sum().reset_index().sort_values(by="quantity", ascending=False).head(1)
        row = top_item.iloc[0]
        st.success(f"**{row['name']}** with **{int(row['quantity'])}** orders")

    # Day vs Night Sales and Category-wise Orders
    st.markdown("---")
    col1, col2 = st.columns(2)

    # 🌞 Day vs 🌙 Night Sales
    with col1:
        st.subheader("🌞 Day vs 🌙 Night Sales")
        if not month_orders.empty:
            def get_period(hour):
                return "Night" if hour < 6 or hour >= 18 else "Day"

            month_orders["period"] = month_orders["created_at"].dt.hour.apply(get_period)
            period_stats = month_orders.groupby("period")["amount"].sum().reset_index()

            # Calculate percentage and formatted label
            total_amount = period_stats["amount"].sum()
            period_stats["percent"] = period_stats["amount"] / total_amount * 100
            period_stats["label"] = period_stats["period"] + " (" + period_stats["percent"].round(1).astype(str) + "%)"

            pie_chart = alt.Chart(period_stats).mark_arc(innerRadius=50).encode(
                theta=alt.Theta(field="amount", type="quantitative"),
                color=alt.Color(field="label", type="nominal", title="Period"),
                tooltip=["period", "amount", alt.Tooltip("percent:Q", format=".1f")]
            ).properties(height=350, width=350)

            st.altair_chart(pie_chart, use_container_width=True)
        else:
            st.info("No order data available.")

    # 📂 Orders by Category
    with col2:
        st.subheader("📂 Orders by Category")
        if not month_items.empty and not foods_df.empty and not categories_df.empty:
            # Merge items with food and category data
            merged = month_items.merge(foods_df, left_on="food_item_id", right_on="id")
            merged = merged.merge(categories_df, left_on="category_id", right_on="id", suffixes=('', '_cat'))
            category_orders = merged.groupby("name_cat")["quantity"].sum().reset_index()

            # Calculate percentage
            total_quantity = category_orders["quantity"].sum()
            category_orders["percent"] = category_orders["quantity"] / total_quantity * 100
            category_orders["label"] = category_orders["name_cat"] + " (" + category_orders["percent"].round(1).astype(str) + "%)"

            cat_pie = alt.Chart(category_orders).mark_arc(innerRadius=50).encode(
                theta=alt.Theta(field="quantity", type="quantitative"),
                color=alt.Color(field="label", type="nominal", title="Category"),
                tooltip=["name_cat", "quantity", alt.Tooltip("percent:Q", format=".1f")]
            ).properties(height=350, width=350)

            st.altair_chart(cat_pie, use_container_width=True)
        else:
            st.info("No category data available.")

    # Category MVP
    st.markdown("---")
    st.subheader("🏆 Category MVP")
    if not categories_df.empty:
        category_names = dict(zip(categories_df.id, categories_df.name))
        selected_cat = st.selectbox("Select Category", list(category_names.values()))
        selected_cat_id = categories_df[categories_df.name == selected_cat].iloc[0].id

        # Find items from this category
        category_items = foods_df[foods_df.category_id == selected_cat_id]
        if not category_items.empty:
            merged = month_items.merge(category_items, left_on="food_item_id", right_on="id")
            top_cat_items = merged.groupby("name")["quantity"].sum().reset_index().sort_values(by="quantity", ascending=False).head(5)
            st.altair_chart(
                alt.Chart(top_cat_items).mark_bar().encode(
                    x="quantity:Q",
                    y=alt.Y("name:N", sort="-x"),
                    tooltip=["name", "quantity"]
                ).properties(height=300), use_container_width=True
            )
        else:
            st.info("No items found for this category in the selected month.")



    # Total Add-ons Used
    st.markdown("---")
    st.subheader("🧂 Add-on Usage")
    if not addons_df.empty:
        merged_addons = addons_df.merge(addon_defs_df, left_on="addon_id", right_on="id")
        addon_usage = merged_addons.groupby("name").size().reset_index(name="count").sort_values(by="count", ascending=False).head(10)
        st.altair_chart(
            alt.Chart(addon_usage).mark_bar().encode(
                x="count:Q",
                y=alt.Y("name:N", sort="-x"),
                tooltip=["name", "count"]
            ).properties(height=350), use_container_width=True
        )

    