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

    /* Sidebar page navigation — now rendered by hand via st.page_link()
       (see app.py) since st.navigation()'s automatic nav can't be
       reliably repositioned. Same big rounded "button" look as before,
       just targeting st.page_link's element instead. */
    [data-testid="stPageLink"] { margin-bottom: 8px; padding: 0 10px; }
    [data-testid="stPageLink"] a,
    [data-testid="stPageLink"] a[data-testid="stPageLink-NavLink"] {
        border-radius: 12px !important;
        padding: 12px 16px !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        color: #E4DDF7 !important;
        background: #241D42 !important;
        border: 1px solid #362B60;
        transition: background 0.15s ease, color 0.15s ease;
        opacity: 1 !important;
        width: 100%;
    }
    [data-testid="stPageLink"] a span,
    [data-testid="stPageLink"] p {
        color: inherit !important;
        opacity: 1 !important;
    }
    [data-testid="stPageLink"] a:hover {
        background: linear-gradient(135deg, #3B2E68 0%, #4F3B8C 100%) !important;
        color: #FFFFFF !important;
        border-color: #4F3B8C;
    }
    /* The active page is marked from Python (see app.py) with a tiny
       <div class="active-page-marker">, since st.page_link decides its
       own "current page" styling in JS and never exposes it as an HTML
       attribute we could select directly. :has() lets us reach forward
       from that marker's container to the NEXT container's page-link. */
    div:has(> .active-page-marker) + div [data-testid="stPageLink"] a {
        background: linear-gradient(135deg, #7C5CBF 0%, #9B7FD4 100%) !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border-color: transparent;
        box-shadow: 0 4px 14px rgba(124, 92, 191, 0.45);
    }

    /* ============ Social icons row, pinned at the bottom of the sidebar ============ */
    .sidebar-social-row {
        display: flex;
        justify-content: center;
        gap: 14px;
        margin: 24px 14px 10px 14px;
    }
    .sidebar-social-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 42px;
        height: 42px;
        border-radius: 50%;
        background: #241D42;
        border: 1px solid #362B60;
        color: #D8CCF0;
        transition: all 0.15s ease;
        text-decoration: none;
    }
    .sidebar-social-icon:hover {
        background: linear-gradient(135deg, #7C5CBF 0%, #9B7FD4 100%);
        color: #FFFFFF;
        border-color: transparent;
        box-shadow: 0 4px 14px rgba(124, 92, 191, 0.45);
    }
    .sidebar-social-icon svg { width: 20px; height: 20px; }

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


# Inline SVGs — no external icon-font CDN needed, so nothing to fail to
# load. GitHub/LinkedIn marks are fill-based; the portfolio icon is a
# stroke-based "globe" (Feather-style) since there's no single official
# generic-portfolio mark.
_ICON_GITHUB = """<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 0.297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.725-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.955-.266 1.98-.399 3-.404 1.02.005 2.045.138 3.005.404 2.29-1.552 3.295-1.23 3.295-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/></svg>"""

_ICON_LINKEDIN = """<svg viewBox="0 0 24 24" fill="currentColor"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>"""

_ICON_PORTFOLIO = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>"""


def render_sidebar_socials():
    """Three circular icon links pinned wherever this is called in the
    sidebar — GitHub, LinkedIn, and portfolio. Real inline SVGs, so
    there's no external icon-font request that can fail or get blocked."""
    with st.sidebar:
        st.markdown(f"""
        <div class="sidebar-social-row">
            <a class="sidebar-social-icon" href="https://github.com/Rokaia-Rezk"
               target="_blank" title="GitHub">{_ICON_GITHUB}</a>
            <a class="sidebar-social-icon" href="https://www.linkedin.com/in/rokaia-rezk-0761052bb"
               target="_blank" title="LinkedIn">{_ICON_LINKEDIN}</a>
            <a class="sidebar-social-icon" href="https://portfolio-rokaia-rezk1.vercel.app/"
               target="_blank" title="Portfolio">{_ICON_PORTFOLIO}</a>
        </div>
        """, unsafe_allow_html=True)
