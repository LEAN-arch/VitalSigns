# panels/task_compliance_panel.py
import streamlit as st
import pandas as pd
import config
import visualizations as viz
import insights
from utils import get_dummy_prev_val
from typing import Callable, Any, Optional
import logging

logger = logging.getLogger(__name__)

def render(st_container: Any, df_tasks_filtered: pd.DataFrame, lang_code: str, _: Callable[[str, Optional[str]], str]):
    st_container.header(_("task_compliance_title"))

    avg_compliance: Optional[float] = None # Initialize for broader scope
    trend_data_for_insights: Optional[pd.Series] = None # Initialize

    if not df_tasks_filtered.empty:
        col1, col2 = st_container.columns([1, 2]) # Layout: 1/3 for gauge, 2/3 for trend

        # --- Metric Card & Gauge ---
        task_compliance_col_actual = config.COLUMN_MAP.get("task_compliance_rate")
        
        if task_compliance_col_actual and task_compliance_col_actual in df_tasks_filtered.columns:
            avg_compliance = df_tasks_filtered[task_compliance_col_actual].mean()
        else:
            logger.warning(f"Task compliance column '{task_compliance_col_actual}' not found.")
            avg_compliance = None # Explicitly None if col missing

        prev_compliance = get_dummy_prev_val(avg_compliance, 0.05, True) if avg_compliance is not None else None

        with col1:
            viz.display_metric_card(
                col1, # Pass the specific column container
                label_key="task_compliance_rate_metric_card",
                value=avg_compliance,
                lang_code=lang_code,
                unit="%",
                higher_is_better=True,
                target_value=config.TASK_COMPLIANCE.get("target"),
                threshold_good=config.TASK_COMPLIANCE.get("good"),
                threshold_warning=config.TASK_COMPLIANCE.get("warning"),
                previous_value=prev_compliance,
                help_text_key="task_compliance_help",
                value_format_str=".1f"
            )
            col1.plotly_chart(viz.create_kpi_gauge(
                value=avg_compliance,
                title_key="task_compliance_rate_gauge",
                lang_code=lang_code,
                unit="%",
                higher_is_worse=False,
                threshold_good=config.TASK_COMPLIANCE.get("good"),
                threshold_warning=config.TASK_COMPLIANCE.get("warning"),
                target_line_value=config.TASK_COMPLIANCE.get("target"),
                previous_value=prev_compliance,
                max_value_override=100.0, # Compliance is typically 0-100%
                value_format_str=".1f"
            ), use_container_width=True)

        # --- Trend Chart ---
        with col2:
            task_date_col_actual = config.COLUMN_MAP.get("task_date")
            if task_date_col_actual and task_compliance_col_actual and \
               all(c in df_tasks_filtered.columns for c in [task_date_col_actual, task_compliance_col_actual]) and \
               df_tasks_filtered[task_compliance_col_actual].notna().any():
                
                tasks_trend_df_prep = df_tasks_filtered[[task_date_col_actual, task_compliance_col_actual]].copy()
                if not pd.api.types.is_datetime64_any_dtype(tasks_trend_df_prep[task_date_col_actual]):
                    try:
                        tasks_trend_df_prep[task_date_col_actual] = pd.to_datetime(tasks_trend_df_prep[task_date_col_actual], errors='coerce')
                    except Exception as e:
                        logger.error(f"Error converting date column for task compliance trend: {e}")
                        tasks_trend_df_prep[task_date_col_actual] = pd.NaT
                
                tasks_trend_df_prep.dropna(subset=[task_date_col_actual, task_compliance_col_actual], inplace=True)
                tasks_trend_df_prep.sort_values(by=task_date_col_actual, inplace=True)

                if not tasks_trend_df_prep.empty:
                    # Resample to monthly average for a cleaner trend for create_task_compliance_trend_themed
                    # This assumes create_task_compliance_trend_themed is adapted from your plot_task_compliance_score
                    try:
                        monthly_compliance_series = tasks_trend_df_prep.set_index(task_date_col_actual)[task_compliance_col_actual].resample('M').mean()
                        trend_data_for_insights = monthly_compliance_series # For insights

                        if not monthly_compliance_series.empty:
                             # Ensure you have `create_task_compliance_trend_themed` in `visualizations.py`
                            fig_trend = viz.create_task_compliance_trend_themed(
                                data_series=monthly_compliance_series,
                                date_index=monthly_compliance_series.index,
                                lang_code=lang_code
                                # Optional: forecast_series, disruption_points_dates can be passed if available
                            )
                            col2.plotly_chart(fig_trend, use_container_width=True)
                        else:
                            col2.info(_("no_data_for_trend") + f" (Post-resampling).")
                    except Exception as e:
                        logger.error(f"Error preparing or plotting task compliance trend: {e}")
                        col2.warning(_("error_processing_trend_data", error_message=str(e))) # Add this key to TEXT_STRINGS
                else:
                    col2.info(_("no_data_for_trend") + f" (After NA drop).")
            else:
                missing_cols = [col_key for col_key, actual_col in [("task_date",task_date_col_actual), ("task_compliance_rate",task_compliance_col_actual)] if not (actual_col and actual_col in df_tasks_filtered.columns)]
                col2.warning(_("no_data_task_compliance") + (f" Missing: {', '.join(missing_cols)}" if missing_cols else ""))
        
        # --- Actionable Insights ---
        try:
            action_insights = insights.generate_task_compliance_insights(
                df_tasks_filtered,
                avg_compliance,
                trend_data_for_insights, # Pass the resampled Series
                lang_code
            )
            if action_insights:
                st_container.markdown("---") # Use st_container for insights section
                st_container.subheader(_("actionable_insights_title"))
                for insight_item in action_insights:
                    st_container.markdown(f"💡 {insight_item}")
        except Exception as e:
            logger.error(f"Error generating task compliance insights: {e}")
            st_container.warning(_("error_generating_insights", error_message=str(e))) # Add this key

    else:
        st_container.info(_("no_data_available"))
    st_container.markdown("---")