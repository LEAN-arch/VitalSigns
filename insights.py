# insights.py
import pandas as pd
from typing import List, Optional, Dict, Any
import config
import logging

logger = logging.getLogger(__name__)

def _ins_loc(text_key: str, lang_code: str, default_text_override: Optional[str] = None, **kwargs) -> str:
    lang_dict = config.TEXT_STRINGS.get(lang_code, config.TEXT_STRINGS.get(config.DEFAULT_LANG, {}))
    base_string = lang_dict.get(text_key, default_text_override if default_text_override is not None else lang_dict.get("translation_missing", "TR_INS: {key}").format(key=text_key))
    if kwargs:
        try: return base_string.format(**kwargs)
        except (KeyError, ValueError) as e:
            logger.warning(f"Error formatting insight loc key '{text_key}' for lang '{lang_code}'. String: '{base_string}', Args: {kwargs}. Error: {e}")
            return base_string
    return base_string

# --- Stability Insights ---
def generate_stability_insights(df_filtered: pd.DataFrame, avg_rotation: Optional[float],
                                trend_df: pd.DataFrame, lang_code: str) -> List[str]:
    insights_list = []
    # Example:
    # if pd.notna(avg_rotation) and avg_rotation > config.STABILITY_ROTATION_RATE["warning"]:
    #     insights_list.append(_ins_loc("insight_high_rotation", lang_code, rot_val=avg_rotation))
    if not insights_list: insights_list.append(_ins_loc("no_specific_insights", lang_code, panel_name=_ins_loc("stability_panel_title", lang_code)))
    return insights_list

# --- Safety Insights ---
def generate_safety_insights(df_filtered: pd.DataFrame, days_no_accidents: Optional[float],
                             total_incidents_period: Optional[float], lang_code: str) -> List[str]:
    insights_list = []
    if not insights_list: insights_list.append(_ins_loc("no_specific_insights", lang_code, panel_name=_ins_loc("safety_pulse_title", lang_code)))
    return insights_list

# --- Engagement Insights ---
def generate_engagement_insights(avg_enps: Optional[float], avg_climate: Optional[float],
                                 participation: Optional[float], lang_code: str) -> List[str]:
    insights_list = []
    if not insights_list: insights_list.append(_ins_loc("no_specific_insights", lang_code, panel_name=_ins_loc("engagement_title", lang_code)))
    return insights_list

# --- Stress Insights ---
def generate_stress_insights(avg_stress_survey: Optional[float], df_trends: pd.DataFrame, lang_code: str) -> List[str]:
    insights_list = []
    if not insights_list: insights_list.append(_ins_loc("no_specific_insights", lang_code, panel_name=_ins_loc("stress_title", lang_code)))
    return insights_list

# --- Task Compliance Insights ---
def generate_task_compliance_insights(df_filtered: pd.DataFrame, avg_compliance: Optional[float],
                                      trend_series: Optional[pd.Series], lang_code: str) -> List[str]:
    insights_list = []
    if not insights_list: insights_list.append(_ins_loc("no_specific_insights", lang_code, panel_name=_ins_loc("task_compliance_title", lang_code)))
    return insights_list

# --- Collaboration Insights ---
def generate_collaboration_insights(df_collaboration_filtered: pd.DataFrame, df_cohesion_filtered: pd.DataFrame,
                                    avg_collab_score: Optional[float], avg_cohesion_score: Optional[float],
                                    lang_code: str) -> List[str]:
    insights_list = []
    if not insights_list: insights_list.append(_ins_loc("no_specific_insights", lang_code, panel_name=_ins_loc("collaboration_metrics_title", lang_code)))
    return insights_list

# --- Wellbeing Insights ---
def generate_wellbeing_insights(avg_wellbeing: Optional[float], avg_psych_safety: Optional[float],
                                avg_perceived_workload: Optional[float], lang_code: str) -> List[str]:
    insights_list = []
    if not insights_list: insights_list.append(_ins_loc("no_specific_insights", lang_code, panel_name=_ins_loc("worker_wellbeing_psych_safety_title", lang_code)))
    return insights_list

# --- Downtime Insights ---
def generate_downtime_insights(df_downtime_filtered: pd.DataFrame, total_downtime: Optional[float],
                               num_incidents: Optional[int], avg_duration_per_incident: Optional[float],
                               lang_code: str) -> List[str]:
    insights_list = []
    if not insights_list: insights_list.append(_ins_loc("no_specific_insights", lang_code, panel_name=_ins_loc("downtime_analysis_title", lang_code)))
    return insights_list

# --- OEE Insights ---
def generate_oee_insights(df_oee_filtered: pd.DataFrame, oee_components: Dict[str, Optional[float]], lang_code: str) -> List[str]:
    insights_list = [] # oee_components could be {"availability": value, "performance": value, ...}
    if not insights_list: insights_list.append(_ins_loc("no_specific_insights", lang_code, panel_name=_ins_loc("oee_dashboard_title", lang_code)))
    return insights_list

# --- Resilience Insights ---
def generate_resilience_insights(df_resilience_filtered: pd.DataFrame, avg_resilience_score: Optional[float], lang_code: str) -> List[str]:
    insights_list = []
    if not insights_list: insights_list.append(_ins_loc("no_specific_insights", lang_code, panel_name=_ins_loc("operational_resilience_title", lang_code)))
    return insights_list

# --- Spatial Dynamics Insights ---
def generate_spatial_dynamics_insights(df_spatial_filtered: pd.DataFrame, lang_code: str) -> List[str]:
    insights_list = []
    if not insights_list: insights_list.append(_ins_loc("no_specific_insights", lang_code, panel_name=_ins_loc("spatial_dynamics_title", lang_code)))
    return insights_list

# Add a generic no insights message to TEXT_STRINGS
# "no_specific_insights": "No specific insights for {panel_name} with current data.",