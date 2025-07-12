import streamlit as st
from src.supabase_client import supabase
from src.models.food_item import FoodItem
from src.widgets.food_card import render_food_card
from src.widgets.add_item_form import render_add_item_form 

def show():
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.warning("🔒 Please login to access this page.")
        st.stop()

    st.title("📋 FlavorFleet Menu Management")

    # Fetch categories
    categories_data = supabase.table("categories").select("*").execute()
    categories = categories_data.data

    if not categories:
        st.warning("⚠️ No categories found.")
        return

    category_names = [cat["name"] for cat in categories]
    category_map = {cat["name"]: cat["id"] for cat in categories}

    # ✅ Add new category section
    with st.expander("➕ Add New Category"):
        new_category_name = st.text_input("Enter new category name", key="new_category_input")
        if st.button("Create Category", key="create_category_btn"):
            if new_category_name.strip() == "":
                st.warning("Category name cannot be empty.")
            else:
                existing_names = [cat["name"].lower() for cat in categories]
                if new_category_name.lower() in existing_names:
                    st.warning("Category already exists.")
                else:
                    supabase.table("categories").insert({"name": new_category_name.strip()}).execute()
                    st.success(f"✅ Added category '{new_category_name}'")
                    st.rerun()

    # ✅ Category selection
    selected_category = st.selectbox("🍽️ Select Food Category", category_names)
    selected_category_id = category_map[selected_category]

    # Fetch food items for selected category
    foods_data = supabase.table("foods").select("*").eq("category_id", selected_category_id).execute()
    food_items = [FoodItem.from_dict(f) for f in foods_data.data]

    st.subheader(f"🍛 Items in '{selected_category}'")

    if not food_items:
        st.info("No food items in this category yet.")

        if "confirm_delete_category" not in st.session_state:
            st.session_state.confirm_delete_category = False

        if not st.session_state.confirm_delete_category:
            if st.button("🗑️ Delete This Category", key="delete_category_btn"):
                st.session_state.confirm_delete_category = True
                st.rerun()
        else:
            st.warning("⚠️ This will permanently delete the selected category.")
            confirm = st.checkbox("Yes, I want to delete this category.")

            if confirm:
                try:
                    supabase.table("categories").delete().eq("id", selected_category_id).execute()
                    st.success(f"✅ Deleted category '{selected_category}'")
                    st.session_state.confirm_delete_category = False
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed to delete category: {e}")
                    st.session_state.confirm_delete_category = False
    else:
        for item in food_items:
            with st.container():
                render_food_card(item)

    # Divider & Add Food Button
    st.markdown("---")
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    if st.button("➕ Add New Item"):
        st.session_state["show_add_item_form"] = True
    st.markdown("</div>", unsafe_allow_html=True)

    # Show add item form
    if st.session_state.get("show_add_item_form"):
        render_add_item_form(selected_category, selected_category_id)
