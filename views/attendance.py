"""
attendance.py
--------------
Click-to-filter: "Average Absences by Department" is clickable (when
absences data exists — see below). Click a department and every other
chart/table on this page narrows to it. Same session_state approach
as finance.py; see get_click_index() in filters.py.

absences and days_late are handled INDEPENDENTLY throughout — app.py
only shows this page at all when at least one of them has real data,
but that doesn't guarantee both do. Every section below checks
HAS_ABSENCES / HAS_LATE itself rather than assuming both are present,
so a dataset with only one of the two still gets a working page
instead of a crash or an empty-looking chart.
"""

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from data_loader import load_standard_data, field_has_data
from filters import department_status_filters, style_fig, get_click_index

st.title("Attendance & Operational Reliability")
st.caption("Absence analysis, tardiness tracking, and identification of critical attendance risk factors.")

df_all = load_standard_data()
HAS_ABSENCES = field_has_data("absences")
HAS_LATE = field_has_data("days_late")

with st.expander("Filters", expanded=True):
    c1, c2, c3 = st.columns(3)
    df = department_status_filters(df_all, "att", c1, c2)
    if HAS_ABSENCES:
        with c3:
            abs_min = int(df_all["absences"].min())
            abs_max = int(df_all["absences"].max())
            abs_range = st.slider("Absences Range", abs_min, abs_max, (abs_min, abs_max), key="att_absences")
        df = df[(df["absences"] >= abs_range[0]) & (df["absences"] <= abs_range[1])]

if df.empty:
    st.warning("No employees match the current filters.")
    st.stop()

if HAS_ABSENCES:
    # dept_abs is built from `df` only — never from the click-filtered view —
    # so its department order stays stable across reruns and a click's
    # point_index always maps back to the right department.
    dept_abs = df.groupby("department")["absences"].mean().sort_values(ascending=False).reset_index()
    click_idx = get_click_index("att_dept_chart")
    sel_dept = dept_abs.iloc[click_idx]["department"] if click_idx is not None and click_idx < len(dept_abs) else None
else:
    dept_abs, sel_dept = None, None

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
c1.metric("Mean Absence Days", f"{df_view['absences'].mean():.1f}" if HAS_ABSENCES and len(df_view) else "N/A")
c2.metric("Mean Lateness (30 Days)", f"{df_view['days_late'].mean():.1f}" if HAS_LATE and len(df_view) else "N/A")
c3.metric("Perfect Attendance", int((df_view["absences"] == 0).sum()) if HAS_ABSENCES and len(df_view) else "N/A")

st.divider()

if HAS_ABSENCES:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Average Absences by Department")
        st.caption("Click a bar to filter everything else on this page by that department.")
        fig = px.bar(dept_abs, x="department", y="absences", color_discrete_sequence=["#B39DDB"])
        fig = style_fig(fig)
        fig.update_xaxes(tickangle=-25)
        st.plotly_chart(fig, width='stretch', theme=None,
                         on_select="rerun", selection_mode="points", key="att_dept_chart")
        worst = dept_abs.iloc[0]
        st.caption(f"**{worst['department']}** has the highest average absences ({worst['absences']:.1f} days) — "
                   f"worth a closer look if it's paired with high turnover in that department too.")

    with col2:
        st.subheader("Absence Frequency Distribution")
        fig2 = px.histogram(df_view, x="absences", nbins=20, color_discrete_sequence=["#7C5CBF"])
        st.plotly_chart(style_fig(fig2), width='stretch', theme=None)
        if len(df_view):
            high_risk = int((df_view["absences"] >= df_view["absences"].quantile(0.9)).sum())
            st.caption(f"{high_risk} employee(s) fall in the top 10% for absences — the watchlist below is exactly this group.")

    st.subheader("High Absence Risk Watchlist")
    watch_cols = ["employee_name", "department", "absences", "employment_status"]
    if HAS_LATE:
        watch_cols.insert(3, "days_late")
    watch = df_view.sort_values("absences", ascending=False)[watch_cols].head(10)
    st.dataframe(watch, width='stretch')
else:
    st.info("This dataset has no absence data, so department/frequency breakdowns and the "
            "risk watchlist aren't available — only lateness is shown below.")

if HAS_ABSENCES or HAS_LATE:
    st.divider()
    st.subheader("Attendance as an Early Warning Signal")
    st.caption("Whether attendance problems actually line up with who ends up leaving — "
               "turns raw absence numbers into a retention signal, not just a record.")

    # One combined chart (not two separate ones) when both exist — absences
    # and lateness use a secondary y-axis since their scales are very
    # different (days vs. tenths of a day). If only one of the two exists,
    # it gets its own single-axis bar instead.
    status_labels = ["Active", "Terminated"]
    fig_combo = go.Figure()

    if HAS_ABSENCES:
        abs_by_status = df_view.groupby("is_active")["absences"].mean()
        abs_vals = [abs_by_status.get(True, float("nan")), abs_by_status.get(False, float("nan"))]
        fig_combo.add_trace(go.Bar(name="Avg Absences", x=status_labels, y=abs_vals,
                                    marker_color="#B39DDB", yaxis="y1"))
    if HAS_LATE:
        late_by_status = df_view.groupby("is_active")["days_late"].mean()
        late_vals = [late_by_status.get(True, float("nan")), late_by_status.get(False, float("nan"))]
        fig_combo.add_trace(go.Bar(name="Avg Days Late", x=status_labels, y=late_vals,
                                    marker_color="#5B3E96", yaxis="y2" if HAS_ABSENCES else "y1"))

    fig_combo = style_fig(fig_combo)
    layout_kwargs = {"barmode": "group"}
    if HAS_ABSENCES:
        layout_kwargs["yaxis"] = dict(title="Average Absences")
        if HAS_LATE:
            layout_kwargs["yaxis2"] = dict(title="Average Days Late", overlaying="y", side="right")
    else:
        layout_kwargs["yaxis"] = dict(title="Average Days Late")
    fig_combo.update_layout(**layout_kwargs)
    st.plotly_chart(fig_combo, width='stretch', theme=None)

    gap_notes = []
    if HAS_ABSENCES and True in abs_by_status.index and False in abs_by_status.index:
        gap_notes.append(("absence", abs_by_status[False] - abs_by_status[True]))
    if HAS_LATE and True in late_by_status.index and False in late_by_status.index:
        gap_notes.append(("late", late_by_status[False] - late_by_status[True]))

    if gap_notes:
        parts = [f"**{gap:+.1f} {label} days**" for label, gap in gap_notes]
        if any(gap > 0 for _, gap in gap_notes):
            st.caption(
                f"Employees who left averaged {' and '.join(parts)} compared to those who stayed, "
                f"among what's currently shown. Combine this with other factors (see the Predictive "
                f"Attrition page) rather than relying on it by itself."
            )
        else:
            st.caption("No meaningful gap between active and terminated employees among what's "
                       "currently shown — worth combining with other factors (see the Predictive "
                       "Attrition page) rather than relying on attendance alone.")
