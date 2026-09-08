import pandas as pd

from column_mapper import (
    detect_columns,
    apply_column_mapping
)

from risk_engine import calculate_risk_scores


# --------------------------------------------------
# LOAD INDUSTRIAL DATA
# --------------------------------------------------

file_path = "data/industry_test_data.csv"

df = pd.read_csv(file_path)


print("\n===== ORIGINAL COMPANY DATA =====")

print(df.head())


# --------------------------------------------------
# DETECT COMPANY COLUMNS
# --------------------------------------------------

mapping = detect_columns(df)


print("\n===== DETECTED COLUMN MAPPING =====")

for standard, original in mapping.items():

    print(
        f"{original}  →  {standard}"
    )


# --------------------------------------------------
# STANDARDIZE DATA
# --------------------------------------------------

df = apply_column_mapping(
    df,
    mapping
)


print("\n===== STANDARDIZED DATA =====")

print(df.head())


# --------------------------------------------------
# CALCULATE RISK
# --------------------------------------------------

df = calculate_risk_scores(df)


print("\n===== FINAL RISK ANALYSIS =====")

print(
    df[
        [
            "part_id",
            "supplier_id_primary",
            "predicted_risk_score",
            "predicted_risk_category"
        ]
    ]
)


# --------------------------------------------------
# RISK SUMMARY
# --------------------------------------------------

print("\n===== RISK SUMMARY =====")

print(
    df["predicted_risk_category"]
    .value_counts()
)


print("\n===== INDUSTRIAL DATASET TEST COMPLETED =====")