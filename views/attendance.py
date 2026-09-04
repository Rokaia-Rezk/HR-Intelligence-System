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
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 5px;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#7C5CBF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                <line x1="16" y1="2" x2="16" y2="6"></line>
                <line x1="8" y1="2" x2="8" y2="6"></line>
                <line x1="3" y1="10" x2="21" y2="10"></line>
            </svg>
            <h3 style="margin: 0; font-family: 'Playfair Display', serif; color: #2A1F4D; font-size: 1.25rem;">Average Absences by Department</h3>
        </div>
    """, unsafe_allow_html=True)
    st.caption("Click a bar to filter everything else on this page by that department.")
    
    fig = px.bar(dept_abs, x="department", y="absences", color_discrete_sequence=["#B39DDB"])
    fig = style_fig(fig)
    fig.update_layout(
        margin=dict(l=40, r=20, t=30, b=50),
        xaxis=dict(automargin=True, tickangle=-25),
        yaxis=dict(automargin=True)
    )
    st.plotly_chart(fig, width='stretch', theme=None,
                     on_select="rerun", selection_mode="points", key="att_dept_chart")
    worst = dept_abs.iloc[0]
    st.caption(f"**{worst['department']}** has the highest average absences ({worst['absences']:.1f} days) — "
               f"worth a closer look if it's paired with high turnover in that department too.")

with col2:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 5px;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#7C5CBF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21.21 15.89A10 10 0 1 1 8 2.83"></path>
                <path d="M22 12A10 10 0 0 0 12 2v10z"></path>
            </svg>
            <h3 style="margin: 0; font-family: 'Playfair Display', serif; color: #2A1F4D; font-size: 1.25rem;">Absence Frequency Distribution</h3>
        </div>
    """, unsafe_allow_html=True)
    st.caption("Distribution spread across personnel.")
    
    fig2 = px.histogram(df_view, x="absences", nbins=20, color_discrete_sequence=["#7C5CBF"])
    fig2 = style_fig(fig2)
    fig2.update_layout(
        margin=dict(l=40, r=20, t=30, b=40),
        xaxis=dict(automargin=True),
        yaxis=dict(automargin=True)
    )
    st.plotly_chart(fig2, width='stretch', theme=None)
    if len(df_view):
        high_risk = int((df_view["absences"] >= df_view["absences"].quantile(0.9)).sum())
        st.caption(f"{high_risk} employee(s) fall in the top 10% for absences — the watchlist below is exactly this group.")

st.subheader("High Absence Risk Watchlist")
watch = df_view.sort_values("absences", ascending=False)[
    ["employee_name", "department", "absences", "days_late", "employment_status"]
].head(10)
st.dataframe(watch, width='stretch')

st.divider()
st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 5px;">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#7C5CBF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
            <line x1="12" y1="9" x2="12" y2="13"></line>
            <line x1="12" y1="17" x2="12.01" y2="17"></line>
        </svg>
        <h3 style="margin: 0; font-family: 'Playfair Display', serif; color: #2A1F4D; font-size: 1.25rem;">Attendance as an Early Warning Signal</h3>
    </div>
""", unsafe_allow_html=True)
st.caption("Whether attendance problems actually line up with who ends up leaving.")

col3, col4 = st.columns(2)
with col3:
    st.markdown("**Absences: Active vs. Terminated**")
    abs_by_status = df_view.groupby("is_active")["absences"].mean()
    fig3 = px.bar(x=abs_by_status.index.map({True: "Active", False: "Terminated"}),
                  y=abs_by_status.values, color_discrete_sequence=["#B39DDB", "#5B3E96"])
    fig3 = style_fig(fig3)
    fig3.update_layout(
        margin=dict(l=40, r=20, t=30, b=40),
        xaxis_title="", yaxis_title="Average Absences",
        xaxis=dict(automargin=True),
        yaxis=dict(automargin=True)
    )
    st.plotly_chart(fig3, width='stretch', theme=None)

with col4:
    st.markdown("**Lateness: Active vs. Terminated**")
    late_by_status = df_view.groupby("is_active")["days_late"].mean()
    fig4 = px.bar(x=late_by_status.index.map({True: "Active", False: "Terminated"}),
                  y=late_by_status.values, color_discrete_sequence=["#B39DDB", "#5B3E96"])
    fig4 = style_fig(fig4)
    fig4.update_layout(
        margin=dict(l=40, r=20, t=30, b=40),
        xaxis_title="", yaxis_title="Average Days Late",
        xaxis=dict(automargin=True),
        yaxis=dict(automargin=True)
    )
    st.plotly_chart(fig4, width='stretch', theme=None)

if True in abs_by_status.index and False in abs_by_status.index:
    gap = abs_by_status[False] - abs_by_status[True]
    if gap > 0:
        st.caption(f"Employees who left averaged **{gap:.1f} more absence days** than those who stayed "
                   f"among what's currently shown — a useful early-warning signal for turnover.")
    else:
        st.caption("Absences don't show a clear gap between active and terminated employees among what's "
                   "currently shown.")