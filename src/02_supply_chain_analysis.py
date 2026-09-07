import pandas as pd
import numpy as np

# Load datasets
parts_df = pd.read_csv("../data/parts_master.csv")
df = pd.read_csv("../data/supply_chain_history.csv")
po_df = pd.read_csv("../data/purchase_orders.csv")
quality_df = pd.read_csv("../data/quality_incidents.csv")

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
print("Start:", df["date"].min())
print("End:", df["date"].max())

print("\nUnique Sites:")
print(df["site_id"].nunique())

print("\nUnique Parts:")
print(df["part_id"].nunique())

print("\nForecast Types:")
print(df["forecast_type"].value_counts())

print("\nPlanned Maintenance:")
print(df["planned_maintenance"].value_counts())

print("\nZero Consumption Records:")
print((df["consumption_qty"] == 0).sum())

print("\nZero Inventory Records:")
print((df["on_hand_qty"] == 0).sum())

print("\nRecords With Backorders:")
print((df["backorder_qty"] > 0).sum())

print("\nRecords With Blocked Inventory:")
print((df["blocked_qty"] > 0).sum())

print("\n===== DEMAND ANALYSIS =====")

print("\nAverage Consumption by Site:")
print(
    df.groupby("site_id")["consumption_qty"]
    .mean()
    .sort_values(ascending=False)
)

print("\nAverage Consumption by Forecast Type:")
print(
    df.groupby("forecast_type")["consumption_qty"]
    .mean()
)

print("\nAverage Consumption During Maintenance:")
print(
    df.groupby("planned_maintenance")["consumption_qty"]
    .mean()
)

print("\nAverage Inventory by Site:")
print(
    df.groupby("site_id")["on_hand_qty"]
    .mean()
    .sort_values(ascending=False)
)

print("\nAverage Backorder by Site:")
print(
    df.groupby("site_id")["backorder_qty"]
    .mean()
    .sort_values(ascending=False)
)

print("\n===== PART-LEVEL DEMAND ANALYSIS =====")

print("\nTop 10 Parts by Average Consumption:")
print(
    df.groupby("part_id")["consumption_qty"]
    .mean()
    .sort_values(ascending=False)
    .head(10)
)

