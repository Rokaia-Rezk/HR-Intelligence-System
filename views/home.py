import streamlit as st
from data_loader import load_raw_data, load_standard_data, active_dataset_name
from style import kpi_icon_card, render_kpi_row, ICON_DATABASE, ICON_PEOPLE, ICON_GRID, ICON_DOLLAR

README_URL = "https://github.com/Rokaia-Rezk/HR-Intelligence-System#readme"

st.title("HR Intelligence System")
st.caption("Dataset-agnostic human resources analytics and automated data engineering pipeline.")

st.markdown(
    "**What this is:** most HR dashboards are secretly built around one specific spreadsheet — "
    "rename a column and the whole thing breaks. This one isn't. Upload any reasonably-shaped HR "
    "export (CSV or Excel) and the system automatically maps your columns to a standard schema, "
    "cleans the data with every decision logged, and adapts every page to whatever fields your "
    "data actually has."
)
st.markdown(
    "**How to use it:** the dashboard below is already exploring a sample dataset — browse the "
    "pages in the sidebar to see it in action. To analyze your own data instead, go to **Upload "
    "Data**, confirm how your columns map to the standard fields, and every page updates instantly."
)
st.markdown(
    f"**About the sample data:** the dataset loaded by default (`{active_dataset_name()}`) is a "
    "general-purpose HR dataset — this system's Recruitment and Predictive Attrition pages in "
    "particular are built around its central question, **employee attrition**: who leaves, when, "
    "and why."
)
st.markdown(f"For the full technical write-up — architecture, the cleaning rules, how the "
            f"prediction model works — see the [project README]({README_URL}).")

st.divider()

df_raw = load_raw_data()
df_cleaned = load_standard_data()

st.subheader("Data Pipeline Overview")
render_kpi_row([
    kpi_icon_card(ICON_DATABASE, "Raw Records", len(df_raw), delta=f"{len(df_cleaned)} Cleaned"),
    kpi_icon_card(ICON_PEOPLE, "Active Workforce", int(df_cleaned["is_active"].sum()),
                  delta=f"{int(df_cleaned['is_active'].mean()*100)}%"),
    kpi_icon_card(ICON_GRID, "Departments Tracked", df_cleaned["department"].nunique()),
    kpi_icon_card(ICON_DOLLAR, "Average Compensation", f"${df_cleaned['salary'].mean():,.0f}"),
])

st.divider()

st.subheader("System Navigation Modules")
st.markdown("""
Select a module from the sidebar to explore deep analytics:
- **Data Cleaning** — Before/after view of the automated cleaning pipeline and why each fix was needed.
- **Finance & Compensation** — Payroll structures, salary distributions, and executive benchmarking.
- **Performance & Engagement** — Productivity correlations, engagement scores, and talent evaluations.
- **Attendance & Reliability** — Absence tracking, lateness patterns, and risk identification.
- **Recruitment & Turnover** — Sourcing channel effectiveness, attrition analysis, and retention metrics.
- **Recommended Actions** — Specific, data-driven next steps generated from what's currently loaded.
- **Predictive Attrition** — A trained model ranking current employees by attrition risk.
""")

st.divider()
with st.expander("Data Source & Schema Mapping Inspection"):
    st.write(f"Active Source File: `{active_dataset_name()}` | Mapped via `schema_mapper.py` "
             "— upload a different HR file from the **Upload Data** page in the sidebar.")
    st.dataframe(df_cleaned.head(10), width='stretch')
