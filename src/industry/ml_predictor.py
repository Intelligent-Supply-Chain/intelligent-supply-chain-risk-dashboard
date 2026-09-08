import pandas as pd
import numpy as np
import joblib
from pathlib import Path


# ============================================================
# LOAD TRAINED MODEL
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = BASE_DIR / "models" / "best_risk_model.pkl"
SCALER_PATH = BASE_DIR / "models" / "risk_scaler.pkl"
FEATURES_PATH = BASE_DIR / "models" / "model_features.pkl"

model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)
model_features = joblib.load(FEATURES_PATH)


# ============================================================
# ML RISK PREDICTION
# ============================================================

def predict_ml_risk(df):

    df = df.copy()

    # --------------------------------------------------------
    # Convert available raw columns to numeric
    # --------------------------------------------------------

    numeric_columns = [
        "unit_cost",
        "lead_time_days",
        "demand",
        "inventory",
        "backorders",
        "defect_rate",
        "delivery_delay"
    ]

    for column in numeric_columns:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            ).fillna(0)


    # ========================================================
    # CREATE MODEL FEATURES FROM COMPANY DATA
    # ========================================================

    # --------------------------------------------------------
    # Basic demand features
    # --------------------------------------------------------

    if "demand" in df.columns:

        df["avg_demand"] = df["demand"]
        df["demand_std"] = 0.0
        df["total_demand"] = df["demand"]
        df["max_demand"] = df["demand"]

    else:

        df["avg_demand"] = 0.0
        df["demand_std"] = 0.0
        df["total_demand"] = 0.0
        df["max_demand"] = 0.0


    # --------------------------------------------------------
    # Inventory features
    # --------------------------------------------------------

    if "inventory" in df.columns:

        df["avg_inventory"] = df["inventory"]

    else:

        df["avg_inventory"] = 0.0


    # --------------------------------------------------------
    # Backorder features
    # --------------------------------------------------------

    if "backorders" in df.columns:

        df["avg_backorder"] = df["backorders"]
        df["total_backorder"] = df["backorders"]

    else:

        df["avg_backorder"] = 0.0
        df["total_backorder"] = 0.0


    # --------------------------------------------------------
    # Blocked inventory
    # --------------------------------------------------------

    if "blocked" in df.columns:

        df["avg_blocked"] = pd.to_numeric(
            df["blocked"],
            errors="coerce"
        ).fillna(0)

    else:

        df["avg_blocked"] = 0.0


    # --------------------------------------------------------
    # Inventory coverage
    # --------------------------------------------------------

    if (
        "inventory" in df.columns
        and "demand" in df.columns
    ):

        df["inventory_coverage"] = (
            df["inventory"] /
            df["demand"].replace(0, np.nan)
        )

        df["inventory_coverage"] = (
            df["inventory_coverage"]
            .replace([np.inf, -np.inf], np.nan)
            .fillna(0)
        )

    else:

        df["inventory_coverage"] = 0.0


    # --------------------------------------------------------
    # Delivery features
    # --------------------------------------------------------

    if "delivery_delay" in df.columns:

        df["avg_delay_days_x"] = df["delivery_delay"]

        df["late_delivery_rate_x"] = (
            df["delivery_delay"] > 0
        ).astype(float)

    else:

        df["avg_delay_days_x"] = 0.0
        df["late_delivery_rate_x"] = 0.0


    # --------------------------------------------------------
    # Fill rate
    # --------------------------------------------------------

    if (
        "demand" in df.columns
        and "backorders" in df.columns
    ):

        df["fill_rate_x"] = (
            1 -
            (
                df["backorders"] /
                df["demand"].replace(0, np.nan)
            )
        )

        df["fill_rate_x"] = (
            df["fill_rate_x"]
            .replace([np.inf, -np.inf], np.nan)
            .fillna(1)
            .clip(0, 1)
        )

    else:

        df["fill_rate_x"] = 1.0


    # --------------------------------------------------------
    # Quality features
    # --------------------------------------------------------

    if "defect_rate" in df.columns:

        df["quality_incidents_x"] = df["defect_rate"]

        if "demand" in df.columns:

            df["total_scrap_x"] = (
                df["defect_rate"] *
                df["demand"]
            )

        else:

            df["total_scrap_x"] = df["defect_rate"]

    else:

        df["quality_incidents_x"] = 0.0
        df["total_scrap_x"] = 0.0


    # ========================================================
    # RISK FEATURES
    # ========================================================

    # --------------------------------------------------------
    # Demand risk
    # --------------------------------------------------------

    if "demand_risk" not in df.columns:

        if "demand" in df.columns:

            demand_mean = df["demand"].mean()

            if demand_mean > 0:

                df["demand_risk"] = (
                    df["demand"] /
                    demand_mean
                ).clip(0, 2) / 2

            else:

                df["demand_risk"] = 0.0

        else:

            df["demand_risk"] = 0.0


    # --------------------------------------------------------
    # Inventory risk
    # --------------------------------------------------------

    if "inventory_risk" not in df.columns:

        if "inventory" in df.columns:

            inventory_mean = df["inventory"].mean()

            if inventory_mean > 0:

                df["inventory_risk"] = (
                    1 -
                    (
                        df["inventory"] /
                        inventory_mean
                    )
                ).clip(0, 1)

            else:

                df["inventory_risk"] = 0.0

        else:

            df["inventory_risk"] = 0.0


    # --------------------------------------------------------
    # Backorder risk
    # --------------------------------------------------------

    if "backorder_risk" not in df.columns:

        if "backorders" in df.columns:

            max_backorders = df["backorders"].max()

            if max_backorders > 0:

                df["backorder_risk"] = (
                    df["backorders"] /
                    max_backorders
                ).clip(0, 1)

            else:

                df["backorder_risk"] = 0.0

        else:

            df["backorder_risk"] = 0.0


    # --------------------------------------------------------
    # Supplier delivery risk
    # --------------------------------------------------------

    if "supplier_delivery_risk" not in df.columns:

        if "delivery_delay" in df.columns:

            max_delay = df["delivery_delay"].max()

            if max_delay > 0:

                df["supplier_delivery_risk"] = (
                    df["delivery_delay"] /
                    max_delay
                ).clip(0, 1)

            else:

                df["supplier_delivery_risk"] = 0.0

        else:

            df["supplier_delivery_risk"] = 0.0


    # --------------------------------------------------------
    # Lead time risk
    # --------------------------------------------------------

    if "lead_time_risk" not in df.columns:

        if "lead_time_days" in df.columns:

            max_lead = df["lead_time_days"].max()

            if max_lead > 0:

                df["lead_time_risk"] = (
                    df["lead_time_days"] /
                    max_lead
                ).clip(0, 1)

            else:

                df["lead_time_risk"] = 0.0

        else:

            df["lead_time_risk"] = 0.0


    # --------------------------------------------------------
    # Quality risk
    # --------------------------------------------------------

    if "quality_risk" not in df.columns:

        if "defect_rate" in df.columns:

            max_defect = df["defect_rate"].max()

            if max_defect > 0:

                df["quality_risk"] = (
                    df["defect_rate"] /
                    max_defect
                ).clip(0, 1)

            else:

                df["quality_risk"] = 0.0

        else:

            df["quality_risk"] = 0.0


    # --------------------------------------------------------
    # Criticality risk
    # --------------------------------------------------------

    if "criticality_risk" not in df.columns:

        df["criticality_risk"] = 0.0


    # --------------------------------------------------------
    # Cost risk
    # --------------------------------------------------------

    if "cost_risk" not in df.columns:

        if "unit_cost" in df.columns:

            max_cost = df["unit_cost"].max()

            if max_cost > 0:

                df["cost_risk"] = (
                    df["unit_cost"] /
                    max_cost
                ).clip(0, 1)

            else:

                df["cost_risk"] = 0.0

        else:

            df["cost_risk"] = 0.0


    # ========================================================
    # PART AND SUPPLIER RISK SCORES
    # ========================================================

    if "part_risk_score" not in df.columns:

        risk_columns = [
            "demand_risk",
            "inventory_risk",
            "backorder_risk",
            "lead_time_risk",
            "quality_risk"
        ]

        available = [
            col for col in risk_columns
            if col in df.columns
        ]

        if available:

            df["part_risk_score"] = (
                df[available]
                .mean(axis=1)
            )

        else:

            df["part_risk_score"] = 0.0


    if "supplier_risk_score" not in df.columns:

        supplier_columns = [
            "supplier_delivery_risk",
            "quality_risk",
            "lead_time_risk"
        ]

        available = [
            col for col in supplier_columns
            if col in df.columns
        ]

        if available:

            df["supplier_risk_score"] = (
                df[available]
                .mean(axis=1)
            )

        else:

            df["supplier_risk_score"] = 0.0


    # ========================================================
    # CREATE ANY REMAINING FEATURES
    # ========================================================

    for feature in model_features:

        if feature not in df.columns:

            df[feature] = 0.0


    # ========================================================
    # SELECT FEATURES IN EXACT TRAINING ORDER
    # ========================================================

    X = df[model_features].copy()


    # ========================================================
    # CONVERT EVERYTHING TO NUMERIC
    # ========================================================

    X = X.apply(
        pd.to_numeric,
        errors="coerce"
    )

    X = X.replace(
        [np.inf, -np.inf],
        np.nan
    )

    X = X.fillna(0)


    # ========================================================
    # SCALE FEATURES
    # ========================================================

    X_scaled = scaler.transform(X)


    # ========================================================
    # ML PREDICTION
    # ========================================================

    predictions = model.predict(X_scaled)


    # ========================================================
    # STORE ML RISK SCORE
    # ========================================================

    df["ml_risk_score"] = predictions

    df["ml_risk_score"] = (
        df["ml_risk_score"]
        .clip(0, 1)
    )


    # ========================================================
    # ML RISK CATEGORY
    # ========================================================

    def classify_risk(score):

        if score >= 0.75:
            return "Immediate Action"

        elif score >= 0.50:
            return "High Priority"

        elif score >= 0.25:
            return "Monitor"

        else:
            return "Normal"


    df["ml_risk_category"] = (
        df["ml_risk_score"]
        .apply(classify_risk)
    )


    return df