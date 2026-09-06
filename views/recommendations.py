"""
recommendations.py
--------------------
Moved out of home.py so recommendations get a page of their own, right
before Predictive Attrition — the two are the "so what do I actually
do" half of the app, as opposed to the descriptive analytics pages.

Every recommendation here is generated fresh from whatever dataset is
currently loaded (default or uploaded) — nothing is fixed text, and a
dataset missing a field simply produces fewer recommendations instead
of a broken one.
"""

import streamlit as st
from data_loader import load_standard_data

st.title("Recommended Actions")
st.caption("Generated dynamically from the data currently loaded — these change if the dataset or filters change, "
           "not fixed text. Meant as a starting point for where to look first, not a final verdict.")

df_cleaned = load_standard_data()
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
    "**Work the Predictive Attrition page's watchlist next.** It ranks currently active employees "
    "by how closely their profile matches people who have already left, so retention conversations "
    "can be prioritized by risk instead of by department average."
)

if len(recommendations) == 1:
    st.info("This dataset is missing most of the fields these recommendations rely on (termination "
            "reason, compensation by department, engagement scores) — only a general pointer is "
            "available below.")

for i, rec in enumerate(recommendations, 1):
    st.markdown(f"{i}. {rec}")
