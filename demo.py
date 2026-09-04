import pandas as pd
from schema_mapper import auto_map, save_mapping, apply_mapping

SOURCE_FILE = "HRDataset_v14.csv"
SOURCE_NAME = "hrdataset_v14"  # used as the config filename

df_raw = pd.read_csv(SOURCE_FILE)
df_raw.columns = df_raw.columns.str.strip()

mapping, unmatched = auto_map(df_raw.columns)

print("=== Auto-mapping result ===")
for field, raw_col in mapping.items():
    status = raw_col if raw_col else "-- NOT FOUND --"
    print(f"  {field:25s} -> {status}")

if unmatched:
    print("\n[!] Required fields with no match (need manual mapping):")
    for f in unmatched:
        print("   -", f)
else:
    print("\nAll required fields matched automatically.")

save_mapping(mapping, SOURCE_NAME)
print(f"\nMapping saved to config/{SOURCE_NAME}.json")

df_standard = apply_mapping(df_raw, mapping)
print("\n=== Standardized dataframe preview (canonical columns) ===")
print(df_standard[["employee_id", "department", "salary", "performance_score",
                    "absences", "days_late", "satisfaction_score"]].head(5).to_string())
