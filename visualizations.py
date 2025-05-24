import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Optional, Any, Union

import config  # For TEXT_STRINGS, thresholds, FACILITY_CONFIG etc.

logger = logging.getLogger(__name__)

# --- Dark Theme Color Definitions ---
COLOR_PAGE_BACKGROUND_DARK = "#2C3E50"
COLOR_PAPER_BG_DARK = COLOR_PAGE_BACKGROUND_DARK
COLOR_PLOT_BG_DARK = "#34495E"
COLOR_PRIMARY_TEXT_LIGHT = "#ECF0F1"
COLOR_SECONDARY_TEXT_LIGHT = "#BDC3C7"
COLOR_GRID_DARK_THEME = "#4A6572"
COLOR_AXIS_LINE_DARK_THEME = "#566573"
COLOR_CRITICAL_RED_DARK_THEME = "#E74C3C"
COLOR_WARNING_AMBER_DARK_THEME = "#F39C12"
COLOR_POSITIVE_GREEN_DARK_THEME = "#2ECC71"
COLOR_INFO_BLUE_DARK_THEME = "#3498DB"
COLOR_NEUTRAL_GRAY_DARK_THEME = "#7F8C8D"
ACCESSIBLE_CATEGORICAL_PALETTE_DARK_BG = ['#3498DB', '#2ECC71', '#F39C12', '#E74C3C', '#9B59B6', '#1ABC9C', '#E67E22'] # Common palette

PLOTLY_TEMPLATE_DARK = "plotly_dark" # Base template
EPSILON = 1e-9 # For float comparisons

# --- Localization Helper ---
def _viz_loc(text_key: str, lang_code: str, default_text_override: Optional[str] = None, **kwargs) -> str:
    lang_dict = config.TEXT_STRINGS.get(lang_code, config.TEXT_STRINGS.get(config.DEFAULT_LANG, {}))
    base_string = lang_dict.get(text_key, default_text_override if default_text_override is not None else lang_dict.get("translation_missing", "TR_VIZ: {key}").format(key=text_key)) # Clearer fallback
    if kwargs:
        try:
            return base_string.format(**kwargs)
        except (KeyError, ValueError) as e: # Catch more formatting errors
            logger.warning(f"Error formatting viz loc key '{text_key}' for lang '{lang_code}'. String: '{base_string}', Args: {kwargs}. Error: {e}")
            return base_string # Return unformatted string
    return base_string

# --- Common Layout ---
def _apply_common_layout_settings(fig: go.Figure, title_text_localized: str,
                                 yaxis_title_localized: Optional[str] = None,
                                 xaxis_title_localized: Optional[str] = None,
                                 yaxis_range: Optional[list] = None,
                                 show_legend: bool = True,
                                 legend_title_key: Optional[str] = None,
                                 lang_code: Optional[str] = None):
    font_main_color = COLOR_PRIMARY_TEXT_LIGHT
    grid_c = COLOR_GRID_DARK_THEME
    axis_line_c = COLOR_AXIS_LINE_DARK_THEME
    legend_bg = "rgba(44, 62, 80, 0.85)" # Dark, slightly transparent legend bg
    legend_border_c = COLOR_NEUTRAL_GRAY_DARK_THEME
    legend_config = None

    if show_legend:
        legend_title_text = _viz_loc(legend_title_key, lang_code, "") if legend_title_key and lang_code else ""
        legend_config = dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            bgcolor=legend_bg, bordercolor=legend_border_c, borderwidth=1,
            font_size=10, traceorder="normal", font=dict(color=font_main_color),
            title_text=legend_title_text if legend_title_text else None
        )

    fig.update_layout(
        template=PLOTLY_TEMPLATE_DARK, # Base dark theme
        title=dict(text=title_text_localized, x=0.5, font=dict(size=16, color=font_main_color)), # Slightly smaller default title
        paper_bgcolor=COLOR_PAPER_BG_DARK,
        plot_bgcolor=COLOR_PLOT_BG_DARK,
        font=dict(color=font_main_color, size=11),
        legend=legend_config,
        margin=dict(l=60, r=30, t=60, b=50), # Consistent margins
        xaxis=dict(
            title_text=xaxis_title_localized, gridcolor=grid_c,
            zerolinecolor=grid_c, zerolinewidth=1, showline=True,
            linewidth=1.5, linecolor=axis_line_c,
            titlefont=dict(size=12, color=font_main_color),
            tickfont=dict(size=10, color=font_main_color),
            rangemode='tozero' if xaxis_title_localized and any(kw.lower() in xaxis_title_localized.lower() for kw in ["time", "step", "month", "date"]) else 'normal'
        ),
        yaxis=dict(
            title_text=yaxis_title_localized, gridcolor=grid_c,
            zerolinecolor=grid_c, zerolinewidth=1, showline=True,
            linewidth=1.5, linecolor=axis_line_c, range=yaxis_range,
            titlefont=dict(size=12, color=font_main_color),
            tickfont=dict(size=10, color=font_main_color)
        ),
        hovermode="x unified", # Good default for time series
        dragmode='pan' # Enable panning by default
    )
    fig.update_traces(
        hoverlabel=dict(
            bgcolor="rgba(52, 73, 94, 0.95)", # Darker hover
            font_size=11, # Slightly smaller hover font
            font_color=COLOR_PRIMARY_TEXT_LIGHT,
            bordercolor=COLOR_NEUTRAL_GRAY_DARK_THEME
        )
    )

