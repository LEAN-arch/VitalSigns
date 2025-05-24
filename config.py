# config.py
from typing import Dict, List, Any

# --- App Basics ---
APP_TITLE_KEY = "app_title"
APP_ICON = "📊"
APP_VERSION = "1.3.2" # Incremented version
DEFAULT_LANG = "EN"

# --- File Paths (Ensure these exist in a 'data/' subdirectory or update paths) ---
STABILITY_DATA_FILE = "data/stability_data.csv"
SAFETY_DATA_FILE = "data/safety_data.csv"
ENGAGEMENT_DATA_FILE = "data/engagement_data.csv"
STRESS_DATA_FILE = "data/stress_data.csv"
TASK_COMPLIANCE_DATA_FILE = "data/task_compliance_data.csv"
COLLABORATION_DATA_FILE = "data/collaboration_data.csv"
WELLBEING_DATA_FILE = "data/wellbeing_data.csv"
DOWNTIME_DATA_FILE = "data/downtime_data.csv"
OEE_DATA_FILE = "data/oee_data.csv"
RESILIENCE_DATA_FILE = "data/resilience_data.csv"
PSYCH_SAFETY_DATA_FILE = "data/psych_safety_data.csv" # Or point to ENGAGEMENT_DATA_FILE if combined
TEAM_COHESION_DATA_FILE = "data/team_cohesion_data.csv" # Or point to COLLABORATION_DATA_FILE
PERCEIVED_WORKLOAD_DATA_FILE = "data/perceived_workload_data.csv" # Or point to STRESS_DATA_FILE
SPATIAL_DATA_FILE = "data/spatial_data.csv"

ALL_DATA_FILE_CONSTANTS = [ # Used by dashboard_page.get_all_raw_dataframes_for_filters
    "STABILITY_DATA_FILE", "SAFETY_DATA_FILE", "ENGAGEMENT_DATA_FILE", "STRESS_DATA_FILE",
    "TASK_COMPLIANCE_DATA_FILE", "COLLABORATION_DATA_FILE", "WELLBEING_DATA_FILE",
    "DOWNTIME_DATA_FILE", "OEE_DATA_FILE", "RESILIENCE_DATA_FILE", "PSYCH_SAFETY_DATA_FILE",
    "TEAM_COHESION_DATA_FILE", "PERCEIVED_WORKLOAD_DATA_FILE", "SPATIAL_DATA_FILE"
]

