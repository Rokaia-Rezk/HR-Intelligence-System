"""
app.py
------
Entry point. st.navigation() has a quirk: it reserves a fixed slot for
the page-list nav near the top of the sidebar, regardless of where in
the code it's called from — that's why the logo kept ending up BELOW
the nav no matter what order render_sidebar_logo() and st.navigation()
were called in.

The fix: position="hidden" tells st.navigation() to still handle
routing (which page is active, URL paths, etc.) but render NO nav UI
of its own. We then build the sidebar by hand with st.page_link(), so
the vertical order — logo, then pages, then social links — is
whatever WE put it in and can never be overridden internally again.
"""

import streamlit as st
from style import apply_custom_theme, render_sidebar_logo, render_sidebar_socials
from data_loader import field_has_data

st.set_page_config(page_title="HR Intelligence System", layout="wide")
apply_custom_theme()

# Performance and Attendance each lean entirely on a handful of fields
# (performance_score / engagement / satisfaction for one, absences /
# days_late for the other). If NONE of a page's fields exist in the
# currently active dataset (default or uploaded), there's nothing real
# for that page to show, so it's left out of the sidebar rather than
# opening onto an empty or crashing page.
pages = [
    st.Page("views/home.py", title="Home", default=True),
    st.Page("views/upload_data.py", title="Upload Data"),
    st.Page("views/data_cleaning.py", title="Data Cleaning"),
    st.Page("views/finance.py", title="Finance"),
]
if any(field_has_data(f) for f in
       ["performance_score", "engagement_score", "satisfaction_score", "special_projects_count"]):
    pages.append(st.Page("views/performance.py", title="Performance"))
if any(field_has_data(f) for f in ["absences", "days_late"]):
    pages.append(st.Page("views/attendance.py", title="Attendance"))
pages.append(st.Page("views/recruitment.py", title="Recruitment"))
pages.append(st.Page("views/recommendations.py", title="Recommended Actions"))
pages.append(st.Page("views/predictive_attrition.py", title="Predictive Attrition"))
pg = st.navigation(pages, position="hidden")

with st.sidebar:
    render_sidebar_logo()
    for page in pages:
        if page.url_path == pg.url_path:
            # st.page_link decides the "active" look itself in JS and never
            # exposes it as an HTML attribute we could style — so instead
            # we mark the active page from Python (comparing against pg,
            # the Page st.navigation() says is currently running) and let
            # the CSS in style.py pick up this marker via :has().
            st.markdown('<div class="active-page-marker"></div>', unsafe_allow_html=True)
        st.page_link(page)
    render_sidebar_socials()

pg.run()

