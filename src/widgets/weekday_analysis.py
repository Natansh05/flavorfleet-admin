import streamlit as st
import pandas as pd
import altair as alt

def render_weekday_analysis(orders, order_items, foods, addons, order_addons):
    st.set_page_config(page_title="📅 Weekday Analytics", layout="wide")

    if not orders:
        st.warning("No order data available.")
        return

    # Convert to DataFrame
    orders_df = pd.DataFrame(orders)
    order_items_df = pd.DataFrame(order_items)
    addons_df = pd.DataFrame(order_addons)
    foods_df = pd.DataFrame(foods)
    addon_defs_df = pd.DataFrame(addons)

    # Process datetime
    orders_df["created_at"] = pd.to_datetime(orders_df["created_at"], format="ISO8601")
    orders_df["weekday"] = orders_df["created_at"].dt.day_name()
    orders_df["hour"] = orders_df["created_at"].dt.hour
    orders_df["month"] = orders_df["created_at"].dt.to_period("M")

    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    # Toggle: Overall vs Monthly
    toggle_mode = st.radio("Select Analysis Scope:", ["Overall", "Monthly"], horizontal=True)
    if toggle_mode == "Monthly":
        available_months = sorted(orders_df["month"].unique(), reverse=True)
        selected_month = st.selectbox("Select Month", available_months, key="weekday_month_select")
        orders_df = orders_df[orders_df["month"] == selected_month]
        st.subheader(f"📊 Analysis for {selected_month.strftime('%B %Y')}")
    else:
        st.subheader("📊 Overall Weekday Analysis")

    # ---------------- 📦 Orders per Weekday ----------------
    st.subheader("📦 Orders & Revenue by Weekday")
    order_counts = orders_df.groupby("weekday").size().reset_index(name="orders")
    revenue_stats = orders_df.groupby("weekday")["amount"].sum().reset_index(name="revenue")
    merged = order_counts.merge(revenue_stats, on="weekday")
    merged["weekday"] = pd.Categorical(merged["weekday"], categories=weekday_order, ordered=True)
    merged = merged.sort_values("weekday")
    merged["avg_order_value"] = merged["revenue"] / merged["orders"]

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Number of Orders")
        st.altair_chart(
            alt.Chart(merged).mark_bar().encode(
                x=alt.X("weekday:N", sort=weekday_order),
                y="orders:Q",
                tooltip=["weekday", "orders"]
            ).properties(height=300),
            use_container_width=True
        )

    with col2:
        st.markdown("#### Revenue per Weekday")
        st.altair_chart(
            alt.Chart(merged).mark_bar().encode(
                x=alt.X("weekday:N", sort=weekday_order),
                y="revenue:Q",
                tooltip=["weekday", "revenue"]
            ).properties(height=300),
            use_container_width=True
        )

    # ---------------- 📊 Average Order Value ----------------
    st.markdown("#### 💵 Average Order Value per Day")
    st.altair_chart(
        alt.Chart(merged).mark_line(point=True).encode(
            x=alt.X("weekday:N", sort=weekday_order),
            y="avg_order_value:Q",
            tooltip=["weekday", "avg_order_value"]
        ).properties(height=300),
        use_container_width=True
    )

    # ---------------- ⏰ Hourly Heatmap ----------------
    st.markdown("---")
    st.subheader("⏱️ Order Frequency Heatmap (Weekday × Hour)")

    heatmap_data = orders_df.groupby(["weekday", "hour"]).size().reset_index(name="orders")
    heatmap_data["weekday"] = pd.Categorical(heatmap_data["weekday"], categories=weekday_order, ordered=True)

    heatmap = alt.Chart(heatmap_data).mark_rect().encode(
        x=alt.X("hour:O", title="Hour of Day"),
        y=alt.Y("weekday:N", title="Weekday", sort=weekday_order),
        color=alt.Color("orders:Q", scale=alt.Scale(scheme="greens")),
        tooltip=["weekday", "hour", "orders"]
    ).properties(height=350)

    st.altair_chart(heatmap, use_container_width=True)