# --- No Data Figures ---
def _get_no_data_figure(title_text_localized: str, lang_code: Optional[str] = None) -> go.Figure:
    fig = go.Figure()
    _apply_common_layout_settings(fig, title_text_localized, show_legend=False, xaxis_title_localized="", yaxis_title_localized="")
    fig.update_xaxes(showticklabels=False, zeroline=False, showgrid=False, showline=False)
    fig.update_yaxes(showticklabels=False, zeroline=False, showgrid=False, showline=False)
    no_data_text = _viz_loc("no_data_for_visualization_default", lang_code or config.DEFAULT_LANG)
    fig.add_annotation(text=no_data_text, showarrow=False, font=dict(size=14, color=COLOR_PRIMARY_TEXT_LIGHT))
    return fig

def _get_no_data_pie_figure(title_text_localized: str, lang_code: Optional[str] = None) -> go.Figure:
    fig = go.Figure()
    _apply_common_layout_settings(fig, title_text_localized, show_legend=False, xaxis_title_localized="", yaxis_title_localized="")
    fig.update_xaxes(visible=False); fig.update_yaxes(visible=False) # Hide axes completely for pie no-data
    no_data_text = _viz_loc("no_data_for_visualization_default", lang_code or config.DEFAULT_LANG)
    fig.add_annotation(text=no_data_text, showarrow=False, xref="paper", yref="paper", x=0.5, y=0.5, font=dict(size=14, color=COLOR_PRIMARY_TEXT_LIGHT))
    return fig

# --- Metric Card ---
def display_metric_card(st_container, label_key: str, value: Optional[Union[int, float]], lang_code: str,
                        unit: str = "", higher_is_better: bool = True, target_value: Optional[float] = None,
                        threshold_good: Optional[float] = None, threshold_warning: Optional[float] = None, # These are for Markdown coloring
                        previous_value: Optional[float] = None, help_text_key: Optional[str] = None,
                        value_format_str: str = ".1f"): # Default to one decimal place for the value part
    localized_label = _viz_loc(label_key, lang_code, label_key.replace("_", " ").title())
    st_container.subheader(localized_label)

    if pd.isna(value):
        st_container.metric(label=_viz_loc("current_value_label", lang_code, "Current"), value="N/A") # Localized "Current" label
        # Simplified help display for N/A
        if help_text_key: st_container.caption(_viz_loc(help_text_key, lang_code, help_text_key))
        return

    val_fmt_actual = value_format_str if isinstance(value, float) and value % 1 != 0 else ".0f"
    display_value_full = f"{value:{val_fmt_actual}}{unit}"
    delta_text = None; delta_color_style = "off"

    if previous_value is not None and pd.notna(previous_value) and pd.notna(value):
        diff = float(value) - float(previous_value)
        delta_val_fmt_actual = value_format_str if isinstance(diff, float) and diff % 1 != 0 else ".0f"
        delta_text = f"{diff:{delta_val_fmt_actual}}{unit}"
        if abs(diff) > EPSILON:
            if higher_is_better: delta_color_style = "normal" if diff > 0 else "inverse"
            else: delta_color_style = "normal" if diff < 0 else "inverse"

    # Apply custom color using Markdown if thresholds are met
    main_value_html = f"<h3>{display_value_full}</h3>" # Default HTML
    if threshold_good is not None and threshold_warning is not None and pd.notna(value):
        val_float = float(value)
        color_to_use = ""
        if higher_is_better:
            if val_float >= threshold_good: color_to_use = COLOR_POSITIVE_GREEN_DARK_THEME
            elif val_float >= threshold_warning: color_to_use = COLOR_WARNING_AMBER_DARK_THEME
            else: color_to_use = COLOR_CRITICAL_RED_DARK_THEME
        else:
            if val_float <= threshold_good: color_to_use = COLOR_POSITIVE_GREEN_DARK_THEME
            elif val_float <= threshold_warning: color_to_use = COLOR_WARNING_AMBER_DARK_THEME
            else: color_to_use = COLOR_CRITICAL_RED_DARK_THEME
        if color_to_use:
            main_value_html = f"<h3 style='color: {color_to_use}; margin-bottom: 0.2rem;'>{display_value_full}</h3>" # Reduced margin

    st_container.markdown(main_value_html, unsafe_allow_html=True)
    if delta_text: # Display delta separately if we used markdown for main value
        delta_html_color = "inherit" # Default text color
        if delta_color_style == "normal": delta_html_color = COLOR_POSITIVE_GREEN_DARK_THEME
        elif delta_color_style == "inverse": delta_html_color = COLOR_CRITICAL_RED_DARK_THEME
        st_container.markdown(f"<p style='font-size:small; color:{delta_html_color}; margin-top: -0.3rem;'>{delta_text} vs Prev.</p>", unsafe_allow_html=True)

    final_help_text = ""
    if help_text_key:
        raw_help = _viz_loc(help_text_key, lang_code, help_text_key if "{target}" not in help_text_key else "Target: {target}")
        if "{target}" in raw_help and target_value is not None:
            target_fmt_str = ".0f" if isinstance(target_value, float) and target_value % 1 == 0 else value_format_str
            final_help_text = raw_help.format(target=f"{target_value:{target_fmt_str}}")
        else: final_help_text = raw_help
    if final_help_text: st_container.caption(final_help_text)

