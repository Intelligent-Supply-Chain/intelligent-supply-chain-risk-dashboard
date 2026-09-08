import pandas as pd

from src.industry.hybrid_risk import calculate_hybrid_risk


test_data = pd.DataFrame({
    "part_id": [
        "MAT001",
        "MAT002",
        "MAT003"
    ],

    "predicted_risk_score": [
        0.188542,
        0.385305,
        0.691518
    ],

    "ml_risk_score": [
        0.811198,
        0.910145,
        1.000000
    ]
})


result = calculate_hybrid_risk(test_data)


print("\n===== HYBRID RISK TEST =====")

print(
    result[
        [
            "part_id",
            "predicted_risk_score",
            "ml_risk_score",
            "hybrid_risk_score",
            "hybrid_risk_category"
        ]
    ]
)

print("\n===== HYBRID RISK TEST COMPLETED =====")