import streamlit as st
from src.supabase_client import supabase
from src.models.food_item import FoodItem
from src.widgets.food_card import render_food_card

def show():
    st.title("📋 Food Menu Management")

    # Load categories
    categories_data = supabase.table("categories").select("*").execute()
    categories = categories_data.data

    if not categories:
        st.warning("⚠️ No categories found.")
        return

    category_names = [cat["name"] for cat in categories]
    category_map = {cat["name"]: cat["id"] for cat in categories}

    selected_category = st.selectbox("🍽️ Select Food Category", category_names)
    selected_category_id = category_map[selected_category]

    # Fetch food items in that category
    foods_data = supabase.table("foods").select("*").eq("category_id", selected_category_id).execute()
    food_items = [FoodItem.from_dict(f) for f in foods_data.data]

    st.subheader(f"🍛 Items in '{selected_category}'")

    if not food_items:
        st.info("No food items in this category yet.")
    else:
        for item in food_items:
            with st.container():
                render_food_card(item)

    # Add Item button
    st.markdown("---")
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    if st.button("➕ Add New Item"):
        st.session_state["show_add_item_form"] = True
    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.get("show_add_item_form"):
        st.switch_page("pages/add_item.py")