print("\nTop 10 Parts by Total Consumption:")
print(
    df.groupby("part_id")["consumption_qty"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

print("\nTop 10 Parts by Demand Variability:")
print(
    df.groupby("part_id")["consumption_qty"]
    .std()
    .sort_values(ascending=False)
    .head(10)
)

print("\n===== DEMAND + PART CHARACTERISTICS =====")

part_demand = (
    df.groupby("part_id")
    .agg(
        avg_demand=("consumption_qty", "mean"),
        demand_std=("consumption_qty", "std"),
        total_demand=("consumption_qty", "sum"),
        avg_inventory=("on_hand_qty", "mean"),
        total_backorders=("backorder_qty", "sum")
    )
    .reset_index()
)

part_profile = part_demand.merge(
    parts_df[
        [
            "part_id",
            "part_family",
            "criticality_class",
            "unit_cost",
            "lead_time_days",
            "supplier_risk_class",
            "is_repairable"
        ]
    ],
    on="part_id",
    how="left"
)

print("\nTop 15 Parts by Average Demand:")
print(
    part_profile
    .sort_values("avg_demand", ascending=False)
    .head(15)
)

print("\n===== INVENTORY HEALTH ANALYSIS =====")

part_inventory = (
    df.groupby("part_id")
    .agg(
        avg_demand=("consumption_qty", "mean"),
        avg_inventory=("on_hand_qty", "mean"),
        max_demand=("consumption_qty", "max"),
        avg_backorder=("backorder_qty", "mean"),
        total_backorder=("backorder_qty", "sum"),
        avg_blocked=("blocked_qty", "mean")
    )
    .reset_index()
)

part_inventory["inventory_coverage"] = (
    part_inventory["avg_inventory"] /
    part_inventory["avg_demand"]
)

print("\nTop 15 Parts with Lowest Inventory Coverage:")

print(
    part_inventory
    .sort_values("inventory_coverage")
    .head(15)
)

print("\n===== INVENTORY + PART RISK PROFILE =====")

inventory_profile = part_inventory.merge(
    parts_df[
        [
            "part_id",
            "part_family",
            "criticality_class",
            "unit_cost",
            "lead_time_days",
            "supplier_risk_class",
            "is_repairable"
        ]
    ],
    on="part_id",
    how="left"
)

print("\nParts with Lowest Inventory Coverage + Part Characteristics:")

print(
    inventory_profile
    .sort_values("inventory_coverage")
    .head(15)
    .to_string(index=False)
)

print("\n===== BACKORDER ANALYSIS =====")

print("\nTop 15 Parts by Total Backorders:")

print(
    inventory_profile[
        [
            "part_id",
            "part_family",
            "criticality_class",
            "unit_cost",
            "lead_time_days",
            "supplier_risk_class",
            "avg_demand",
            "avg_inventory",
            "total_backorder",
            "inventory_coverage"
        ]
    ]
    .sort_values("total_backorder", ascending=False)
    .head(15)
    .to_string(index=False)
)

print("\n===== SUPPLIER DELIVERY PERFORMANCE =====")

po_df = pd.read_csv("../data/purchase_orders.csv")

po_df["order_date"] = pd.to_datetime(po_df["order_date"])
po_df["promised_date"] = pd.to_datetime(po_df["promised_date"])
po_df["receipt_date"] = pd.to_datetime(po_df["receipt_date"])

po_df["delivery_delay_days"] = (
    po_df["receipt_date"] - po_df["promised_date"]
).dt.days

po_df["delivery_status"] = np.where(
    po_df["delivery_delay_days"] > 0,
    "Late",
    "On Time"
)

supplier_performance = (
    po_df.groupby("supplier_id")
    .agg(
        total_orders=("po_id", "count"),
        avg_delay_days=("delivery_delay_days", "mean"),
        late_orders=("delivery_status", lambda x: (x == "Late").sum()),
        total_ordered=("ordered_qty", "sum"),
        total_received=("received_qty", "sum")
    )
    .reset_index()
)

supplier_performance["late_delivery_rate"] = (
    supplier_performance["late_orders"] /
    supplier_performance["total_orders"]
)

supplier_performance["fill_rate"] = (
    supplier_performance["total_received"] /
    supplier_performance["total_ordered"]
)

print(
    supplier_performance
    .sort_values("late_delivery_rate", ascending=False)
    .head(15)
    .to_string(index=False)
)

print("\n===== SUPPLIER-PART RISK ANALYSIS =====")

supplier_risk = supplier_performance[
    [
        "supplier_id",
        "avg_delay_days",
        "late_delivery_rate",
        "fill_rate"
    ]
]

supplier_part_analysis = parts_df.merge(
    supplier_risk,
    left_on="supplier_id_primary",
    right_on="supplier_id",
    how="left"
)

print("\nParts supplied by suppliers with highest late-delivery rates:")

print(
    supplier_part_analysis[
        [
            "part_id",
            "part_family",
            "criticality_class",
            "unit_cost",
            "lead_time_days",
            "supplier_id_primary",
            "supplier_risk_class",
            "avg_delay_days",
            "late_delivery_rate",
            "fill_rate"
        ]
    ]
    .sort_values("late_delivery_rate", ascending=False)
    .head(20)
    .to_string(index=False)
)

print("\n===== SUPPLIER PERFORMANCE + BACKORDER ANALYSIS =====")

# Supplier performance for each part
part_supplier_performance = (
    po_df.groupby(["supplier_id", "part_id"])
    .agg(
        total_orders=("po_id", "count"),
        avg_delay_days=("delivery_delay_days", "mean"),
        late_orders=("delivery_status", lambda x: (x == "Late").sum()),
        total_ordered=("ordered_qty", "sum"),
        total_received=("received_qty", "sum")
    )
    .reset_index()
)

part_supplier_performance["late_delivery_rate"] = (
    part_supplier_performance["late_orders"] /
    part_supplier_performance["total_orders"]
)

part_supplier_performance["fill_rate"] = (
    part_supplier_performance["total_received"] /
    part_supplier_performance["total_ordered"]
)

# Merge with inventory/backorder information
supplier_backorder_analysis = part_inventory.merge(
    part_supplier_performance,
    on="part_id",
    how="left"
)

print("\nParts with highest backorders and supplier performance:")

print(
    supplier_backorder_analysis[
        [
            "part_id",
            "avg_demand",
            "avg_inventory",
            "total_backorder",
            "inventory_coverage",
            "supplier_id",
            "avg_delay_days",
            "late_delivery_rate",
            "fill_rate"
        ]
    ]
    .sort_values("total_backorder", ascending=False)
    .head(20)
    .to_string(index=False)
)

print("\n===== QUALITY / SUPPLIER ANALYSIS =====")

quality_df = pd.read_csv("../data/quality_incidents.csv")

quality_supplier = (
    quality_df.groupby("supplier_id")
    .agg(
        total_incidents=("incident_id", "count"),
        total_scrap=("scrap_qty", "sum"),
        avg_scrap=("scrap_qty", "mean")
    )
    .reset_index()
)

print("\nTop Suppliers by Quality Incidents:")

print(
    quality_supplier
    .sort_values("total_incidents", ascending=False)
    .head(15)
    .to_string(index=False)
)

print("\n===== QUALITY / PART ANALYSIS =====")

quality_part = (
    quality_df.groupby(["supplier_id", "part_id"])
    .agg(
        quality_incidents=("incident_id", "count"),
        total_scrap=("scrap_qty", "sum"),
        avg_scrap=("scrap_qty", "mean")
    )
    .reset_index()
)

quality_part_profile = quality_part.merge(
    parts_df[
        [
            "part_id",
            "part_family",
            "criticality_class",
            "unit_cost",
            "lead_time_days",
            "supplier_risk_class",
            "is_repairable"
        ]
    ],
    on="part_id",
    how="left"
)

print("\nParts with highest quality incident counts:")

print(
    quality_part_profile
    .sort_values("quality_incidents", ascending=False)
    .head(20)
    .to_string(index=False)
)

po_df["order_date"] = pd.to_datetime(po_df["order_date"])
po_df["promised_date"] = pd.to_datetime(po_df["promised_date"])
po_df["receipt_date"] = pd.to_datetime(po_df["receipt_date"])

po_df["delivery_delay_days"] = (
    po_df["receipt_date"] - po_df["promised_date"]
).dt.days

po_df["delivery_status"] = np.where(
    po_df["delivery_delay_days"] > 0,
    "Late",
    "On Time"
)

print("\n===== BUILDING MASTER PART RISK DATASET =====")

# --------------------------------------------------
# 1. PART CHARACTERISTICS
# --------------------------------------------------

part_master = parts_df[
    [
        "part_id",
        "part_family",
        "criticality_class",
        "unit_cost",
        "lead_time_days",
        "supplier_id_primary",
        "supplier_risk_class",
        "is_repairable"
    ]
].copy()


# --------------------------------------------------
# 2. DEMAND ANALYSIS
# --------------------------------------------------

part_demand = (
    df.groupby("part_id")
    .agg(
        avg_demand=("consumption_qty", "mean"),
        demand_std=("consumption_qty", "std"),
        total_demand=("consumption_qty", "sum"),
        max_demand=("consumption_qty", "max")
    )
    .reset_index()
)


# --------------------------------------------------
# 3. INVENTORY ANALYSIS
# --------------------------------------------------

part_inventory_master = (
    df.groupby("part_id")
    .agg(
        avg_inventory=("on_hand_qty", "mean"),
        avg_backorder=("backorder_qty", "mean"),
        total_backorder=("backorder_qty", "sum"),
        avg_blocked=("blocked_qty", "mean")
    )
    .reset_index()

)
part_inventory_master["inventory_coverage"] = np.where(
    part_demand["avg_demand"] > 0,
    part_inventory_master["avg_inventory"] / part_demand["avg_demand"],
    0
)
# --------------------------------------------------
# 4. SUPPLIER PERFORMANCE
# --------------------------------------------------

supplier_part = (
    po_df.groupby(["supplier_id", "part_id"])
    .agg(
        total_orders=("po_id", "count"),
        avg_delay_days=("delivery_delay_days", "mean"),
        late_orders=("delivery_status", lambda x: (x == "Late").sum()),
        total_ordered=("ordered_qty", "sum"),
        total_received=("received_qty", "sum")
    )
    .reset_index()
)

supplier_part["late_delivery_rate"] = (
    supplier_part["late_orders"] /
    supplier_part["total_orders"]
)

supplier_part["fill_rate"] = (
    supplier_part["total_received"] /
    supplier_part["total_ordered"]
)

supplier_part = supplier_part.rename(
    columns={"supplier_id": "supplier_id_primary"}
)


# --------------------------------------------------
# 5. QUALITY ANALYSIS
# --------------------------------------------------

part_quality = (
    quality_df.groupby("part_id")
    .agg(
        quality_incidents=("incident_id", "count"),
        total_scrap=("scrap_qty", "sum"),
        avg_scrap=("scrap_qty", "mean")
    )
    .reset_index()
)


# --------------------------------------------------
# 6. MERGE EVERYTHING
# --------------------------------------------------

master_part_risk = part_master.merge(
    part_demand,
    on="part_id",
    how="left"
)

master_part_risk = master_part_risk.merge(
    part_inventory_master,
    on="part_id",
    how="left"
)

master_part_risk = master_part_risk.merge(
    supplier_part[
        [
            "part_id",
            "supplier_id_primary",
            "avg_delay_days",
            "late_delivery_rate",
            "fill_rate"
        ]
    ],
    on=["part_id", "supplier_id_primary"],
    how="left"
)

master_part_risk = master_part_risk.merge(
    part_quality,
    on="part_id",
    how="left"
)


# --------------------------------------------------
# 7. HANDLE MISSING VALUES
# --------------------------------------------------

master_part_risk["quality_incidents"] = (
    master_part_risk["quality_incidents"].fillna(0)
)

master_part_risk["total_scrap"] = (
    master_part_risk["total_scrap"].fillna(0)
)

master_part_risk["avg_scrap"] = (
    master_part_risk["avg_scrap"].fillna(0)
)


# --------------------------------------------------
# 8. DISPLAY RESULT
# --------------------------------------------------

print("\nMaster Dataset Shape:")
print(master_part_risk.shape)

print("\nMaster Dataset Columns:")
print(master_part_risk.columns)

print("\nFirst 10 Rows:")
print(master_part_risk.head(10).to_string(index=False))

print("\nMissing Values:")
print(master_part_risk.isnull().sum())

master_part_risk.to_csv(
    "../data/master_part_risk.csv",
    index=False
)

print("\nMaster Part Risk Dataset saved successfully!")

# ============================================================
# PART RISK SCORE
# ============================================================

print("\n===== CALCULATING PART RISK SCORE =====")

# Make a copy of the master dataset
risk_df = master_part_risk.copy()

# ------------------------------------------------------------
# 1. DEMAND RISK
# ------------------------------------------------------------

risk_df["demand_risk"] = (
    risk_df["avg_demand"].rank(pct=True) * 0.5 +
    risk_df["demand_std"].rank(pct=True) * 0.5
)


# ------------------------------------------------------------
# 2. INVENTORY RISK
# Lower inventory coverage = higher risk
# ------------------------------------------------------------

risk_df["inventory_risk"] = (
    1 - risk_df["inventory_coverage"].rank(pct=True)
)


# ------------------------------------------------------------
# 3. BACKORDER RISK
# ------------------------------------------------------------

risk_df["backorder_risk"] = (
    risk_df["total_backorder"].rank(pct=True)
)


# ------------------------------------------------------------
# 4. SUPPLIER DELIVERY RISK
# ------------------------------------------------------------

risk_df["supplier_delivery_risk"] = (
    risk_df["avg_delay_days"].rank(pct=True) * 0.4 +
    risk_df["late_delivery_rate"].rank(pct=True) * 0.4 +
    (1 - risk_df["fill_rate"].rank(pct=True)) * 0.2
)


# ------------------------------------------------------------
# 5. LEAD TIME RISK
# ------------------------------------------------------------

risk_df["lead_time_risk"] = (
    risk_df["lead_time_days"].rank(pct=True)
)


# ------------------------------------------------------------
# 6. QUALITY RISK
# ------------------------------------------------------------

risk_df["quality_risk"] = (
    risk_df["quality_incidents"].rank(pct=True) * 0.6 +
    risk_df["total_scrap"].rank(pct=True) * 0.4
)


# ------------------------------------------------------------
# 7. CRITICALITY RISK
# ------------------------------------------------------------

criticality_map = {
    "A": 1.0,
    "B": 0.6,
    "C": 0.3
}

risk_df["criticality_risk"] = (
    risk_df["criticality_class"].map(criticality_map)
)


# ------------------------------------------------------------
# 8. COST EXPOSURE
# ------------------------------------------------------------

risk_df["cost_risk"] = (
    risk_df["unit_cost"].rank(pct=True)
)


# ------------------------------------------------------------
# 9. FINAL PART RISK SCORE
# ------------------------------------------------------------

risk_df["part_risk_score"] = (
    risk_df["demand_risk"] * 0.15 +
    risk_df["inventory_risk"] * 0.20 +
    risk_df["backorder_risk"] * 0.15 +
    risk_df["supplier_delivery_risk"] * 0.15 +
    risk_df["lead_time_risk"] * 0.10 +
    risk_df["quality_risk"] * 0.10 +
    risk_df["criticality_risk"] * 0.10 +
    risk_df["cost_risk"] * 0.05
)


# ------------------------------------------------------------
# 10. RISK CATEGORY
# ------------------------------------------------------------

def classify_risk(score):

    if score >= 0.75:
        return "Critical"

    elif score >= 0.50:
        return "High"

    elif score >= 0.25:
        return "Medium"

    else:
        return "Low"


risk_df["risk_category"] = risk_df["part_risk_score"].apply(
    classify_risk
)


# ------------------------------------------------------------
# 11. SORT BY RISK
# ------------------------------------------------------------

risk_df = risk_df.sort_values(
    "part_risk_score",
    ascending=False
)


# ------------------------------------------------------------
# 12. DISPLAY RESULTS
# ------------------------------------------------------------

print("\nTop 20 Highest Risk Parts:")

print(
    risk_df[
        [
            "part_id",
            "part_family",
            "criticality_class",
            "unit_cost",
            "lead_time_days",
            "avg_demand",
            "inventory_coverage",
            "total_backorder",
            "avg_delay_days",
            "late_delivery_rate",
            "quality_incidents",
            "part_risk_score",
            "risk_category"
        ]
    ].head(20)
)


print("\nRisk Category Distribution:")

print(
    risk_df["risk_category"].value_counts()
)


# ------------------------------------------------------------
# 13. SAVE RISK DATASET
# ------------------------------------------------------------

risk_df.to_csv(
    "../data/part_risk_dataset.csv",
    index=False
)

print("\nPart Risk Dataset saved successfully!")

# ============================================================
# SUPPLIER RISK SCORE
# ============================================================

print("\n===== CALCULATING SUPPLIER RISK SCORE =====")

# ------------------------------------------------------------
# 1. SUPPLIER PERFORMANCE DATA
# ------------------------------------------------------------

supplier_risk = (
    po_df.groupby("supplier_id")
    .agg(
        total_orders=("po_id", "count"),
        avg_delay_days=("delivery_delay_days", "mean"),
        late_orders=("delivery_status", lambda x: (x == "Late").sum()),
        total_ordered=("ordered_qty", "sum"),
        total_received=("received_qty", "sum")
    )
    .reset_index()
)

# ------------------------------------------------------------
# 2. DELIVERY PERFORMANCE
# ------------------------------------------------------------

supplier_risk["late_delivery_rate"] = (
    supplier_risk["late_orders"] /
    supplier_risk["total_orders"]
)

supplier_risk["fill_rate"] = np.where(
    supplier_risk["total_ordered"] > 0,
    supplier_risk["total_received"] /
    supplier_risk["total_ordered"],
    0
)

# ------------------------------------------------------------
# 3. QUALITY PERFORMANCE
# ------------------------------------------------------------

supplier_quality = (
    quality_df.groupby("supplier_id")
    .agg(
        quality_incidents=("incident_id", "count"),
        total_scrap=("scrap_qty", "sum"),
        avg_scrap=("scrap_qty", "mean")
    )
    .reset_index()
)

# Merge quality data
supplier_risk = supplier_risk.merge(
    supplier_quality,
    on="supplier_id",
    how="left"
)

# Suppliers with no quality incidents
supplier_risk["quality_incidents"] = (
    supplier_risk["quality_incidents"].fillna(0)
)

supplier_risk["total_scrap"] = (
    supplier_risk["total_scrap"].fillna(0)
)

supplier_risk["avg_scrap"] = (
    supplier_risk["avg_scrap"].fillna(0)
)

# ------------------------------------------------------------
# 4. SUPPLIER RISK COMPONENTS
# ------------------------------------------------------------

# Delivery delay risk
supplier_risk["delay_risk"] = (
    supplier_risk["avg_delay_days"].rank(pct=True)
)

# Late delivery risk
supplier_risk["late_delivery_risk"] = (
    supplier_risk["late_delivery_rate"].rank(pct=True)
)

# Low fill rate = high risk
supplier_risk["fill_rate_risk"] = (
    1 - supplier_risk["fill_rate"].rank(pct=True)
)

# Quality incident risk
supplier_risk["quality_risk"] = (
    supplier_risk["quality_incidents"].rank(pct=True)
)

# Scrap risk
supplier_risk["scrap_risk"] = (
    supplier_risk["total_scrap"].rank(pct=True)
)

# ------------------------------------------------------------
# 5. FINAL SUPPLIER RISK SCORE
# ------------------------------------------------------------

supplier_risk["supplier_risk_score"] = (
    supplier_risk["delay_risk"] * 0.20 +
    supplier_risk["late_delivery_risk"] * 0.25 +
    supplier_risk["fill_rate_risk"] * 0.20 +
    supplier_risk["quality_risk"] * 0.20 +
    supplier_risk["scrap_risk"] * 0.15
)

# ------------------------------------------------------------
# 6. SUPPLIER RISK CATEGORY
# ------------------------------------------------------------

def classify_supplier_risk(score):

    if score >= 0.75:
        return "Critical"

    elif score >= 0.50:
        return "High"

    elif score >= 0.25:
        return "Medium"

    else:
        return "Low"


supplier_risk["risk_category"] = (
    supplier_risk["supplier_risk_score"]
    .apply(classify_supplier_risk)
)

# ------------------------------------------------------------
# 7. SORT SUPPLIERS BY RISK
# ------------------------------------------------------------

supplier_risk = supplier_risk.sort_values(
    "supplier_risk_score",
    ascending=False
)

# ------------------------------------------------------------
# 8. DISPLAY RESULTS
# ------------------------------------------------------------

print("\nTop 15 Highest Risk Suppliers:")

print(
    supplier_risk[
        [
            "supplier_id",
            "total_orders",
            "avg_delay_days",
            "late_delivery_rate",
            "fill_rate",
            "quality_incidents",
            "total_scrap",
            "supplier_risk_score",
            "risk_category"
        ]
    ].head(15).to_string(index=False)
)

# ------------------------------------------------------------
# 9. RISK CATEGORY DISTRIBUTION
# ------------------------------------------------------------

print("\nSupplier Risk Category Distribution:")

print(
    supplier_risk["risk_category"]
    .value_counts()
)

# ------------------------------------------------------------
# 10. SAVE SUPPLIER RISK DATASET
# ------------------------------------------------------------

supplier_risk.to_csv(
    "../data/supplier_risk_dataset.csv",
    index=False
)

print("\nSupplier Risk Dataset saved successfully!")

# ============================================================
# PART-SUPPLIER COMBINED RISK ANALYSIS
# ============================================================

print("\n===== CALCULATING PART-SUPPLIER COMBINED RISK =====")

# ------------------------------------------------------------
# 1. LOAD PART RISK DATASET
# ------------------------------------------------------------

part_risk = pd.read_csv(
    "../data/part_risk_dataset.csv"
)

# ------------------------------------------------------------
# 2. SELECT SUPPLIER RISK INFORMATION
# ------------------------------------------------------------

supplier_risk_selected = supplier_risk[
    [
        "supplier_id",
        "supplier_risk_score",
        "risk_category",
        "avg_delay_days",
        "late_delivery_rate",
        "fill_rate",
        "quality_incidents",
        "total_scrap"
    ]
].copy()

# Rename supplier risk category to avoid confusion
supplier_risk_selected = supplier_risk_selected.rename(
    columns={
        "risk_category": "supplier_risk_category"
    }
)

# ------------------------------------------------------------
# 3. MERGE PART RISK + SUPPLIER RISK
# ------------------------------------------------------------

part_supplier_risk = part_risk.merge(
    supplier_risk_selected,
    left_on="supplier_id_primary",
    right_on="supplier_id",
    how="left"
)

# ------------------------------------------------------------
# 4. CALCULATE COMBINED RISK SCORE
# ------------------------------------------------------------

part_supplier_risk["combined_risk_score"] = (
    part_supplier_risk["part_risk_score"] * 0.60 +
    part_supplier_risk["supplier_risk_score"] * 0.40
)

# ------------------------------------------------------------
# 5. CRITICALITY ADJUSTMENT
# ------------------------------------------------------------

criticality_multiplier = {
    "A": 1.15,
    "B": 1.05,
    "C": 1.00
}

part_supplier_risk["combined_risk_score"] = (
    part_supplier_risk["combined_risk_score"] *
    part_supplier_risk["criticality_class"].map(
        criticality_multiplier
    )
)

# Keep score within 0–1
part_supplier_risk["combined_risk_score"] = (
    part_supplier_risk["combined_risk_score"].clip(0, 1)
)

# ------------------------------------------------------------
# 6. FINAL RISK CATEGORY
# ------------------------------------------------------------

def classify_combined_risk(score):

    if score >= 0.75:
        return "Immediate Action"

    elif score >= 0.60:
        return "High Priority"

    elif score >= 0.40:
        return "Monitor"

    else:
        return "Normal"


part_supplier_risk["combined_risk_category"] = (
    part_supplier_risk["combined_risk_score"]
    .apply(classify_combined_risk)
)

# ------------------------------------------------------------
# 7. PRIORITY RECOMMENDATION
# ------------------------------------------------------------

def generate_recommendation(row):

    if row["combined_risk_category"] == "Immediate Action":
        return "Immediate supplier review and contingency planning"

    elif row["combined_risk_category"] == "High Priority":
        return "Increase safety stock and monitor supplier closely"

    elif row["combined_risk_category"] == "Monitor":
        return "Monitor inventory and supplier performance"

    else:
        return "Normal monitoring"

    
part_supplier_risk["recommendation"] = (
    part_supplier_risk.apply(
        generate_recommendation,
        axis=1
    )
)

# ------------------------------------------------------------
# 8. SORT BY COMBINED RISK
# ------------------------------------------------------------

part_supplier_risk = part_supplier_risk.sort_values(
    "combined_risk_score",
    ascending=False
)

# ------------------------------------------------------------
# 9. DISPLAY TOP 20
# ------------------------------------------------------------

print("\nTop 20 Highest Part-Supplier Risks:")

print(
    part_supplier_risk[
        [
            "part_id",
            "part_family",
            "criticality_class",
            "unit_cost",
            "lead_time_days",
            "supplier_id_primary",
            "part_risk_score",
            "supplier_risk_score",
            "combined_risk_score",
            "combined_risk_category",
            "recommendation"
        ]
    ].head(20).to_string(index=False)
)

# ------------------------------------------------------------
# 10. RISK CATEGORY DISTRIBUTION
# ------------------------------------------------------------

print("\nCombined Risk Category Distribution:")

print(
    part_supplier_risk[
        "combined_risk_category"
    ].value_counts()
)

# ------------------------------------------------------------
# 11. SAVE DATASET
# ------------------------------------------------------------

part_supplier_risk.to_csv(
    "../data/part_supplier_risk_dataset.csv",
    index=False
)

print(
    "\nPart-Supplier Risk Dataset saved successfully!"
)

import pandas as pd
import numpy as np

# Load dataset
df = pd.read_csv("../data/part_supplier_risk_dataset.csv")

print("===== ML DATASET =====")

print("\nDataset Shape:")
print(df.shape)

print("\nColumn Names:")
print(df.columns)

print("\nFirst 5 Rows:")
print(df.head())

print("\nMissing Values:")
print(df.isnull().sum())

print("\nDuplicate Rows:")
print(df.duplicated().sum())


# ============================================================
# STEP 2: HANDLE MISSING VALUES
# ============================================================

print("\n===== HANDLING MISSING VALUES =====")

# Check missing values
missing_values = df.isnull().sum()

print("\nMissing Values Before Handling:")
print(missing_values)

# Handle numerical columns
numeric_columns = df.select_dtypes(include=["int64", "float64"]).columns

df[numeric_columns] = df[numeric_columns].fillna(
    df[numeric_columns].median()
)

# Handle categorical columns
categorical_columns = df.select_dtypes(include=["object"]).columns

for column in categorical_columns:
    df[column] = df[column].fillna(
        df[column].mode()[0]
    )

print("\nMissing Values After Handling:")
print(df.isnull().sum())

print("\nMissing values handled successfully!")

# ============================================================
# STEP 3: REMOVE DUPLICATES
# ============================================================

print("\n===== REMOVING DUPLICATES =====")

print("Duplicate rows before:", df.duplicated().sum())

df = df.drop_duplicates()

print("Duplicate rows after:", df.duplicated().sum())

print("\nDataset Shape After Removing Duplicates:")
print(df.shape)


# ============================================================
# STEP 4: FEATURE SELECTION
# ============================================================

print("\n===== FEATURE SELECTION =====")

print("\nDataset Shape:")
print(df.shape)

print("\nAvailable Columns:")
print(df.columns)


# ------------------------------------------------------------
# SELECT FEATURES
# ------------------------------------------------------------

features = [
    "unit_cost",
    "lead_time_days",
    "avg_demand",
    "demand_std",
    "total_demand",
    "max_demand",
    "avg_inventory",
    "avg_backorder",
    "total_backorder",
    "avg_blocked",
    "inventory_coverage",

    "avg_delay_days_x",
    "late_delivery_rate_x",
    "fill_rate_x",
    "quality_incidents_x",
    "total_scrap_x",

    "demand_risk",
    "inventory_risk",
    "backorder_risk",
    "supplier_delivery_risk",
    "lead_time_risk",
    "quality_risk",
    "criticality_risk",
    "cost_risk",
    "part_risk_score",
    "supplier_risk_score"
]


# ------------------------------------------------------------
# TARGET
# ------------------------------------------------------------

target = "combined_risk_score"


# ------------------------------------------------------------
# CREATE X AND Y
# ------------------------------------------------------------

X = df[features].copy()

y = df[target].copy()


# ------------------------------------------------------------
# DISPLAY RESULT
# ------------------------------------------------------------

print("\nSelected Features:")
print(X.columns.tolist())

print("\nNumber of Features:")
print(len(features))

print("\nFeature Dataset Shape:")
print(X.shape)

print("\nTarget:")
print(target)

print("\nTarget Shape:")
print(y.shape)

print("\n===== FEATURE SELECTION COMPLETED =====")

# ============================================================
# STEP 5: TRAIN-TEST SPLIT
# ============================================================

print("\n===== TRAIN-TEST SPLIT =====")

from sklearn.model_selection import train_test_split

# Target variable
y = df["combined_risk_score"]

# Selected features
X = df[features].copy()

# Split the dataset
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)

print("\nTraining Data Shape:")
print(X_train.shape)

print("\nTesting Data Shape:")
print(X_test.shape)

print("\nTraining Target Shape:")
print(y_train.shape)

print("\nTesting Target Shape:")
print(y_test.shape)

print("\nTrain-Test Split completed successfully!")

# ============================================================
# STEP 6: TRAIN-TEST SPLIT
# ============================================================

print("\n===== TRAIN-TEST SPLIT =====")

from sklearn.model_selection import train_test_split

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)

