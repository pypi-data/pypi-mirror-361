import streamlit as st
from sidebar_accordion_menu import sidebar_accordion_menu

st.set_page_config(
    page_title="My App",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Simple dictionary format - NEW! 🎉
menu = {
    "🏠 Home": None,  # None or "home" for main page
    "📊 Analytics": {
        "Sales Dashboard": "sales_dashboard",  # .py extension added automatically
        "User Analytics": "user_analytics",
    },
    "⚙️ Settings": {
        "General": "general_settings",
        "Advanced": "advanced_settings",
    }
}

# Render the accordion menu
sidebar_accordion_menu(menu)

# Your main page content
st.title("Welcome to My App")
st.write("Select a page from the sidebar menu.")