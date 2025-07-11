import streamlit as st
import re, uuid, tempfile, os
from src.supabase_client import supabase

def render_add_item_form(selected_category: str, selected_category_id: int):
    st.subheader("➕ Add New Food Item")

    name = st.text_input("Food Name")
    description = st.text_area("Description", height=100)
    price = st.number_input("Price (₹)", min_value=0.0, step=0.5)
    image_file = st.file_uploader("📷 Upload Food Image (Max 5MB)", type=["jpg", "jpeg", "png"])
    available = st.checkbox("Available", value=True)

    # Handle checkbox toggle with session state
    if "use_addons" not in st.session_state:
        st.session_state.use_addons = False
    if "prev_use_addons" not in st.session_state:
        st.session_state.prev_use_addons = False

    st.session_state.use_addons = st.checkbox("Add Add-ons", value=st.session_state.use_addons)

    # Reset addon inputs when toggled off → on
    if st.session_state.use_addons != st.session_state.prev_use_addons:
        st.session_state.prev_use_addons = st.session_state.use_addons
        for key in list(st.session_state.keys()):
            if key.startswith("addon_name_") or key.startswith("addon_price_"):
                del st.session_state[key]

    addon_inputs = []
    if st.session_state.use_addons:
        num_addons = st.number_input("How many add-ons?", min_value=1, step=1, value=1, key="num_addons")
        for i in range(num_addons):
            col1, col2 = st.columns([2, 1])
            with col1:
                name_input = st.text_input(f"Add-On Name {i+1}", key=f"addon_name_{i}")
            with col2:
                price_input = st.number_input("₹ Price", min_value=0.0, step=0.5, key=f"addon_price_{i}")
            addon_inputs.append((name_input, price_input))

    if st.button("✅ Submit"):
        if name.strip() == "" or description.strip() == "":
            st.warning("Name and Description cannot be empty.")
        elif price <= 0:
            st.warning("Price must be greater than 0.")
        elif not image_file:
            st.warning("Please upload an image.")
        elif image_file.size > 5 * 1024 * 1024:
            st.warning("Image must be under 5MB.")
        else:
            try:
                safe_category = re.sub(r"[^\w\-]", "_", selected_category)
                ext = image_file.type.split("/")[-1]
                filename = f"{uuid.uuid4()}.{ext}"
                path = f"{safe_category}/{filename}"

                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
                    tmp.write(image_file.read())
                    tmp_path = tmp.name

                supabase.storage.from_("food-images").upload(path=path, file=tmp_path, file_options={"content-type": image_file.type})
                os.remove(tmp_path)

                image_url = supabase.storage.from_("food-images").get_public_url(path)
                result = supabase.table("foods").insert({
                    "name": name, "price": price, "description": description,
                    "available": available, "image_url": image_url, "category_id": selected_category_id
                }).execute()

                food_id = result.data[0]["id"]

                if st.session_state.use_addons:
                    for addon_name, addon_price in addon_inputs:
                        if addon_name.strip():
                            supabase.table("addons").insert({
                                "food_id": food_id,
                                "name": addon_name.strip(),
                                "price": addon_price
                            }).execute()

                st.success("✅ Food item and add-ons added successfully.")
                st.session_state["show_add_item_form"] = False
                st.rerun()

            except Exception as e:
                st.error(f"❌ Upload failed: {str(e)}")