print("\nTraining Data Shape:")
print(X_train.shape)

print("\nTesting Data Shape:")
print(X_test.shape)

print("\nTraining Target Shape:")
print(y_train.shape)

print("\nTesting Target Shape:")
print(y_test.shape)

print("\nTrain-Test Split Completed Successfully!")

# ============================================================
# STEP 7: FEATURE SCALING
# ============================================================

print("\n===== FEATURE SCALING =====")

from sklearn.preprocessing import StandardScaler

# Create scaler
scaler = StandardScaler()

# Fit scaler ONLY on training data
X_train_scaled = scaler.fit_transform(X_train)

# Use the same scaler to transform test data
X_test_scaled = scaler.transform(X_test)

print("\nOriginal Training Data Shape:")
print(X_train.shape)

print("\nScaled Training Data Shape:")
print(X_train_scaled.shape)

print("\nOriginal Testing Data Shape:")
print(X_test.shape)

print("\nScaled Testing Data Shape:")
print(X_test_scaled.shape)

print("\nFeature Scaling Completed Successfully!")

# ============================================================
# STEP 8: MODEL TRAINING
# ============================================================

print("\n===== MODEL TRAINING =====")

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor

# ------------------------------------------------------------
# 1. LINEAR REGRESSION
# ------------------------------------------------------------

