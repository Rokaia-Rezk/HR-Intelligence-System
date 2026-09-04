import streamlit as st
import plotly.express as px
from data_loader import load_standard_data
from filters import department_status_filters, style_fig

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

turnover_rate = (~df["is_active"]).mean() * 100

c1, c2, c3 = st.columns(3)
c1.metric("Turnover Rate (filtered)", f"{turnover_rate:.1f}%")
c2.metric("Active Personnel", int(df["is_active"].sum()))
c3.metric("Exited Personnel", int((~df["is_active"]).sum()))

st.divider()

col1, col2 = st.columns(2)
with col1:
    st.subheader("Recruitment Source Performance")
    src_counts = df["recruitment_source"].value_counts().reset_index()
    src_counts.columns = ["recruitment_source", "count"]
    # Long source names (e.g. "On-line Web application") read poorly as a
    # vertical column chart, so this is a horizontal bar, sorted.
    fig = px.bar(src_counts.sort_values("count"), x="count", y="recruitment_source",
                 orientation="h", color_discrete_sequence=["#9575CD"])
    st.plotly_chart(style_fig(fig), use_container_width=True, theme=None)
    best_source = src_counts.sort_values("count", ascending=False).iloc[0]
    st.caption(f"**{best_source['recruitment_source']}** brought in the most hires "
               f"({best_source['count']} of {len(df)}).")

    st.markdown("**Turnover Rate by Source** (quality of hire, not just volume)")
    src_turnover = df.groupby("recruitment_source")["is_active"].apply(
        lambda s: (~s).mean() * 100
    ).sort_values(ascending=False).reset_index(name="turnover_rate")
    fig1b = px.bar(src_turnover, x="turnover_rate", y="recruitment_source", orientation="h",
                   color_discrete_sequence=["#5B3E96"])
    fig1b.update_xaxes(ticksuffix="%")
    st.plotly_chart(style_fig(fig1b), use_container_width=True, theme=None)
    worst_src = src_turnover.iloc[0]
    st.caption(f"**{worst_src['recruitment_source']}** has the highest turnover rate "
               f"({worst_src['turnover_rate']:.0f}%) — a source that brings in a lot of hires isn't "
               f"necessarily a source that brings in hires who stay.")

with col2:
    st.subheader("Top Termination Drivers")
    left_df = df[~df["is_active"]]
    reason_counts = left_df["termination_reason"].value_counts().reset_index()
    reason_counts.columns = ["reason", "count"]
    top_reasons = reason_counts.head(8).sort_values("count")
    fig2 = px.bar(top_reasons, x="count", y="reason", orientation="h",
                  color_discrete_sequence=["#7C5CBF"])
    st.plotly_chart(style_fig(fig2), use_container_width=True, theme=None)
    if not reason_counts.empty:
        top_reason = reason_counts.sort_values("count", ascending=False).iloc[0]
        st.caption(f"**{top_reason['reason']}** is the single biggest reason people leave "
                   f"({top_reason['count']} of {len(left_df)} exits).")

st.subheader("Historical Hires Trend")
hires = df.dropna(subset=["hire_date"]).copy()
hires["hire_year"] = hires["hire_date"].dt.year
yearly = hires.groupby("hire_year").size().reset_index(name="hires")
fig3 = px.line(yearly, x="hire_year", y="hires", markers=True, color_discrete_sequence=["#7C5CBF"])
st.plotly_chart(style_fig(fig3), use_container_width=True, theme=None)
