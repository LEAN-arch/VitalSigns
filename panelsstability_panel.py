# panels/stability_panel.py
import streamlit as st
import pandas as pd
import config
import visualizations as viz # This refers to the comprehensive, themed visualizations.py
import insights
from utils import get_dummy_prev_val # If you still want dummy values for previous_value
from typing import Callable, Any

def render(st_container: Any, df_stability_filtered: pd.DataFrame, lang_code: str, _: Callable[[str, str], str]):
    st_container.header(_("stability_panel_title"))
    avg_rotation_current = float('nan')
    agg_trend_stability_for_insights = pd.DataFrame() # Initialize for insights

    if not df_stability_filtered.empty:
        cols_metrics_stab = st_container.columns(4) # Four columns for rotation + 3 retention metrics

        # --- Rotation Rate Metric & Gauge ---
        rot_rate_actual_col = config.COLUMN_MAP.get("rotation_rate")
        if rot_rate_actual_col and rot_rate_actual_col in df_stability_filtered.columns:
            avg_rotation_current = df_stability_filtered[rot_rate_actual_col].mean()
        else:
            logger.warning(f"Rotation rate column '{rot_rate_actual_col}' not found in stability data.")

        prev_avg_rotation_val = get_dummy_prev_val(avg_rotation_current, 0.05, True)

        with cols_metrics_stab[0]:
            viz.display_metric_card(
                cols_metrics_stab[0], # Pass the column container for this card
                label_key="rotation_rate_metric", # Key for the card's subheader title
                value=avg_rotation_current,
                lang_code=lang_code,
                unit="%",
                higher_is_better=False,
                target_value=config.STABILITY_ROTATION_RATE.get("target"),
                threshold_good=config.STABILITY_ROTATION_RATE.get("good"), # For Markdown coloring
                threshold_warning=config.STABILITY_ROTATION_RATE.get("warning"), # For Markdown coloring
                previous_value=prev_avg_rotation_val,
                help_text_key="rotation_rate_metric_help",
                value_format_str=".1f"
            )
            cols_metrics_stab[0].plotly_chart(viz.create_kpi_gauge(
                value=avg_rotation_current,
                title_key="rotation_rate_gauge", # Key for the gauge's internal title
                lang_code=lang_code,
                unit="%",
                higher_is_worse=True,
                threshold_good=config.STABILITY_ROTATION_RATE.get("good"),
                threshold_warning=config.STABILITY_ROTATION_RATE.get("warning"),
                target_line_value=config.STABILITY_ROTATION_RATE.get("target"),
                previous_value=prev_avg_rotation_val,
                max_value_override=config.STABILITY_ROTATION_RATE.get("max_display"), # From config
                value_format_str=".1f"
            ), use_container_width=True)

        # --- Retention Metrics ---
        retention_metrics_config = [
            ("retention_6m", "retention_6m_metric"),
            ("retention_12m", "retention_12m_metric"),
            ("retention_18m", "retention_18m_metric")
        ]
        for i, (col_conceptual_key, label_key_for_card) in enumerate(retention_metrics_config):
            actual_col_name = config.COLUMN_MAP.get(col_conceptual_key)
            value_retention = float('nan')
            if actual_col_name and actual_col_name in df_stability_filtered.columns:
                value_retention = df_stability_filtered[actual_col_name].mean()
            else:
                logger.warning(f"Retention column '{actual_col_name}' (for {col_conceptual_key}) not found.")

            prev_value_retention = get_dummy_prev_val(value_retention, 0.03, True)

            with cols_metrics_stab[i+1]: # Place in subsequent columns
                viz.display_metric_card(
                    cols_metrics_stab[i+1],
                    label_key=label_key_for_card,
                    value=value_retention,
                    lang_code=lang_code,
                    unit="%",
                    higher_is_better=True,
                    target_value=config.STABILITY_RETENTION.get("target"),
                    threshold_good=config.STABILITY_RETENTION.get("good"),
                    threshold_warning=config.STABILITY_RETENTION.get("warning"),
                    previous_value=prev_value_retention,
                    help_text_key="retention_metric_help",
                    value_format_str=".1f"
                )
                # Optionally, add small gauges for retention metrics if desired, similar to rotation
                # cols_metrics_stab[i+1].plotly_chart(viz.create_kpi_gauge(...), use_container_width=True)


        st_container.markdown("<br>", unsafe_allow_html=True) # Spacer before trend chart

        # --- Hires vs. Exits Trend Chart ---
        date_actual_col = config.COLUMN_MAP.get("date")
        hires_actual_col = config.COLUMN_MAP.get("hires")
        exits_actual_col = config.COLUMN_MAP.get("exits")

        if all(col and col in df_stability_filtered.columns for col in [date_actual_col, hires_actual_col, exits_actual_col]):
            trend_df_prep = df_stability_filtered[[date_actual_col, hires_actual_col, exits_actual_col]].copy()
            if not pd.api.types.is_datetime64_any_dtype(trend_df_prep[date_actual_col]):
                try:
                    trend_df_prep[date_actual_col] = pd.to_datetime(trend_df_prep[date_actual_col], errors='coerce')
                except Exception as e:
                    logger.error(f"Error converting date column for stability trend: {e}")
                    trend_df_prep[date_actual_col] = pd.NaT # Set to NaT if conversion fails
            
            trend_df_prep.dropna(subset=[date_actual_col], inplace=True) # Crucial after potential coerce
            trend_df_prep.sort_values(by=date_actual_col, inplace=True)
            
            if not trend_df_prep.empty:
                try:
                    agg_trend_stability_for_insights = trend_df_prep.groupby(pd.Grouper(key=date_actual_col, freq='M')).agg(
                        Hires_Total_Agg=(hires_actual_col, 'sum'),
                        Exits_Total_Agg=(exits_actual_col, 'sum')
                    ).reset_index()
                except Exception as e:
                    logger.error(f"Error grouping stability trend data: {e}")
                    agg_trend_stability_for_insights = pd.DataFrame() # Ensure it's an empty DF on error

                if not agg_trend_stability_for_insights.empty:
                    map_for_trend = { # localization_key : new_aggregated_column_name
                        "hires_label": "Hires_Total_Agg",
                        "exits_label": "Exits_Total_Agg"
                    }
                    units_for_trend = {"Hires_Total_Agg": "", "Exits_Total_Agg": ""} # Unit defined by Y-axis title
                    
                    st_container.plotly_chart(viz.create_trend_chart(
                        df=agg_trend_stability_for_insights,
                        date_col=date_actual_col,
                        value_cols_map=map_for_trend,
                        title_key="hires_vs_exits_chart_title",
                        lang_code=lang_code,
                        y_axis_title_key="people_count_label",
                        x_axis_title_key="month_axis_label",
                        show_average_line=True, # Example: Show average lines
                        rolling_avg_window=3,    # Example: Show 3-month rolling average
                        value_col_units_map=units_for_trend
                    ), use_container_width=True)
                else:
                     st_container.info(_("no_data_for_trend") + f" ({_('no_data_hires_exits')})") # More specific
            else:
                st_container.info(_("no_data_for_trend") + f" ({_('no_data_hires_exits')})")
        else:
            missing_cols = [col_key for col_key, actual_col in [("date",date_actual_col), ("hires",hires_actual_col), ("exits",exits_actual_col)] if not (actual_col and actual_col in df_stability_filtered.columns)]
            st_container.warning(_("no_data_hires_exits") + f" Missing: {', '.join(missing_cols) or 'Unknown'}.")
        
        # --- Actionable Insights ---
        try:
            action_insights = insights.generate_stability_insights(
                df_stability_filtered,
                avg_rotation_current,
                agg_trend_stability_for_insights, # Pass the aggregated DataFrame
                lang_code
            )
            if action_insights:
                st_container.markdown("---")
                st_container.subheader(_("actionable_insights_title"))
                for insight_item in action_insights:
                    st_container.markdown(f"💡 {insight_item}")
        except Exception as e:
            logger.error(f"Error generating stability insights: {e}")
            st_container.warning(_("error_generating_insights", error_message=str(e)))

    else:
        st_container.info(_("no_data_available"))
    st_container.markdown("---") # Separator for the next panel