# --- Column Mapping (Conceptual Name -> Actual CSV Column Header) ---
# !!! THIS IS CRITICAL - MAKE SURE IT MATCHES YOUR CSV FILES EXACTLY !!!
COLUMN_MAP: Dict[str, Any] = {
    # Common
    "date": "Date", "site": "Site", "region": "Region", "department": "Department",
    "fc": "Functional Category", "shift": "Shift",

    # Stability
    "rotation_rate": "Rotation Rate (%)", "retention_6m": "6-Month Retention (%)",
    "retention_12m": "12-Month Retention (%)", "retention_18m": "18-Month Retention (%)",
    "hires": "Hires", "exits": "Exits",

    # Safety
    "month": "Month", "incidents": "Incidents", "near_misses": "Near Misses",
    "days_without_accidents": "Days Without Accidents", "active_alerts": "Active Safety Alerts",
    "production_incident_id": "IncidentID",

    # Engagement & Psych Safety
    "labor_climate_score": "Labor Climate Score", "enps_score": "eNPS",
    "participation_rate": "Survey Participation Rate (%)", "recognitions_count": "Recognitions Count",
    "psych_safety_score": "Psychological Safety Score", "psych_safety_date": "Survey Date PS",

    "engagement_radar_dims_cols": {
        "initiative": "Engagement - Initiative", "autonomy": "Engagement - Autonomy",
        "recognition": "Engagement - Recognition", "growth": "Engagement - Growth Opportunities",
        "belonging": "Engagement - Belonging" # Example dimension
    },
    "engagement_radar_dims_labels": { # For localizing radar dimension labels
        "initiative": "initiative_label", "autonomy": "autonomy_label",
        "recognition": "recognition_label", "growth": "growth_label", "belonging": "belonging_label"
    },

    # Stress & Workload
    "stress_level_survey": "Stress Level (Survey 0-10)", "overtime_hours": "Overtime Hours",
    "unfilled_shifts": "Unfilled Shifts", "workload_perception": "Workload Perception (0-10)",
    "psychological_signals": "Psychological Stress Signals (0-10)",
    "perceived_workload": "Perceived Workload Index (0-10)", "workload_date": "Workload Survey Date",

    # Task Compliance
    "task_compliance_rate": "Task Compliance Rate (%)", "task_date": "Task Date",

    # Collaboration & Team Cohesion
    "collaboration_score": "Collaboration Score (0-100)", "collaboration_date": "Collaboration Assessment Date",
    "team_cohesion_index": "Team Cohesion Index (0-100)", "team_cohesion_date": "Cohesion Survey Date",

    # Well-being
    "wellbeing_index": "Well-Being Index (0-10)", "wellbeing_date": "Wellbeing Survey Date",

    # Downtime
    "downtime_duration": "Downtime (Minutes)", "downtime_cause": "Downtime Cause",
    "downtime_date": "Downtime Start Date", "downtime_shift": "Shift Of Downtime",

    # OEE
    "oee_availability": "Availability (%)", "oee_performance": "Performance (%)",
    "oee_quality": "Quality (%)", "oee_overall": "OEE (%)", "oee_date": "OEE Calculation Date",

    # Resilience
    "resilience_score": "Operational Resilience Score (0-100)", "resilience_date": "Resilience Assessment Date",

    # Spatial Dynamics
    "worker_x_coord": "X-Coordinate", "worker_y_coord": "Y-Coordinate",
    "spatial_timestamp": "Location Timestamp", "spatial_worker_id": "Worker ID",
    "spatial_zone": "Zone", "spatial_status": "Status", "spatial_z_coord": "Z-Coordinate", # If using 3D

    # Facility Config related conceptual keys (map to keys in FACILITY_CONFIG dict)
    "facility_width_key": "FACILITY_WIDTH", "facility_height_key": "FACILITY_HEIGHT",
    "facility_minutes_per_interval_key": "MINUTES_PER_INTERVAL",
    "facility_work_areas_key": "WORK_AREAS", "facility_entry_exit_key": "ENTRY_EXIT_POINTS"
}

# --- Default Filter Selections ---
DEFAULT_SITES: List[str] = []
DEFAULT_REGIONS: List[str] = []
DEFAULT_DEPARTMENTS: List[str] = []
DEFAULT_FUNCTIONAL_CATEGORIES: List[str] = []
DEFAULT_SHIFTS: List[str] = []

# --- Thresholds for KPIs ---
STABILITY_ROTATION_RATE = {"good": 5.0, "warning": 10.0, "target": 3.0, "max_display": 25.0}
STABILITY_RETENTION = {"good": 90.0, "warning": 80.0, "target": 95.0}
SAFETY_DAYS_NO_INCIDENTS = {"good": 180, "warning": 90, "target": 365}
ENGAGEMENT_CLIMATE_SCORE = {"good": 8.0, "warning": 6.5, "target": 8.5, "max_scale": 10.0}
ENGAGEMENT_ENPS = {"good": 50, "warning": 20, "target": 60, "max_scale": 100}
ENGAGEMENT_PARTICIPATION = {"good": 85.0, "warning": 70.0, "target": 90.0}
ENGAGEMENT_RADAR_DIM_TARGET = 4.0 # Assuming a 0-5 scale for dimensions
ENGAGEMENT_RADAR_DIM_SCALE_MAX = 5.0
STRESS_LEVEL_PSYCHOSOCIAL = {"low": 3.0, "medium": 7.0, "max_scale": 10.0, "target": 2.5} # Medium is the upper bound of acceptable
TASK_COMPLIANCE = {"good": 95.0, "warning": 85.0, "target": 98.0}
COLLABORATION_SCORE_THRESHOLDS = {"good": 85.0, "warning": 70.0, "target": 90.0, "max_scale": 100.0}
WELLBEING_INDEX_THRESHOLDS = {"good": 8.0, "warning": 6.0, "target": 8.5, "max_scale": 10.0}
PERCEIVED_WORKLOAD_THRESHOLDS = {"good": 3.0, "warning": 7.0, "target": 2.5, "max_scale": 10.0} # Higher is worse for workload
TOTAL_DOWNTIME_THRESHOLDS = {"good": 30, "warning": 90, "target": 15, "max_display": 240} # minutes
OEE_THRESHOLDS = { # OEE components (Availability, Performance, Quality, Overall OEE)
    "availability": {"good": 90.0, "warning": 80.0, "target": 95.0},
    "performance": {"good": 95.0, "warning": 85.0, "target": 99.0},
    "quality": {"good": 99.0, "warning": 95.0, "target": 99.9},
    "overall": {"good": 85.0, "warning": 75.0, "target": 90.0}, # Overall OEE
}
RESILIENCE_SCORE_THRESHOLDS = {"good": 80.0, "warning": 65.0, "target": 90.0, "max_scale": 100.0}

