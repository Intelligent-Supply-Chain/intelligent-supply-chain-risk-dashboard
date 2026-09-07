import pandas as pd

df = pd.read_csv("../data/parts_master.csv")

print("First 5 rows:")
print(df.head())

print("\nDataset Shape:")
print(df.shape)

print("\nColumn Names:")
print(df.columns)

print("\nDataset Information:")
df.info()

print("\nMissing Values:")
print(df.isnull().sum())

print("\nDuplicate Rows:")
print(df.duplicated().sum())

print("\nStatistical Summary:")
print(df.describe())

print("\nCriticality Distribution:")
print(df["criticality_class"].value_counts())

print("\nPart Family Distribution:")
print(df["part_family"].value_counts())

print("\nSupplier Risk Distribution:")
print(df["supplier_risk_class"].value_counts())

print("\nRepairability Distribution:")
print(df["is_repairable"].value_counts())

print("\nNumber of Unique Suppliers:")
print(df["supplier_id_primary"].nunique())

print("\nNumber of Unique Parts:")
print(df["part_id"].nunique())

print("\n===== PART ANALYSIS =====")

print("\nAverage Unit Cost by Part Family:")
print(
    df.groupby("part_family")["unit_cost"]
    .mean()
    .sort_values(ascending=False)
)

print("\nAverage Lead Time by Part Family:")
print(
    df.groupby("part_family")["lead_time_days"]
    .mean()
    .sort_values(ascending=False)
)

print("\nAverage Unit Cost by Criticality:")
print(
    df.groupby("criticality_class")["unit_cost"]
    .mean()
    .sort_values(ascending=False)
)

print("\nAverage Lead Time by Criticality:")
print(
    df.groupby("criticality_class")["lead_time_days"]
    .mean()
    .sort_values(ascending=False)
)

print("\nParts Supplied by Each Supplier:")
print(
    df["supplier_id_primary"]
    .value_counts()
)

print("\nAverage Unit Cost by Supplier Risk:")
print(
    df.groupby("supplier_risk_class")["unit_cost"]
    .mean()
    .sort_values(ascending=False)
)

print("\n===== PART EXPOSURE PROFILE =====")

profile = df[
    [
        "part_id",
        "part_family",
        "criticality_class",
        "unit_cost",
        "lead_time_days",
        "supplier_risk_class",
        "is_repairable"
    ]
].copy()

print("\nTop 10 Highest Cost Parts:")
print(
    profile.sort_values(
        "unit_cost",
        ascending=False
    ).head(10)
)

print("\nTop 10 Longest Lead-Time Parts:")
print(
    profile.sort_values(
        "lead_time_days",
        ascending=False
    ).head(10)
)