# utils.py
import pandas as pd
import streamlit as st
from typing import List, Dict, Optional, Union, Any
import numpy as np
import config # For COLUMN_MAP, TEXT_STRINGS (error messages), DEFAULT_LANG

@st.cache_data
def load_data_main(file_path_str: str, date_cols_actual_names: Optional[List[str]] = None) -> pd.DataFrame:
    """Loads and minimally cleans data from a CSV file."""
    try:
        df = pd.read_csv(file_path_str, parse_dates=date_cols_actual_names if date_cols_actual_names else False)
        for col in df.columns: # Iterate over actual columns in the loaded DataFrame
            if df[col].dtype == 'object' and df[col].notna().any(): # Check if column is of object type
                try: df[col] = df[col].astype(str).str.strip() # Ensure string conversion before strip
                except AttributeError: pass # Handles non-string objects if any slip through
        return df
    except FileNotFoundError:
        # Using direct lookup for error messages as _ might not be available here easily if config fails
        error_msg = "Error loading data from {0}. Please verify file path and presence."
        try:
            error_msg = config.TEXT_STRINGS[config.DEFAULT_LANG].get("error_loading_data_generic", error_msg).format(file_path_str) + \
                        f". " + config.TEXT_STRINGS[config.DEFAULT_LANG].get("check_file_path_instruction", "")
        except Exception: # Fallback if config/TEXT_STRINGS access fails
            pass
        st.error(error_msg)
        return pd.DataFrame()
    except Exception as e:
        error_msg_detail = "Error loading data from {0} - Exception: {1}"
        try:
            error_msg_detail = config.TEXT_STRINGS[config.DEFAULT_LANG].get("error_loading_data_generic", "Error loading {0}").format(file_path_str) + \
                               f" - {config.TEXT_STRINGS[config.DEFAULT_LANG].get('exception_detail_prefix','Exception')}: {e}"
        except Exception:
            pass
        st.error(error_msg_detail.format(file_path_str, e))
        return pd.DataFrame()

def get_unique_options_from_dfs_list(dfs_list_input: List[pd.DataFrame], column_conceptual_key: str) -> List[str]:
    """Gets unique sorted string options for a filter dropdown from multiple dataframes."""
    actual_col_name = config.COLUMN_MAP.get(column_conceptual_key)
    if not actual_col_name:
        st.warning(f"Filter column key '{column_conceptual_key}' not found in COLUMN_MAP.")
        return []
    all_options_set = set()
    for df_item in dfs_list_input:
        if not df_item.empty and actual_col_name in df_item.columns:
            # Ensure items are strings, handle NaN gracefully before adding to set
            options = df_item[actual_col_name].dropna().astype(str).unique()
            all_options_set.update(options)
    return sorted(list(all_options_set))

def apply_all_filters_to_df(df_to_filter: pd.DataFrame, selections: Dict[str, List[str]]) -> pd.DataFrame:
    """Applies selected filters to a DataFrame."""
    if df_to_filter.empty: return df_to_filter.copy()
    df_filtered = df_to_filter.copy() # Work on a copy
    for concept_key, selected_opts_list in selections.items():
        actual_col_in_df = config.COLUMN_MAP.get(concept_key)
        if actual_col_in_df and selected_opts_list and actual_col_in_df in df_filtered.columns:
            # Robust filtering: convert column to string for comparison with string selections
            try:
                # Ensure filter options are strings, as unique options are collected as strings
                string_selected_opts = [str(opt) for opt in selected_opts_list]
                df_filtered = df_filtered[df_filtered[actual_col_in_df].astype(str).isin(string_selected_opts)]
            except Exception as e:
                st.error(f"Error applying filter for '{concept_key}' on column '{actual_col_in_df}': {e}")
    return df_filtered

def get_dummy_prev_val(curr_val: Optional[Union[int, float, np.number]],
                       factor: float = 0.1, is_percent: bool = False,
                       variation_abs: Optional[Union[int, float]] = None) -> Optional[float]:
    """Generates a plausible dummy previous value for KPI cards."""
    if pd.isna(curr_val) or not isinstance(curr_val, (int,float,np.number)): return None # Also check for np.number
    current_float_val = float(curr_val)
    if variation_abs is not None or (abs(current_float_val) < 10 and not is_percent) :
         abs_var_val = variation_abs if variation_abs is not None else (1.0 if current_float_val >= 0 else -1.0)
         change_amount = abs_var_val * np.random.uniform(-1, 1)
    else: # Percentage based variation for larger numbers
        change_amount = current_float_val * factor * np.random.uniform(-0.7, 0.7) # More subtle % variation
    previous_val_calculated = current_float_val - change_amount
    if is_percent: return round(max(0.0, min(100.0, previous_val_calculated)),1) # Clamp percentages
    # For non-percentages, decide if rounding to int or float makes sense based on original value type or context
    return round(previous_val_calculated, 1 if isinstance(curr_val, float) else 0) if not pd.isna(previous_val_calculated) else None