# Facility Configuration Example (used by spatial plots)
FACILITY_CONFIG = {
    "FACILITY_WIDTH": 100, # meters
    "FACILITY_HEIGHT": 60, # meters
    "MINUTES_PER_INTERVAL": 2, # For titles like "Time: X min" if showing discrete steps
    "WORK_AREAS": { # Name: {"coords": [(x0,y0), (x1,y1)] or other shape definition}
        "Assembly Line 1": {"coords": [(10, 5), (70, 15)]},
        "Welding Bay": {"coords": [(75, 20), (95, 40)]},
    },
    "ENTRY_EXIT_POINTS": [ # Name: {"coords": (x,y)}
        {"name": "Main Entry", "coords": (5, 30)},
        {"name": "Dock A", "coords": (95, 5)},
    ]
}

# --- Placeholder Text ---
PLACEHOLDER_TEXT_PLANT_MAP = """<div style='text-align: center; border: 1px dashed #7F8C8D; padding: 15px; margin:10px 0; background-color: #34495E;'><h5 style='color: #ECF0F1;'>📍 Interactive Plant Map (Future)</h5><p style='color: #BDC3C7; font-size: small;'><i>Visualize KPIs on a plant layout.</i></p></div>"""
PLACEHOLDER_TEXT_AI_INSIGHTS = """<div style='text-align: center; border: 1px dashed #3498DB; padding: 15px; margin:10px 0; background-color: #34495E;'><h5 style='color: #ECF0F1;'>🤖 Predictive AI Insights (Future)</h5><p style='color: #BDC3C7; font-size: small;'><i>AI-driven predictions and recommendations.</i></p></div>"""

