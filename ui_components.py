# ui_components.py
import streamlit as st
import config
from typing import Callable, Dict, List, Any # For st_session_state typehint
import pandas as pd # For List[pd.DataFrame] typehint

def display_language_selector(st_session_state: Any, _: Callable[[str, Optional[str]], str]) -> str: # Matched signature for _
    """Displays language selector and updates session state."""
    st.sidebar.markdown("---")
    available_langs_list = list(config.TEXT_STRINGS.keys())

    # This initialization is primarily for the first run before app.py fully sets it.
    if 'selected_lang_code' not in st_session_state:
        st_session_state.selected_lang_code = config.DEFAULT_LANG

    def update_language_state_callback():
        st_session_state.selected_lang_code = st_session_state._app_lang_selector_key_widget

    lang_selector_widget_key = "_app_lang_selector_key_widget" # Ensure this key is unique if selectbox appears elsewhere
    # Label uses direct lookup as it needs to be bilingual before _ is fully established with current lang
    current_label_en = config.TEXT_STRINGS['EN'].get('language_selector', 'Language')
    current_label_es = config.TEXT_STRINGS['ES'].get('language_selector', 'Idioma')

    st.sidebar.selectbox(
        label=f"{current_label_en} / {current_label_es}",
        options=available_langs_list,
        index=available_langs_list.index(st_session_state.selected_lang_code),
        format_func=lambda x: _(f"language_name_full_{x.upper()}", x.upper()), # _ from app.py
        key=lang_selector_widget_key,
        on_change=update_language_state_callback
    )
    return st_session_state.selected_lang_code

def display_navigation(st_session_state: Any, _: Callable[[str, Optional[str]], str]) -> str:
    """Displays the main app navigation radio buttons."""
    st.sidebar.markdown("---")
    dashboard_nav_label_loc = _("dashboard_nav_label") # No default needed if keys are guaranteed
    glossary_nav_label_loc = _("glossary_nav_label")

    # Initialize navigation mode in session state if not present, default to dashboard
    if 'app_navigation_mode_radio' not in st_session_state: # Using the widget key for session state
        st_session_state.app_navigation_mode_radio = dashboard_nav_label_loc

    app_mode_selected = st.sidebar.radio(
        label=_("navigation_label"),
        options=[dashboard_nav_label_loc, glossary_nav_label_loc],
        key="app_navigation_mode_radio" # Let Streamlit manage the state of THIS widget with this key
    )
    st.sidebar.markdown("---")
    return app_mode_selected


def display_sidebar_filters(all_raw_dfs: List[pd.DataFrame], _: Callable[[str, Optional[str]], str]) -> Dict[str, List[str]]:
    """Displays all multiselect filters in the sidebar and returns selections."""
    from utils import get_unique_options_from_dfs_list # Avoid circular import if utils imports config

    st.sidebar.header(_("filters_header"))
    
    filter_keys_and_labels = { # conceptual_key: localization_text_key
        "site": "select_site",
        "region": "select_region",
        "department": "select_department",
        "fc": "select_fc", # Functional Category
        "shift": "select_shift",
    }
    default_filter_values = { # conceptual_key: default_value_from_config
        "site": config.DEFAULT_SITES,
        "region": config.DEFAULT_REGIONS,
        "department": config.DEFAULT_DEPARTMENTS,
        "fc": config.DEFAULT_FUNCTIONAL_CATEGORIES,
        "shift": config.DEFAULT_SHIFTS,
    }
    
    selections: Dict[str, List[str]] = {}
    for key, label_loc_key in filter_keys_and_labels.items():
        options = get_unique_options_from_dfs_list(all_raw_dfs, key)
        # Use unique keys for each multiselect widget
        selections[key] = st.sidebar.multiselect(
            _(label_loc_key), # Get localized label
            options=options,
            default=default_filter_values[key],
            key=f"sidebar_filter_multiselect_{key}" # Unique key for each filter
        )
    return selections

def display_optional_modules_toggle(_: Callable[[str, Optional[str]], str]):
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"## {_('optional_modules_header')}")
    show_optional = st.sidebar.checkbox(
        _('show_optional_modules'),
        key="sidebar_optional_modules_toggle_checkbox", # Ensure key is unique
        value=False # Default to collapsed/hidden
    )
    if show_optional:
        with st.sidebar.expander(_('optional_modules_title'), expanded=True):
            optional_list_content = _('optional_modules_list',
                                      default_text_override=config.TEXT_STRINGS[config.DEFAULT_LANG].get('optional_modules_list',"")) # Fallback
            st.markdown(optional_list_content, unsafe_allow_html=True)

def display_footer(_: Callable[[str, Optional[str]], str]):
    st.sidebar.markdown("---")
    st.sidebar.caption(f"{_(config.APP_TITLE_KEY)} {config.APP_VERSION}")
    st.sidebar.caption(_("Built with Streamlit, Plotly, and Pandas.")) # Removed bilingual hardcoding
    st.sidebar.caption(_("Data Last Updated: (N/A for sample data)"))