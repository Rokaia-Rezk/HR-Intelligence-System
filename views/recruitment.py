"""
recruitment.py
---------------
Click-to-filter: "Recruitment Source Performance" is clickable. Click
a source and every other chart/metric on this page — turnover rate,
termination drivers, the hires trend — narrows to it. Same
session_state approach as finance.py; see get_click_index() in
filters.py.
"""
 
import streamlit as st
import plotly.express as px
from data_loader import load_standard_data
from filters import department_status_filters, style_fig, get_click_index
 
st.title("Recruitment & Attrition Intelligence")
st.caption("Sourcing channel efficacy, turnover ratios, and termination driver analytics.")
 
df_all = load_standard_data()
 
with st.expander("Filters", expanded=True):
    c1, c2, c3 = st.columns(3)
    df = department_status_filters(df_all, "recruit", c1, c2)
    with c3:
        sources = sorted(df_all["recruitment_source"].dropna().unique().tolist())
        selected_sources = st.multiselect("Recruitment Source", sources, default=sources, key="recruit_source")
    df = df[df["recruitment_source"].isin(selected_sources)] if selected_sources else df.iloc[0:0]
 
if df.empty:
    st.warning("No employees match the current filters.")
    st.stop()
 
# src_counts is built from `df` only — never from the click-filtered
# view — so its source order stays stable across reruns and a click's
# point_index always maps back to the right source.
src_counts = df["recruitment_source"].value_counts().reset_index()
src_counts.columns = ["recruitment_source", "count"]
src_counts_sorted = src_counts.sort_values("count")  # this is the exact row order the chart is drawn in
 
click_idx = get_click_index("recruit_src_chart")
sel_source = src_counts_sorted.iloc[click_idx]["recruitment_source"] if click_idx is not None and click_idx < len(src_counts_sorted) else None
df_view = df[df["recruitment_source"] == sel_source] if sel_source else df
 
if sel_source:
    sc1, sc2 = st.columns([5, 1])
    with sc1:
        st.info(f"Everything below is filtered to **{sel_source}** — click the same bar again, "
                f"or use Clear, to see all sources.")
    with sc2:
        if st.button("Clear selection", key="recruit_clear"):
            st.session_state.pop("recruit_src_chart", None)
            st.rerun()
 
turnover_rate = (~df_view["is_active"]).mean() * 100 if len(df_view) else 0
 
c1, c2, c3 = st.columns(3)
c1.metric("Turnover Rate (filtered)", f"{turnover_rate:.1f}%")
c2.metric("Active Personnel", int(df_view["is_active"].sum()))
c3.metric("Exited Personnel", int((~df_view["is_active"]).sum()))
 
st.divider()
 
col1, col2 = st.columns(2)
with col1:
    st.subheader("Recruitment Source Performance")
    st.caption("Click a bar to filter everything else on this page by that source.")
    # Long source names (e.g. "On-line Web application") read poorly as a
    # vertical column chart, so this is a horizontal bar, sorted.
    fig = px.bar(src_counts_sorted, x="count", y="recruitment_source",
                 orientation="h", color_discrete_sequence=["#9575CD"])
    st.plotly_chart(style_fig(fig), use_container_width=True, theme=None,
                     on_select="rerun", selection_mode="points", key="recruit_src_chart")
    best_source = src_counts.sort_values("count", ascending=False).iloc[0]
    st.caption(f"**{best_source['recruitment_source']}** brought in the most hires "
               f"({best_source['count']} of {len(df)}).")
 
    st.markdown("**Turnover Rate by Source** (quality of hire, not just volume)")
    src_turnover = df_view.groupby("recruitment_source")["is_active"].apply(
        lambda s: (~s).mean() * 100
    ).sort_values(ascending=False).reset_index(name="turnover_rate")
    if not src_turnover.empty:
        fig1b = px.bar(src_turnover, x="turnover_rate", y="recruitment_source", orientation="h",
                       color_discrete_sequence=["#5B3E96"])
        fig1b.update_xaxes(ticksuffix="%")
        st.plotly_chart(style_fig(fig1b), use_container_width=True, theme=None)
        worst_src = src_turnover.iloc[0]
        st.caption(f"**{worst_src['recruitment_source']}** has the highest turnover rate among what's "
                   f"currently shown ({worst_src['turnover_rate']:.0f}%) — a source that brings in a lot "
                   f"of hires isn't necessarily a source that brings in hires who stay.")
 