# --- Gauge ---
def create_kpi_gauge(value: Optional[float], title_key: str, lang_code: str, unit: str = "%",
                     threshold_good: Optional[float] = None, threshold_warning: Optional[float] = None,
                     target_line_value: Optional[float] = None, higher_is_worse: bool = False,
                     max_value_override: Optional[float] = None, previous_value: Optional[float] = None,
                     value_format_str: str = ".1f"): # Number format for the gauge value
    localized_title = _viz_loc(title_key, lang_code, title_key.replace("_metric", "").replace("_gauge","").replace("_", " ").title())
    if pd.isna(value): return _get_no_data_figure(localized_title, lang_code=lang_code)

    current_value_float = float(value)
    fig = go.Figure()
    # Determine bar color based on performance against thresholds
    bar_color_main = COLOR_NEUTRAL_GRAY_DARK_THEME # Default bar color
    if threshold_good is not None and threshold_warning is not None:
        if higher_is_worse:
            if current_value_float <= threshold_good: bar_color_main = COLOR_POSITIVE_GREEN_DARK_THEME
            elif current_value_float <= threshold_warning: bar_color_main = COLOR_WARNING_AMBER_DARK_THEME
            else: bar_color_main = COLOR_CRITICAL_RED_DARK_THEME
        else:
            if current_value_float >= threshold_good: bar_color_main = COLOR_POSITIVE_GREEN_DARK_THEME
            elif current_value_float >= threshold_warning: bar_color_main = COLOR_WARNING_AMBER_DARK_THEME
            else: bar_color_main = COLOR_CRITICAL_RED_DARK_THEME

    # Determine effective maximum value for the gauge axis
    max_val_eff = max_value_override if max_value_override is not None else (100.0 if unit == "%" else (current_value_float * 1.5 if abs(current_value_float) > EPSILON else 10.0))
    if current_value_float > max_val_eff : max_val_eff = current_value_float * 1.2
    if target_line_value is not None and pd.notna(target_line_value) and target_line_value > max_val_eff: max_val_eff = target_line_value * 1.2
    if abs(max_val_eff) < EPSILON: max_val_eff = max(1.0, current_value_float * 2 if abs(current_value_float) > EPSILON else 1.0)

    # Define steps for gauge background coloring
    steps_list = []
    if threshold_good is not None and threshold_warning is not None:
        s_g, s_w = float(threshold_good), float(threshold_warning)
        # Ensure order for higher_is_worse logic (good values are lower)
        if higher_is_worse: low_ok, mid_warn, high_crit = s_g, s_w, max_val_eff
        else: low_crit, mid_warn, high_ok = s_w, s_g, max_val_eff

        if higher_is_worse:
            steps_list = [{'range': [0, low_ok], 'color': COLOR_POSITIVE_GREEN_DARK_THEME},
                          {'range': [low_ok, mid_warn], 'color': COLOR_WARNING_AMBER_DARK_THEME},
                          {'range': [mid_warn, high_crit], 'color': COLOR_CRITICAL_RED_DARK_THEME}]
        else:
            steps_list = [{'range': [0, low_crit], 'color': COLOR_CRITICAL_RED_DARK_THEME},
                          {'range': [low_crit, mid_warn], 'color': COLOR_WARNING_AMBER_DARK_THEME},
                          {'range': [mid_warn, high_ok], 'color': COLOR_POSITIVE_GREEN_DARK_THEME}]
        # Clean up steps to be sequential and within [0, max_val_eff]
        valid_steps = []
        current_step_start = 0.0
        for step in sorted(steps_list, key=lambda x: x['range'][0]): # Ensure sorted by start of range
            start_range = max(current_step_start, min(step['range'][0], max_val_eff))
            end_range = max(start_range, min(step['range'][1], max_val_eff))
            if end_range > start_range + EPSILON:
                valid_steps.append({'range': [start_range, end_range], 'color': step['color']})
                current_step_start = end_range
        if current_step_start < max_val_eff - EPSILON and valid_steps: # Fill gap if any
             valid_steps.append({'range': [current_step_start, max_val_eff], 'color': valid_steps[-1]['color']}) # Use last color to fill
        elif not valid_steps : # Fallback if no valid steps generated
            valid_steps.append({'range': [0, max_val_eff], 'color': COLOR_NEUTRAL_GRAY_DARK_THEME})
        steps_list = valid_steps

    else: # Default if no thresholds
        steps_list.append({'range': [0, max_val_eff], 'color': COLOR_NEUTRAL_GRAY_DARK_THEME})

    fig.add_trace(go.Indicator(
        mode="gauge+number" + ("+delta" if previous_value is not None and pd.notna(previous_value) else ""),
        value=current_value_float,
        delta={'reference': float(previous_value) if pd.notna(previous_value) else None,
               'increasing': {'color': COLOR_POSITIVE_GREEN_DARK_THEME if not higher_is_worse else COLOR_CRITICAL_RED_DARK_THEME},
               'decreasing': {'color': COLOR_CRITICAL_RED_DARK_THEME if not higher_is_worse else COLOR_POSITIVE_GREEN_DARK_THEME},
               'font': {'size': 11, 'color': COLOR_PRIMARY_TEXT_LIGHT}},
        title={'text': localized_title, 'font': {'size': 13, 'color': COLOR_PRIMARY_TEXT_LIGHT}},
        number={'suffix': unit, 'font': {'size': 18, 'color': COLOR_PRIMARY_TEXT_LIGHT}, 'valueformat': value_format_str},
        gauge={'axis': {'range': [0, max_val_eff], 'tickwidth': 1, 'tickcolor': COLOR_AXIS_LINE_DARK_THEME, 'tickfont': {'size': 9, 'color': COLOR_SECONDARY_TEXT_LIGHT}},
               'bar': {'color': bar_color_main, 'thickness': 0.7}, # Main value bar color
               'bgcolor': "rgba(0,0,0,0)", # Transparent gauge area
               'borderwidth': 1, 'bordercolor': COLOR_NEUTRAL_GRAY_DARK_THEME, 'steps': steps_list,
               'threshold': {'line': {'color': COLOR_PRIMARY_TEXT_LIGHT, 'width': 2}, 'thickness': 0.8,
                             'value': target_line_value} if target_line_value is not None else None}))
    fig.update_layout(height=180, margin=dict(l=15, r=15, t=45, b=10),
                      paper_bgcolor=COLOR_PAPER_BG_DARK, plot_bgcolor="rgba(0,0,0,0)") # Plot area transparent
    return fig

