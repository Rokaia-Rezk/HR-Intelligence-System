import os
import streamlit as st


def apply_custom_theme():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600;700&family=Inter:wght@400;500;600;700&display=swap');

    /* ============ Base / light content area (matches the Power BI look) ============ */
    .stApp {
        background-color: #F5F2FB;
        color: #2E2350;
        font-family: 'Inter', sans-serif;
    }
    [data-testid="stAppViewContainer"] > .main {
        background-color: #F5F2FB;
    }
    [data-testid="stHeader"] { background-color: rgba(0,0,0,0); }

    /* Headings — Playfair Display for a classy, slightly vintage feel,
       Inter for everything else so it stays practical and readable */
    h1, h2, h3 {
        font-family: 'Playfair Display', serif !important;
        color: #2A1F4D !important;
        font-weight: 600;
        letter-spacing: 0.2px;
    }
    [data-testid="stCaptionContainer"], .stCaption {
        color: #6B5E92 !important;
    }

    /* ============ Sidebar (dark purple, logo pinned at the very top) ============ */
    [data-testid="stSidebar"] {
        background-color: #17122B;
        border-right: none;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.2rem;
    }

    .sidebar-logo-card {
        background: #FFFFFF;
        border-radius: 18px;
        padding: 14px 10px 10px 10px;
        margin: 0 14px 22px 14px;
        text-align: center;
        box-shadow: 0 6px 18px rgba(0,0,0,0.35);
    }
    .sidebar-logo-card img {
        border-radius: 10px;
        max-width: 100%;
    }
    .sidebar-logo-fallback {
        color: #2A1F4D;
        font-family: 'Playfair Display', serif;
        font-weight: 700;
        font-size: 1.2rem;
        margin: 6px 0 0 0;
    }

    /* Sidebar page navigation — big rounded "buttons" like the Power BI mock.
       Unselected items now get a visible background of their own (not just
       text), so the tab list doesn't look "dead" — only the current page
       is obviously different, not the only one that's legible. */
    [data-testid="stSidebarNav"] ul { padding: 0 10px; }
    [data-testid="stSidebarNav"] li { margin-bottom: 8px; }
    [data-testid="stSidebarNav"] a,
    [data-testid="stSidebarNavLink"] {
        border-radius: 12px !important;
        padding: 12px 16px !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        color: #E4DDF7 !important;
        background: #241D42 !important;
        border: 1px solid #362B60;
        transition: background 0.15s ease, color 0.15s ease;
        opacity: 1 !important;
    }
    [data-testid="stSidebarNav"] a span,
    [data-testid="stSidebarNavLink"] span {
        color: inherit !important;
        opacity: 1 !important;
    }
    [data-testid="stSidebarNav"] a:hover,
    [data-testid="stSidebarNavLink"]:hover {
        background: linear-gradient(135deg, #3B2E68 0%, #4F3B8C 100%) !important;
        color: #FFFFFF !important;
        border-color: #4F3B8C;
    }
    [data-testid="stSidebarNav"] a[aria-current="page"],
    [data-testid="stSidebarNavLink"][aria-current="page"] {
        background: linear-gradient(135deg, #7C5CBF 0%, #9B7FD4 100%) !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border-color: transparent;
        box-shadow: 0 4px 14px rgba(124, 92, 191, 0.45);
    }

    /* ============ KPI cards (white, rounded, soft shadow) ============ */
    [data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #EAE4F7;
        padding: 16px 20px;
        border-radius: 14px;
        box-shadow: 0 3px 14px rgba(90, 70, 150, 0.08);
    }
    [data-testid="stMetricLabel"] {
        color: #8A7BB8 !important;
        font-weight: 600;
        font-size: 0.82rem !important;
        text-transform: uppercase;
        letter-spacing: 0.4px;
    }
    [data-testid="stMetricValue"] {
        color: #2A1F4D !important;
        font-weight: 700;
        font-size: 1.7rem !important;
        font-family: 'Playfair Display', serif !important;
    }

    /* ============ Chart cards — every plotly chart sits in its own white card ============ */
    [data-testid="stPlotlyChart"] {
        background: #FFFFFF;
        border: 1px solid #EAE4F7;
        border-radius: 16px;
        padding: 14px;
        box-shadow: 0 3px 14px rgba(90, 70, 150, 0.08);
    }

    /* ============ Filters bar (expander) styled as a light card ============ */
    .streamlit-expanderHeader {
        background-color: #FFFFFF !important;
        border: 1px solid #EAE4F7 !important;
        border-radius: 12px;
        color: #2A1F4D !important;
        font-weight: 600;
    }
    [data-testid="stExpander"] {
        background-color: #FFFFFF;
        border: 1px solid #EAE4F7 !important;
        border-radius: 12px;
        box-shadow: 0 3px 14px rgba(90, 70, 150, 0.06);
    }

    /* Multiselect / slider chips in the purple family */
    [data-baseweb="tag"] {
        background-color: #7C5CBF !important;
    }
    .stSlider [data-baseweb="slider"] > div > div { background: #7C5CBF !important; }

    /* ============ Dataframes ============ */
    [data-testid="stDataFrame"] {
        background: #FFFFFF;
        border: 1px solid #EAE4F7;
        border-radius: 14px;
        overflow: hidden;
        box-shadow: 0 3px 14px rgba(90, 70, 150, 0.08);
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #7C5CBF 0%, #9B7FD4 100%);
        color: #FFFFFF;
        border: none;
        border-radius: 10px;
        font-weight: 600;
        padding: 8px 20px;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #6B4DAE 0%, #8A6EC5 100%);
    }

    /* Info boxes (audit log lines) */
    [data-testid="stAlert"] {
        background-color: #FFFFFF;
        border: 1px solid #EAE4F7;
        border-radius: 10px;
        color: #2E2350;
    }

    hr { border-color: #E4DCF5 !important; }
    </style>
    """, unsafe_allow_html=True)


def render_sidebar_logo():
    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.jpeg")
    with st.sidebar:
        st.markdown('<div class="sidebar-logo-card">', unsafe_allow_html=True)
        if os.path.exists(logo_path):
            st.image(logo_path, use_container_width=True)
        else:
            st.markdown('<p class="sidebar-logo-fallback">Rokaia Rezk</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
