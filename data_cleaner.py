"""
data_cleaner.py
----------------
Cleaning logic that operates ONLY on canonical field names (never on
raw column names from any specific source file). This is what keeps
it dataset-agnostic: swap the CSV, the mapper re-maps it to canonical
fields, and this module cleans it the exact same way every time.

Rules (as agreed):
- A missing value is not automatically deleted or blindly filled.
- 'termination_date' being empty means "still employed" — not missing data.
- Categorical fields: safe to fill with "Unknown" (loses no information).
- Numeric fields: fill with median ONLY if missing % is below a safe
  threshold; otherwise leave as-is and flag it for manual review.
- Outliers are reported, never silently removed (they're usually real
  business values, e.g. executive salaries).
- Duplicate rows are removed (never valid in employee-level data).
"""

NUMERIC_FIELDS = [
    "salary", "engagement_score", "satisfaction_score",
    "absences", "days_late", "special_projects_count",
]
CATEGORICAL_FIELDS = [
    "department", "position", "manager_name", "gender",
    "recruitment_source", "termination_reason", "employment_status",
]
MISSING_THRESHOLD = 0.30  # don't auto-impute a column if >30% is missing


def clean_standard_data(df):
    """
    Input: a DataFrame already mapped to canonical field names
           (i.e. the output of schema_mapper.apply_mapping).
    Returns: (cleaned_df, audit_log) where audit_log is a list of
             human-readable strings describing exactly what was done.
    """
    df = df.copy()
    log = []

    # 1. termination_date: empty means "still active", not missing data
    if "termination_date" in df.columns:
        still_active = int(df["termination_date"].isna().sum())
        log.append(
            f"'termination_date' is empty for {still_active} employees — "
            f"treated as still active, not as missing data."
        )

    # 2. duplicate rows
    dup_count = int(df.duplicated().sum())
    if dup_count > 0:
        df = df.drop_duplicates()
        log.append(f"Removed {dup_count} fully duplicate row(s).")
    else:
        log.append("No duplicate rows found.")

    # 3. categorical fields -> safe to fill with "Unknown" (and strip stray whitespace)
    for col in CATEGORICAL_FIELDS:
        if col in df.columns:
            df[col] = df[col].astype("string").str.strip()
            missing = int(df[col].isna().sum())
            if missing > 0:
                df[col] = df[col].fillna("Unknown")
                log.append(f"'{col}': filled {missing} missing value(s) with 'Unknown'.")

    # 4. numeric fields -> median only if missing % is safely low
    for col in NUMERIC_FIELDS:
        if col not in df.columns:
            continue
        missing = int(df[col].isna().sum())
        if missing == 0:
            continue
        pct = missing / len(df)
        if pct <= MISSING_THRESHOLD:
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
            log.append(
                f"'{col}': filled {missing} missing value(s) ({pct:.0%}) with the median ({median_val:.1f})."
            )
        else:
            log.append(
                f"'{col}': {missing} missing value(s) ({pct:.0%}) — too high to safely impute automatically. "
                f"Left as-is; needs manual review."
            )

    # 5. outliers -> report only, never altered
    for col in NUMERIC_FIELDS:
        if col not in df.columns or df[col].notna().sum() == 0:
            continue
        q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        iqr = q3 - q1
        if iqr > 0:
            mask = (df[col] < q1 - 1.5 * iqr) | (df[col] > q3 + 1.5 * iqr)
            n_out = int(mask.sum())
            if n_out > 0:
                log.append(
                    f"'{col}': {n_out} statistical outlier(s) detected and kept "
                    f"(treated as real business values, not errors)."
                )

    return df, log
