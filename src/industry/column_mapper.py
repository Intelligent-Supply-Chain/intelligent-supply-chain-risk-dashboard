import pandas as pd


# Standard fields used by our risk analytics system
STANDARD_COLUMNS = {
    "part_id": [
        "part_id",
        "part",
        "part_number",
        "part_no",
        "material_id",
        "material_code",
        "sku",
        "sku_id"
    ],

    "supplier_id_primary": [
        "supplier_id",
        "supplier",
        "supplier_id_primary",
        "supplier_code",
        "vendor_id",
        "vendor_code",
        "vendor"
    ],

    "inventory": [
        "inventory",
        "inventory_qty",
        "stock",
        "stock_on_hand",
        "current_stock",
        "available_stock"
    ],

    "demand": [
        "demand",
        "monthly_demand",
        "daily_demand",
        "avg_demand",
        "average_demand",
        "forecast_demand"
    ],

    "lead_time_days": [
        "lead_time",
        "lead_time_days",
        "supplier_lead_time",
        "delivery_days",
        "delivery_time"
    ],

        "backorders": [
        "backorders",
        "backorder",
        "backorder_qty",
        "backorder_quantity",
        "pending_orders"
    ],

    "defect_rate": [
        "defect_rate",
        "defect_percentage",
        "defect_percent",
        "quality_rate",
        "rejection_rate"
    ],

    "criticality": [
        "criticality",
        "criticality_class",
        "criticality_level",
        "priority",
        "part_criticality"
    ],

    "unit_cost": [
        "unit_cost",
        "cost_per_unit",
        "item_cost",
        "part_cost",
        "price"
    ],

    "delivery_delay": [
        "delivery_delay",
        "delivery_delay_days",
        "delay_days",
        "supplier_delay",
        "late_delivery_days"
    ]
}


def normalize_column_name(column):
    """
    Convert a column name into a consistent format.
    """

    return (
        str(column)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
    )


def detect_columns(df):
    """
    Detect company columns and map them
    to our standard column names.
    """

    detected_mapping = {}

    normalized_columns = {
        normalize_column_name(column): column
        for column in df.columns
    }

    for standard_name, possible_names in STANDARD_COLUMNS.items():

        for possible_name in possible_names:

            normalized_name = normalize_column_name(
                possible_name
            )

            if normalized_name in normalized_columns:

                detected_mapping[standard_name] = (
                    normalized_columns[normalized_name]
                )

                break

    return detected_mapping


def apply_column_mapping(df, mapping):
    """
    Rename company columns to our standard
    internal column names.
    """

    reverse_mapping = {
        original: standard
        for standard, original in mapping.items()
    }

    return df.rename(columns=reverse_mapping)