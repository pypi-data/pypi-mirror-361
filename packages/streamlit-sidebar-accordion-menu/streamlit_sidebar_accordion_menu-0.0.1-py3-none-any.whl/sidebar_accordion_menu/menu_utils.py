"""Menu structure utilities for sidebar accordion menu."""

import os
import sys
from pathlib import Path
import streamlit as st


def get_main_script_path():
    """
    Automatically detect the main Streamlit script filename.
    
    This function uses multiple methods to reliably detect the main script:
    1. Check sys.argv for the script path
    2. Check __main__ module
    3. Default to 'streamlit_app.py' if all else fails
    
    Returns:
        str: The filename of the main Streamlit script (e.g., 'example.py').
    """
    if "root_script" not in st.session_state:
        # Method 1: Check sys.argv for the script path
        for arg in reversed(sys.argv):
            if arg.endswith('.py') and os.path.exists(arg):
                st.session_state.root_script = os.path.basename(arg)
                return st.session_state.root_script
        
        # Method 2: Check __main__ module
        main_module = sys.modules.get('__main__')
        if main_module and hasattr(main_module, '__file__'):
            st.session_state.root_script = os.path.basename(main_module.__file__)
            return st.session_state.root_script
        
        # Default fallback
        st.session_state.root_script = "streamlit_app.py"
    
    return st.session_state.root_script


def convert_dict_menu(menu_dict):
    """
    Convert a simple dictionary menu structure to the internal format.
    
    Example input:
        {
            "🏠 Home": None,  # or "home" for main page
            "📊 Analytics": {
                "Sales": "sales",
                "Reports": "reports"
            }
        }
    
    Returns:
        List of tuples in the internal menu format
    """
    menu_list = []
    for label, value in menu_dict.items():
        if value is None or isinstance(value, str):
            # Single item or home page
            page_key = "__ROOT__" if value in (None, "home", "main") else f"pages/{value}.py" if not value.endswith('.py') else value
            menu_list.append((label, page_key))
        elif isinstance(value, dict):
            # Section with children
            children = []
            for child_label, child_page in value.items():
                page_key = f"pages/{child_page}.py" if not child_page.endswith('.py') else child_page
                children.append((child_label, page_key))
            menu_list.append((label, children))
    return menu_list


def normalize_menu(menu, root_script):
    """
    Normalize menu structure for both parent-clickable and simple children-only menus.
    
    Converts various menu formats into a consistent structure for the React component.
    
    Args:
        menu: Menu structure in various formats
        root_script: The main script filename
    
    Returns:
        List of normalized menu items
    """
    if not menu:
        return []

    # Already normalized
    if isinstance(menu, list) and all(
        isinstance(i, dict) and "label" in i and "key" in i for i in menu
    ):
        return menu

    normalized = []
    for item in menu:
        if isinstance(item[1], str):
            # Parent item with a key (clickable)
            # Keep __ROOT__ as is, don't replace with script name
            normalized.append({
                "label": item[0],
                "key": item[1],
            })
        else:
            # Parent item with children
            label = item[0]
            children = item[1]
            normalized_children = []
            for child in children:
                child_label, child_key = child
                normalized_children.append({
                    "label": child_label,
                    "key": child_key,
                })
            normalized.append({
                "label": label,
                "key": label,  # Parent can be clicked if needed
                "children": normalized_children,
            })
    return normalized