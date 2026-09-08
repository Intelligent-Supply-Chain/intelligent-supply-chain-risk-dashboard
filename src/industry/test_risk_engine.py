import pandas as pd

from risk_engine import calculate_risk_scores


company_data = pd.DataFrame({
    "part_id": [
        "MAT001",
        "MAT002",
        "MAT003"
    ],

    "supplier_id_primary": [
        "VEN01",
        "VEN02",
        "VEN03"
    ],

    "inventory": [
        500,
        250,
        100
    ],

    "demand": [
        450,
        300,
        250
    ],

    "lead_time_days": [
        10,
        25,
        40
    ]
})


result = calculate_risk_scores(
    company_data
)


print("\n===== RISK ENGINE TEST =====")

print(
    result[
        [
            "part_id",
            "demand_risk",
            "inventory_risk",
            "lead_time_risk",
            "combined_risk_score",
            "predicted_risk_score",
            "predicted_risk_category"
        ]
    ]
)

print("\n===== TEST COMPLETED =====")