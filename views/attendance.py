"""
attendance.py
--------------
Click-to-filter: "Average Absences by Department" is clickable. Click
a department and every other chart/table on this page — the absence
distribution, the watchlist, and the active-vs-terminated comparisons
— narrows to it. Same session_state approach as finance.py; see
get_click_index() in filters.py.
"""
 
import streamlit as st
import plotly.express as px
from data_loader import load_standard_data
from filters import department_status_filters, style_fig, get_click_index
 
st.title("Attendance & Operational Reliability")
st.caption("Absence analysis, tardiness tracking, and identification of critical attendance risk factors.")
 
df_all = load_standard_data()
 
with st.expander("Filters", expanded=True):
    c1, c2, c3 = st.columns(3)
    df = department_status_filters(df_all, "att", c1, c2)
    with c3:
        abs_min, abs_max = int(df_all["absences"].min()), int(df_all["absences"].max())
        abs_range = st.slider("Absences Range", abs_min, abs_max, (abs_min, abs_max), key="att_absences")
    df = df[(df["absences"] >= abs_range[0]) & (df["absences"] <= abs_range[1])]
 
if df.empty:
    st.warning("No employees match the current filters.")
    st.stop()
 
# dept_abs is built from `df` only — never from the click-filtered view —
# so its department order stays stable across reruns and a click's
# point_index always maps back to the right department.
dept_abs = df.groupby("department")["absences"].mean().sort_values(ascending=False).reset_index()
 
click_idx = get_click_index("att_dept_chart")
sel_dept = dept_abs.iloc[click_idx]["department"] if click_idx is not None and click_idx < len(dept_abs) else None
df_view = df[df["department"] == sel_dept] if sel_dept else df
 
if sel_dept:
    sc1, sc2 = st.columns([5, 1])
    with sc1:
        st.info(f"Everything below is filtered to **{sel_dept}** — click the same bar again, "
                f"or use Clear, to see all departments.")
    with sc2:
        if st.button("Clear selection", key="att_clear"):
            st.session_state.pop("att_dept_chart", None)
            st.rerun()
 
c1, c2, c3 = st.columns(3)
c1.metric("Mean Absence Days", f"{df_view['absences'].mean():.1f}" if len(df_view) else "N/A")
c2.metric("Mean Lateness (30 Days)", f"{df_view['days_late'].mean():.1f}" if len(df_view) else "N/A")
c3.metric("Perfect Attendance", int((df_view["absences"] == 0).sum()) if len(df_view) else 0)
 
st.divider()
 
col1, col2 = st.columns(2)
with col1:
    st.subheader("Average Absences by Department")
    st.caption("Click a bar to filter everything else on this page by that department.")
    fig = px.bar(dept_abs, x="department", y="absences", color_discrete_sequence=["#B39DDB"])
    st.plotly_chart(style_fig(fig), use_container_width=True, theme=None,
                     on_select="rerun", selection_mode="points", key="att_dept_chart")
    worst = dept_abs.iloc[0]
    st.caption(f"**{worst['department']}** has the highest average absences ({worst['absences']:.1f} days) — "
               f"worth a closer look if it's paired with high turnover in that department too.")
 
with col2:
    st.subheader("Absence Frequency Distribution")
    fig2 = px.histogram(df_view, x="absences", nbins=20, color_discrete_sequence=["#7C5CBF"])
    st.plotly_chart(style_fig(fig2), use_container_width=True, theme=None)
    if len(df_view):
        high_risk = int((df_view["absences"] >= df_view["absences"].quantile(0.9)).sum())
        st.caption(f"{high_risk} employee(s) fall in the top 10% for absences — the watchlist below is exactly this group.")
 
st.subheader("High Absence Risk Watchlist")
watch = df_view.sort_values("absences", ascending=False)[
    ["employee_name", "department", "absences", "days_late", "employment_status"]
].head(10)
st.dataframe(watch, use_container_width=True)
 
st.divider()
st.subheader("Attendance as an Early Warning Signal")
st.caption("Whether attendance problems actually line up with who ends up leaving — "
           "turns raw absence numbers into a retention signal, not just a record.")
 
col3, col4 = st.columns(2)
with col3:
    st.markdown("**Absences: Active vs. Terminated**")
    abs_by_status = df_view.groupby("is_active")["absences"].mean()
    fig3 = px.bar(x=abs_by_status.index.map({True: "Active", False: "Terminated"}),
                  y=abs_by_status.values, color_discrete_sequence=["#B39DDB", "#5B3E96"])
    fig3.update_layout(xaxis_title="", yaxis_title="Average Absences")
    st.plotly_chart(style_fig(fig3), use_container_width=True, theme=None)
 
with col4:
    st.markdown("**Lateness: Active vs. Terminated**")
    late_by_status = df_view.groupby("is_active")["days_late"].mean()
    fig4 = px.bar(x=late_by_status.index.map({True: "Active", False: "Terminated"}),
                  y=late_by_status.values, color_discrete_sequence=["#B39DDB", "#5B3E96"])
    fig4.update_layout(xaxis_title="", yaxis_title="Average Days Late")
    st.plotly_chart(style_fig(fig4), use_container_width=True, theme=None)
 
if True in abs_by_status.index and False in abs_by_status.index:
    gap = abs_by_status[False] - abs_by_status[True]
    if gap > 0:
        st.caption(f"Employees who left averaged **{gap:.1f} more absence days** than those who stayed "
                   f"among what's currently shown — a useful (if partial) early-warning signal for turnover.")
    else:
        st.caption("Absences don't show a clear gap between active and terminated employees among what's "
                   "currently shown — worth combining with other factors (see the Predictive Attrition page) "
                   "rather than relying on absences alone.")