# --- Trend Chart ---
def create_trend_chart(df: pd.DataFrame, date_col: str, value_cols_map: Dict[str, str], title_key: str, lang_code: str,
                       y_axis_title_key: str, x_axis_title_key: str, show_average_line: bool = False,
                       rolling_avg_window: Optional[int] = None, value_col_units_map: Optional[Dict[str,str]] = None):
    localized_title = _viz_loc(title_key, lang_code); default_x_title = _viz_loc("date_label", lang_code)
    if df.empty or date_col not in df.columns: return _get_no_data_figure(localized_title, lang_code=lang_code)
    localized_y_title = _viz_loc(y_axis_title_key, lang_code); localized_x_title = _viz_loc(x_axis_title_key, lang_code, default_x_title)
    fig = go.Figure(); palette = ACCESSIBLE_CATEGORICAL_PALETTE_DARK_BG
    for i, (disp_key, actual_col) in enumerate(value_cols_map.items()):
        if actual_col in df.columns and df[actual_col].notna().any():
            unit = value_col_units_map.get(actual_col, "") if value_col_units_map else ""
            trace_name = _viz_loc(disp_key, lang_code)
            fig.add_trace(go.Scatter(x=df[date_col], y=df[actual_col], mode='lines+markers', name=trace_name,
                                     line=dict(color=palette[i % len(palette)], width=2.2), marker=dict(size=5),
                                     hovertemplate=f'<b>{trace_name}</b><br>{localized_x_title}: %{{x|%Y-%m-%d}}<br>{localized_y_title}: %{{y:.2f}}{unit}<extra></extra>'))
            if show_average_line and pd.notna(df[actual_col].mean()):
                avg_val = df[actual_col].mean(); avg_lbl = _viz_loc("average_label", lang_code)
                fig.add_hline(y=avg_val, line_dash="dot", line_color=COLOR_NEUTRAL_GRAY_DARK_THEME, width=1.5,
                              annotation_text=f"{avg_lbl} ({trace_name}): {avg_val:.2f}{unit}", annotation_position="bottom right",
                              annotation_font=dict(size=9, color=COLOR_SECONDARY_TEXT_LIGHT))
            if rolling_avg_window and df[actual_col].notna().sum() >= rolling_avg_window:
                roll_mean = df[actual_col].rolling(window=rolling_avg_window, min_periods=1).mean(); roll_lbl = _viz_loc("period_rolling_avg_label", lang_code)
                fig.add_trace(go.Scatter(x=df[date_col], y=roll_mean, mode='lines', name=f"{trace_name} ({rolling_avg_window}-{roll_lbl})",
                                         line=dict(dash='longdashdot', color=palette[i % len(palette)], width=1.5), opacity=0.7))
    _apply_common_layout_settings(fig, localized_title, yaxis_title_localized=localized_y_title,
                                 xaxis_title_localized=localized_x_title, legend_title_key="legend_metrics_title", lang_code=lang_code)
    return fig

# --- Bar Chart ---
def create_comparison_bar_chart(df: pd.DataFrame, category_col: str, value_cols_map: Dict[str, str], title_key: str, lang_code: str,
                                x_axis_title_key: str, y_axis_title_key: str, barmode: str = 'group',
                                show_total_for_stacked: bool = False, data_label_format_str: str = ".1f"):
    localized_title = _viz_loc(title_key, lang_code); default_x_title = _viz_loc("category_label", lang_code, "Category")
    if df.empty or category_col not in df.columns: return _get_no_data_figure(localized_title, lang_code=lang_code)
    localized_x_title = _viz_loc(x_axis_title_key, lang_code, default_x_title); localized_y_title = _viz_loc(y_axis_title_key, lang_code)
    fig = go.Figure(); palette = ACCESSIBLE_CATEGORICAL_PALETTE_DARK_BG
    actual_fmt = data_label_format_str[data_label_format_str.find(":")+1:data_label_format_str.find("}")] if data_label_format_str.startswith("{") else data_label_format_str
    for i, (disp_key, actual_col) in enumerate(value_cols_map.items()):
        if actual_col in df.columns and df[actual_col].notna().any():
            trace_name = _viz_loc(disp_key, lang_code)
            fig.add_trace(go.Bar(name=trace_name, x=df[category_col], y=df[actual_col],
                                 text=[f"{val:{actual_fmt}}" if pd.notna(val) else "" for val in df[actual_col]],
                                 textposition='auto', marker_color=palette[i % len(palette)],
                                 hovertemplate=f'<b>{trace_name}</b><br>{df[category_col].name}: %{{x}}<br>{localized_y_title}: %{{y:{actual_fmt}}}<extra></extra>'))
    if barmode == 'stack' and show_total_for_stacked and len(value_cols_map) > 1:
        df['_Total_Stacked'] = df[[col for col in value_cols_map.values() if col in df.columns]].sum(axis=1, skipna=True)
        fig.add_trace(go.Scatter(x=df[category_col], y=df['_Total_Stacked'], text=[f"{total:{actual_fmt}}" if pd.notna(total) else "" for total in df['_Total_Stacked']],
                                 mode='text', textposition='top center', textfont=dict(color=COLOR_PRIMARY_TEXT_LIGHT, size=10), showlegend=False, hoverinfo='skip'))
    _apply_common_layout_settings(fig, localized_title, yaxis_title_localized=localized_y_title,
                                 xaxis_title_localized=localized_x_title, legend_title_key="legend_categories_title", lang_code=lang_code)
    fig.update_layout(barmode=barmode);
    if barmode == 'stack': fig.update_traces(textfont=dict(color=COLOR_PRIMARY_TEXT_LIGHT), textangle=0, textposition='inside', insidetextanchor='middle')
    else: fig.update_traces(textfont=dict(color=COLOR_PRIMARY_TEXT_LIGHT))
    return fig