linear_model = LinearRegression()

linear_model.fit(
    X_train_scaled,
    y_train
)

print("\nLinear Regression trained successfully!")


# ------------------------------------------------------------
# 2. RANDOM FOREST REGRESSOR
# ------------------------------------------------------------

rf_model = RandomForestRegressor(
    n_estimators=200,
    random_state=42,
    max_depth=None
)

rf_model.fit(
    X_train_scaled,
    y_train
)

print("Random Forest trained successfully!")


# ------------------------------------------------------------
# 3. GRADIENT BOOSTING REGRESSOR
# ------------------------------------------------------------

gb_model = GradientBoostingRegressor(
    n_estimators=200,
    learning_rate=0.05,
    max_depth=3,
    random_state=42
)

gb_model.fit(
    X_train_scaled,
    y_train
)

print("Gradient Boosting trained successfully!")


print("\nAll ML Models Trained Successfully!")

# ============================================================
# STEP 9: MODEL PREDICTION
# ============================================================

print("\n===== MODEL PREDICTION =====")

# ------------------------------------------------------------
# 1. LINEAR REGRESSION PREDICTIONS
# ------------------------------------------------------------

y_pred_linear = linear_model.predict(X_test_scaled)

print("\nLinear Regression predictions generated!")


# ------------------------------------------------------------
# 2. RANDOM FOREST PREDICTIONS
# ------------------------------------------------------------

