import os
import pandas as pd
import streamlit as st
from schema_mapper import auto_map, apply_mapping, save_mapping, load_mapping
from data_cleaner import clean_standard_data

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_FILE = "HRDataset_v14.csv"
SOURCE_NAME = "hrdataset_v14"


def find_dataset_path():
    for file in os.listdir(BASE_DIR):
        if file.lower() == "hrdataset_v14.csv":
            return os.path.join(BASE_DIR, file)
        elif file.lower().endswith((".csv", ".xlsx", ".xls")):
            return os.path.join(BASE_DIR, file)
    return os.path.join(BASE_DIR, SOURCE_FILE)


@st.cache_data
def load_raw_data():
    """Raw data, exactly as it exists in the source file — no mapping, no cleaning."""
    path = find_dataset_path()
    if path.endswith((".xlsx", ".xls")):
        df = pd.read_excel(path)
    else:
        df = pd.read_csv(path)
    return df


@st.cache_data
def load_mapped_data() -> pd.DataFrame:
    """Raw data translated to canonical field names + basic type casting.
    Not cleaned yet — this is the pure 'schema adapter' output."""
    df_raw = load_raw_data()
    df_raw.columns = df_raw.columns.str.strip()

    mapping = load_mapping(SOURCE_NAME)
    if mapping is None:
        mapping, unmatched = auto_map(df_raw.columns)
        save_mapping(mapping, SOURCE_NAME)

    df = apply_mapping(df_raw, mapping)

    for col in ["salary", "engagement_score", "satisfaction_score",
                "absences", "days_late", "special_projects_count"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in ["hire_date", "termination_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    return df


@st.cache_data
def load_standard_data() -> pd.DataFrame:
    """What every analytics page should use: mapped + cleaned canonical data."""
    df, _log = load_standard_data_with_audit()
    return df


@st.cache_data
def load_standard_data_with_audit():
    """Same as load_standard_data, but also returns the cleaning audit log
    (what was actually done to this specific dataset, generated dynamically)."""
    df = load_mapped_data()
    df_clean, log = clean_standard_data(df)

    if "termination_date" in df_clean.columns:
        df_clean["is_active"] = df_clean["termination_date"].isna()
    else:
        df_clean["is_active"] = True

    return df_clean, log
