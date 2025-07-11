import streamlit as st
from src.supabase_client import supabase
from src.models.food_item import FoodItem

def render_food_card(item: FoodItem):
    edit_key = f"edit_{item.id}"
    is_editing = st.session_state.get(edit_key, False)

    if not is_editing:
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        with col1:
            st.markdown(f"**{item.name}**")
        with col2:
            st.markdown(f"₹ {item.price}")
        with col3:
            if st.button("✏️", key=f"edit_btn_{item.id}"):
                st.session_state[edit_key] = True
        with col4:
            if st.button("🗑️", key=f"del_{item.id}"):
                supabase.table("foods").delete().eq("id", item.id).execute()
                st.success(f"Deleted {item.name}")
                st.experimental_rerun()
    else:
        with st.form(f"edit_form_{item.id}"):
            new_name = st.text_input("Food Name", value=item.name)
            new_price = st.number_input("Price (₹)", value=item.price, min_value=0.0, step=0.5)
            col_save, col_cancel = st.columns(2)
            with col_save:
                if st.form_submit_button("💾 Save"):
                    supabase.table("foods").update({
                        "name": new_name,
                        "price": new_price
                    }).eq("id", item.id).execute()
                    st.success("Updated successfully")
                    st.session_state[edit_key] = False
                    st.experimental_rerun()
            with col_cancel:
                if st.form_submit_button("❌ Cancel"):
                    st.session_state[edit_key] = False
