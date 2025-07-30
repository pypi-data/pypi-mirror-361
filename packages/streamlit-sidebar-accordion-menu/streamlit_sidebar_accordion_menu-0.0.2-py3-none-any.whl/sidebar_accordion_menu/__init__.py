import os
import streamlit.components.v1 as components
import streamlit as st
from pathlib import Path
from .menu_utils import get_main_script_path, convert_dict_menu, normalize_menu

# Create a _RELEASE constant. We'll set this to False while we're developing
# the component, and True when we're ready to package and distribute it.
# (This is, of course, optional - there are innumerable ways to manage your
# release process.)
_RELEASE = True

# Declare a Streamlit component. `declare_component` returns a function
# that is used to create instances of the component. We're naming this
# function "_component_func", with an underscore prefix, because we don't want
# to expose it directly to users. Instead, we will create a custom wrapper
# function, below, that will serve as our component's public API.

# It's worth noting that this call to `declare_component` is the
# *only thing* you need to do to create the binding between Streamlit and
# your component frontend. Everything else we do in this file is simply a
# best practice.

if not _RELEASE:
    _component_func = components.declare_component(
        # We give the component a simple, descriptive name ("sidebar_accordion_menu"
        # clearly describes what this component does)
        "sidebar_accordion_menu",
        # Pass `url` here to tell Streamlit that the component will be served
        # by the local dev server that you run via `npm run start`.
        # (This is useful while your component is in development.)
        url="http://localhost:3001",
    )
else:
    # When we're distributing a production version of the component, we'll
    # replace the `url` param with `path`, and point it to the component's
    # build directory:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("sidebar_accordion_menu", path=build_dir)


# Create a wrapper function for the component. This is an optional
# best practice - we could simply expose the component function returned by
# `declare_component` and call it done. The wrapper allows us to customize
# our component's API: we can pre-process its input args, post-process its
# output value, and add a docstring for users.
def sidebar_accordion_menu(menu_structure=None, key=None, root_script=None):
    """Create a new instance of "sidebar_accordion_menu".

    This component creates a beautiful sidebar accordion menu with page navigation support
    for multi-page Streamlit applications.

    Parameters
    ----------
    menu_structure : dict or list, optional
        The menu structure definition. Can be provided in multiple formats:
        
        Dictionary format (recommended):
            {
                "🏠 Home": None,  # Link to main page
                "📊 Reports": {
                    "Daily": "daily_report",
                    "Weekly": "weekly_report"
                }
            }
        
        List format:
            [
                ("🏠 Home", "__ROOT__"),
                ("📊 Reports", [
                    ("Daily", "pages/daily_report.py"),
                    ("Weekly", "pages/weekly_report.py")
                ])
            ]
    
    key : str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.
    
    root_script : str or None
        The filename of the main Streamlit script. If None, it will be
        automatically detected.

    Returns
    -------
    None
        This component handles page navigation internally and doesn't return a value.

    Examples
    --------
    >>> # Simple dictionary format
    >>> menu = {
    ...     "🏠 Home": None,
    ...     "📊 Analytics": {
    ...         "Sales": "sales_dashboard",
    ...         "Users": "user_analytics"
    ...     }
    ... }
    >>> sidebar_accordion_menu(menu)
    """
    # Get the app root directory
    app_root = Path.cwd()

    # Auto-detect the main script if not provided
    if root_script is None:
        root_script = get_main_script_path()

    # Convert dict format to list format if needed
    if isinstance(menu_structure, dict):
        menu_structure = convert_dict_menu(menu_structure)

    # Normalize the menu structure for the frontend
    menu = normalize_menu(menu_structure, root_script)

    # Call through to our private component function. Arguments we pass here
    # will be sent to the frontend, where they'll be available in an "args"
    # dictionary.
    #
    # "default" is a special argument that specifies the initial return
    # value of the component before the user has interacted with it.
    with st.sidebar:
        selected_key = _component_func(
            menu_structure=menu,
            key=key,
            default=None,
        )

    # Handle the component's return value (selected menu item)
    if "last_selected_key" not in st.session_state:
        st.session_state.last_selected_key = None

    # Only navigate if the selection has changed
    if selected_key != st.session_state.last_selected_key:
        st.session_state.last_selected_key = selected_key

        if selected_key:
            # Navigate to the selected page
            if selected_key == "__ROOT__":
                st.switch_page(root_script)
            elif selected_key.endswith(".py"):
                # Remove 'pages/' prefix if it exists to avoid duplication
                page_file = selected_key.replace("pages/", "")
                pages_path = app_root / "pages" / page_file
                if pages_path.exists():
                    st.switch_page(f"pages/{page_file}")
                else:
                    st.error(f"Page not found: {page_file}")


# Export version and main function
__version__ = "0.0.1"