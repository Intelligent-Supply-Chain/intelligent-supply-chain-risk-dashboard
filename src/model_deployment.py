import pandas as pd
import joblib

print("===== MODEL DEPLOYMENT =====")

# ------------------------------------------------------------
# 1. LOAD MODEL
# ------------------------------------------------------------

model = joblib.load("../models/best_risk_model.pkl")

print("\nBest model loaded successfully!")


# ------------------------------------------------------------
# 2. LOAD SCALER
# ------------------------------------------------------------

scaler = joblib.load("../models/risk_scaler.pkl")

print("Scaler loaded successfully!")


# ------------------------------------------------------------
# 3. LOAD FEATURE NAMES
# ------------------------------------------------------------

features = joblib.load("../models/model_features.pkl")

print("Feature list loaded successfully!")


# ------------------------------------------------------------
# 4. LOAD DATA
# ------------------------------------------------------------

df = pd.read_csv("../data/part_supplier_risk_dataset.csv")

print("\nDataset loaded successfully!")

print("\nDataset Shape:")
print(df.shape)


# ------------------------------------------------------------
# 5. PREPARE FEATURES
# ------------------------------------------------------------

X = df[features].copy()

print("\nFeatures prepared successfully!")

print("Number of Features:", len(features))


# ------------------------------------------------------------
# 6. SCALE FEATURES
# ------------------------------------------------------------

X_scaled = scaler.transform(X)

print("\nFeatures scaled successfully!")


# ------------------------------------------------------------
# 7. GENERATE PREDICTIONS
# ------------------------------------------------------------

predictions = model.predict(X_scaled)

print("\nRisk predictions generated successfully!")


# ------------------------------------------------------------
# 8. ADD PREDICTIONS TO DATASET
# ------------------------------------------------------------

df["predicted_risk_score"] = predictions


# ------------------------------------------------------------
# 9. CLASSIFY PREDICTED RISK
# ------------------------------------------------------------

def classify_risk(score):

    if score >= 0.75:
        return "Immediate Action"

    elif score >= 0.60:
        return "High Priority"

    elif score >= 0.40:
        return "Monitor"

    else:
        return "Normal"


df["predicted_risk_category"] = (
    df["predicted_risk_score"]
    .apply(classify_risk)
)


# ------------------------------------------------------------
# 10. DISPLAY RESULTS
# ------------------------------------------------------------

print("\n===== PREDICTION RESULTS =====")

print(
    df[
        [
            "part_id",
            "supplier_id_primary",
            "combined_risk_score",
            "predicted_risk_score",
            "combined_risk_category",
            "predicted_risk_category"
        ]
    ].head(20).to_string(index=False)
)


# ------------------------------------------------------------
# 11. RISK CATEGORY DISTRIBUTION
# ------------------------------------------------------------

print("\n===== PREDICTED RISK DISTRIBUTION =====")

print(
    df["predicted_risk_category"]
    .value_counts()
)


# ------------------------------------------------------------
# 12. SAVE PREDICTIONS
# ------------------------------------------------------------

output_path = "../data/final_risk_predictions.csv"

df.to_csv(
    output_path,
    index=False
)

print("\nFinal predictions saved successfully!")

print("File:", output_path)


print("\n===== MODEL DEPLOYMENT COMPLETED =====")