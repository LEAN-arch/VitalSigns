# pages/glossary_page.py
import streamlit as st
import config
from glossary_data import GLOSSARY_TERMS
from typing import Callable

def render(st_session_state, _):
    """Renders the glossary page."""
    st.title(_("glossary_page_title"))
    st.markdown(_("glossary_intro"))
    st.markdown("---")

    search_term = st.text_input(_("search_term_label"), key="glossary_search_text_field")
    
    sorted_terms = dict(sorted(GLOSSARY_TERMS.items()))
    displayed_count = 0

    if sorted_terms:
        for term_key, definitions in sorted_terms.items():
            display_term = True
            if search_term:
                search_lower = search_term.lower()
                match_key = search_lower in term_key.lower()
                match_en = search_lower in definitions.get("EN", "").lower()
                match_es = search_lower in definitions.get("ES", "").lower()
                if not (match_key or match_en or match_es):
                    display_term = False
            
            if display_term:
                displayed_count += 1
                with st.expander(term_key, expanded=(search_term != "")):
                    primary_lang = st_session_state.selected_lang_code.upper()
                    secondary_lang = "ES" if primary_lang == "EN" else "EN"

                    if primary_lang in definitions and definitions[primary_lang]:
                        st.markdown(f"**{_('definition_label')}:**")
                        st.markdown(definitions[primary_lang])
                    
                    if secondary_lang in definitions and definitions[secondary_lang]:
                        if primary_lang in definitions and definitions[primary_lang]:
                            st.markdown("---")
                        sec_lang_full = _(f"language_name_full_{secondary_lang}", secondary_lang)
                        st.caption(f"*{sec_lang_full}:* {definitions[secondary_lang]}")
                    elif "EN" in definitions and definitions["EN"] and primary_lang != "EN": # Fallback to EN
                        st.markdown(f"**{config.TEXT_STRINGS['EN'].get('definition_label', 'Definition')}:**")
                        st.markdown(definitions["EN"])

        if search_term and displayed_count == 0:
            st.info(_("no_term_found"))
    elif not GLOSSARY_TERMS:
        st.warning(_("glossary_empty_message"))