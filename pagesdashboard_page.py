# pages/dashboard_page.py
import streamlit as st
import pandas as pd
import config
from utils import load_data_main, apply_all_filters_to_df
from typing import Callable, Dict, List, Any
import logging

logger = logging.getLogger(__name__)

# Import panel rendering functions dynamically to avoid large import block if some are optional
# This is more robust if a panel file is missing or has import errors.
PANEL_MODULE_NAMES = [
    "stability_panel", "safety_panel", "engagement_panel", "stress_panel",
    "task_compliance_panel", "collaboration_panel", "wellbeing_panel",
    "downtime_panel", "oee_panel", "resilience_panel", "spatial_dynamics_panel"
]

# Dataframe mapping: panel_name -> list of conceptual dataframe keys it needs
PANEL_DATA_REQUIREMENTS = {
    "stability_panel": ["stability"],
    "safety_panel": ["safety"],
    "engagement_panel": ["engagement", "psych_safety"], # Example: engagement also uses psych_safety data
    "stress_panel": ["stress", "perceived_workload"],
    "task_compliance_panel": ["tasks"],
    "collaboration_panel": ["collaboration", "team_cohesion"],
    "wellbeing_panel": ["wellbeing", "psych_safety", "perceived_workload"], # Can also access engagement/stress if needed via all_dfs
    "downtime_panel": ["downtime"],
    "oee_panel": ["oee"],
    "resilience_panel": ["resilience"],
    "spatial_dynamics_panel": ["spatial"]
}

DATA_SOURCE_MAP = { # Conceptual key -> (FILE_CONSTANT_NAME_IN_CONFIG, date_col_conceptual_key_or_None)
    "stability": ("STABILITY_DATA_FILE", "date"),
    "safety": ("SAFETY_DATA_FILE", None), # Month is text
    "engagement": ("ENGAGEMENT_DATA_FILE", None),
    "stress": ("STRESS_DATA_FILE", "date"),
    "tasks": ("TASK_COMPLIANCE_DATA_FILE", "task_date"),
    "collaboration": ("COLLABORATION_DATA_FILE", "collaboration_date"),
    "wellbeing": ("WELLBEING_DATA_FILE", "wellbeing_date"),
    "downtime": ("DOWNTIME_DATA_FILE", "downtime_date"),
    "oee": ("OEE_DATA_FILE", "oee_date"),
    "resilience": ("RESILIENCE_DATA_FILE", "resilience_date"),
    "psych_safety": ("PSYCH_SAFETY_DATA_FILE", "psych_safety_date"), # Potentially overlaps with engagement
    "team_cohesion": ("TEAM_COHESION_DATA_FILE", "team_cohesion_date"), # Potentially overlaps with collab
    "perceived_workload": ("PERCEIVED_WORKLOAD_DATA_FILE", "workload_date"), # Potentially overlaps with stress
    "spatial": ("SPATIAL_DATA_FILE", "spatial_timestamp")
}


@st.cache_data # Cache the combined loading and filtering logic if filter_selections are hashable
def load_and_filter_data_for_dashboard(filter_selections_tuple: tuple) -> Dict[str, pd.DataFrame]:
    # Convert tuple back to dict for selections
    filter_selections = dict(filter_selections_tuple)
    loaded_dfs_raw: Dict[str, pd.DataFrame] = {}
    loaded_dfs_filtered: Dict[str, pd.DataFrame] = {}

    for key, (file_const_name, date_col_key) in DATA_SOURCE_MAP.items():
        file_path = getattr(config, file_const_name, None)
        if not file_path:
            logger.warning(f"File constant {file_const_name} not found in config. Skipping data source: {key}")
            loaded_dfs_raw[key] = pd.DataFrame()
            loaded_dfs_filtered[key] = pd.DataFrame()
            continue

        date_col_actual_name = config.COLUMN_MAP.get(date_col_key) if date_col_key else None
        df_raw = load_data_main(file_path, date_cols_actual_names=[date_col_actual_name] if date_col_actual_name else None)
        loaded_dfs_raw[key] = df_raw
        loaded_dfs_filtered[key] = apply_all_filters_to_df(df_raw, filter_selections)
    return loaded_dfs_filtered