y_pred_rf = rf_model.predict(X_test_scaled)

print("Random Forest predictions generated!")


# ------------------------------------------------------------
# 3. GRADIENT BOOSTING PREDICTIONS
# ------------------------------------------------------------

y_pred_gb = gb_model.predict(X_test_scaled)

print("Gradient Boosting predictions generated!")


# ------------------------------------------------------------
# 4. DISPLAY SAMPLE PREDICTIONS
# ------------------------------------------------------------

print("\nSample Predictions:")

prediction_comparison = pd.DataFrame({
    "Actual": y_test.values,
    "Linear_Regression": y_pred_linear,
    "Random_Forest": y_pred_rf,
    "Gradient_Boosting": y_pred_gb
})

print(prediction_comparison.head(10))


print("\nModel Prediction Completed Successfully!")

# ============================================================
# STEP 10: MODEL EVALUATION
# ============================================================

print("\n===== MODEL EVALUATION =====")

from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
import numpy as np

# ------------------------------------------------------------
# 1. LINEAR REGRESSION
# ------------------------------------------------------------

mae_linear = mean_absolute_error(y_test, y_pred_linear)
mse_linear = mean_squared_error(y_test, y_pred_linear)
rmse_linear = np.sqrt(mse_linear)
r2_linear = r2_score(y_test, y_pred_linear)


