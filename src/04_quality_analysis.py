import pandas as pd

df = pd.read_csv("../data/quality_incidents.csv")

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

print("\nDate Range:")
print("Start:", df["incident_date"].min())
print("End:", df["incident_date"].max())

print("\nUnique Suppliers:")
print(df["supplier_id"].nunique())

print("\nUnique Sites:")
print(df["site_id"].nunique())

print("\nUnique Parts:")
print(df["part_id"].nunique())

print("\nDefect Severity:")
print(df["defect_severity"].value_counts())

print("\nDefect Types:")
print(df["defect_type"].value_counts())

print("\nTotal Scrap Quantity:")
print(df["scrap_qty"].sum())