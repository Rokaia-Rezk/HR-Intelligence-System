"""
performance.py
---------------
Click-to-filter: "Performance Score Breakdown" is clickable. Click a
tier (or a slice) and every other chart on this page — the engagement
scatter, the special-projects comparison, and the department
breakdown — narrows to that tier. Uses the same session_state-based
approach as finance.py; see get_click_index() in filters.py.
"""

import streamlit as st
import plotly.express as px
from data_loader import load_standard_data
from filters import department_status_filters, style_fig, style_slices, DISTINCT_PALETTE, get_click_index

st.title("Performance & Employee Engagement")
st.caption("Cross-evaluation of performance ratings, job satisfaction indexes, and special project contributions.")

df_all = load_standard_data()

with st.expander("Filters", expanded=True):
    c1, c2, c3 = st.columns(3)
    df = department_status_filters(df_all, "perf", c1, c2)
    with c3:
        tiers = sorted(df_all["performance_score"].dropna().unique().tolist())
        selected_tiers = st.multiselect("Performance Score", tiers, default=tiers, key="perf_tier")
    df = df[df["performance_score"].isin(selected_tiers)] if selected_tiers else df.iloc[0:0]

if df.empty:
    st.warning("No employees match the current filters.")
    st.stop()

FIXED_PERF = sorted(df["performance_score"].dropna().unique().tolist())
perf_counts = df["performance_score"].value_counts().reset_index()
perf_counts.columns = ["performance_score", "count"]

click_idx = get_click_index("perf_score_chart")
sel_tier = FIXED_PERF[click_idx] if click_idx is not None and click_idx < len(FIXED_PERF) else None
df_view = df[df["performance_score"] == sel_tier] if sel_tier else df

if sel_tier:
    sc1, sc2 = st.columns([5, 1])
    with sc1:
        st.info(f"Everything below is filtered to **{sel_tier}** — click the same bar again, "
                f"or use Clear, to see all tiers.")
    with sc2:
        if st.button("Clear selection", key="perf_clear"):
            st.session_state.pop("perf_score_chart", None)
            st.rerun()

c1, c2, c3 = st.columns(3)
c1.metric("Average Engagement", f"{df_view['engagement_score'].mean():.2f} / 5.0" if len(df_view) else "N/A")
c2.metric("Average Satisfaction", f"{df_view['satisfaction_score'].mean():.2f} / 5.0" if len(df_view) else "N/A")
c3.metric("Avg Special Projects", f"{df_view['special_projects_count'].mean():.1f}" if len(df_view) else "N/A")

st.divider()

col1, col2 = st.columns(2)
with col1:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 5px;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#7C5CBF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M18 20V10"></path>
                <path d="M12 20V4"></path>
                <path d="M6 20v-6"></path>
            </svg>
            <h3 style="margin: 0; font-family: 'Playfair Display', serif; color: #2A1F4D; font-size: 1.25rem;">Performance Score Breakdown</h3>
        </div>
    """, unsafe_allow_html=True)
    st.caption("Click a bar to filter every other chart on this page by that tier.")
    
    perf_counts_fixed = perf_counts.set_index("performance_score").reindex(FIXED_PERF).fillna(0).reset_index()
    fig = px.bar(perf_counts_fixed, x="performance_score", y="count", color_discrete_sequence=["#9575CD"])
    fig = style_fig(fig)
    fig.update_layout(
        margin=dict(l=40, r=20, t=30, b=40),
        xaxis=dict(automargin=True, tickangle=-20),
        yaxis=dict(automargin=True)
    )
    st.plotly_chart(fig, width='stretch', theme=None,
                     on_select="rerun", selection_mode="points", key="perf_score_chart")
    top_tier = perf_counts.sort_values("count", ascending=False).iloc[0]
    st.caption(
        f"**{top_tier['performance_score']}** is the largest group "
        f"({top_tier['count']} of {len(df)} employees, {top_tier['count']/len(df):.0%})."
    )

with col2:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 5px;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#7C5CBF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <path d="M12 8v4l3 3"></path>
            </svg>
            <h3 style="margin: 0; font-family: 'Playfair Display', serif; color: #2A1F4D; font-size: 1.25rem;">Engagement vs Satisfaction</h3>
        </div>
    """, unsafe_allow_html=True)
    st.caption("Correlation and distribution.")
    
    fig2 = px.scatter(df_view, x="engagement_score", y="satisfaction_score",
                       color="department", hover_data=["employee_name"],
                       color_discrete_sequence=px.colors.qualitative.Set2)
    fig2.update_traces(marker=dict(size=8, opacity=0.75, line=dict(width=0.5, color="#FFFFFF")))
    fig2 = style_fig(fig2)
    fig2.update_layout(
        margin=dict(l=40, r=20, t=30, b=40),
        xaxis=dict(automargin=True),
        yaxis=dict(automargin=True)
    )
    st.plotly_chart(fig2, width='stretch', theme=None)
    if len(df_view) > 1:
        corr = df_view["engagement_score"].corr(df_view["satisfaction_score"])
        st.caption(f"Correlation between engagement and satisfaction: **{corr:.2f}** "
                   f"({'moves together' if corr > 0.3 else 'weak relationship' if corr > -0.3 else 'move in opposite directions'}).")

st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-top: 15px; margin-bottom: 5px;">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#7C5CBF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect>
            <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path>
        </svg>
        <h3 style="margin: 0; font-family: 'Playfair Display', serif; color: #2A1F4D; font-size: 1.25rem;">Performance Distribution by Department</h3>
    </div>
""", unsafe_allow_html=True)

cross = df_view.groupby(["department", "performance_score"]).size().reset_index(name="count")
fig3 = px.bar(cross, x="department", y="count", color="performance_score", barmode="stack",
              color_discrete_sequence=DISTINCT_PALETTE)
fig3 = style_slices(fig3)
fig3 = style_fig(fig3)
fig3.update_layout(
    margin=dict(l=40, r=20, t=30, b=50),
    xaxis=dict(automargin=True, tickangle=-20),
    yaxis=dict(automargin=True)
)
st.plotly_chart(fig3, width='stretch', theme=None)

st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-top: 15px; margin-bottom: 5px;">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#7C5CBF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
        </svg>
        <h3 style="margin: 0; font-family: 'Playfair Display', serif; color: #2A1F4D; font-size: 1.25rem;">Does Extra Effort Pay Off? Special Projects vs. Performance</h3>
    </div>
""", unsafe_allow_html=True)
st.caption("Checks whether employees who take on more special projects actually rate higher.")
if df_view["performance_score"].notna().any():
    fig4 = px.box(df_view.dropna(subset=["performance_score"]), x="performance_score", y="special_projects_count",
                  color_discrete_sequence=["#5B3E96"])
    fig4 = style_fig(fig4)
    fig4.update_layout(
        margin=dict(l=40, r=20, t=30, b=40),
        xaxis=dict(automargin=True),
        yaxis=dict(automargin=True)
    )
    st.plotly_chart(fig4, width='stretch', theme=None)
    if len(df_view) > 1:
        corr2 = df_view["special_projects_count"].corr(df_view["engagement_score"])
        st.caption(f"Correlation between special projects taken on and engagement score: **{corr2:.2f}**.")
else:
    st.info("No performance score data available for this filter.")