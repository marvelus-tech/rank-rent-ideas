from __future__ import annotations

from datetime import date, timedelta


def init_pipeline_fields(leads_df):
    if "pipeline_stage" not in leads_df.columns:
        leads_df["pipeline_stage"] = "cold"
    if "initial_contact_date" not in leads_df.columns:
        leads_df["initial_contact_date"] = ""
    if "contact_method" not in leads_df.columns:
        leads_df["contact_method"] = ""
    if "followup_due_date" not in leads_df.columns:
        leads_df["followup_due_date"] = ""
    if "response_status" not in leads_df.columns:
        leads_df["response_status"] = "no_response"
    if "last_interaction" not in leads_df.columns:
        leads_df["last_interaction"] = ""
    if "notes" not in leads_df.columns:
        leads_df["notes"] = ""
    return leads_df


def mark_contacted(leads_df, place_id: str, method: str, followup_days: int):
    idx = leads_df[leads_df["place_id"] == place_id].index
    if len(idx) == 0:
        return leads_df

    i = idx[0]
    today = date.today().isoformat()
    due = (date.today() + timedelta(days=followup_days)).isoformat()

    leads_df.at[i, "pipeline_stage"] = "contacted"
    leads_df.at[i, "initial_contact_date"] = today
    leads_df.at[i, "contact_method"] = method
    leads_df.at[i, "followup_due_date"] = due
    leads_df.at[i, "last_interaction"] = today
    return leads_df


def due_followups(leads_df):
    today = date.today().isoformat()
    return leads_df[
        (leads_df["pipeline_stage"].isin(["contacted", "interested", "proposal"]))
        & (leads_df["followup_due_date"].astype(str) <= today)
    ]
