"""
upload_data.py
---------------
The missing piece of "dataset-agnostic": an actual upload UI. Before
this, canonical_schema.py + schema_mapper.py could adapt to any HR
file in principle, but only the bundled HRDataset_v14.csv was ever
actually loaded — there was no way for someone else's HR export to
reach that pipeline at all.

Flow:
  1. Upload a CSV/XLSX.
  2. auto_map() guesses a mapping the same way it always has.
  3. Every canonical field gets a dropdown, pre-filled with the guess
     (or blank if auto-map couldn't find one) — the user confirms or
     corrects every field, not just the ones auto-map missed, since a
     wrong confident guess is worse than an unmatched one.
  4. On confirm: required fields must all be mapped to something, then
     the exact same apply_mapping -> type casting -> clean_standard_data
     pipeline every other dataset goes through runs on this one too.
  5. Results go in st.session_state, which data_loader.py now checks
     first — every other page picks this up with zero changes needed.
"""

import pandas as pd
import streamlit as st

from canonical_schema import CANONICAL_FIELDS
from schema_mapper import auto_map, apply_mapping
from data_cleaner import clean_standard_data
from data_loader import cast_canonical_types, add_is_active, active_dataset_name

st.title("Upload Your Own HR Data")
st.caption("Swap the sample dataset for your own HR export. Any reasonably-shaped HR file works — "
           "you'll confirm which of your columns maps to what before anything runs.")

current_source = active_dataset_name()
is_uploaded = st.session_state.get("uploaded_standard_df") is not None

if is_uploaded:
    st.success(f"Currently active dataset: **{current_source}** (uploaded)")
    if st.button("Switch back to the sample dataset"):
        for k in ["uploaded_raw_df", "uploaded_mapped_df", "uploaded_standard_df",
                  "uploaded_audit_log", "uploaded_file_name", "pending_raw_df"]:
            st.session_state.pop(k, None)
        st.rerun()
    st.divider()
else:
    st.info(f"Currently active dataset: **{current_source}** (bundled sample)")

uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx", "xls"])
st.caption("Limit 200MB per file. Working with a much bigger export? Sample it down first — "
           "a few thousand rows is plenty to demonstrate the pipeline.")

if uploaded_file is not None:
    try:
        if uploaded_file.name.lower().endswith((".xlsx", ".xls")):
            df_raw = pd.read_excel(uploaded_file)
        else:
            df_raw = pd.read_csv(uploaded_file)
        df_raw.columns = df_raw.columns.str.strip()
    except Exception as e:
        st.error(f"Couldn't read that file: {e}")
        st.stop()

    if df_raw.empty or len(df_raw.columns) == 0:
        st.error("That file has no columns Streamlit could read — check it's a valid CSV/Excel file.")
        st.stop()

    st.session_state["pending_raw_df"] = df_raw
    st.session_state["pending_file_name"] = uploaded_file.name

# Work off whatever was uploaded most recently in this session, so the
# mapping UI below survives the widget reruns that happen as the user
# changes dropdowns (file_uploader itself doesn't need to be re-touched).
df_raw = st.session_state.get("pending_raw_df")

if df_raw is not None:
    st.subheader(f"Confirm column mapping — {st.session_state.get('pending_file_name', 'your file')}")
    st.caption(f"{len(df_raw)} rows, {len(df_raw.columns)} columns detected. "
               "Every field below is pre-filled with a best guess where one was found — "
               "check it, and fix anything that's wrong or missing (required fields are marked).")

    with st.expander("Preview raw data (first 5 rows)"):
        st.dataframe(df_raw.head(5), width="stretch")

    auto_mapping, unmatched_required = auto_map(df_raw.columns)
    raw_columns = list(df_raw.columns)
    NOT_PRESENT = "— not present —"
    options = [NOT_PRESENT] + raw_columns

    confirmed_mapping = {}
    missing_required = []

    for field, meta in CANONICAL_FIELDS.items():
        guessed = auto_mapping.get(field)
        default_index = options.index(guessed) if guessed in options else 0
        label = f"{field} {'(required)' if meta['required'] else ''}".strip()
        chosen = st.selectbox(
            label, options, index=default_index, key=f"map_{field}",
            help=meta["description"],
        )
        confirmed_mapping[field] = None if chosen == NOT_PRESENT else chosen
        if meta["required"] and confirmed_mapping[field] is None:
            missing_required.append(field)

    if missing_required:
        st.warning(f"Still need a column for: {', '.join(missing_required)} — "
                   "these are required for the analytics pages to work.")

    if st.button("Apply Mapping & Load Data", disabled=bool(missing_required)):
        mapped_df = apply_mapping(df_raw, confirmed_mapping)
        mapped_df = cast_canonical_types(mapped_df)
        standard_df, audit_log = clean_standard_data(mapped_df)
        standard_df = add_is_active(standard_df)

        st.session_state["uploaded_raw_df"] = df_raw
        st.session_state["uploaded_mapped_df"] = mapped_df
        st.session_state["uploaded_standard_df"] = standard_df
        st.session_state["uploaded_audit_log"] = audit_log
        st.session_state["uploaded_file_name"] = st.session_state.get("pending_file_name", "uploaded file")
        st.session_state.pop("pending_raw_df", None)
        st.session_state.pop("pending_file_name", None)

        st.success(f"Loaded {len(standard_df)} employees. Every page in the sidebar now uses this dataset — "
                   "head to Home or Data Cleaning to see it.")
        st.rerun()