def render(st_session_state: Any, _: Callable[[str, Optional[str]], str], filter_selections: Dict[str, List[str]]):
    """Renders the entire dashboard content."""
    # Make filter_selections hashable for caching
    # Convert lists to tuples within the dict values
    hashable_filter_selections = tuple(sorted((k, tuple(sorted(v))) for k, v in filter_selections.items()))
    all_filtered_dfs = load_and_filter_data_for_dashboard(hashable_filter_selections)

    # --- Main Dashboard Area ---
    st.title(_("dashboard_title"))
    st.markdown(_("dashboard_subtitle"))
    st.caption(_("alignment_note"))
    st.markdown("---")
    st.info(_("psych_safety_note"))
    st.markdown("---")

    # --- Dynamically Render Panels ---
    panel_render_order = [ # Define the order you want panels to appear
        "stability_panel", "safety_panel", "engagement_panel", "stress_panel",
        # "advanced_analytics_title_header", # Special key for header
        "task_compliance_panel", "collaboration_panel", "wellbeing_panel",
        "downtime_panel", "oee_panel", "resilience_panel", "spatial_dynamics_panel"
    ]

    advanced_header_rendered = False
    for panel_name_key in panel_render_order:
        # Check if it's time to render the "Advanced Analytics" header
        if panel_name_key == "task_compliance_panel" and not advanced_header_rendered:
            st.header(_("advanced_analytics_title"))
            st.markdown("---")
            advanced_header_rendered = True

        try:
            panel_module = __import__(f"panels.{panel_name_key}", fromlist=[panel_name_key])
            # Prepare specific arguments for the panel's render function
            # This needs to be flexible based on what each panel's render function expects
            render_args = [st, st_session_state.selected_lang_code, _] # Common args

            if panel_name_key == "stability_panel":
                render_args.insert(1, all_filtered_dfs.get("stability", pd.DataFrame()))
            elif panel_name_key == "safety_panel":
                render_args.insert(1, all_filtered_dfs.get("safety", pd.DataFrame()))
            elif panel_name_key == "engagement_panel":
                render_args.insert(1, all_filtered_dfs.get("engagement", pd.DataFrame()))
                render_args.insert(2, all_filtered_dfs.get("psych_safety", pd.DataFrame())) # Add psych_safety
            elif panel_name_key == "stress_panel":
                render_args.insert(1, all_filtered_dfs.get("stress", pd.DataFrame()))
                render_args.insert(2, all_filtered_dfs.get("perceived_workload", pd.DataFrame()))
            elif panel_name_key == "task_compliance_panel":
                 render_args.insert(1, all_filtered_dfs.get("tasks", pd.DataFrame()))
            elif panel_name_key == "collaboration_panel":
                render_args.insert(1, all_filtered_dfs.get("collaboration", pd.DataFrame()))
                render_args.insert(2, all_filtered_dfs.get("team_cohesion", pd.DataFrame()))
            elif panel_name_key == "wellbeing_panel":
                render_args.insert(1, all_filtered_dfs.get("wellbeing", pd.DataFrame()))
                render_args.insert(2, all_filtered_dfs.get("psych_safety", pd.DataFrame()))
                render_args.insert(3, all_filtered_dfs.get("perceived_workload", pd.DataFrame()))
            elif panel_name_key == "downtime_panel":
                render_args.insert(1, all_filtered_dfs.get("downtime", pd.DataFrame()))
                render_args.insert(2, filter_selections.get('shift', [])) # Pass selected shifts for context
            elif panel_name_key == "oee_panel":
                render_args.insert(1, all_filtered_dfs.get("oee", pd.DataFrame()))
            elif panel_name_key == "resilience_panel":
                render_args.insert(1, all_filtered_dfs.get("resilience", pd.DataFrame()))
            elif panel_name_key == "spatial_dynamics_panel":
                 render_args.insert(1, all_filtered_dfs.get("spatial", pd.DataFrame()))
            # Add more elif blocks here for other panels if they have unique arg needs

            panel_module.render(*render_args)

        except ImportError:
            logger.warning(f"Panel module 'panels.{panel_name_key}.py' not found or not implemented.")
            # Optionally, display a placeholder or skip
            # st.warning(_("panel_not_available", panel_name=_(f"{panel_name_key}_title", panel_name_key.replace("_"," ").title())))
        except Exception as e:
            panel_display_name = _(f"{panel_name_key}_title", panel_name_key.replace("_panel","").replace("_"," ").title())
            logger.error(f"Error rendering panel '{panel_name_key}': {e}", exc_info=True)
            st.error(_("error_rendering_panel", panel_name=panel_display_name, error_message=str(e)))
            st.markdown("---")


    # --- Placeholder Modules ---
    st.header(_("plant_map_title"))
    st.markdown(config.PLACEHOLDER_TEXT_PLANT_MAP, unsafe_allow_html=True)
    # st.warning(_("This module is a placeholder for future development.", "Module currently in development.")) # Redundant with placeholder text
    st.markdown("---")
    st.header(_("ai_insights_title"))
    st.markdown(config.PLACEHOLDER_TEXT_AI_INSIGHTS, unsafe_allow_html=True)
    # st.warning(_("This module is a placeholder for future development."))
    st.markdown("---")

def get_all_raw_dataframes_for_filters() -> List[pd.DataFrame]:
    """Loads all raw DFs defined in config.ALL_DATA_FILE_CONSTANTS for populating filter options. load_data_main is cached."""
    df_list = []
    for file_const_name in config.ALL_DATA_FILE_CONSTANTS:
        file_path = getattr(config, file_const_name, None)
        if file_path:
            # For filter population, we don't strictly need date parsing,
            # but load_data_main includes it if date_cols_actual_names is passed.
            # Here, we can omit it for faster loading if it's only for unique string options.
            # However, to keep it simple and consistent with dashboard loading if DATA_SOURCE_MAP uses it:
            # We find the conceptual key for the file_const_name to get its date_col_key
            date_col_key_for_file = None
            for _, (f_const, d_col_key) in DATA_SOURCE_MAP.items():
                if f_const == file_const_name:
                    date_col_key_for_file = d_col_key
                    break
            
            date_col_actual = config.COLUMN_MAP.get(date_col_key_for_file) if date_col_key_for_file else None
            df_list.append(load_data_main(file_path, date_cols_actual_names=[date_col_actual] if date_col_actual else None))
        else:
            logger.warning(f"File constant '{file_const_name}' not found in config during filter option loading.")
            
    return [df for df in df_list if not df.empty]