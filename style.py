import os
import streamlit as st


def apply_custom_theme():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@500;600;700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    /* =====================================================================
       PERSONNEL LEDGER — design concept
       Paper cream content area + dark ledger-green "cover" sidebar.
       Serif for headings (like a bound register's title page), monospace
       for every number (salaries, %, dates — aligned like a real ledger),
       Inter for body copy. Hairline rules instead of card-and-shadow kit;
       nothing floats, nothing glows, one accent color, no gradients.
       ===================================================================== */

    :root {
        --paper: #F6F3EC;
        --paper-line: #DED5C0;
        --ink: #1E2A24;
        --ink-soft: #5B6259;
        --cover: #1C2A22;
        --cover-line: #33453A;
        --cover-text: #E9E4D6;
        --ledger: #2F4B3C;
        --ledger-soft: #7C8F82;
        --alert: #8C3B2E;
        --alert-bg: #F1E4DF;
    }

    /* ============ Base / paper content area ============ */
    .stApp {
        background-color: var(--paper);
        color: var(--ink);
        font-family: 'Inter', sans-serif;
    }
    [data-testid="stAppViewContainer"] > .main {
        background-color: var(--paper);
    }
    [data-testid="stHeader"] { background-color: rgba(0,0,0,0); }

    /* Headings — serif title-page feel, no letter-spacing tricks, no caps */
    h1, h2, h3 {
        font-family: 'Source Serif 4', serif !important;
        color: var(--ink) !important;
        font-weight: 600;
    }
    h1 {
        border-bottom: 2px solid var(--ledger);
        padding-bottom: 10px;
    }
    [data-testid="stCaptionContainer"], .stCaption {
        color: var(--ink-soft) !important;
    }

    /* Numbers everywhere read like ledger entries, not UI chrome */
    [data-testid="stMetricValue"], .kpi-value, .quality-score-inner,
    [data-testid="stDataFrame"] * , .step-num {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* ============ Sidebar — the ledger's cover ============ */
    [data-testid="stSidebar"] {
        background-color: var(--cover);
        border-right: 1px solid var(--cover-line);
    }
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.4rem;
        display: flex;
        flex-direction: column;
        min-height: 100vh;
    }

    /* Wordmark instead of a logo card — just a title on the cover */
    .sidebar-logo-card {
        padding: 0 20px 18px 20px;
        margin: 0 0 18px 0;
        border-bottom: 1px solid var(--cover-line);
    }
    .sidebar-logo-fallback {
        color: var(--cover-text);
        font-family: 'Source Serif 4', serif;
        font-weight: 600;
        font-size: 1.15rem;
        margin: 0;
    }

    /* Sidebar navigation — folder tabs, not pill buttons. Each tab is flush
       on the cover; the active one takes on the PAPER color, so it visually
       reads as "this is the page you're on top of" instead of a highlighted
       button among buttons. */
    [data-testid="stPageLink"] { margin-bottom: 2px; padding: 0 12px; }
    [data-testid="stPageLink"] a {
        border-radius: 6px 0 0 6px !important;
        padding: 10px 14px !important;
        font-size: 0.92rem !important;
        font-weight: 500 !important;
        color: var(--ledger-soft) !important;
        background: transparent !important;
        border: none !important;
        border-left: 3px solid transparent !important;
        transition: background 0.12s ease, color 0.12s ease, border-color 0.12s ease;
        opacity: 1 !important;
        width: 100%;
    }
    [data-testid="stPageLink"] a span,
    [data-testid="stPageLink"] p {
        color: inherit !important;
        opacity: 1 !important;
    }
    [data-testid="stPageLink"] a:hover {
        background: var(--cover-line) !important;
        color: var(--cover-text) !important;
    }
    /* Active page — rendered in app.py as plain styled markup (NOT a
       st.page_link) for exactly the current page, so this class is ours
       to control completely and never depends on guessing what attribute
       Streamlit puts on its own generated links. */
    .active-nav-item {
        margin: 0 12px 2px 12px;
        padding: 10px 14px;
        border-radius: 6px 0 0 6px;
        background: var(--paper);
        color: var(--ink);
        font-weight: 600;
        font-size: 0.92rem;
        border-left: 3px solid var(--alert);
    }

    /* ============ KPI cards (st.metric) — hairline row, no card box ============ */
    [data-testid="stMetric"] {
        background: transparent;
        border: none;
        border-bottom: 1px solid var(--paper-line);
        padding: 4px 4px 12px 4px;
        border-radius: 0;
    }
    [data-testid="stMetricLabel"] {
        color: var(--ink-soft) !important;
        font-weight: 500;
        font-size: 0.82rem !important;
    }
    [data-testid="stMetricValue"] {
        color: var(--ink) !important;
        font-weight: 600;
        font-size: 1.6rem !important;
    }

    /* ============ Icon KPI cards (custom HTML) — ledger-row style ============ */
    .kpi-row {
        display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 0; margin: 8px 0 20px 0;
        border-top: 1px solid var(--paper-line);
    }
    .kpi-icon-card {
        background: transparent;
        border: none;
        border-bottom: 1px solid var(--paper-line);
        border-right: 1px solid var(--paper-line);
        border-radius: 0;
        padding: 14px 18px;
        display: flex;
        align-items: flex-start;
        gap: 12px;
    }
    .kpi-icon-card .kpi-icon {
        width: 30px; height: 30px; flex-shrink: 0;
        border-radius: 3px;
        background: var(--ledger);
        display: flex; align-items: center; justify-content: center;
    }
    .kpi-icon-card .kpi-icon svg { width: 16px; height: 16px; stroke: var(--paper); }
    .kpi-icon-card .kpi-label { color: var(--ink-soft); font-weight: 500; font-size: 0.78rem; }
    .kpi-icon-card .kpi-value { font-weight: 600; font-size: 1.4rem; color: var(--ink); margin-top: 2px; }
    .kpi-icon-card .kpi-delta { font-size: 0.8rem; font-weight: 500; margin-top: 2px; font-family: 'JetBrains Mono', monospace; }
    .kpi-icon-card .kpi-delta.up { color: var(--ledger); }
    .kpi-icon-card .kpi-delta.down { color: var(--alert); }

    /* ============ Data Quality Score — a stamped seal, not a donut gauge ============ */
    .quality-score-card {
        background: transparent;
        border: 1px dashed var(--ledger-soft);
        border-radius: 4px;
        padding: 18px 22px;
        display: flex; align-items: center; gap: 20px;
        margin: 8px 0 20px 0;
    }
    .quality-score-ring {
        width: 72px; height: 72px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        border: 3px solid var(--ledger);
        flex-shrink: 0;
        transform: rotate(-8deg);
    }
    .quality-score-inner {
        font-weight: 700; font-size: 1.05rem; color: var(--ledger);
        transform: rotate(8deg);
    }
    .quality-score-text h3 { margin: 0 0 4px 0; font-size: 1.05rem; }
    .quality-score-text p { margin: 0; color: var(--ink-soft); font-size: 0.88rem; }

    /* ============ Numbered workflow steps (cleaning audit log) — memo list ============ */
    .workflow-step {
        display: flex; gap: 14px; align-items: flex-start;
        background: transparent; border: none; border-bottom: 1px solid var(--paper-line);
        border-radius: 0;
        padding: 10px 4px; margin: 0;
    }
    .workflow-step .step-num {
        width: 22px; height: 22px; border-radius: 3px; flex-shrink: 0;
        background: var(--ledger);
        color: var(--paper); font-weight: 600; font-size: 0.78rem;
        display: flex; align-items: center; justify-content: center;
    }
    .workflow-step .step-text { color: var(--ink); font-size: 0.92rem; padding-top: 2px; }

    /* ============ Chart panels — flush on the page, ruled off, no card ============ */
    [data-testid="stPlotlyChart"] {
        background: transparent;
        border: none;
        border-top: 1px solid var(--paper-line);
        border-radius: 0;
        padding: 10px 0 0 0;
    }

    /* ============ Filters bar ============ */
    .streamlit-expanderHeader {
        background-color: transparent !important;
        border: none !important;
        border-bottom: 1px solid var(--paper-line) !important;
        border-radius: 0;
        color: var(--ink) !important;
        font-weight: 600;
    }
    [data-testid="stExpander"] {
        background-color: transparent;
        border: none !important;
        border-radius: 0;
    }

    /* Multiselect / slider chips */
    [data-baseweb="tag"] {
        background-color: var(--ledger) !important;
        border-radius: 3px !important;
    }
    .stSlider [data-baseweb="slider"] > div > div { background: var(--ledger) !important; }

    /* ============ Dataframes — ruled ledger table ============ */
    [data-testid="stDataFrame"] {
        background: var(--paper);
        border: none;
        border-top: 1px solid var(--ink);
        border-bottom: 1px solid var(--ink);
        border-radius: 0;
    }

    /* Buttons — flat, no gradient */
    .stButton > button {
        background: var(--ledger);
        color: var(--paper);
        border: none;
        border-radius: 3px;
        font-weight: 600;
        padding: 8px 20px;
    }
    .stButton > button:hover {
        background: var(--ink);
    }

    /* Info boxes */
    [data-testid="stAlert"] {
        background-color: transparent;
        border: none;
        border-left: 3px solid var(--ledger);
        border-radius: 0;
        color: var(--ink);
        padding-left: 14px;
    }

    /* ============ Recommendation memos (severity-styled) ============ */
    .memo-card {
        border: 1px solid var(--paper-line);
        border-radius: 2px;
        padding: 16px 18px;
        margin-bottom: 14px;
        background: var(--paper);
        position: relative;
    }
    .memo-card .memo-title {
        font-family: 'Source Serif 4', serif;
        font-size: 1.05rem;
        font-weight: 600;
        color: var(--ink);
        margin-bottom: 6px;
    }
    .memo-card .memo-detail { color: var(--ink-soft); font-size: 0.92rem; }
    .memo-stamp {
        position: absolute; top: 14px; right: 18px;
        border: 2px solid var(--alert);
        color: var(--alert);
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        font-size: 0.72rem;
        letter-spacing: 1px;
        padding: 3px 9px;
        border-radius: 3px;
        transform: rotate(6deg);
        opacity: 0.85;
    }

    /* ============ Cover page — title page + table of contents ============ */
    .cover-wrap {
        max-width: 620px;
        margin: 30px auto 0 auto;
    }
    .cover-eyebrow {
        color: var(--ink-soft);
        font-size: 0.85rem;
        margin-bottom: 4px;
    }
    .cover-title {
        font-family: 'Source Serif 4', serif;
        font-size: 2.4rem;
        font-weight: 700;
        color: var(--ink);
        margin: 0 0 6px 0;
        border-bottom: 2px solid var(--ledger);
        padding-bottom: 14px;
    }
    .cover-sub {
        color: var(--ink-soft);
        font-size: 0.95rem;
        margin: 10px 0 26px 0;
        line-height: 1.6;
    }
    .toc-heading {
        font-family: 'Source Serif 4', serif;
        font-size: 1.05rem;
        color: var(--ink);
        margin-bottom: 10px;
    }
    .toc-row {
        display: flex;
        align-items: baseline;
        gap: 8px;
        padding: 9px 0;
        border-bottom: 1px dotted var(--paper-line);
    }
    .toc-row .toc-name {
        font-weight: 600;
        color: var(--ink);
        white-space: nowrap;
    }
    .toc-row .toc-leader {
        flex: 1;
        border-bottom: 1px dotted var(--ledger-soft);
        transform: translateY(-4px);
    }
    .toc-row .toc-desc {
        color: var(--ink-soft);
        font-size: 0.85rem;
        white-space: nowrap;
    }

    /* Social links footer — plain text links on the cover, no icon tiles */
    .sidebar-social {
        margin-top: auto;
        padding-top: 16px;
        border-top: 1px solid var(--cover-line);
        display: flex;
        justify-content: center;
        gap: 14px;
    }
    .sidebar-social a {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        border-radius: 3px;
        background: transparent;
        border: 1px solid var(--cover-line);
        transition: border-color 0.12s ease;
    }
    .sidebar-social a:hover {
        border-color: var(--cover-text);
    }
    .sidebar-social svg { width: 16px; height: 16px; fill: var(--cover-text); }

    hr { border-color: var(--paper-line) !important; }
    </style>
    """, unsafe_allow_html=True)


def render_sidebar_logo():
    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.jpeg")
    with st.sidebar:
        st.markdown('<div class="sidebar-logo-card">', unsafe_allow_html=True)
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
    to render_kpi_row() — single-line string on purpose (Markdown treats
    indented multi-line HTML as a code block otherwise)."""
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
    """A stamped seal instead of a circular percentage gauge — score_pct is 0-100."""
    subtitle = subtitle or "Based on completeness, duplicates, and outlier checks on this dataset."
    st.markdown(
        f'<div class="quality-score-card">'
        f'<div class="quality-score-ring">'
        f'<div class="quality-score-inner">{score_pct:.0f}%</div></div>'
        f'<div class="quality-score-text"><h3>{title}</h3><p>{subtitle}</p></div></div>',
        unsafe_allow_html=True,
    )