# --- Radar Chart ---
def create_enhanced_radar_chart(df_radar: pd.DataFrame, category_col: str, value_col: str, title_key: str, lang_code: str,
                               range_max_override: Optional[float] = None, target_values_map: Optional[Dict[str, float]] = None,
                               fill_opacity: float = 0.35):
    localized_title = _viz_loc(title_key, lang_code)
    if df_radar.empty or category_col not in df_radar.columns or value_col not in df_radar.columns:
        return _get_no_data_figure(localized_title, lang_code=lang_code)
    fig = go.Figure(); categories = df_radar[category_col].tolist(); values = df_radar[value_col].tolist()
    current_scores_label = _viz_loc("current_scores_label", lang_code)
    fig.add_trace(go.Scatterpolar(r=values + [values[0]], theta=categories + [categories[0]], fill='toself', name=current_scores_label,
                                  fillcolor=f'rgba(52, 152, 219, {fill_opacity})', line=dict(color=COLOR_INFO_BLUE_DARK_THEME, width=2), hoverinfo="r+theta"))
    if target_values_map:
        target_r = [target_values_map.get(cat, 0) for cat in categories]; target_label = _viz_loc("target_scores_label", lang_code)
        fig.add_trace(go.Scatterpolar(r=target_r + [target_r[0]], theta=categories + [categories[0]], mode='lines', name=target_label,
                                      line=dict(color=COLOR_WARNING_AMBER_DARK_THEME, dash='dash', width=2), hoverinfo="r+theta"))
    max_r_calc = [v for v in values if pd.notna(v)]
    max_r = range_max_override if range_max_override is not None else (max(max_r_calc) * 1.15 if max_r_calc else 5.0)
    if target_values_map and target_values_map.values(): max_r = max(max_r, max(target_values_map.values()) * 1.15 if target_values_map else 0)
    if max_r < EPSILON : max_r = 5.0
    fig.update_layout(template=PLOTLY_TEMPLATE_DARK, title=dict(text=localized_title, x=0.5, font=dict(color=COLOR_PRIMARY_TEXT_LIGHT, size=16)),
                      paper_bgcolor=COLOR_PAPER_BG_DARK, plot_bgcolor=COLOR_PLOT_BG_DARK, font=dict(color=COLOR_PRIMARY_TEXT_LIGHT),
                      polar=dict(bgcolor=COLOR_PLOT_BG_DARK, radialaxis=dict(visible=True, range=[0, max_r], color=COLOR_SECONDARY_TEXT_LIGHT, gridcolor=COLOR_GRID_DARK_THEME, linecolor=COLOR_AXIS_LINE_DARK_THEME, angle=90, tickfont_size=9),
                                 angularaxis=dict(color=COLOR_SECONDARY_TEXT_LIGHT, gridcolor=COLOR_GRID_DARK_THEME, linecolor=COLOR_AXIS_LINE_DARK_THEME, direction="clockwise", tickfont_size=10)),
                      showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5, bgcolor="rgba(44,62,80,0.7)", bordercolor=COLOR_NEUTRAL_GRAY_DARK_THEME, font=dict(color=COLOR_PRIMARY_TEXT_LIGHT, size=10)))
    return fig

# --- Stress Semaforo ---
def create_stress_semaforo_visual(avg_stress_level: Optional[float], lang_code: str, scale_max: float = 10.0):
    localized_panel_title = _viz_loc("overall_stress_indicator_title", lang_code)
    if pd.isna(avg_stress_level): return _get_no_data_figure(localized_panel_title, lang_code=lang_code)
    s_thresh = config.STRESS_LEVEL_PSYCHOSOCIAL; low_t = s_thresh["low"]; med_t_upper = s_thresh["medium"]
    color = COLOR_POSITIVE_GREEN_DARK_THEME; status_key = "stress_low_label"
    if avg_stress_level > med_t_upper: color = COLOR_CRITICAL_RED_DARK_THEME; status_key = "stress_high_label"
    elif avg_stress_level > low_t: color = COLOR_WARNING_AMBER_DARK_THEME; status_key = "stress_medium_label"
    status_loc = _viz_loc(status_key, lang_code); gauge_title_loc = _viz_loc("overall_stress_level_label", lang_code)
    full_title = f"{gauge_title_loc} ({status_loc})"
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = avg_stress_level, domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': full_title, 'font': {'size': 13, 'color': COLOR_PRIMARY_TEXT_LIGHT}},
        number={'valueformat': ".1f", 'font': {'size': 18, 'color': COLOR_PRIMARY_TEXT_LIGHT}},
        gauge = {'axis': {'range': [0, scale_max], 'tickwidth': 1, 'tickcolor': COLOR_AXIS_LINE_DARK_THEME, 'tickfont':{'size':9, 'color': COLOR_SECONDARY_TEXT_LIGHT}},
                 'bar': {'color': color, 'thickness': 0.7}, 'bgcolor': "rgba(0,0,0,0)", 'borderwidth': 1, 'bordercolor': COLOR_NEUTRAL_GRAY_DARK_THEME,
                 'steps': [{'range': [0, low_t], 'color': COLOR_POSITIVE_GREEN_DARK_THEME}, {'range': [low_t, med_t_upper], 'color': COLOR_WARNING_AMBER_DARK_THEME}, {'range': [med_t_upper, scale_max], 'color': COLOR_CRITICAL_RED_DARK_THEME}],
                 'threshold': {'line': {'color': COLOR_PRIMARY_TEXT_LIGHT, 'width': 2}, 'thickness': 0.8, 'value': s_thresh.get("target", low_t)} if s_thresh.get("target") is not None else None}))
    fig.update_layout(height=180, margin={'t':45, 'b':10, 'l':15, 'r':15}, paper_bgcolor=COLOR_PAPER_BG_DARK, plot_bgcolor="rgba(0,0,0,0)")
    return fig

