"""
performance.py
---------------
Click-to-filter: "Performance Score Breakdown" is clickable (when
performance_score data exists). Click a tier and every other chart on
this page narrows to that tier. Same session_state approach as
finance.py; see get_click_index() in filters.py.

performance_score / engagement_score / satisfaction_score /
special_projects_count are each checked independently with
HAS_* flags. app.py only shows this page when at least one of them
has data, but that doesn't guarantee all four do — a dataset missing
some of them still gets a working page showing whatever it has,
instead of a crash or a "nan" reading.
"""

import streamlit as st
import plotly.express as px
from data_loader import load_standard_data, field_has_data
from filters import department_status_filters, style_fig, style_slices, DISTINCT_PALETTE, get_click_index

st.title("Performance & Employee Engagement")
st.caption("Cross-evaluation of performance ratings, job satisfaction indexes, and special project contributions.")

df_all = load_standard_data()
HAS_PERF = field_has_data("performance_score")
HAS_ENG = field_has_data("engagement_score")
HAS_SAT = field_has_data("satisfaction_score")
HAS_PROJ = field_has_data("special_projects_count")

with st.expander("Filters", expanded=True):
    c1, c2, c3 = st.columns(3)
    df = department_status_filters(df_all, "perf", c1, c2)
    if HAS_PERF:
        with c3:
            tiers = sorted(df_all["performance_score"].dropna().unique().tolist())
            selected_tiers = st.multiselect("Performance Score", tiers, default=tiers, key="perf_tier")
        df = df[df["performance_score"].isin(selected_tiers)] if selected_tiers else df.iloc[0:0]

if df.empty:
    st.warning("No employees match the current filters.")
    st.stop()

if HAS_PERF:
    # Fixed alphabetical order (not sorted by count) so a bar's position —
    # and therefore its click index — always maps to the same tier,
    # regardless of how the counts change with other filters. perf_counts
    # itself stays in value_counts() order only for the caption below.
    FIXED_PERF = sorted(df["performance_score"].dropna().unique().tolist())
    perf_counts = df["performance_score"].value_counts().reset_index()
    perf_counts.columns = ["performance_score", "count"]
    click_idx = get_click_index("perf_score_chart")
    sel_tier = FIXED_PERF[click_idx] if click_idx is not None and click_idx < len(FIXED_PERF) else None
else:
    sel_tier = None

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
c1.metric("Average Engagement", f"{df_view['engagement_score'].mean():.2f} / 5.0" if HAS_ENG and len(df_view) else "N/A")
c2.metric("Average Satisfaction", f"{df_view['satisfaction_score'].mean():.2f} / 5.0" if HAS_SAT and len(df_view) else "N/A")
c3.metric("Avg Special Projects", f"{df_view['special_projects_count'].mean():.1f}" if HAS_PROJ and len(df_view) else "N/A")

st.divider()

if HAS_PERF or (HAS_ENG and HAS_SAT):
    col1, col2 = st.columns(2)
else:
    col1 = col2 = st.container()

if HAS_PERF:
    with col1:
        st.subheader("Performance Score Breakdown")
        st.caption("Click a bar to filter every other chart on this page by that tier.")
        # Always a bar (not a pie) — pie charts don't reliably fire click/select
        # events across Streamlit versions, and a fixed alphabetical order
        # keeps a bar's index mapped to the same tier every rerun.
        perf_counts_fixed = perf_counts.set_index("performance_score").reindex(FIXED_PERF).fillna(0).reset_index()
        fig = px.bar(perf_counts_fixed, x="performance_score", y="count", color_discrete_sequence=["#9575CD"])
        fig = style_fig(fig)
        fig.update_xaxes(tickangle=-20)
        st.plotly_chart(fig, width='stretch', theme=None,
                         on_select="rerun", selection_mode="points", key="perf_score_chart")
        top_tier = perf_counts.sort_values("count", ascending=False).iloc[0]
        st.caption(
            f"**{top_tier['performance_score']}** is the largest group "
            f"({top_tier['count']} of {len(df)} employees, {top_tier['count']/len(df):.0%})."
        )

if HAS_ENG and HAS_SAT:
    with col2:
        st.subheader("Engagement vs Satisfaction")
        fig2 = px.scatter(df_view, x="engagement_score", y="satisfaction_score")
        # Single color, not colored by department — a dominant department
        # plus near-invisible slivers isn't a real breakdown; the
        # correlation caption below carries the actual insight here.
        fig2.update_traces(marker=dict(size=8, opacity=0.65, color="#7C5CBF",
                                        line=dict(width=0.5, color="#FFFFFF")))
        st.plotly_chart(style_fig(fig2), width='stretch', theme=None)
        if len(df_view) > 1:
            corr = df_view["engagement_score"].corr(df_view["satisfaction_score"])
            st.caption(f"Correlation between engagement and satisfaction: **{corr:.2f}** "
                       f"({'moves together' if corr > 0.3 else 'weak relationship' if corr > -0.3 else 'move in opposite directions'}).")

if HAS_PERF:
    st.subheader("Performance Distribution by Department")
    cross = df_view.groupby(["department", "performance_score"]).size().reset_index(name="count")
    fig3 = px.bar(cross, x="department", y="count", color="performance_score", barmode="stack",
                  color_discrete_sequence=DISTINCT_PALETTE)
    fig3 = style_slices(fig3)
    fig3 = style_fig(fig3)
    fig3.update_xaxes(tickangle=-20)
    st.plotly_chart(fig3, width='stretch', theme=None)

if HAS_PERF and HAS_PROJ:
    st.subheader("Does Extra Effort Pay Off? Special Projects vs. Performance")
    st.caption("Checks whether employees who take on more special projects actually rate higher — "
               "useful for validating (or challenging) how 'high performer' is being defined.")
    if df_view["performance_score"].notna().any():
        fig4 = px.box(df_view.dropna(subset=["performance_score"]), x="performance_score", y="special_projects_count",
                      color_discrete_sequence=["#5B3E96"])
        st.plotly_chart(style_fig(fig4), width='stretch', theme=None)
        if HAS_ENG and len(df_view) > 1:
            corr2 = df_view["special_projects_count"].corr(df_view["engagement_score"])
            st.caption(f"Correlation between special projects taken on and engagement score: **{corr2:.2f}**.")
    else:
        st.info("No performance score data available for this filter.")

if not (HAS_PERF or HAS_ENG or HAS_SAT or HAS_PROJ):
    st.info("This dataset doesn't include performance, engagement, satisfaction, or special-projects "
            "data, so there's nothing for this page to show.")
