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

FIXED_DEPTS = sorted(df["department"].dropna().unique().tolist())
FIXED_PERF = sorted(df["performance_score"].dropna().unique().tolist())
FIXED_STATUS = [(True, "Active"), (False, "Terminated")]

n_bins = min(8, df["salary"].nunique())
bin_edges = np.linspace(df["salary"].min(), df["salary"].max(), n_bins + 1)
bin_labels = [f"${int(bin_edges[i]/1000)}K\u2013${int(bin_edges[i+1]/1000)}K" for i in range(n_bins)]
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

df_view = cross_filter(df)

active_selections = []
if sel_dept: active_selections.append(f"Department = **{sel_dept}**")
if sel_bin: active_selections.append(f"Salary range = **{sel_bin}**")
if sel_perf: active_selections.append(f"Performance = **{sel_perf}**")
if sel_status is not None: active_selections.append(f"Status = **{'Active' if sel_status else 'Terminated'}**")

if active_selections:
    sc1, sc2 = st.columns([5, 1])
    with sc1:
        st.info("Filtered by " + ", ".join(active_selections) + " — click a selected bar again, or use Clear, to remove it.")
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
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 5px;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#7C5CBF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="12" y1="1" x2="12" y2="23"></line>
                <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
            </svg>
            <h3 style="margin: 0; font-family: 'Playfair Display', serif; color: #2A1F4D; font-size: 1.25rem;">Average Compensation by Department</h3>
        </div>
    """, unsafe_allow_html=True)
    st.caption("Click a bar to filter every other chart on this page by that department.")
    
    dept_data = cross_filter(df, exclude="dept")
    dept_agg = dept_data.groupby("department")["salary"].mean().reindex(FIXED_DEPTS).reset_index()
    fig = px.bar(dept_agg, x="department", y="salary", color_discrete_sequence=["#9575CD"])
    fig.update_yaxes(tickprefix="$", tickformat=",.0f")
    fig = style_fig(fig)
    fig.update_layout(
        margin=dict(l=50, r=20, t=30, b=50),
        xaxis=dict(automargin=True, tickangle=-25),
        yaxis=dict(automargin=True)
    )
    st.plotly_chart(fig, width='stretch', theme=None,
                     on_select="rerun", selection_mode="points", key="finance_dept_chart")
    top_dept = dept_agg.dropna().sort_values("salary", ascending=False).iloc[0] if dept_agg["salary"].notna().any() else None
    if top_dept is not None:
        st.caption(f"**{top_dept['department']}** pays the highest average (${top_dept['salary']:,.0f}) among what's currently shown.")

with col2:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 5px;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#7C5CBF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect>
                <line x1="8" y1="21" x2="16" y2="21"></line>
                <line x1="12" y1="17" x2="12" y2="21"></line>
            </svg>
            <h3 style="margin: 0; font-family: 'Playfair Display', serif; color: #2A1F4D; font-size: 1.25rem;">Compensation Distribution</h3>
        </div>
    """, unsafe_allow_html=True)
    st.caption("Click a salary band to filter every other chart.")
    
    bin_data = cross_filter(df, exclude="bin")
    bin_agg = bin_data["salary_bin"].value_counts().reindex(bin_labels).fillna(0).reset_index()
    bin_agg.columns = ["salary_bin", "count"]
    fig2 = px.bar(bin_agg, x="salary_bin", y="count", color_discrete_sequence=["#7C5CBF"])
    fig2.update_layout(
        xaxis_title="Salary Range", yaxis_title="Employees",
        margin=dict(l=40, r=20, t=30, b=40),
        xaxis=dict(automargin=True, tickangle=-20),
        yaxis=dict(automargin=True)
    )
    fig2 = style_fig(fig2)
    st.plotly_chart(fig2, width='stretch', theme=None,
                     on_select="rerun", selection_mode="points", key="finance_bin_chart")
    if bin_agg["count"].sum() > 0:
        top_bin = bin_agg.sort_values("count", ascending=False).iloc[0]
        st.caption(f"Most employees currently shown fall in **{top_bin['salary_bin']}**.")

st.subheader("Top Compensation Roster")
top_paid = df_view.sort_values("salary", ascending=False)[
    ["employee_name", "department", "position", "salary"]
].head(10)
st.dataframe(top_paid, width='stretch')

st.divider()
st.subheader("Compensation vs. Retention")

col3, col4 = st.columns(2)
with col3:
    st.markdown("**Average Salary by Performance Tier**")
    perf_data = cross_filter(df, exclude="perf")
    if perf_data["performance_score"].notna().any():
        perf_agg = perf_data.groupby("performance_score")["salary"].mean().reindex(FIXED_PERF).reset_index()
        fig3 = px.bar(perf_agg, x="performance_score", y="salary", color_discrete_sequence=["#5B3E96"])
        fig3.update_yaxes(tickprefix="$", tickformat=",.0f")
        fig3 = style_fig(fig3)
        fig3.update_layout(
            margin=dict(l=50, r=20, t=30, b=40),
            xaxis=dict(automargin=True, tickangle=-20),
            yaxis=dict(automargin=True)
        )
        st.plotly_chart(fig3, width='stretch', theme=None,
                         on_select="rerun", selection_mode="points", key="finance_perf_chart")
        if perf_agg["salary"].notna().any():
            top_tier = perf_agg.dropna().sort_values("salary", ascending=False).iloc[0]
            st.caption(f"**{top_tier['performance_score']}** performers have the highest average salary.")
    else:
        st.info("No performance score data available for this filter.")

with col4:
    st.markdown("**Salary: Active vs. Terminated**")
    status_data = cross_filter(df, exclude="status")
    status_agg = status_data.groupby("is_active")["salary"].mean()
    status_labels = [label for _, label in FIXED_STATUS]
    status_values = [status_agg.get(val, np.nan) for val, _ in FIXED_STATUS]
    fig4 = px.bar(x=status_labels, y=status_values, color_discrete_sequence=["#B39DDB", "#5B3E96"])
    fig4.update_yaxes(tickprefix="$", tickformat=",.0f")
    fig4 = style_fig(fig4)
    fig4.update_layout(
        margin=dict(l=50, r=20, t=30, b=40),
        xaxis_title="", yaxis_title="Average Salary",
        xaxis=dict(automargin=True),
        yaxis=dict(automargin=True)
    )
    st.plotly_chart(fig4, width='stretch', theme=None,
                     on_select="rerun", selection_mode="points", key="finance_status_chart")
    if pd.notna(status_agg.get(True, np.nan)) and pd.notna(status_agg.get(False, np.nan)):
        gap = status_agg[True] - status_agg[False]
        direction = "more" if gap > 0 else "less"
        st.caption(f"Active employees earn on average **${abs(gap):,.0f} {direction}** than employees who left.")