def render_workflow_steps(steps):
    """steps: list of plain-text strings (e.g. the cleaning audit log)."""
    html = "".join(
        f'<div class="workflow-step"><div class="step-num">{i}</div>'
        f'<div class="step-text">{step}</div></div>'
        for i, step in enumerate(steps, 1)
    )
    st.markdown(html, unsafe_allow_html=True)


def render_toc(items):
    """items: list of (name, description) tuples — rendered as a dotted
    table-of-contents list, like the front page of a bound register."""
    rows = "".join(
        f'<div class="toc-row"><span class="toc-name">{name}</span>'
        f'<span class="toc-leader"></span><span class="toc-desc">{desc}</span></div>'
        for name, desc in items
    )
    st.markdown(f'<div class="toc-heading">Contents</div>{rows}', unsafe_allow_html=True)


def render_memo_card(title, detail, severity="low"):
    """A recommendation styled as an interoffice memo. severity='high' gets
    a rotated 'URGENT' stamp; 'medium'/'low' render as a plain memo."""
    stamp = '<div class="memo-stamp">URGENT</div>' if severity == "high" else ""
    st.markdown(
        f'<div class="memo-card">{stamp}'
        f'<div class="memo-title">{title}</div>'
        f'<div class="memo-detail">{detail}</div></div>',
        unsafe_allow_html=True,
    )
