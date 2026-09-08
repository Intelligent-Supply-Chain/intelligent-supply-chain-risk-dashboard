import pandas as pd


def calculate_hybrid_risk(df):
    df = df.copy()

    # --------------------------------------------------
    # CHECK REQUIRED COLUMNS
    # --------------------------------------------------

    if "predicted_risk_score" not in df.columns:
        raise ValueError(
            "predicted_risk_score column is missing."
        )

    if "ml_risk_score" not in df.columns:
        raise ValueError(
            "ml_risk_score column is missing."
        )

    # --------------------------------------------------
    # HYBRID RISK SCORE
    # --------------------------------------------------

    df["hybrid_risk_score"] = (
        0.40 * df["predicted_risk_score"]
        + 0.60 * df["ml_risk_score"]
    )

    # Keep score between 0 and 1
    df["hybrid_risk_score"] = (
        df["hybrid_risk_score"]
        .clip(0, 1)
    )

    # --------------------------------------------------
    # HYBRID RISK CATEGORY
    # --------------------------------------------------

    def classify_risk(score):

        if score >= 0.75:
            return "Immediate Action"

        elif score >= 0.50:
            return "High Priority"

        elif score >= 0.25:
            return "Monitor"

        else:
            return "Normal"

    df["hybrid_risk_category"] = (
        df["hybrid_risk_score"]
        .apply(classify_risk)
    )

    return df