"""
finance.py
----------
Every chart on this page is click-to-filter, and selections combine
with AND: click a department, then a performance tier, then a status,
and the KPIs / Top Roster reflect all three at once.

How the cross-filtering works (no extra libraries — built on
st.plotly_chart's native on_select):
  - Each chart has its own widget `key`. Streamlit persists that
    widget's last selection in st.session_state[key] across reruns,
    so we can read every chart's current selection BEFORE any chart
    renders this run, then use those selections to cross-filter the
    data each OTHER chart is built from.
  - Category order on every chart is fixed (not re-sorted by value)
    so a bar's position — and therefore its click index — always maps
    to the same category, no matter how the other filters have
    narrowed the data.
  - "Salary by Performance Tier" is a bar of average salary (not a
    box plot) so it can be click-filtered the same way as the others;
    that's the one trade-off of making it interactive.
"""

import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
from data_loader import load_standard_data
from filters import department_status_filters, style_fig, get_click_index

st.title("Finance & Compensation Intelligence")
st.caption("Comprehensive payroll distribution, departmental cost structure, and executive compensation analysis.")

df_all = load_standard_data()

with st.expander("Filters", expanded=True):
    c1, c2, c3 = st.columns(3)
    df = department_status_filters(df_all, "finance", c1, c2)
    with c3:
        sal_min, sal_max = int(df_all["salary"].min()), int(df_all["salary"].max())
        sal_range = st.slider("Salary Range", sal_min, sal_max, (sal_min, sal_max), key="finance_salary")
    df = df[(df["salary"] >= sal_range[0]) & (df["salary"] <= sal_range[1])]

if df.empty:
    st.warning("No employees match the current filters.")
    st.stop()

# ---- Fixed category orders (computed once from the page-filtered data,
# BEFORE any chart-click selection) so a bar's index always means the
# same category across reruns, no matter what else is selected. -------
FIXED_DEPTS = sorted(df["department"].dropna().unique().tolist())
FIXED_PERF = sorted(df["performance_score"].dropna().unique().tolist())
FIXED_STATUS = [(True, "Active"), (False, "Terminated")]

n_bins = min(8, df["salary"].nunique())
bin_edges = np.linspace(df["salary"].min(), df["salary"].max(), n_bins + 1)
bin_labels = [f"${int(bin_edges[i]):,}\u2013${int(bin_edges[i+1]):,}" for i in range(n_bins)]
df["salary_bin"] = pd.cut(df["salary"], bins=bin_edges, labels=bin_labels, include_lowest=True)

CHART_KEYS = ["finance_dept_chart", "finance_bin_chart", "finance_perf_chart", "finance_status_chart"]


dept_idx = get_click_index("finance_dept_chart")
bin_idx = get_click_index("finance_bin_chart")
perf_idx = get_click_index("finance_perf_chart")
status_idx = get_click_index("finance_status_chart")

sel_dept = FIXED_DEPTS[dept_idx] if dept_idx is not None and dept_idx < len(FIXED_DEPTS) else None
sel_bin = bin_labels[bin_idx] if bin_idx is not None and bin_idx < len(bin_labels) else None
sel_perf = FIXED_PERF[perf_idx] if perf_idx is not None and perf_idx < len(FIXED_PERF) else None
sel_status = FIXED_STATUS[status_idx][0] if status_idx is not None and status_idx < 2 else None


def cross_filter(base_df, exclude=None):
    """Filter by every active click-selection except the one named in
    `exclude` — used to build each chart's OWN data (so it still shows
    all its categories) while every other chart is filtered by it."""
    d = base_df
    if sel_dept is not None and exclude != "dept":
        d = d[d["department"] == sel_dept]
    if sel_bin is not None and exclude != "bin":
        d = d[d["salary_bin"] == sel_bin]
    if sel_perf is not None and exclude != "perf":
        d = d[d["performance_score"] == sel_perf]
    if sel_status is not None and exclude != "status":
        d = d[d["is_active"] == sel_status]
    return d


df_view = cross_filter(df)  # every selection applied — used for KPIs / roster

active_selections = []
if sel_dept: active_selections.append(f"Department = **{sel_dept}**")
if sel_bin: active_selections.append(f"Salary range = **{sel_bin}**")
if sel_perf: active_selections.append(f"Performance = **{sel_perf}**")
if sel_status is not None: active_selections.append(f"Status = **{'Active' if sel_status else 'Terminated'}**")

if active_selections:
    sc1, sc2 = st.columns([5, 1])
    with sc1:
        st.info("Filtered by " + ", ".join(active_selections) +
                " — click a selected bar again, or use Clear, to remove it.")
    with sc2:
        if st.button("Clear all selections"):
            for k in CHART_KEYS:
                st.session_state.pop(k, None)
            st.rerun()

