import streamlit as st
from data_loader import load_raw_data, load_standard_data

st.title("HR Intelligence System")
st.caption("Dataset-agnostic human resources analytics and automated data engineering pipeline.")

df_raw = load_raw_data()
df_cleaned = load_standard_data()

st.subheader("Data Pipeline Overview")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Raw Records", len(df_raw), delta=f"{len(df_cleaned)} Cleaned")
col2.metric("Active Workforce", int(df_cleaned["is_active"].sum()), delta=f"{int(df_cleaned['is_active'].mean()*100)}%")
col3.metric("Departments Tracked", df_cleaned["department"].nunique())
col4.metric("Average Compensation", f"${df_cleaned['salary'].mean():,.0f}")

st.divider()

st.subheader("System Navigation Modules")
st.markdown("""
Select a module from the sidebar to explore deep analytics:
- **Data Cleaning** — Before/after view of the automated cleaning pipeline and why each fix was needed.
- **Finance & Compensation** — Payroll structures, salary distributions, and executive benchmarking.
- **Performance & Engagement** — Productivity correlations, engagement scores, and talent evaluations.
- **Attendance & Reliability** — Absence tracking, lateness patterns, and risk identification.
- **Recruitment & Turnover** — Sourcing channel effectiveness, attrition analysis, and retention metrics.
""")

st.divider()
with st.expander("Data Source & Schema Mapping Inspection"):
    st.write("Active Source File: `HRDataset_v14.csv` | Mapped via `schema_mapper.py`")
    st.dataframe(df_cleaned.head(10), use_container_width=True)