# ------------------------------------------------------------
# 2. RANDOM FOREST
# ------------------------------------------------------------

mae_rf = mean_absolute_error(y_test, y_pred_rf)
mse_rf = mean_squared_error(y_test, y_pred_rf)
rmse_rf = np.sqrt(mse_rf)
r2_rf = r2_score(y_test, y_pred_rf)


# ------------------------------------------------------------
# 3. GRADIENT BOOSTING
# ------------------------------------------------------------

mae_gb = mean_absolute_error(y_test, y_pred_gb)
mse_gb = mean_squared_error(y_test, y_pred_gb)
rmse_gb = np.sqrt(mse_gb)
r2_gb = r2_score(y_test, y_pred_gb)


# ------------------------------------------------------------
# 4. DISPLAY RESULTS
# ------------------------------------------------------------

evaluation_results = pd.DataFrame({
    "Model": [
        "Linear Regression",
        "Random Forest",
        "Gradient Boosting"
    ],
    "MAE": [
        mae_linear,
        mae_rf,
        mae_gb
    ],
    "MSE": [
        mse_linear,
        mse_rf,
        mse_gb
    ],
    "RMSE": [
        rmse_linear,
        rmse_rf,
        rmse_gb
    ],
    "R2_Score": [
        r2_linear,
        r2_rf,
        r2_gb
    ]
})