c1, c2, c3 = st.columns(3)
c1.metric("Total Payroll (filtered)", f"${df_view['salary'].sum():,.0f}")
c2.metric("Mean Compensation", f"${df_view['salary'].mean():,.0f}" if len(df_view) else "N/A")
c3.metric("Median Compensation", f"${df_view['salary'].median():,.0f}" if len(df_view) else "N/A")

st.divider()

col1, col2 = st.columns(2)
with col1:
    st.subheader("Average Compensation by Department")
    st.caption("Click a bar to filter every other chart on this page by that department.")
    dept_data = cross_filter(df, exclude="dept")
    dept_agg = dept_data.groupby("department")["salary"].mean().reindex(FIXED_DEPTS).reset_index()
    fig = px.bar(dept_agg, x="department", y="salary", color_discrete_sequence=["#9575CD"])
    fig.update_yaxes(tickprefix="$", tickformat=",.0f")
    st.plotly_chart(style_fig(fig), use_container_width=True, theme=None,
                     on_select="rerun", selection_mode="points", key="finance_dept_chart")
    top_dept = dept_agg.dropna().sort_values("salary", ascending=False).iloc[0] if dept_agg["salary"].notna().any() else None
    if top_dept is not None:
        st.caption(f"**{top_dept['department']}** pays the highest average (${top_dept['salary']:,.0f}) "
                   f"among what's currently shown.")

with col2:
    st.subheader("Compensation Distribution")
    st.caption("Click a salary band to filter every other chart on this page by that range.")
    bin_data = cross_filter(df, exclude="bin")
    bin_agg = bin_data["salary_bin"].value_counts().reindex(bin_labels).fillna(0).reset_index()
    bin_agg.columns = ["salary_bin", "count"]
    fig2 = px.bar(bin_agg, x="salary_bin", y="count", color_discrete_sequence=["#7C5CBF"])
    fig2.update_layout(xaxis_title="Salary Range", yaxis_title="Employees")
    st.plotly_chart(style_fig(fig2), use_container_width=True, theme=None,
                     on_select="rerun", selection_mode="points", key="finance_bin_chart")
    if bin_agg["count"].sum() > 0:
        top_bin = bin_agg.sort_values("count", ascending=False).iloc[0]
        st.caption(f"Most employees currently shown fall in **{top_bin['salary_bin']}** "
                   f"({int(top_bin['count'])} of {int(bin_agg['count'].sum())}).")

st.subheader("Top Compensation Roster")
top_paid = df_view.sort_values("salary", ascending=False)[
    ["employee_name", "department", "position", "salary"]
].head(10)
st.dataframe(top_paid, use_container_width=True)

st.divider()
st.subheader("Compensation vs. Retention")
st.caption("Not just how much people are paid — whether pay level relates to who actually stays.")

col3, col4 = st.columns(2)
with col3:
    st.markdown("**Average Salary by Performance Tier**")
    st.caption("Click a bar to filter every other chart on this page by that tier.")
    perf_data = cross_filter(df, exclude="perf")
    if perf_data["performance_score"].notna().any():
        perf_agg = perf_data.groupby("performance_score")["salary"].mean().reindex(FIXED_PERF).reset_index()
        fig3 = px.bar(perf_agg, x="performance_score", y="salary", color_discrete_sequence=["#5B3E96"])
        fig3.update_yaxes(tickprefix="$", tickformat=",.0f")
        st.plotly_chart(style_fig(fig3), use_container_width=True, theme=None,
                         on_select="rerun", selection_mode="points", key="finance_perf_chart")
        if perf_agg["salary"].notna().any():
            top_tier = perf_agg.dropna().sort_values("salary", ascending=False).iloc[0]
            st.caption(f"**{top_tier['performance_score']}** performers have the highest average salary "
                       f"(${top_tier['salary']:,.0f}) among what's currently shown.")
    else:
        st.info("No performance score data available for this filter.")

with col4:
    st.markdown("**Salary: Active vs. Terminated**")
    st.caption("Click a bar to filter every other chart on this page by that status.")
    status_data = cross_filter(df, exclude="status")
    status_agg = status_data.groupby("is_active")["salary"].mean()
    status_labels = [label for _, label in FIXED_STATUS]
    status_values = [status_agg.get(val, np.nan) for val, _ in FIXED_STATUS]
    fig4 = px.bar(x=status_labels, y=status_values, color_discrete_sequence=["#B39DDB", "#5B3E96"])
    fig4.update_yaxes(tickprefix="$", tickformat=",.0f")
    fig4.update_layout(xaxis_title="", yaxis_title="Average Salary")
    st.plotly_chart(style_fig(fig4), use_container_width=True, theme=None,
                     on_select="rerun", selection_mode="points", key="finance_status_chart")
    if pd.notna(status_agg.get(True, np.nan)) and pd.notna(status_agg.get(False, np.nan)):
        gap = status_agg[True] - status_agg[False]
        direction = "more" if gap > 0 else "less"
        st.caption(f"Active employees earn on average **${abs(gap):,.0f} {direction}** than employees who left "
                   f"among what's currently shown.")
