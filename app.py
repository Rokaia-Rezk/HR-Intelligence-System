"""
app.py
------
Entry point. This now uses st.navigation() instead of the automatic
pages/ folder navigation, for one specific reason: Streamlit ALWAYS
renders the folder-based nav at the very top of the sidebar, before
anything your own code adds to st.sidebar — that's exactly why the
logo kept ending up below the page list instead of above it.

st.navigation() renders the nav wherever it's called, so calling
render_sidebar_logo() first and st.navigation() second guarantees the
logo sits above the page list, like the Power BI reference layout.
"""

import streamlit as st
from style import apply_custom_theme, render_sidebar_logo

st.set_page_config(page_title="HR Intelligence System", layout="wide")
apply_custom_theme()

with st.sidebar:
    render_sidebar_logo()

pages = [
    st.Page("views/home.py", title="Home", default=True),
    st.Page("views/data_cleaning.py", title="Data Cleaning"),
    st.Page("views/finance.py", title="Finance"),
    st.Page("views/performance.py", title="Performance"),
    st.Page("views/attendance.py", title="Attendance"),
    st.Page("views/recruitment.py", title="Recruitment"),
    st.Page("views/predictive_attrition.py", title="Predictive Attrition"),
]
pg = st.navigation(pages)
pg.run()
