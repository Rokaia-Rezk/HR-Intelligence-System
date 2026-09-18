"""
filters.py
----------
Shared slicer widgets + chart styling used across analytics pages.
Department and Employment Status are common to every page; each page
adds one more slicer relevant to its own topic (salary range,
performance tier, absence range, recruitment source...).

Palette updated to match style.py's "Personnel Ledger" theme (paper +
ledger green + brick alert) — no purple/gradient left in the charts.
"""

import pandas as pd
import streamlit as st

CHART_HEIGHT = 380  # every chart on every page uses this same height

PAPER = "#F6F3EC"
PAPER_LINE = "#DED5C0"
INK = "#1E2A24"
INK_SOFT = "#5B6259"
LEDGER = "#2F4B3C"
LEDGER_SOFT = "#7C8F82"
ALERT = "#8C3B2E"

# A palette with real contrast between steps for pies / stacked bars where
# multiple categories sit side by side and need to be told apart at a
# glance — built as tonal steps of ledger-green + one warm accent, instead
# of a purple gradient family.
DISTINCT_PALETTE = ["#2F4B3C", "#7C8F82", "#8C3B2E", "#B79C6B", "#4C6558", "#C9BFA3"]


def department_status_filters(df, key_prefix, col1, col2):
    """Renders Department + Employment Status multiselects into the given
    st.columns, returns the filtered dataframe."""
    with col1:
        departments = sorted(df["department"].dropna().unique().tolist())
        selected_depts = st.multiselect(
            "Department", departments, default=departments, key=f"{key_prefix}_dept"
        )
    with col2:
        statuses = ["Active", "Terminated"]
        selected_status = st.multiselect(
            "Employment Status", statuses, default=statuses, key=f"{key_prefix}_status"
        )

    if not selected_depts or not selected_status:
        return df.iloc[0:0]

    filtered = df[df["department"].isin(selected_depts)]
    mask = pd.Series(False, index=filtered.index)
    if "Active" in selected_status:
        mask = mask | filtered["is_active"]
    if "Terminated" in selected_status:
        mask = mask | ~filtered["is_active"]
    return filtered[mask]


def style_fig(fig):
    """Apply the shared ledger/paper theme + fixed height to any plotly
    figure. Charts render on the same paper tone as the page (not a white
    card) since they now sit flush against it, ruled off by a hairline
    (see [data-testid="stPlotlyChart"] in style.py) instead of boxed.

    automargin=True on both axes lets Plotly grow its own margin to fit
    long department names / $ salary ticks instead of a fixed guess.
    """
    fig.update_layout(
        plot_bgcolor=PAPER,
        paper_bgcolor=PAPER,
        font_color=INK,
        font_family="Inter, sans-serif",
        height=CHART_HEIGHT,
        margin=dict(l=10, r=10, t=30, b=10),
        title_font_color=INK,
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
    fig.update_xaxes(gridcolor=PAPER_LINE, zerolinecolor=PAPER_LINE, color=INK_SOFT,
                      automargin=True, title_standoff=10)
    fig.update_yaxes(gridcolor=PAPER_LINE, zerolinecolor=PAPER_LINE, color=INK_SOFT,
                      automargin=True, title_standoff=10)
    return fig


def style_slices(fig):
    """For pie / stacked-bar figures: adds a paper-colored border around
    every slice/segment so adjacent tonal shades stay visually separated
    instead of blending into one blob."""
    fig.update_traces(marker=dict(line=dict(color=PAPER, width=2)))
    return fig


def get_click_index(key):
    """Read a plotly chart's current click selection (a category point
    index) straight from session_state, without needing that chart to
    render first in the current script run. This is what makes
    click-to-filter cross-filtering possible: every OTHER chart on the
    page can know what was clicked before it builds its own data,
    regardless of render order.

    Handles both shapes Streamlit's on_select return value can take
    depending on version: an object with attribute access
    (ev.selection.points) or a plain dict (ev["selection"]["points"]).
    """
    ev = st.session_state.get(key)
    if ev is None:
        return None

    selection = getattr(ev, "selection", None)
    if selection is None and isinstance(ev, dict):
        selection = ev.get("selection")
    if selection is None:
        return None

    points = getattr(selection, "points", None)
    if points is None and isinstance(selection, dict):
        points = selection.get("points")
    if not points:
        return None

    first = points[0]
    if isinstance(first, dict):
        return first.get("point_index") if first.get("point_index") is not None else first.get("pointIndex")
    return getattr(first, "point_index", None)
