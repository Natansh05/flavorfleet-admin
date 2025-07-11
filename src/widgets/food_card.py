import streamlit as st
from src.supabase_client import supabase
from src.models.food_item import FoodItem
from src.models.addOn import AddOn
from urllib.parse import urlparse

def render_food_card(item: FoodItem):
    edit_key = f"edit_{item.id}"
    is_editing = st.session_state.get(edit_key, False)

    # Fetch Add-ons for this food item
    addons_data = supabase.table("addons").select("*").eq("food_id", item.id).execute()
    addons = [AddOn.from_dict(a) for a in addons_data.data] if addons_data.data else []

    if not is_editing:
        with st.container():
            cols = st.columns([1, 3, 1])
            with cols[0]:
                st.image(item.image_url, width=80) if item.image_url else st.write("📷 No Image")
            with cols[1]:
                st.markdown(f"**{item.name}**")
                st.markdown(f"💬 _{item.description}_")
                st.markdown(f"💰 ₹ {item.price}")
                st.markdown(f"🟢 Available: {'Yes' if item.available else 'No'}")

                if addons:
                    st.markdown("**🧂 Add-ons:**")
                    with st.container():
                        addon_texts = [f"🔹 {a.name} (₹{a.price})" for a in addons]
                        st.markdown(
                            f"<div style='max-height:100px; overflow-y:auto; padding:5px; border:1px solid #ccc; border-radius:6px;'>"
                            + "<br>".join(addon_texts) +
                            "</div>", unsafe_allow_html=True
                        )
                else:
                    st.markdown("_No add-ons available_")

            with cols[2]:
                if st.button("✏️", key=f"edit_btn_{item.id}"):
                    st.session_state[edit_key] = True
                if st.button("🗑️", key=f"del_btn_{item.id}"):
                    # Extract the image path from public URL
                    if item.image_url:
                        parsed_url = urlparse(item.image_url)
                        path_parts = parsed_url.path.split("/")
                        image_path = "/".join(path_parts[5:])  # path after /storage/v1/object/public/<bucket-name>/

                        try:
                            supabase.storage.from_("food-images").remove([image_path])  # <-- pass as list!
                        except Exception as e:
                            st.warning(f"⚠️ Failed to remove image: {e}")

                    # Delete the food item
                    supabase.table("foods").delete().eq("id", item.id).execute()
                    st.success(f"Deleted {item.name}")
                    st.rerun()


    else:
        with st.form(f"edit_form_{item.id}"):
            new_name = st.text_input("Food Name", value=item.name)
            new_description = st.text_area("Description", value=item.description, height=100)
            new_price = st.number_input("Price (₹)", value=item.price, min_value=0.0, step=0.5)
            new_available = st.checkbox("Available", value=item.available)

            st.markdown("**🧂 Edit Add-ons**")
            for addon in addons:
                addon_name = st.text_input(f"Name ({addon.name})", value=addon.name, key=f"addon_name_{addon.id}")
                addon_price = st.number_input(f"Price (₹)", value=addon.price, min_value=0.0, step=0.5, key=f"addon_price_{addon.id}")
                cols = st.columns([1, 1])
                with cols[0]:
                    if st.form_submit_button(f"💾 Save Add-on {addon.name}"):
                        supabase.table("addons").update({
                            "name": addon_name,
                            "price": addon_price
                        }).eq("id", addon.id).execute()
                        st.success(f"Updated add-on '{addon.name}'")
                        st.rerun()
                with cols[1]:
                    if st.form_submit_button(f"🗑️ Delete Add-on {addon.name}"):
                        supabase.table("addons").delete().eq("id", addon.id).execute()
                        st.warning(f"Deleted add-on '{addon.name}'")
                        st.rerun()

            st.markdown("**➕ Add New Add-on**")
            new_addon_name = st.text_input("New Add-on Name", key=f"new_addon_name_{item.id}")
            new_addon_price = st.number_input("New Add-on Price (₹)", min_value=0.0, step=0.5, key=f"new_addon_price_{item.id}")
            if st.form_submit_button("Add Add-on"):
                if new_addon_name.strip():
                    supabase.table("addons").insert({
                        "food_id": item.id,
                        "name": new_addon_name,
                        "price": new_addon_price
                    }).execute()
                    st.success(f"Added add-on '{new_addon_name}'")
                    st.rerun()
                else:
                    st.warning("Add-on name cannot be empty.")

            st.markdown("---")

            col_save, col_cancel = st.columns(2)
            with col_save:
                if st.form_submit_button("💾 Save Item"):
                    supabase.table("foods").update({
                        "name": new_name,
                        "description": new_description,
                        "price": new_price,
                        "available": new_available
                    }).eq("id", item.id).execute()
                    st.success("Updated successfully")
                    st.session_state[edit_key] = False
                    st.rerun()
            with col_cancel:
                if st.form_submit_button("❌ Cancel"):
                    st.session_state[edit_key] = False

    st.markdown("---")
