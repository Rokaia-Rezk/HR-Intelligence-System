"""
welcome.py
-----------
The register's title page. First thing anyone sees — a text-only cover
(no stock photo, no icon set) that matches the rest of the Personnel
Ledger theme: serif title, a short description, and a table of contents
in place of a hero image. Ends with a single button into the real Home
page, via st.switch_page.
"""

import streamlit as st
from style import render_toc
from data_loader import active_dataset_name

st.markdown('<div class="cover-wrap">', unsafe_allow_html=True)

st.markdown('<div class="cover-eyebrow">A Register of Personnel Analytics</div>', unsafe_allow_html=True)
st.markdown('<div class="cover-title">HR Intelligence System</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="cover-sub">'
    f'A dataset-agnostic HR analytics platform. Upload any HR export — different columns, '
    f'different structure — and every page in this register adapts to it automatically, '
    f'instead of being built around one spreadsheet. Currently open on '
    f'<b>{active_dataset_name()}</b>.'
    f'</div>',
    unsafe_allow_html=True,
)

render_toc([
    ("Home", "Pipeline overview, headline KPIs"),
    ("Upload Data", "Bring your own HR export"),
    ("Data Cleaning", "Quality score & audit log"),
    ("Finance", "Payroll & compensation"),
    ("Performance", "Engagement & ratings"),
    ("Attendance", "Absence & reliability"),
    ("Recruitment", "Sourcing & turnover"),
    ("Recommended Actions", "What to look at first"),
    ("Predictive Attrition", "Who's at risk of leaving"),
])

st.markdown("<br>", unsafe_allow_html=True)
if st.button("Open the Register →"):
    st.switch_page("views/home.py")

st.markdown('</div>', unsafe_allow_html=True)