print("\nModel Evaluation Results:")
print(evaluation_results.to_string(index=False))

print("\nModel Evaluation Completed Successfully!")

# ============================================================
# STEP 11: MODEL COMPARISON & BEST MODEL SELECTION
# ============================================================

print("\n===== MODEL COMPARISON =====")

# ------------------------------------------------------------
# 1. FIND BEST MODEL
# ------------------------------------------------------------

best_model_index = evaluation_results["R2_Score"].idxmax()

best_model_name = evaluation_results.loc[
    best_model_index,
    "Model"
]

best_r2 = evaluation_results.loc[
    best_model_index,
    "R2_Score"
]

best_mae = evaluation_results.loc[
    best_model_index,
    "MAE"
]

best_rmse = evaluation_results.loc[
    best_model_index,
    "RMSE"
]


# ------------------------------------------------------------
# 2. DISPLAY BEST MODEL
# ------------------------------------------------------------

print("\nBest Model:")
print(best_model_name)

print("\nBest Model Performance:")
print("MAE :", round(best_mae, 6))
print("RMSE:", round(best_rmse, 6))
print("R2  :", round(best_r2, 6))


# ------------------------------------------------------------
# 3. SELECT BEST MODEL OBJECT
# ------------------------------------------------------------

if best_model_name == "Linear Regression":
    best_model = linear_model

elif best_model_name == "Random Forest":
    best_model = rf_model

else:
    best_model = gb_model


print("\nBest model selected successfully!")

# ============================================================
# STEP 12: SAVE BEST MODEL
# ============================================================

print("\n===== SAVING BEST MODEL =====")

import joblib
import os

# ------------------------------------------------------------
# 1. CREATE MODEL DIRECTORY
# ------------------------------------------------------------

model_dir = "../models"

os.makedirs(model_dir, exist_ok=True)


# ------------------------------------------------------------
# 2. SAVE BEST MODEL
# ------------------------------------------------------------

model_path = os.path.join(
    model_dir,
    "best_risk_model.pkl"
)

joblib.dump(
    best_model,
    model_path
)

print("\nBest model saved successfully!")
print("Model:", best_model_name)
print("Path:", model_path)


# ------------------------------------------------------------
# 3. SAVE SCALER
# ------------------------------------------------------------

scaler_path = os.path.join(
    model_dir,
    "risk_scaler.pkl"
)

joblib.dump(
    scaler,
    scaler_path
)

print("Scaler saved successfully!")
print("Path:", scaler_path)


# ------------------------------------------------------------
# 4. SAVE FEATURE NAMES
# ------------------------------------------------------------

features_path = os.path.join(
    model_dir,
    "model_features.pkl"
)

joblib.dump(
    features,
    features_path
)

print("Feature list saved successfully!")
print("Path:", features_path)


print("\n===== ML MODEL SAVING COMPLETED =====")

# ============================================================
# STEP 14: LOAD SAVED MODEL AND MAKE PREDICTIONS
# ============================================================

print("\n===== STEP 14: MODEL INFERENCE =====")

import pandas as pd
import joblib

# ------------------------------------------------------------
# 1. LOAD SAVED MODEL
# ------------------------------------------------------------

model_path = "../models/best_risk_model.pkl"
scaler_path = "../models/risk_scaler.pkl"
features_path = "../models/model_features.pkl"

best_model = joblib.load(model_path)
scaler = joblib.load(scaler_path)
features = joblib.load(features_path)

print("\nSaved model loaded successfully!")
print("Saved scaler loaded successfully!")
print("Saved feature list loaded successfully!")


# ------------------------------------------------------------
# 2. LOAD RISK DATASET
# ------------------------------------------------------------

prediction_df = pd.read_csv(
    "../data/part_supplier_risk_dataset.csv"
)

print("\nPrediction Dataset Shape:")
print(prediction_df.shape)


# ------------------------------------------------------------
# 3. SELECT MODEL FEATURES
# ------------------------------------------------------------

X_new = prediction_df[features].copy()

print("\nFeatures used for prediction:")
print(X_new.columns.tolist())


# ------------------------------------------------------------
# 4. SCALE FEATURES
# ------------------------------------------------------------

X_new_scaled = scaler.transform(X_new)

print("\nFeature scaling completed!")