with col2:
    st.subheader("Top Termination Drivers")
    left_df = df_view[~df_view["is_active"]]
    reason_counts = left_df["termination_reason"].value_counts().reset_index()
    reason_counts.columns = ["reason", "count"]
    top_reasons = reason_counts.head(8).sort_values("count")
    if not top_reasons.empty:
        fig2 = px.bar(top_reasons, x="count", y="reason", orientation="h",
                      color_discrete_sequence=["#7C5CBF"])
        st.plotly_chart(style_fig(fig2), use_container_width=True, theme=None)
        top_reason = reason_counts.sort_values("count", ascending=False).iloc[0]
        st.caption(f"**{top_reason['reason']}** is the single biggest reason people leave "
                   f"among what's currently shown ({top_reason['count']} of {len(left_df)} exits).")
    else:
        st.info("No terminated employees in what's currently shown.")
 
st.subheader("Historical Hires Trend")
hires = df_view.dropna(subset=["hire_date"]).copy()
if not hires.empty:
    hires["hire_year"] = hires["hire_date"].dt.year
    yearly = hires.groupby("hire_year").size().reset_index(name="hires")
    fig3 = px.line(yearly, x="hire_year", y="hires", markers=True, color_discrete_sequence=["#7C5CBF"])
    st.plotly_chart(style_fig(fig3), use_container_width=True, theme=None)
else:
    st.info("No hire-date data in what's currently shown.")
 
st.divider()
st.subheader("When Do People Actually Leave? Tenure at Exit")
st.caption("Turns 'people are leaving' into 'people are leaving at THIS point in their tenure' — "
           "the two call for very different fixes (onboarding vs. burnout/career plateau).")
 
TENURE_BUCKETS = ["< 1 year", "1\u20133 years", "3\u20135 years", "5+ years"]
 
 
def bucket_tenure(days):
    years = days / 365.25
    if years < 1:
        return TENURE_BUCKETS[0]
    elif years < 3:
        return TENURE_BUCKETS[1]
    elif years < 5:
        return TENURE_BUCKETS[2]
    return TENURE_BUCKETS[3]
 
 
left_with_dates = df_view[(~df_view["is_active"]) &
                           df_view["hire_date"].notna() &
                           df_view["termination_date"].notna()].copy()
 
if not left_with_dates.empty:
    left_with_dates["tenure_days"] = (left_with_dates["termination_date"] - left_with_dates["hire_date"]).dt.days
    left_with_dates["tenure_bucket"] = left_with_dates["tenure_days"].clip(lower=0).apply(bucket_tenure)
    tenure_counts = left_with_dates["tenure_bucket"].value_counts().reindex(TENURE_BUCKETS).fillna(0).reset_index()
    tenure_counts.columns = ["tenure_bucket", "exits"]
 
    fig5 = px.bar(tenure_counts, x="tenure_bucket", y="exits", color_discrete_sequence=["#5B3E96"])
    fig5.update_layout(xaxis_title="Tenure at Exit", yaxis_title="Number of Exits")
    st.plotly_chart(style_fig(fig5), use_container_width=True, theme=None)
 
    total_exits = tenure_counts["exits"].sum()
    top_bucket_row = tenure_counts.sort_values("exits", ascending=False).iloc[0]
    top_bucket, top_count = top_bucket_row["tenure_bucket"], top_bucket_row["exits"]
    top_pct = top_count / total_exits * 100 if total_exits else 0
 
    if top_bucket == "< 1 year":
        action = ("This points to an onboarding or early-fit problem, not a general morale issue — "
                   "worth reviewing the first 90 days specifically (manager check-ins, role clarity, "
                   "realistic expectations at hire) rather than a company-wide retention program.")
    elif top_bucket in ("1\u20133 years", "3\u20135 years"):
        action = ("This is the classic 'no growth path' window — worth checking whether promotion "
                   "and skill-development opportunities exist for this group specifically, rather "
                   "than assuming pay is the only lever.")
    else:
        action = ("Long-tenured departures often signal burnout or career plateau rather than "
                   "dissatisfaction with the job itself — worth looking at internal mobility or "
                   "role-refresh options for senior staff before assuming compensation is the fix.")
 
    st.caption(f"**{top_pct:.0f}%** of exits currently shown happened within **{top_bucket}** of tenure "
               f"({int(top_count)} of {int(total_exits)}). {action}")
else:
    st.info("Not enough hire/termination date data in what's currently shown to analyze tenure at exit.")
 