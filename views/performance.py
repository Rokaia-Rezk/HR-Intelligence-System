import streamlit as st
import plotly.express as px
from data_loader import load_standard_data
from filters import department_status_filters, style_fig, style_slices, DISTINCT_PALETTE

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

c1, c2, c3 = st.columns(3)
c1.metric("Average Engagement", f"{df['engagement_score'].mean():.2f} / 5.0")
c2.metric("Average Satisfaction", f"{df['satisfaction_score'].mean():.2f} / 5.0")
c3.metric("Avg Special Projects", f"{df['special_projects_count'].mean():.1f}")

st.divider()

col1, col2 = st.columns(2)
with col1:
    st.subheader("Performance Score Breakdown")
    perf_counts = df["performance_score"].value_counts().reset_index()
    perf_counts.columns = ["performance_score", "count"]
    if perf_counts["performance_score"].nunique() <= 6:
        # Distinct-contrast palette + a white border per slice — a sequential
        # "all-purple" gradient made every slice blur into the next one.
        fig = px.pie(perf_counts, names="performance_score", values="count",
                     color_discrete_sequence=DISTINCT_PALETTE)
        fig = style_slices(fig)
    else:
        fig = px.bar(perf_counts.sort_values("count"), x="count", y="performance_score",
                      orientation="h", color_discrete_sequence=["#9575CD"])
    st.plotly_chart(style_fig(fig), use_container_width=True, theme=None)
    top_tier = perf_counts.sort_values("count", ascending=False).iloc[0]
    st.caption(
        f"**{top_tier['performance_score']}** is the largest group "
        f"({top_tier['count']} of {len(df)} employees, {top_tier['count']/len(df):.0%})."
    )

with col2:
    st.subheader("Engagement vs Satisfaction")
    fig2 = px.scatter(df, x="engagement_score", y="satisfaction_score",
                       color="department", hover_data=["employee_name"],
                       color_discrete_sequence=px.colors.qualitative.Set2)
    fig2.update_traces(marker=dict(size=8, opacity=0.75, line=dict(width=0.5, color="#FFFFFF")))
    st.plotly_chart(style_fig(fig2), use_container_width=True, theme=None)
    corr = df["engagement_score"].corr(df["satisfaction_score"])
    st.caption(f"Correlation between engagement and satisfaction: **{corr:.2f}** "
               f"({'moves together' if corr > 0.3 else 'weak relationship' if corr > -0.3 else 'move in opposite directions'}).")

st.subheader("Performance Distribution by Department")
cross = df.groupby(["department", "performance_score"]).size().reset_index(name="count")
fig3 = px.bar(cross, x="department", y="count", color="performance_score", barmode="stack",
              color_discrete_sequence=DISTINCT_PALETTE)
fig3 = style_slices(fig3)
st.plotly_chart(style_fig(fig3), use_container_width=True, theme=None)

st.subheader("Does Extra Effort Pay Off? Special Projects vs. Performance")
st.caption("Checks whether employees who take on more special projects actually rate higher — "
           "useful for validating (or challenging) how 'high performer' is being defined.")
if df["performance_score"].notna().any():
    fig4 = px.box(df.dropna(subset=["performance_score"]), x="performance_score", y="special_projects_count",
                  color_discrete_sequence=["#5B3E96"])
    st.plotly_chart(style_fig(fig4), use_container_width=True, theme=None)
    corr2 = df["special_projects_count"].corr(df["engagement_score"])
    st.caption(f"Correlation between special projects taken on and engagement score: **{corr2:.2f}**.")
else:
    st.info("No performance score data available for this filter.")