# --- Pie Chart ---
def create_pie_chart(df: pd.DataFrame, names_col: str, values_col: str, title_key: str, lang_code: str):
    localized_title = _viz_loc(title_key, lang_code)
    if df.empty or names_col not in df.columns or values_col not in df.columns or df[values_col].sum() < EPSILON:
        return _get_no_data_pie_figure(localized_title, lang_code=lang_code)
    fig = px.pie(df, names=names_col, values=values_col, hole=0.45, color_discrete_sequence=ACCESSIBLE_CATEGORICAL_PALETTE_DARK_BG)
    fig.update_traces(textposition='outside', textinfo='percent+label', pull=[0.03]*len(df),
                      marker=dict(line=dict(color=COLOR_PLOT_BG_DARK, width=2.5)), opacity=0.9,
                      hoverlabel=dict(bgcolor=COLOR_PLOT_BG_DARK, font_color=COLOR_PRIMARY_TEXT_LIGHT, bordercolor=COLOR_NEUTRAL_GRAY_DARK_THEME),
                      textfont=dict(size=10, color=COLOR_PRIMARY_TEXT_LIGHT))
    _apply_common_layout_settings(fig, localized_title, yaxis_title_localized="", xaxis_title_localized="", show_legend=(len(df) <= 6),
                                 legend_title_key="legend_categories_title", lang_code=lang_code)
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', legend=dict(font_size=9))
    return fig

# --- EXAMPLE: Adapting ONE of your specific trend charts (Task Compliance) ---
def create_task_compliance_trend_themed(
    data_series: pd.Series, date_index: pd.Index, lang_code: str,
    title_key: str = "task_compliance_trend_chart_title", y_axis_key: str = "score_percentage_label",
    x_axis_key: str = "date_label", compliance_trace_key: str = "compliance_label",
    forecast_series: Optional[pd.Series] = None, forecast_trace_key: str = "forecast_label",
    disruption_points_dates: Optional[List[Any]] = None):

    localized_title = _viz_loc(title_key, lang_code)
    if not isinstance(data_series, pd.Series) or data_series.empty or not data_series.notna().any():
        return _get_no_data_figure(localized_title, lang_code=lang_code)

    fig = go.Figure(); palette = ACCESSIBLE_CATEGORICAL_PALETTE_DARK_BG
    localized_compliance_label = _viz_loc(compliance_trace_key, lang_code)
    localized_x_title = _viz_loc(x_axis_key, lang_code); localized_y_title = _viz_loc(y_axis_key, lang_code)

    fig.add_trace(go.Scatter(x=date_index, y=data_series, mode='lines+markers', name=localized_compliance_label,
                             line=dict(color=palette[0 % len(palette)], width=2.2), marker=dict(size=5, symbol="circle"),
                             hovertemplate=f'<b>{localized_compliance_label}</b><br>{localized_x_title}: %{{x|%Y-%m-%d}}<br>{localized_y_title}: %{{y:.1f}}%<extra></extra>'))
    if forecast_series is not None and isinstance(forecast_series, pd.Series) and not forecast_series.empty and forecast_series.notna().any():
        localized_forecast_label = _viz_loc(forecast_trace_key, lang_code)
        fc_index = forecast_series.index if isinstance(forecast_series.index, pd.DatetimeIndex) and forecast_series.index.equals(date_index) else date_index # Check index compatibility
        fig.add_trace(go.Scatter(x=fc_index, y=forecast_series, mode='lines', name=localized_forecast_label,
                                 line=dict(color=palette[1 % len(palette)], dash='dashdot', width=1.8),
                                 hovertemplate=f'<b>{localized_forecast_label}</b><br>{localized_x_title}: %{{x|%Y-%m-%d}}<br>{localized_y_title}: %{{y:.1f}}%<extra></extra>'))
    if disruption_points_dates:
        for dp_date in disruption_points_dates:
            fig.add_vline(x=dp_date, line=dict(color=COLOR_WARNING_AMBER_DARK_THEME, width=1.5, dash="longdash"),
                          annotation_text="▼", annotation_position="top", annotation=dict(font_size=12, font_color=COLOR_WARNING_AMBER_DARK_THEME, showarrow=False, yshift=10))

    all_values = data_series.tolist();
    if forecast_series is not None and isinstance(forecast_series, pd.Series): all_values.extend(forecast_series.tolist())
    valid_values = [v for v in all_values if pd.notna(v)]
    min_val_data = min(valid_values) if valid_values else 0.0
    max_val_data = max(valid_values) if valid_values else 100.0
    padding = (max_val_data - min_val_data) * 0.1 if (max_val_data - min_val_data) > EPSILON else 5.0
    y_range = [max(0, min_val_data - padding), min(105, max_val_data + padding)] # Adjusted min y-axis to 0 if possible
    if y_range[1] <= y_range[0] + EPSILON : y_range = [y_range[0], y_range[0] + 10.0]

    _apply_common_layout_settings(fig, localized_title, yaxis_title_localized=localized_y_title,
                                 xaxis_title_localized=localized_x_title, yaxis_range=y_range,
                                 legend_title_key="legend_metrics_title", lang_code=lang_code)
    return fig