# ------------------------------------------------------------
# 5. MAKE PREDICTIONS
# ------------------------------------------------------------

predicted_risk = best_model.predict(X_new_scaled)

prediction_df["predicted_risk_score"] = predicted_risk


# ------------------------------------------------------------
# 6. CLASSIFY PREDICTED RISK
# ------------------------------------------------------------

def classify_predicted_risk(score):

    if score >= 0.75:
        return "Immediate Action"

    elif score >= 0.60:
        return "High Priority"

    elif score >= 0.40:
        return "Monitor"

    else:
        return "Normal"


prediction_df["predicted_risk_category"] = (
    prediction_df["predicted_risk_score"]
    .apply(classify_predicted_risk)
)


# ------------------------------------------------------------
# 7. DISPLAY PREDICTIONS
# ------------------------------------------------------------

print("\n===== SAMPLE PREDICTIONS =====")

print(
    prediction_df[
        [
            "part_id",
            "supplier_id_primary",
            "combined_risk_score",
            "predicted_risk_score",
            "predicted_risk_category"
        ]
    ]
    .head(20)
    .to_string(index=False)
)


# ------------------------------------------------------------
# 8. RISK CATEGORY DISTRIBUTION
# ------------------------------------------------------------

print("\n===== PREDICTED RISK DISTRIBUTION =====")

print(
    prediction_df["predicted_risk_category"]
    .value_counts()
)


# ------------------------------------------------------------
# 9. SAVE PREDICTIONS
# ------------------------------------------------------------

prediction_path = "../data/final_risk_predictions.csv"

prediction_df.to_csv(
    prediction_path,
    index=False
)

print("\nFinal predictions saved successfully!")
print("Path:", prediction_path)

print("\n===== STEP 14 COMPLETED SUCCESSFULLY =====")

# ============================================================
# STEP 15: FINAL RISK ANALYSIS & BUSINESS RECOMMENDATIONS
# ============================================================

print("\n===== STEP 15: FINAL RISK ANALYSIS =====")

# ------------------------------------------------------------
# 1. LOAD FINAL PREDICTIONS
# ------------------------------------------------------------

final_predictions = pd.read_csv(
    "../data/final_risk_predictions.csv"
)

print("\nFinal Prediction Dataset Shape:")
print(final_predictions.shape)

# ------------------------------------------------------------
# 2. RISK CATEGORY DISTRIBUTION
# ------------------------------------------------------------

print("\n===== RISK CATEGORY DISTRIBUTION =====")

risk_distribution = (
    final_predictions["predicted_risk_category"]
    .value_counts()
)

print(risk_distribution)

# ------------------------------------------------------------
# 3. IMMEDIATE ACTION PARTS
# ------------------------------------------------------------

print("\n===== IMMEDIATE ACTION REQUIRED =====")

immediate_action = final_predictions[
    final_predictions["predicted_risk_category"]
    == "Immediate Action"
]

print(
    immediate_action[
        [
            "part_id",
            "supplier_id_primary",
            "combined_risk_score",
            "predicted_risk_score",
            "predicted_risk_category"
        ]
    ].to_string(index=False)
)

# ------------------------------------------------------------
# 4. HIGH PRIORITY PARTS
# ------------------------------------------------------------

print("\n===== HIGH PRIORITY PARTS =====")

high_priority = final_predictions[
    final_predictions["predicted_risk_category"]
    == "High Priority"
]

print(
    high_priority[
        [
            "part_id",
            "supplier_id_primary",
            "combined_risk_score",
            "predicted_risk_score",
            "predicted_risk_category"
        ]
    ]
    .sort_values(
        "predicted_risk_score",
        ascending=False
    )
    .head(20)
    .to_string(index=False)
)

# ------------------------------------------------------------
# 5. TOP 20 HIGHEST RISK PARTS
# ------------------------------------------------------------

print("\n===== TOP 20 HIGHEST RISK PARTS =====")

top_risk_parts = (
    final_predictions
    .sort_values(
        "predicted_risk_score",
        ascending=False
    )
    .head(20)
)

print(
    top_risk_parts[
        [
            "part_id",
            "supplier_id_primary",
            "combined_risk_score",
            "predicted_risk_score",
            "predicted_risk_category"
        ]
    ].to_string(index=False)
)

# ------------------------------------------------------------
# 6. SUPPLIER-WISE RISK ANALYSIS
# ------------------------------------------------------------

print("\n===== SUPPLIER-WISE RISK ANALYSIS =====")

supplier_summary = (
    final_predictions
    .groupby("supplier_id_primary")
    .agg(
        total_parts=("part_id", "count"),
        average_risk=("predicted_risk_score", "mean"),
        maximum_risk=("predicted_risk_score", "max"),
        immediate_action_parts=(
            "predicted_risk_category",
            lambda x: (x == "Immediate Action").sum()
        ),
        high_priority_parts=(
            "predicted_risk_category",
            lambda x: (x == "High Priority").sum()
        )
    )
    .reset_index()
)

supplier_summary = supplier_summary.sort_values(
    "average_risk",
    ascending=False
)

print(
    supplier_summary
    .head(15)
    .to_string(index=False)
)

# ------------------------------------------------------------
# 7. BUSINESS RECOMMENDATIONS
# ------------------------------------------------------------

print("\n===== BUSINESS RECOMMENDATIONS =====")

print("\n1. Immediate Action:")
print(
    "Review suppliers and parts classified as Immediate Action."
)

print("\n2. High Priority:")
print(
    "Increase safety stock and closely monitor supplier performance."
)

print("\n3. Monitor:")
print(
    "Continue monitoring inventory, demand and supplier performance."
)

print("\n4. Normal:")
print(
    "Continue normal inventory and supplier monitoring."
)

# ------------------------------------------------------------
# 8. SAVE SUPPLIER SUMMARY
# ------------------------------------------------------------

supplier_summary.to_csv(
    "../data/supplier_risk_summary.csv",
    index=False
)

print(
    "\nSupplier risk summary saved successfully!"
)

print("\n===== STEP 15 COMPLETED SUCCESSFULLY =====")
