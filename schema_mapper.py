"""
schema_mapper.py
-----------------
Maps the real columns of ANY incoming HR CSV to the CANONICAL_FIELDS
defined in canonical_schema.py.

Flow:
    1. auto_map(columns)      -> best-guess mapping + list of unmatched canonical fields
    2. (optional) human fills in the gaps for fields it couldn't guess
    3. save_mapping(...)      -> remembers this file's mapping for next time
    4. apply_mapping(df, ...) -> returns a new DataFrame using ONLY canonical
                                  column names, ready for the dashboard/model

Because everything downstream only ever sees canonical column names,
swapping the source CSV for a different one just means re-running this
mapping step (auto, or with one-time manual confirmation) -- nothing
else in the app has to change.
"""

import json
import os
import difflib
from canonical_schema import CANONICAL_FIELDS, normalize

CONFIG_DIR = os.path.join(os.path.dirname(__file__), "config")
os.makedirs(CONFIG_DIR, exist_ok=True)


def auto_map(raw_columns):
    """
    Try to match each canonical field to one of the raw_columns.

    Returns:
        mapping: dict {canonical_field: raw_column_or_None}
        unmatched: list of canonical field names that need a human decision
    """
    normalized_lookup = {normalize(col): col for col in raw_columns}
    mapping = {}
    unmatched = []

    for field, meta in CANONICAL_FIELDS.items():
        match = None

        # 1) exact match against any alias (fast path)
        for alias in meta["aliases"]:
            if normalize(alias) in normalized_lookup:
                match = normalized_lookup[normalize(alias)]
                break

        # 2) fuzzy match fallback (handles typos / slightly different naming)
        if match is None:
            candidates = list(normalized_lookup.keys())
            for alias in meta["aliases"]:
                close = difflib.get_close_matches(
                    normalize(alias), candidates, n=1, cutoff=0.82
                )
                if close:
                    match = normalized_lookup[close[0]]
                    break

        mapping[field] = match
        if match is None and meta["required"]:
            unmatched.append(field)

    return mapping, unmatched


def save_mapping(mapping, source_name):
    """Persist a confirmed mapping so the same file (or same-shaped
    file) doesn't need to be re-mapped by hand next time."""
    path = os.path.join(CONFIG_DIR, f"{source_name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)
    return path


def load_mapping(source_name):
    path = os.path.join(CONFIG_DIR, f"{source_name}.json")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def apply_mapping(df, mapping):
    """
    Return a new DataFrame with canonical column names only.
    Canonical fields that had no match are created as empty (NaN) columns
    so downstream code can always rely on the full canonical schema
    being present, even if a given source file was missing that field.
    """
    import pandas as pd

    out = pd.DataFrame(index=df.index)
    for field, raw_col in mapping.items():
        if raw_col is not None and raw_col in df.columns:
            out[field] = df[raw_col]
        else:
            out[field] = pd.NA
    return out