# ==============================================================================
# !!!! IMPORTANT !!!!
# YOU MUST NOW COPY YOUR SPECIFIC PLOTTING FUNCTIONS FROM YOUR
# `visualizations_v2.py` (the one with plot_task_compliance_score,
# plot_worker_density_heatmap, plot_downtime_causes_pie, etc.)
# INTO THIS FILE, BELOW THIS COMMENT BLOCK.
#
# FOR EACH FUNCTION YOU COPY, YOU MUST:
# 1. Rename it (e.g., add `_themed` suffix: `plot_worker_density_heatmap` -> `create_worker_density_heatmap_themed`)
# 2. Add `lang_code: str` as a parameter.
# 3. Use `_viz_loc(key, lang_code, default_text)` for ALL user-facing text.
# 4. Call `_apply_common_layout_settings(fig, localized_title, ...)` at the end of the function.
# 5. Replace hardcoded colors with the theme color constants.
# 6. Ensure it handles empty or invalid input DataFrames by returning `_get_no_data_figure()`.
# 7. For spatial plots, they will need `facility_size_tuple` and `facility_config_dict`
#    passed from the panel, which gets them from `config.FACILITY_CONFIG`.
# ==============================================================================

# === STUBS FOR YOUR SPECIFIC PLOTS - REPLACE THESE WITH YOUR ADAPTED CODE ===

def create_collaboration_trend_themed(data_series: pd.Series, date_index: pd.Index, lang_code: str,
                                     title_key:str = "collaboration_multitrend_chart_title", **kwargs):
    logger.critical(f"STUB: `create_collaboration_trend_themed`. Implement by adapting `plot_collaboration_proximity_index`.")
    return _get_no_data_figure(_viz_loc(title_key, lang_code), lang_code=lang_code)

def create_oee_trends_themed(df: pd.DataFrame, date_col:str, oee_metrics_map:Dict[str,str], lang_code:str,
                             title_key:str="oee_trends_chart_title", **kwargs):
    logger.critical(f"STUB: `create_oee_trends_themed`. Implement by adapting `plot_operational_efficiency`.")
    # This one is a multi-line trend like `create_trend_chart` but specifically for OEE components.
    # You can use `create_trend_chart` directly if it fits, or adapt your `plot_operational_efficiency`.
    return _get_no_data_figure(_viz_loc(title_key, lang_code), lang_code=lang_code)

def create_wellbeing_trend_themed(data_series: pd.Series, date_index: pd.Index, lang_code: str,
                                  title_key:str="wellbeing_psych_safety_trend_title", **kwargs): # Combine this for multiple lines
    logger.critical(f"STUB: `create_wellbeing_trend_themed`. Implement by adapting `plot_worker_wellbeing`.")
    return _get_no_data_figure(_viz_loc(title_key, lang_code), lang_code=lang_code)

def create_psych_safety_trend_themed(data_series: pd.Series, date_index: pd.Index, lang_code: str,
                                     title_key:str="wellbeing_psych_safety_trend_title", **kwargs):
    logger.critical(f"STUB: `create_psych_safety_trend_themed`. Implement by adapting `plot_psychological_safety`.")
    return _get_no_data_figure(_viz_loc(title_key, lang_code), lang_code=lang_code)

def create_downtime_interval_plot_themed(df:pd.DataFrame, date_col:str, value_col:str, lang_code:str,
                                         title_key:str="downtime_interval_plot_title", **kwargs): # Bar chart
    logger.critical(f"STUB: `create_downtime_interval_plot_themed`. Implement by adapting `plot_downtime_trend` (which is a bar chart).")
    return _get_no_data_figure(_viz_loc(title_key, lang_code), lang_code=lang_code)

def create_downtime_causes_pie_themed(downtime_events_df: pd.DataFrame, cause_col: str, duration_col:str, lang_code: str,
                                      title_key:str="downtime_by_cause_pie_title", **kwargs): # Adapt your plot_downtime_causes_pie
    logger.critical(f"STUB: `create_downtime_causes_pie_themed`. Implement by adapting `plot_downtime_causes_pie`.")
    return _get_no_data_pie_figure(_viz_loc(title_key, lang_code), lang_code=lang_code)

def create_team_cohesion_trend_themed(data_series: pd.Series, date_index: pd.Index, lang_code: str,
                                      title_key:str = "collaboration_multitrend_chart_title", **kwargs):
    logger.critical(f"STUB: `create_team_cohesion_trend_themed`. Implement by adapting `plot_team_cohesion`.")
    return _get_no_data_figure(_viz_loc(title_key, lang_code), lang_code=lang_code)

def create_perceived_workload_trend_themed(data_series: pd.Series, date_index: pd.Index, lang_code: str,
                                           title_key:str = "workload_vs_psych_chart_title", **kwargs): # Example, if you make it a trend
    logger.critical(f"STUB: `create_perceived_workload_trend_themed`. Implement by adapting `plot_perceived_workload`.")
    return _get_no_data_figure(_viz_loc(title_key, lang_code), lang_code=lang_code)


