import streamlit as st
from data_loader import load_raw_data, load_standard_data, active_dataset_name
from style import kpi_icon_card, render_kpi_row, ICON_DATABASE, ICON_PEOPLE, ICON_GRID, ICON_DOLLAR

st.title("HR Intelligence System")
st.caption("Dataset-agnostic human resources analytics and automated data engineering pipeline.")

df_raw = load_raw_data()
df_cleaned = load_standard_data()

st.subheader("Data Pipeline Overview")
render_kpi_row([
    kpi_icon_card(ICON_DATABASE, "Raw Records", len(df_raw), delta=f"{len(df_cleaned)} Cleaned"),
    kpi_icon_card(ICON_PEOPLE, "Active Workforce", int(df_cleaned["is_active"].sum()),
                  delta=f"{int(df_cleaned['is_active'].mean()*100)}%"),
    kpi_icon_card(ICON_GRID, "Departments Tracked", df_cleaned["department"].nunique()),
    kpi_icon_card(ICON_DOLLAR, "Average Compensation", f"${df_cleaned['salary'].mean():,.0f}"),
])

st.divider()

st.subheader("System Navigation Modules")
st.markdown("""
Select a module from the sidebar to explore deep analytics:
- **Data Cleaning** — Before/after view of the automated cleaning pipeline and why each fix was needed.
- **Finance & Compensation** — Payroll structures, salary distributions, and executive benchmarking.
- **Performance & Engagement** — Productivity correlations, engagement scores, and talent evaluations.
- **Attendance & Reliability** — Absence tracking, lateness patterns, and risk identification.
- **Recruitment & Turnover** — Sourcing channel effectiveness, attrition analysis, and retention metrics.
""")

st.divider()

st.subheader("Recommended Actions")
st.caption("Generated dynamically from the data currently loaded — these change if the dataset or filters change, "
           "not fixed text. Meant as a starting point for where to look first, not a final verdict.")

recommendations = []

turnover_by_dept = (
    df_cleaned.groupby("department")["is_active"]
    .apply(lambda s: (~s).mean() * 100)
    .sort_values(ascending=False)
)
if len(turnover_by_dept) and turnover_by_dept.iloc[0] > 0:
    worst_dept, worst_rate = turnover_by_dept.index[0], turnover_by_dept.iloc[0]
    recommendations.append(
        f"**Prioritize retention efforts in {worst_dept}.** Turnover there is {worst_rate:.0f}% — "
        f"the highest of any department. Start with the Recruitment page's Top Termination Drivers "
        f"for that department specifically."
    )

if "termination_reason" in df_cleaned.columns:
    term_reasons = df_cleaned.loc[~df_cleaned["is_active"], "termination_reason"].dropna().value_counts()
    if len(term_reasons) and term_reasons.index[0] not in ("Unknown", "N/A - still employed"):
        recommendations.append(
            f"**Address '{term_reasons.index[0]}' directly.** It's the single most common reason "
            f"employees have left ({int(term_reasons.iloc[0])} case(s)) — worth a root-cause review "
            f"rather than a general retention push."
        )

if "salary" in df_cleaned.columns and len(turnover_by_dept):
    company_avg_salary = df_cleaned["salary"].mean()
    dept_salary = df_cleaned.groupby("department")["salary"].mean()
    underpaid_high_turnover = [
        d for d in turnover_by_dept.index[:3]
        if dept_salary.get(d, company_avg_salary) < company_avg_salary
    ]
    if underpaid_high_turnover:
        d = underpaid_high_turnover[0]
        recommendations.append(
            f"**Review compensation in {d}.** It's both paying below the company-wide average and "
            f"among the highest-turnover departments — a common signature of pay-driven exits, "
            f"and worth checking on the Finance page before assuming the cause is something else."
        )

if "engagement_score" in df_cleaned.columns:
    eng_by_dept = df_cleaned.groupby("department")["engagement_score"].mean().dropna().sort_values()
    if len(eng_by_dept):
        low_eng_dept, low_eng_val = eng_by_dept.index[0], eng_by_dept.iloc[0]
        recommendations.append(
            f"**Check in with {low_eng_dept}.** It has the lowest average engagement score "
            f"company-wide ({low_eng_val:.2f}/5.0) — low engagement here tends to precede turnover "
            f"elsewhere in this data, not just show up alongside it."
        )

recommendations.append(
    "**Work the Predictive Attrition page's watchlist first.** It ranks currently active employees "
    "by how closely their profile matches people who have already left, so retention conversations "
    "can be prioritized by risk instead of by department average."
)

for i, rec in enumerate(recommendations, 1):
    st.markdown(f"{i}. {rec}")

st.divider()
with st.expander("Data Source & Schema Mapping Inspection"):
    st.write(f"Active Source File: `{active_dataset_name()}` | Mapped via `schema_mapper.py` "
             "— upload a different HR file from the **Upload Data** page in the sidebar.")
    st.dataframe(df_cleaned.head(10), width='stretch')
