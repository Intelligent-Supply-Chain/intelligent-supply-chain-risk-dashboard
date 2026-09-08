import pandas as pd

from column_mapper import (
    detect_columns,
    apply_column_mapping
)


# Simulated company dataset
company_data = pd.DataFrame({
    "Material_Code": ["MAT001", "MAT002", "MAT003"],
    "Vendor_ID": ["VEN01", "VEN02", "VEN03"],
    "Stock_On_Hand": [500, 250, 100],
    "Monthly_Demand": [450, 300, 250],
    "Supplier_Lead_Time": [10, 25, 40]
})


print("\n===== COMPANY DATA =====")

print(company_data)


# Detect columns
mapping = detect_columns(company_data)


print("\n===== DETECTED COLUMN MAPPING =====")

for standard, original in mapping.items():

    print(
        f"{original}  →  {standard}"
    )


# Apply mapping
standardized_data = apply_column_mapping(
    company_data,
    mapping
)


print("\n===== STANDARDIZED DATA =====")

print(standardized_data)