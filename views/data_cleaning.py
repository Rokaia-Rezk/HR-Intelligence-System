import streamlit as st
from data_loader import load_mapped_data, load_standard_data_with_audit
from style import (kpi_icon_card, render_kpi_row, render_quality_score, render_workflow_steps,
                    ICON_DATABASE, ICON_COPY, ICON_ALERT, ICON_DOLLAR, ICON_PEOPLE, ICON_CHECK)

st.title("Data Health & Automated Audit")
st.markdown("Schema mapping, dynamic validation, and rule-based cleaning — runs fresh on whatever dataset is currently loaded.")

df_before = load_mapped_data()
df_after, audit_log = load_standard_data_with_audit()

# ---- Data Quality Score --------------------------------------------------
# termination_date being empty means "still employed", not missing data —
# counting it as missing would make every healthy dataset look worse than
# it is, so it's excluded from both the score and the "true missing" KPI.
score_cols = [c for c in df_after.columns if c != "termination_date"]
total_cells = len(df_after) * len(score_cols)
true_missing_after = int(df_after[score_cols].isna().sum().sum())
dup_before = int(df_before.duplicated().sum())
completeness = 1 - (true_missing_after / total_cells) if total_cells else 1
quality_score = max(0, min(100, completeness * 100 - (dup_before / max(len(df_before), 1)) * 100))

render_quality_score(
    quality_score,
    subtitle=f"{total_cells - true_missing_after} of {total_cells} fields complete, "
              f"{dup_before} duplicate row(s) found — excludes termination_date, "
              f"since empty there means 'still employed', not missing."
)

st.subheader("Before Cleaning (raw, mapped to canonical fields)")
render_kpi_row([
    kpi_icon_card(ICON_DATABASE, "Records", len(df_before)),
    kpi_icon_card(ICON_ALERT, "Missing Cells (raw count)", int(df_before.isna().sum().sum())),
    kpi_icon_card(ICON_COPY, "Duplicate Rows", dup_before),
    kpi_icon_card(ICON_DOLLAR, "Average Compensation",
                  f"${df_before['salary'].mean():,.0f}" if df_before["salary"].notna().any() else "N/A"),
])
st.caption("'Missing Cells (raw count)' includes termination_date being empty for active employees — "
           "that's expected, not a data problem. See the Data Quality Score above for the corrected view.")

st.subheader("After Cleaning")
render_kpi_row([
    kpi_icon_card(ICON_DATABASE, "Records", len(df_after), delta=f"{len(df_after) - len(df_before)}"),
    kpi_icon_card(ICON_CHECK, "True Missing (excl. termination_date)", true_missing_after),
    kpi_icon_card(ICON_PEOPLE, "Active Workforce", int(df_after["is_active"].sum())),
    kpi_icon_card(ICON_DOLLAR, "Average Compensation", f"${df_after['salary'].mean():,.0f}"),
])

st.divider()

st.subheader("What was found, and what was done about it")
st.caption("Generated dynamically from this specific dataset — not fixed text. Swap the CSV and this list changes with it.")
render_workflow_steps(list(audit_log))

st.divider()

st.subheader("Cleaned data preview (canonical fields)")
st.dataframe(df_after.head(10), width='stretch')

st.success("Data is mapped, cleaned, and ready. Continue to the analytics pages from the sidebar.")
