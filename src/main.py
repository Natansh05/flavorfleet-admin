import streamlit as st
from src.pages import home, analytics
import os
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

# Login function
def login():
    st.title("🔐 Admin Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            st.session_state.logged_in = True
            st.success("✅ Login successful")
            st.rerun()
        else:
            st.error("❌ Invalid username or password")


# Main app router
def run():
    st.set_page_config(page_title="Admin Panel", page_icon="🍔")

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        login()
        return

    st.sidebar.title("🍽️ Admin Menu")

    # Main menu options
    menu_selection = st.sidebar.radio("Go to", ["Home", "Analytics"])

    # Spacer to push logout to the bottom
    st.sidebar.markdown("<br><br><br><br><br><br><br><br><br><br>", unsafe_allow_html=True)

    # Logout button at bottom
    logout_placeholder = st.sidebar.empty()
    if logout_placeholder.button("🔓 Logout"):
        st.session_state.logged_in = False
        st.success("👋 Logged out")
        st.rerun()

    # Render selected page
    if menu_selection == "Home":
        home.show()
    elif menu_selection == "Analytics":
        analytics.show()


if __name__ == "__main__":
    run()
