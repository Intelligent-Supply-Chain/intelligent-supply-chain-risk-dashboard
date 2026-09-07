import pandas as pd

df = pd.read_csv("../data/purchase_orders.csv")

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
print("Order Start:", df["order_date"].min())
print("Order End:", df["order_date"].max())

print("\nUnique Suppliers:")
print(df["supplier_id"].nunique())

print("\nUnique Sites:")
print(df["site_id"].nunique())

print("\nUnique Parts:")
print(df["part_id"].nunique())

print("\nOrders With Partial Delivery:")
print((df["received_qty"] < df["ordered_qty"]).sum())

print("\nOrders With Full Delivery:")
print((df["received_qty"] == df["ordered_qty"]).sum())

print("\nOrders With Excess Delivery:")
print((df["received_qty"] > df["ordered_qty"]).sum())