# SPATIAL PLOTS - THESE REQUIRE YOUR FULL, ADAPTED CODE
# They also need facility_config_dict which contains facility_size_tuple.
def create_worker_density_heatmap_themed(
    team_positions_df: pd.DataFrame, # This should be the filtered spatial data
    facility_config_dict: dict, # Contains facility_size, work_areas, entry_exit from config.FACILITY_CONFIG
    lang_code: str,
    title_key: str = "worker_density_heatmap_figure_title",
    x_col_name: str = "worker_x_coord", # Conceptual key, resolved by panel
    y_col_name: str = "worker_y_coord"  # Conceptual key, resolved by panel
):
    """
    ADAPT YOUR `plot_worker_density_heatmap` HERE.
    It needs to extract facility_size from facility_config_dict.
    And use lang_code, _viz_loc, _apply_common_layout_settings, theme colors.
    """
    logger.critical(f"FUNCTION `create_worker_density_heatmap_themed` IS A STUB. YOU MUST IMPLEMENT IT FULLY.")
    localized_title = _viz_loc(title_key, lang_code, "Worker Density Heatmap")
    facility_size = facility_config_dict.get("FACILITY_SIZE", (100,60)) # Example fallback
    if team_positions_df.empty or x_col_name not in team_positions_df.columns or y_col_name not in team_positions_df.columns:
        return _get_no_data_figure(localized_title, lang_code=lang_code)

    fig = px.density_heatmap(team_positions_df, x=x_col_name, y=y_col_name,
                             nbinsx=int(facility_size[0]/max(1,facility_size[0]/25)), # Dynamic binning based on size
                             nbinsy=int(facility_size[1]/max(1,facility_size[1]/20)),
                             color_continuous_scale="Inferno") # Good for dark themes
    _apply_common_layout_settings(fig, localized_title,
                                  xaxis_title_localized=_viz_loc("x_coordinate_label", lang_code),
                                  yaxis_title_localized=_viz_loc("y_coordinate_label", lang_code))
    fig.update_layout(xaxis_range=[0, facility_size[0]], yaxis_range=[0, facility_size[1]],
                      coloraxis_colorbar=dict(title=_viz_loc("density_label", lang_code, "Density"), tickfont_size=9))
    # Add shapes for work areas, entry/exit from facility_config_dict here
    # ... (logic from your original plot_worker_density_heatmap for shapes)
    return fig

def create_spatial_distribution_map_themed(
    team_positions_df: pd.DataFrame, # This is the filtered spatial data
    facility_config_dict: dict,
    lang_code: str,
    title_key: str = "worker_distribution_map_figure_title",
    x_col_name: str = "worker_x_coord",
    y_col_name: str = "worker_y_coord",
    color_col_actual: Optional[str] = None, # Actual column name for coloring (e.g., 'Zone' or 'Status')
    worker_id_col_actual: Optional[str] = None, # Actual column name for worker ID (hover)
    status_col_actual: Optional[str] = None, # Actual column name for status (hover/symbol)
    zone_col_actual: Optional[str] = None, # Actual column name for zone (hover)
    selected_step_for_title: Optional[int] = None # If showing snapshot
):
    """
    ADAPT YOUR `plot_worker_distribution` HERE.
    Extract facility_size, MINUTES_PER_INTERVAL from facility_config_dict.
    """
    logger.critical(f"FUNCTION `create_spatial_distribution_map_themed` IS A STUB. YOU MUST IMPLEMENT IT FULLY.")
    base_title = _viz_loc(title_key, lang_code, "Worker Distribution")
    facility_size = facility_config_dict.get("FACILITY_SIZE", (100,60))
    localized_title = base_title
    if selected_step_for_title is not None:
        mpi = facility_config_dict.get("MINUTES_PER_INTERVAL", 2)
        time_text = _viz_loc("time_label_spatial", lang_code, time_val=selected_step_for_title * mpi)
        localized_title = f"{base_title} ({time_text})"

    if team_positions_df.empty or x_col_name not in team_positions_df.columns or y_col_name not in team_positions_df.columns:
        return _get_no_data_figure(localized_title, lang_code=lang_code)

    hover_data_list = {}
    if worker_id_col_actual and worker_id_col_actual in team_positions_df.columns: hover_data_list['Worker ID'] = team_positions_df[worker_id_col_actual]
    if status_col_actual and status_col_actual in team_positions_df.columns: hover_data_list['Status'] = team_positions_df[status_col_actual]
    if zone_col_actual and zone_col_actual in team_positions_df.columns and color_col_actual != zone_col_actual : hover_data_list['Zone'] = team_positions_df[zone_col_actual]


    fig = px.scatter(team_positions_df, x=x_col_name, y=y_col_name,
                     color=color_col_actual if color_col_actual and color_col_actual in team_positions_df.columns else None,
                     hover_name=worker_id_col_actual if worker_id_col_actual and worker_id_col_actual in team_positions_df.columns else None,
                     hover_data=hover_data_list if hover_data_list else None,
                     color_discrete_sequence=ACCESSIBLE_CATEGORICAL_PALETTE_DARK_BG)
    _apply_common_layout_settings(fig, localized_title,
                                  xaxis_title_localized=_viz_loc("x_coordinate_label", lang_code),
                                  yaxis_title_localized=_viz_loc("y_coordinate_label", lang_code),
                                  show_legend=bool(color_col_actual) # Only show legend if coloring by a column
                                  )
    fig.update_layout(xaxis_range=[0, facility_size[0]], yaxis_range=[0, facility_size[1]])
    # Add shapes for work areas, entry/exit from facility_config_dict here
    # ... (logic from your original plot_worker_distribution for shapes)
    return fig