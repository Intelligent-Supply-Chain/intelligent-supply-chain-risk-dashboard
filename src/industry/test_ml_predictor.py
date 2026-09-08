import pandas as pd

from src.industry.ml_predictor import predict_ml_risk


test_data = pd.DataFrame({

    "part_id": [
        "MAT001",
        "MAT002",
        "MAT003"
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
    ],

    "backorders": [
        5,
        20,
        50
    ],

    "defect_rate": [
        0.02,
        0.05,
        0.12
    ],

    "delivery_delay": [
        2,
        7,
        15
    ]
})


print("\n===== ML MODEL TEST =====")

result = predict_ml_risk(test_data)

print(
    result[
        [
            "part_id",
            "ml_risk_score",
            "ml_risk_category"
        ]
    ]
)

print("\n===== ML MODEL TEST COMPLETED =====")