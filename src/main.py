import streamlit as st
from src.pages import home

def run():
    st.set_page_config(page_title="Admin Panel", page_icon="🍔")
    st.sidebar.title("🍽️ Admin Menu")
    page = st.sidebar.selectbox("Go to", ["Home"])

    if page == "Home":
        home.show()