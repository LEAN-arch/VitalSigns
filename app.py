# app.py
import streamlit as st
import config
from ui_components import (display_language_selector, display_navigation,
                           display_sidebar_filters, display_optional_modules_toggle,
                           display_footer)
from pages import dashboard_page, glossary_page
from typing import Callable, Dict, List, Any
import pandas as pd
import logging

# Configure logging at the application level
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Page Configuration (Applied once at the top) ---
# Determine initial language for page config before full session state might be active
# or before the _ function is fully initialized with the selected language.
if 'selected_lang_code' not in st.session_state: # Initialize if not present
    st.session_state.selected_lang_code = config.DEFAULT_LANG
initial_lang_code_for_page_config = st.session_state.selected_lang_code

st.set_page_config(
    page_title=config.TEXT_STRINGS[initial_lang_code_for_page_config].get(config.APP_TITLE_KEY, "Vital Signs Dashboard"), # Fallback title
    page_icon=config.APP_ICON,
    layout="wide"
)

# --- Localization Helper ---
# This _ function will be passed to other modules
def create_localization_helper(current_lang_texts_dict: Dict[str, str]) -> Callable[[str, Optional[str]], str]: # Matched type hint
    def get_localized_text(text_key: str, default_text_override: Optional[str] = None) -> str: # Matched type hint
        return current_lang_texts_dict.get(text_key, default_text_override if default_text_override is not None else current_lang_texts_dict.get("translation_missing","TR_APP: {key}").format(key=text_key))
    return get_localized_text

# --- Language Selection & UI Setup ---
# `display_language_selector` uses `st.session_state.selected_lang_code` and updates it via callback
_ = create_localization_helper(config.TEXT_STRINGS['EN']) # Temp _ for initial selector label if needed before full state sync
display_language_selector(st.session_state, _) # Call the function that contains the selectbox

# Fetch the current language dictionary based on updated session state
# This ensures _ is set up with the truly selected language for the rest of the app
current_lang_texts = config.TEXT_STRINGS.get(st.session_state.selected_lang_code, config.TEXT_STRINGS[config.DEFAULT_LANG])
_ = create_localization_helper(current_lang_texts)

# --- App Navigation ---
dashboard_nav_label = _("dashboard_nav_label")
glossary_nav_label = _("glossary_nav_label")
app_mode_selected = display_navigation(st.session_state, _)

# --- Sidebar Filters (Displayed only if on Dashboard page) ---
filter_selections: Dict[str, List[str]] = {}
if app_mode_selected == dashboard_nav_label:
    try:
        all_raw_dataframes_for_filter_options = dashboard_page.get_all_raw_dataframes_for_filters()
        filter_selections = display_sidebar_filters(all_raw_dataframes_for_filter_options, _)
    except Exception as e:
        logger.error(f"Error populating sidebar filters: {e}")
        st.sidebar.error("Error loading filter options.")

# --- Main Content Area ---
try:
    if app_mode_selected == dashboard_nav_label:
        dashboard_page.render(st.session_state, _, filter_selections)
    elif app_mode_selected == glossary_nav_label:
        glossary_page.render(st.session_state, _)
except Exception as e:
    logger.error(f"Error rendering page '{app_mode_selected}': {e}", exc_info=True)
    st.error(f"An error occurred while rendering the page: {e}")


# --- Optional Modules & Footer (Always in Sidebar) ---
display_optional_modules_toggle(_)
display_footer(_)