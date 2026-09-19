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

Active-page highlighting: NOT done via CSS guessing at Streamlit's
internal DOM/attributes (that was tried twice and didn't render — see
git history). Instead, the current page is rendered as a plain
`.active-nav-item` div (styled in style.py) instead of a st.page_link
at all — every other page still gets a real, clickable st.page_link.
Since Python already knows which page is current (page.url_path ==
pg.url_path), this can't silently fail the way a CSS-attribute guess
can.

"Welcome" is the register's title page and opens first (default=True).
It's a plain cover — text only, no stock photo — with a table of
contents and a button into Home, matching the Personnel Ledger theme.
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
    st.Page("views/welcome.py", title="Welcome", default=True),
    st.Page("views/home.py", title="Home"),
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
            st.markdown(f'<div class="active-nav-item">{page.title}</div>', unsafe_allow_html=True)
        else:
            st.page_link(page)
    render_sidebar_socials()

pg.run()
