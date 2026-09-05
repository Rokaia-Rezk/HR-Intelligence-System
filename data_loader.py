import os
import pandas as pd
import streamlit as st
from schema_mapper import auto_map, apply_mapping, save_mapping, load_mapping
from data_cleaner import clean_standard_data

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_FILE = "HRDataset_v14.csv"
SOURCE_NAME = "hrdataset_v14"

NUMERIC_CANONICAL_FIELDS = ["salary", "engagement_score", "satisfaction_score",
                            "absences", "days_late", "special_projects_count"]
DATE_CANONICAL_FIELDS = ["hire_date", "termination_date"]


def cast_canonical_types(df):
    """Numeric/date casting shared by the default loader AND the upload
    page (views/upload_data.py) — one place to keep them consistent."""
    df = df.copy()
    for col in NUMERIC_CANONICAL_FIELDS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    for col in DATE_CANONICAL_FIELDS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def add_is_active(df):
    df = df.copy()
    if "termination_date" in df.columns:
        df["is_active"] = df["termination_date"].isna()
    else:
        df["is_active"] = True
    return df


def find_dataset_path():
    for file in os.listdir(BASE_DIR):
        if file.lower() == "hrdataset_v14.csv":
            return os.path.join(BASE_DIR, file)
        elif file.lower().endswith((".csv", ".xlsx", ".xls")):
            return os.path.join(BASE_DIR, file)
    return os.path.join(BASE_DIR, SOURCE_FILE)


@st.cache_data
def _load_default_raw_data():
    """Raw data, exactly as it exists in the bundled sample file — no
    mapping, no cleaning. Cached because this file never changes during
    a session (unlike an upload, which can change any time)."""
    path = find_dataset_path()
    if path.endswith((".xlsx", ".xls")):
        df = pd.read_excel(path)
    else:
        df = pd.read_csv(path)
    return df


@st.cache_data
def _load_default_mapped_data() -> pd.DataFrame:
    """Bundled sample data translated to canonical field names + type
    casting. Not cleaned yet — the pure 'schema adapter' output."""
    df_raw = _load_default_raw_data()
    df_raw.columns = df_raw.columns.str.strip()

    mapping = load_mapping(SOURCE_NAME)
    if mapping is None:
        mapping, unmatched = auto_map(df_raw.columns)
        save_mapping(mapping, SOURCE_NAME)

    df = apply_mapping(df_raw, mapping)
    return cast_canonical_types(df)


@st.cache_data
def _load_default_standard_data_with_audit():
    df = _load_default_mapped_data()
    df_clean, log = clean_standard_data(df)
    df_clean = add_is_active(df_clean)
    return df_clean, log


def load_raw_data():
    """Raw data for whichever dataset is currently active — a
    user-uploaded file (see views/upload_data.py) if one has been
    confirmed this session, otherwise the bundled sample CSV. Every
    analytics page calls this same function either way, so nothing
    downstream needs to know or care which source is live."""
    if st.session_state.get("uploaded_raw_df") is not None:
        return st.session_state["uploaded_raw_df"]
    return _load_default_raw_data()


def load_mapped_data() -> pd.DataFrame:
    if st.session_state.get("uploaded_mapped_df") is not None:
        return st.session_state["uploaded_mapped_df"]
    return _load_default_mapped_data()


def load_standard_data() -> pd.DataFrame:
    df, _log = load_standard_data_with_audit()
    return df


def load_standard_data_with_audit():
    if st.session_state.get("uploaded_standard_df") is not None:
        return st.session_state["uploaded_standard_df"], st.session_state.get("uploaded_audit_log", [])
    return _load_default_standard_data_with_audit()


def active_dataset_name():
    """For display only — what to call the currently active dataset,
    wherever a page wants to show it (e.g. 'Active dataset: X')."""
    return st.session_state.get("uploaded_file_name", SOURCE_FILE)


def field_has_data(field_name):
    """True if a canonical field has at least one real value in the
    CURRENTLY ACTIVE dataset (default or uploaded).

    Checked against load_mapped_data() — before cleaning — on purpose:
    clean_standard_data() fills every missing categorical value with
    'Unknown', so checking the cleaned data would make a field that was
    100% absent in the source look like it "has data" (a column full of
    the placeholder word). Numeric fields are never auto-filled at 100%
    missing, so for them pre- and post-cleaning give the same answer
    anyway — this one check works correctly for both kinds of field.

    Pages use this to hide a whole page (app.py) or an individual
    chart/section (inside a page) when the field behind it is simply
    not present in whatever dataset is currently loaded, instead of
    crashing on NaN or rendering an empty/"nan"-labelled chart."""
    df = load_mapped_data()
    return field_name in df.columns and df[field_name].notna().any()