# --- Text Strings for Internationalization (i18n) ---
TEXT_STRINGS: Dict[str, Dict[str, str]] = {
    "EN": {
        "app_title": "Vital Signs Dashboard", "language_selector": "Language", "language_name_full_EN": "English", "language_name_full_ES": "Español",
        "dashboard_nav_label": "Dashboard", "glossary_nav_label": "Glossary", "navigation_label": "Navigation", "filters_header": "Filters",
        "select_site": "Select Site(s)", "select_region": "Select Region(s)", "select_department": "Select Department(s)", "select_fc": "Select Functional Category(s)", "select_shift": "Select Shift(s)",
        "dashboard_title": "Vital Signs: People & Operations Dashboard", "dashboard_subtitle": "Monitoring key indicators for a healthy and productive workforce.",
        "alignment_note": "Note: Ensure data alignment by common dimensions for accurate filtering.", "psych_safety_note": "Data is aggregated and anonymized for privacy.",
        "no_data_available": "No data available for the selected filters.", "error_loading_data_generic": "Error loading data from {0}",
        "check_file_path_instruction": "Please verify file path.", "exception_detail_prefix": "Exception", "actionable_insights_title": "🔍 Actionable Insights",
        "days_unit": "days", "minutes_unit_short": "min", "percentage_label": "Percentage (%)", "score_label": "Score", "score_percentage_label": "Score (%)",
        "count_label": "Count", "hours_or_shifts_label": "Hours / Shifts", "people_count_label": "Number of People", "month_axis_label": "Month",
        "date_label": "Date", "time_step_interval_label": "Time Step", "category_label": "Category", "definition_label": "Definition", "search_term_label": "Search Term:",
        "no_term_found": "No matching terms found.", "glossary_page_title": "Glossary of Terms", "glossary_intro": "Definitions for key metrics and terms.",
        "glossary_empty_message": "The glossary is currently empty.", "optional_modules_header": "Optional Modules",
        "show_optional_modules": "Show Advanced/Beta Modules", "optional_modules_title": "Advanced/Beta Modules",
        "optional_modules_list": "- **Predictive Analytics**\n- **Scenario Modeling**\n- **Detailed Drill-Downs**",
        "no_data_for_visualization_default": "No data available for this visualization.", "average_label": "Avg", "period_rolling_avg_label": "MA",
        "legend_metrics_title": "Metrics", "legend_categories_title": "Categories", "current_scores_label": "Current Scores", "target_scores_label": "Target Scores", "current_value_label":"Current", "density_label":"Density",

        "stability_panel_title": "📈 Labor Stability", "rotation_rate_metric": "Avg. Rotation Rate", "rotation_rate_gauge": "Rotation Rate",
        "rotation_rate_metric_help": "Target: < {target}% (Lower is better)", "retention_6m_metric": "6-Month Retention", "retention_12m_metric": "12-Month Retention",
        "retention_18m_metric": "18-Month Retention", "retention_metric_help": "Target: > {target}% (Higher is better)",
        "hires_vs_exits_chart_title": "Monthly Hires vs. Exits", "no_data_hires_exits": "Hires, Exits, or Date column missing.", "hires_label": "Hires", "exits_label": "Exits",

        "safety_pulse_title": "🛡️ Safety Pulse", "monthly_incidents_chart_title": "Monthly Incidents & Near Misses", "no_data_incidents_near_misses": "Month, Incidents, or Near Misses column missing.",
        "incidents_label": "Incidents", "near_misses_label": "Near Misses", "days_without_accidents_metric": "Days Without Accidents", "days_no_incident_help": "Higher is better.",
        "active_safety_alerts_metric": "Active Safety Alerts", "engagement_title": "🤝 Employee Engagement & Commitment", "engagement_dimensions_radar_title": "Engagement Dimensions",
        "no_data_radar": "Not enough data for radar.", "no_data_radar_columns": "Engagement radar columns missing.",
        "initiative_label": "Initiative", "autonomy_label": "Autonomy", "recognition_label": "Recognition", "growth_label": "Growth", "belonging_label": "Belonging",
        "labor_climate_score_metric": "Labor Climate Score", "enps_metric": "eNPS", "enps_metric_help": "Target: > {target}",
        "survey_participation_metric": "Survey Participation", "recognitions_count_metric": "Recognitions Given",

        "stress_title": "🧘 Operational Stress & Workload", "overall_stress_indicator_title": "Overall Stress Indicator", "overall_stress_level_label": "Overall Stress Level",
        "stress_indicator_help": "Psychosocial Stress Level (0-10). Target: < {target}.", "stress_low_label": "Low", "stress_medium_label": "Medium", "stress_high_label": "High",
        "monthly_shift_load_chart_title": "Monthly Overtime & Unfilled Shifts", "no_data_shift_load": "Date, Overtime, or Unfilled Shifts missing.",
        "overtime_label": "Total Overtime", "unfilled_shifts_label": "Total Unfilled Shifts", "workload_vs_psych_chart_title": "Workload Perception vs. Psych. Stress Signals",
        "no_data_workload_psych": "Date, Workload, or Psych. Signals missing.", "workload_perception_label": "Avg. Workload Perception", "psychological_signals_label": "Avg. Psych. Stress Signals",
        "average_score_label": "Average Score (0-10)", "advanced_analytics_title": "🚀 Advanced Operational & People Analytics",

        "task_compliance_title": "✅ Task Compliance", "task_compliance_rate_metric_card": "Avg. Task Compliance", "task_compliance_rate_gauge": "Task Compliance Rate",
        "task_compliance_trend_chart_title": "Task Compliance Score Trend", "compliance_label": "Compliance", "forecast_label": "Forecast", "task_compliance_help": "Target: > {target}%",
        "no_data_task_compliance": "Task compliance or date columns missing.",

        "collaboration_metrics_title": "💬 Collaboration & Team Dynamics", "collaboration_score_metric_card": "Collaboration Score", "collaboration_score_gauge": "Collaboration Score",
        "collaboration_score_label": "Avg. Collab Score", "collaboration_score_help": "Target: > {target} (0-100)", "team_cohesion_label": "Avg. Team Cohesion", "team_cohesion_gauge": "Team Cohesion",
        "collaboration_multitrend_chart_title": "Collaboration & Cohesion Trends", "worker_wellbeing_psych_safety_title": "❤️ Worker Well-Being & Psych. Safety",

        "wellbeing_index_metric_card": "Well-Being Index", "wellbeing_index_gauge": "Well-Being Index", "wellbeing_index_label": "Avg. Well-Being",
        "wellbeing_index_help": "Target: > {target} (0-10)", "perceived_workload_metric_card": "Perceived Workload", "perceived_workload_gauge": "Perceived Workload (0-10)",
        "perceived_workload_help": "Target: < {target} (0-10, lower is better)", "psych_safety_score_metric_card": "Psych. Safety Score",
        "psych_safety_score_gauge": "Psychological Safety", "psych_safety_score_label": "Avg. Psych Safety", "wellbeing_psych_safety_trend_title": "Well-Being & Psych. Safety Trends",

        "downtime_analysis_title": "⏱️ Downtime Analysis", "total_downtime_metric_card": "Total Downtime", "total_downtime_gauge": "Total Downtime",
        "total_downtime_help": "Target: < {target} min", "number_of_incidents_metric_card": "Downtime Incidents", "num_incidents_help": "Distinct incidents causing downtime.",
        "avg_duration_incident_metric_card": "Avg. Duration/Incident", "avg_duration_help": "Avg. downtime per incident.",
        "total_downtime_shift_clock_title": "Downtime This Shift", "downtime_current_shift_card": "Shift Downtime", "downtime_shift_help": "Total downtime for selected shift(s).",
        "downtime_interval_plot_title": "Downtime per Interval", "downtime_duration_label": "Downtime", "no_data_downtime_interval": "Downtime date or duration missing.",
        "downtime_cause_plot_title": "Downtime by Cause", "downtime_by_cause_pie_title": "Downtime by Cause", "no_data_downtime_cause": "Downtime cause or duration missing.",

        "oee_dashboard_title": "⚙️ OEE", "oee_availability_card": "Availability", "oee_availability_gauge": "Availability (%)",
        "oee_performance_card": "Performance", "oee_performance_gauge": "Performance (%)", "oee_quality_card": "Quality", "oee_quality_gauge": "Quality (%)",
        "oee_overall_card": "Overall OEE", "oee_overall_gauge": "Overall OEE (%)", "oee_metric_help": "Target: > {target}%", "oee_trends_chart_title": "OEE Component Trends",

        "operational_resilience_title": "💪 Operational Resilience", "resilience_score_card": "Resilience Score", "resilience_score_gauge": "Resilience Score",
        "resilience_score_help": "Target: > {target} (0-100)", "spatial_dynamics_title": "🗺️ Spatial Dynamics Analysis",

        "worker_density_heatmap_panel_title": "Worker Density Heatmap", "worker_density_heatmap_figure_title": "Worker Density",
        "heatmap_note": "Heatmap shows worker concentration.", "heatmap_viz_missing": "Heatmap viz function unavailable.", "no_data_spatial_heatmap": "Coordinate columns missing.",
        "worker_distribution_map_panel_title": "Worker Distribution Map", "worker_distribution_map_figure_title": "Worker Distribution",
        "time_label_spatial": "Time: {time_val} min", "distribution_map_note": "Scatter plot of worker locations.", "scatter_map_viz_missing": "Scatter map viz function unavailable.",
        "no_data_spatial_scatter": "Coordinate columns missing.", "x_coordinate_label": "X Coordinate (m)", "y_coordinate_label": "Y Coordinate (m)",

        "plant_map_title": "📍 Plant Map (Future)", "ai_insights_title": "🤖 AI Insights (Future)",
        "no_data_for_metric": "No data for this metric.", "no_data_for_trend": "No data for this trend.", "no_data_for_plot": "No data for this plot.",
        "translation_missing": "MISSING TRANSLATION ({key})" # For debugging missing translations
    },
    "ES": { # YOU NEED TO FILL THIS OUT COMPLETELY
        "app_title": "Dashboard de Signos Vitales", "language_selector": "Idioma", "language_name_full_EN": "English", "language_name_full_ES": "Español",
        "dashboard_nav_label": "Dashboard", "glossary_nav_label": "Glosario", "navigation_label": "Navegación",
        "filters_header": "Filtros", "select_site": "Seleccionar Sitio(s)", # ... and so on for ALL keys
        "stability_panel_title": "📈 Estabilidad Laboral",
        "rotation_rate_gauge": "Tasa de Rotación",
        "no_data_for_visualization_default": "No hay datos disponibles para esta visualización.",
        "translation_missing": "TRADUCCIÓN FALTANTE ({key})",
        # ... MANY MORE TRANSLATIONS NEEDED ...
    }
}