import streamlit as st
from data_loader import load_mapped_data, load_standard_data_with_audit

st.title("Data Health & Automated Audit")
st.markdown("Schema mapping, dynamic validation, and rule-based cleaning — runs fresh on whatever dataset is currently loaded.")

df_before = load_mapped_data()          # mapped to canonical fields, NOT cleaned yet
df_after, audit_log = load_standard_data_with_audit()   # mapped AND cleaned

st.subheader("Before Cleaning (raw, mapped to canonical fields)")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Records", len(df_before))
c2.metric("Missing Cells", int(df_before.isna().sum().sum()))
c3.metric("Duplicate Rows", int(df_before.duplicated().sum()))
avg_sal_before = df_before["salary"].mean()
c4.metric("Average Compensation", f"${avg_sal_before:,.0f}" if avg_sal_before == avg_sal_before else "N/A")

st.subheader("After Cleaning")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Records", len(df_after), delta=f"{len(df_after) - len(df_before)}")
c2.metric("Missing Cells", int(df_after.isna().sum().sum()),
          delta=f"{int(df_after.isna().sum().sum()) - int(df_before.isna().sum().sum())}")
c3.metric("Active Workforce", int(df_after["is_active"].sum()))
c4.metric("Average Compensation", f"${df_after['salary'].mean():,.0f}")

st.divider()

st.subheader("What was found, and what was done about it")
st.caption("Generated dynamically from this specific dataset — not a fixed script. Swap the CSV and this list changes with it.")
for line in audit_log:
    st.info(line)

st.divider()

st.subheader("Cleaned data preview (canonical fields)")
st.dataframe(df_after.head(10), use_container_width=True)

st.success("Data is mapped, cleaned, and ready. Continue to the analytics pages from the sidebar.")
