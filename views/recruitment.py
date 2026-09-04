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
 
src_counts = df["recruitment_source"].value_counts().reset_index()
src_counts.columns = ["recruitment_source", "count"]
src_counts_sorted = src_counts.sort_values("count")
 
click_idx = get_click_index("recruit_src_chart")
sel_source = src_counts_sorted.iloc[click_idx]["recruitment_source"] if click_idx is not None and click_idx < len(src_counts_sorted) else None
df_view = df[df["recruitment_source"] == sel_source] if sel_source else df
 
if sel_source:
    sc1, sc2 = st.columns([5, 1])
    with sc1:
        st.info(f"Everything below is filtered to **{sel_source}** — click the same bar again, or use Clear, to see all sources.")
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
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 5px;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#7C5CBF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                <circle cx="9" cy="7" r="4"></circle>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
            </svg>
            <h3 style="margin: 0; font-family: 'Playfair Display', serif; color: #2A1F4D; font-size: 1.25rem;">Recruitment Source Performance</h3>
        </div>
    """, unsafe_allow_html=True)
    st.caption("Click a bar to filter everything else on this page by that source.")
    
    fig = px.bar(src_counts_sorted, x="count", y="recruitment_source",
                 orientation="h", color_discrete_sequence=["#9575CD"])
    fig = style_fig(fig)
    fig.update_layout(
        margin=dict(l=140, r=20, t=20, b=30),
        xaxis=dict(automargin=True),
        yaxis=dict(automargin=True)
    )
    st.plotly_chart(fig, use_container_width=True, theme=None,
                     on_select="rerun", selection_mode="points", key="recruit_src_chart")
    best_source = src_counts.sort_values("count", ascending=False).iloc[0]
    st.caption(f"**{best_source['recruitment_source']}** brought in the most hires.")
 
    st.markdown("**Turnover Rate by Source**")
    src_turnover = df_view.groupby("recruitment_source")["is_active"].apply(
        lambda s: (~s).mean() * 100
    ).sort_values(ascending=False).reset_index(name="turnover_rate")
    if not src_turnover.empty:
        fig1b = px.bar(src_turnover, x="turnover_rate", y="recruitment_source", orientation="h",
                       color_discrete_sequence=["#5B3E96"])
        fig1b.update_xaxes(ticksuffix="%")
        fig1b = style_fig(fig1b)
        fig1b.update_layout(
            margin=dict(l=140, r=20, t=20, b=30),
            xaxis=dict(automargin=True),
            yaxis=dict(automargin=True)
        )
        st.plotly_chart(fig1b, use_container_width=True, theme=None)
 
with col2:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 5px;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#7C5CBF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M16 16v1a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h2m5.66 0H14a2 2 0 0 1 2 2v3.34"></path>
                <line x1="23" y1="1" x2="1" y2="23"></line>
            </svg>
            <h3 style="margin: 0; font-family: 'Playfair Display', serif; color: #2A1F4D; font-size: 1.25rem;">Top Termination Drivers</h3>
        </div>
    """, unsafe_allow_html=True)
    st.caption("Primary exit causes.")
    
    left_df = df_view[~df_view["is_active"]]
    reason_counts = left_df["termination_reason"].value_counts().reset_index()
    reason_counts.columns = ["reason", "count"]
    top_reasons = reason_counts.head(8).sort_values("count")
    if not top_reasons.empty:
        fig2 = px.bar(top_reasons, x="count", y="reason", orientation="h",
                      color_discrete_sequence=["#7C5CBF"])
        fig2 = style_fig(fig2)
        fig2.update_layout(
            margin=dict(l=140, r=20, t=20, b=30),
            xaxis=dict(automargin=True),
            yaxis=dict(automargin=True)
        )
        st.plotly_chart(fig2, use_container_width=True, theme=None)
    else:
        st.info("No terminated employees in what's currently shown.")
 
st.subheader("Historical Hires Trend")
hires = df_view.dropna(subset=["hire_date"]).copy()
if not hires.empty:
    hires["hire_year"] = hires["hire_date"].dt.year
    yearly = hires.groupby("hire_year").size().reset_index(name="hires")
    fig3 = px.line(yearly, x="hire_year", y="hires", markers=True, color_discrete_sequence=["#7C5CBF"])
    fig3 = style_fig(fig3)
    fig3.update_layout(
        margin=dict(l=40, r=20, t=30, b=30),
        xaxis=dict(automargin=True),
        yaxis=dict(automargin=True)
    )
    st.plotly_chart(fig3, use_container_width=True, theme=None)
else:
    st.info("No hire-date data in what's currently shown.")

st.divider()
st.subheader("Tenure at Exit")
TENURE_BUCKETS = ["< 1 year", "1\u20133 years", "3\u20135 years", "5+ years"]

def bucket_tenure(days):
    years = days / 365.25
    if years < 1: return TENURE_BUCKETS[0]
    elif years < 3: return TENURE_BUCKETS[1]
    elif years < 5: return TENURE_BUCKETS[2]
    return TENURE_BUCKETS[3]

left_with_dates = df_view[(~df_view["is_active"]) & df_view["hire_date"].notna() & df_view["termination_date"].notna()].copy()
if not left_with_dates.empty:
    left_with_dates["tenure_days"] = (left_with_dates["termination_date"] - left_with_dates["hire_date"]).dt.days
    left_with_dates["tenure_bucket"] = left_with_dates["tenure_days"].clip(lower=0).apply(bucket_tenure)
    tenure_counts = left_with_dates["tenure_bucket"].value_counts().reindex(TENURE_BUCKETS).fillna(0).reset_index()
    tenure_counts.columns = ["tenure_bucket", "exits"]
 
    fig5 = px.bar(tenure_counts, x="tenure_bucket", y="exits", color_discrete_sequence=["#5B3E96"])
    fig5.update_layout(xaxis_title="Tenure at Exit", yaxis_title="Number of Exits")
    fig5 = style_fig(fig5)
    fig5.update_layout(
        margin=dict(l=40, r=20, t=30, b=40),
        xaxis=dict(automargin=True),
        yaxis=dict(automargin=True)
    )
    st.plotly_chart(fig5, use_container_width=True, theme=None)