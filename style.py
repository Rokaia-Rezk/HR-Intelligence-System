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
        display: flex;
        flex-direction: column;
        min-height: 100vh;
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

    /* Sidebar page navigation — rendered by hand via st.page_link() in
       app.py (position="hidden" turns off st.navigation()'s own nav UI,
       since it insists on a fixed slot near the top of the sidebar that
       can't be moved below the logo). Same big rounded "button" look. */
    [data-testid="stPageLink"] { margin-bottom: 8px; padding: 0 10px; }
    [data-testid="stPageLink"] a {
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
    /* st.page_link decides "current page" styling itself in JS and never
       exposes it as a selectable HTML attribute — so app.py marks the
       active page from Python with a tiny <div class="active-page-marker">
       right before it, and :has() lets this rule reach forward from that
       marker's container to the NEXT container's page-link. */
    div:has(> .active-page-marker) + div [data-testid="stPageLink"] a {
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

    /* ============ Icon KPI cards (custom HTML — used where a per-card
       icon is wanted; same visual language as stMetric above) ============ */
    .kpi-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin: 8px 0 20px 0; }
    .kpi-icon-card {
        background: #FFFFFF;
        border: 1px solid #EAE4F7;
        border-radius: 14px;
        padding: 16px 20px;
        box-shadow: 0 3px 14px rgba(90, 70, 150, 0.08);
        display: flex;
        align-items: flex-start;
        gap: 12px;
    }
    .kpi-icon-card .kpi-icon {
        width: 38px; height: 38px; flex-shrink: 0;
        border-radius: 10px;
        background: linear-gradient(135deg, #7C5CBF 0%, #9B7FD4 100%);
        display: flex; align-items: center; justify-content: center;
    }
    .kpi-icon-card .kpi-icon svg { width: 20px; height: 20px; stroke: #FFFFFF; }
    .kpi-icon-card .kpi-label { color: #8A7BB8; font-weight: 600; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.4px; }
    .kpi-icon-card .kpi-value { font-family: 'Playfair Display', serif; font-weight: 700; font-size: 1.55rem; color: #2A1F4D; margin-top: 2px; }
    .kpi-icon-card .kpi-delta { font-size: 0.8rem; font-weight: 600; margin-top: 2px; }
    .kpi-icon-card .kpi-delta.up { color: #3E9B5C; }
    .kpi-icon-card .kpi-delta.down { color: #C0524A; }

    /* ============ Data Quality Score badge ============ */
    .quality-score-card {
        background: #FFFFFF;
        border: 1px solid #EAE4F7;
        border-radius: 16px;
        padding: 20px 24px;
        box-shadow: 0 3px 14px rgba(90, 70, 150, 0.08);
        display: flex; align-items: center; gap: 20px;
        margin: 8px 0 20px 0;
    }
    .quality-score-ring {
        width: 84px; height: 84px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        background: conic-gradient(#7C5CBF calc(var(--pct) * 1%), #EFE9FA 0);
        flex-shrink: 0;
    }
    .quality-score-ring::before {
        content: "";
        position: absolute;
    }
    .quality-score-inner {
        width: 66px; height: 66px; border-radius: 50%; background: #FFFFFF;
        display: flex; align-items: center; justify-content: center;
        font-family: 'Playfair Display', serif; font-weight: 700; font-size: 1.15rem; color: #2A1F4D;
    }
    .quality-score-text h3 { margin: 0 0 4px 0; font-size: 1.1rem; }
    .quality-score-text p { margin: 0; color: #6B5E92; font-size: 0.9rem; }

    /* ============ Numbered workflow steps (cleaning audit log) ============ */
    .workflow-step {
        display: flex; gap: 14px; align-items: flex-start;
        background: #FFFFFF; border: 1px solid #EAE4F7; border-radius: 12px;
        padding: 12px 16px; margin: 8px 0;
        box-shadow: 0 2px 10px rgba(90, 70, 150, 0.06);
    }
    .workflow-step .step-num {
        width: 28px; height: 28px; border-radius: 50%; flex-shrink: 0;
        background: linear-gradient(135deg, #7C5CBF 0%, #9B7FD4 100%);
        color: #FFFFFF; font-weight: 700; font-size: 0.85rem;
        display: flex; align-items: center; justify-content: center;
    }
    .workflow-step .step-text { color: #2E2350; font-size: 0.92rem; padding-top: 3px; }

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

    /* Social links footer (GitHub / LinkedIn / Portfolio) */
    .sidebar-social {
        margin-top: auto;
        padding-top: 16px;
        display: flex;
        justify-content: center;
        gap: 14px;
    }
    .sidebar-social a {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 40px;
        height: 40px;
        border-radius: 10px;
        background: #241D42;
        border: 1px solid #362B60;
        transition: background 0.15s ease, transform 0.15s ease;
    }
    .sidebar-social a:hover {
        background: linear-gradient(135deg, #7C5CBF 0%, #9B7FD4 100%);
        transform: translateY(-2px);
    }
    .sidebar-social svg { width: 20px; height: 20px; fill: #E4DDF7; }
    .sidebar-social a:hover svg { fill: #FFFFFF; }

    hr { border-color: #E4DCF5 !important; }
    </style>
    """, unsafe_allow_html=True)


def render_sidebar_logo():
    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.jpeg")
    with st.sidebar:
        st.markdown('<div class="sidebar-logo-card">', unsafe_allow_html=True)
        if os.path.exists(logo_path):
            st.image(logo_path, width='stretch')
        else:
            st.markdown('<p class="sidebar-logo-fallback">Rokaia Rezk</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


def render_sidebar_socials():
    """Call this LAST in app.py (after st.navigation()'s pg.run(), or at
    minimum after render_sidebar_logo()) — order in app.py is what decides
    order on screen here, same rule as the logo."""
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-social">
            <a href="https://github.com/Rokaia-Rezk" target="_blank" title="GitHub">
                <svg viewBox="0 0 24 24"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.3 3.438 9.8 8.207 11.387.6.113.793-.26.793-.577 0-.285-.01-1.04-.016-2.04-3.338.725-4.042-1.61-4.042-1.61-.546-1.386-1.332-1.756-1.332-1.756-1.09-.744.082-.729.082-.729 1.204.084 1.837 1.236 1.837 1.236 1.07 1.834 2.807 1.304 3.492.997.108-.775.418-1.305.762-1.605-2.665-.303-5.466-1.332-5.466-5.93 0-1.31.468-2.38 1.235-3.22-.124-.303-.535-1.523.117-3.176 0 0 1.007-.322 3.3 1.23A11.5 11.5 0 0 1 12 5.803c1.02.005 2.047.138 3.006.404 2.29-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.873.118 3.176.77.84 1.233 1.91 1.233 3.22 0 4.61-2.804 5.624-5.475 5.92.43.372.823 1.102.823 2.222 0 1.606-.015 2.898-.015 3.293 0 .32.192.694.8.576C20.565 21.795 24 17.298 24 12c0-6.63-5.373-12-12-12z"/></svg>
            </a>
            <a href="https://www.linkedin.com/in/rokaia-rezk-0761052bb" target="_blank" title="LinkedIn">
                <svg viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 1 1 0-4.124 2.062 2.062 0 0 1 0 4.124zM7.114 20.452H3.558V9h3.556v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
            </a>
            <a href="https://portfolio-rokaia-rezk1.vercel.app/" target="_blank" title="Portfolio">
                <svg viewBox="0 0 24 24"><path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm9.949 11h-4.462c-.146-2.923-.9-5.6-1.94-7.61A10.02 10.02 0 0 1 21.949 11zM12 2.05c1.27 0 2.744 2.86 3.451 6.95h-6.902C9.256 4.91 10.73 2.05 12 2.05zM8.453 10c-.146 2.923-.9 5.6-1.94 7.61A10.02 10.02 0 0 1 2.051 13h4.462A17.9 17.9 0 0 0 8.453 10zm0-2A17.9 17.9 0 0 0 6.513 5h-4.462A10.02 10.02 0 0 1 6.513 2.39C7.553 4.4 8.307 7.077 8.453 10zM12 21.95c-1.27 0-2.744-2.86-3.451-6.95h6.902c-.707 4.09-2.181 6.95-3.451 6.95zm3.549-8.95H8.451c.146-2.923.9-5.6 1.94-7.61.5-.09 1.02-.14 1.549-.14s1.049.05 1.549.14c1.04 2.01 1.794 4.687 1.94 7.61h.12zm.898 2c-.146 2.923-.9 5.6-1.94 7.61A10.02 10.02 0 0 0 21.949 13h-4.462a17.9 17.9 0 0 1-1.94 3zm1.94-5h4.462a10.02 10.02 0 0 0-4.462-8.61c1.04 2.01 1.794 4.687 1.94 7.61z"/></svg>
            </a>
        </div>
        """, unsafe_allow_html=True)


# ---- Small icon set for KPI cards (feather-style, stroke-based) -----------
ICON_DATABASE = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>"""
ICON_PEOPLE = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>"""
ICON_GRID = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>"""
ICON_DOLLAR = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>"""
ICON_ALERT = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>"""
ICON_COPY = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>"""
ICON_CHECK = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>"""


def kpi_icon_card(icon_svg, label, value, delta=None, delta_up=True):
    """Builds one icon-KPI card as an HTML string. Pass a list of these
    to render_kpi_row() — this is the icon-card equivalent of st.metric,
    used where a per-card icon (like the HR Pulse reference) is wanted.

    Returns a single-line string on purpose (no embedded newlines) —
    Markdown treats any line indented 4+ spaces as a code block and
    stops parsing HTML from that point on, which is exactly what was
    turning these cards into visible raw <div> text instead of a
    rendered card."""
    delta_html = ""
    if delta:
        cls = "up" if delta_up else "down"
        delta_html = f'<div class="kpi-delta {cls}">{delta}</div>'
    return (f'<div class="kpi-icon-card"><div class="kpi-icon">{icon_svg}</div>'
            f'<div><div class="kpi-label">{label}</div>'
            f'<div class="kpi-value">{value}</div>{delta_html}</div></div>')


def render_kpi_row(cards):
    """cards: list of HTML strings from kpi_icon_card()."""
    st.markdown(f'<div class="kpi-row">{"".join(cards)}</div>', unsafe_allow_html=True)


def render_quality_score(score_pct, title="Data Quality Score", subtitle=None):
    """A prominent circular score badge, like the reference dashboard's
    '98.5%' indicator — score_pct is 0-100. Single-line HTML for the
    same reason as kpi_icon_card() above — no indented multi-line
    string that Markdown would mistake for a code block."""
    subtitle = subtitle or "Based on completeness, duplicates, and outlier checks on this dataset."
    st.markdown(
        f'<div class="quality-score-card">'
        f'<div class="quality-score-ring" style="--pct: {score_pct};">'
        f'<div class="quality-score-inner">{score_pct:.0f}%</div></div>'
        f'<div class="quality-score-text"><h3>{title}</h3><p>{subtitle}</p></div></div>',
        unsafe_allow_html=True,
    )


def render_workflow_steps(steps):
    """steps: list of plain-text strings (e.g. the cleaning audit log) —
    rendered as numbered cards instead of plain info boxes."""
    html = "".join(
        f'<div class="workflow-step"><div class="step-num">{i}</div>'
        f'<div class="step-text">{step}</div></div>'
        for i, step in enumerate(steps, 1)
    )
    st.markdown(html, unsafe_allow_html=True)
