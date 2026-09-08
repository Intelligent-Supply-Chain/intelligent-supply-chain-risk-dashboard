import pandas as pd
import numpy as np


def calculate_risk_scores(df):
    """
    Calculate adaptive supply-chain risk scores
    using the risk factors available in the
    company's dataset.
    """

    df = df.copy()

    risk_factors = {}
    risk_weights = {}

    # --------------------------------------------------
    # DEMAND RISK
    # --------------------------------------------------

    if "demand" in df.columns:

        df["demand"] = pd.to_numeric(
            df["demand"],
            errors="coerce"
        )

        demand_mean = df["demand"].mean()

        if pd.notna(demand_mean) and demand_mean > 0:

            df["demand_risk"] = (
                df["demand"] / demand_mean
            ).clip(0, 2) / 2

            risk_factors["demand_risk"] = df["demand_risk"]
            risk_weights["demand_risk"] = 0.30

    # --------------------------------------------------
    # INVENTORY RISK
    # --------------------------------------------------

    if "inventory" in df.columns:

        df["inventory"] = pd.to_numeric(
            df["inventory"],
            errors="coerce"
        )

        inventory_mean = df["inventory"].mean()

        if pd.notna(inventory_mean) and inventory_mean > 0:

            df["inventory_risk"] = (
                1 -
                (df["inventory"] / inventory_mean)
            ).clip(0, 1)

            risk_factors["inventory_risk"] = df[
                "inventory_risk"
            ]

            risk_weights["inventory_risk"] = 0.30

    # --------------------------------------------------
    # LEAD TIME RISK
    # --------------------------------------------------

    if "lead_time_days" in df.columns:

        df["lead_time_days"] = pd.to_numeric(
            df["lead_time_days"],
            errors="coerce"
        )

        max_lead_time = df["lead_time_days"].max()

        if pd.notna(max_lead_time) and max_lead_time > 0:

            df["lead_time_risk"] = (
                df["lead_time_days"] /
                max_lead_time
            ).clip(0, 1)

            risk_factors["lead_time_risk"] = df[
                "lead_time_risk"
            ]

            risk_weights["lead_time_risk"] = 0.25

    # --------------------------------------------------
    # STOCK COVERAGE RISK
    # --------------------------------------------------

    if (
        "inventory" in df.columns
        and "demand" in df.columns
    ):

        df["stock_coverage"] = (
            df["inventory"] /
            df["demand"].replace(0, np.nan)
        )

        df["stock_coverage"] = (
            df["stock_coverage"]
            .replace(
                [np.inf, -np.inf],
                np.nan
            )
            .fillna(0)
        )

        df["stock_coverage_risk"] = (
            1 -
            df["stock_coverage"].clip(0, 1)
        )

        risk_factors["stock_coverage_risk"] = df[
            "stock_coverage_risk"
        ]

        risk_weights["stock_coverage_risk"] = 0.15

    # --------------------------------------------------
    # OPTIONAL: BACKORDER RISK
    # --------------------------------------------------

    if "backorders" in df.columns:

        df["backorders"] = pd.to_numeric(
            df["backorders"],
            errors="coerce"
        ).fillna(0)

        max_backorders = df["backorders"].max()

        if max_backorders > 0:

            df["backorder_risk"] = (
                df["backorders"] /
                max_backorders
            ).clip(0, 1)

            risk_factors["backorder_risk"] = df[
                "backorder_risk"
            ]

            risk_weights["backorder_risk"] = 0.20

    # --------------------------------------------------
    # OPTIONAL: QUALITY RISK
    # --------------------------------------------------

    if "defect_rate" in df.columns:

        df["defect_rate"] = pd.to_numeric(
            df["defect_rate"],
            errors="coerce"
        ).fillna(0)

        max_defect_rate = df["defect_rate"].max()

        if max_defect_rate > 0:

            df["quality_risk"] = (
                df["defect_rate"] /
                max_defect_rate
            ).clip(0, 1)

            risk_factors["quality_risk"] = df[
                "quality_risk"
            ]

            risk_weights["quality_risk"] = 0.20

        # --------------------------------------------------
    # OPTIONAL: DELIVERY DELAY RISK
    # --------------------------------------------------

    if "delivery_delay" in df.columns:

        df["delivery_delay"] = pd.to_numeric(
            df["delivery_delay"],
            errors="coerce"
        ).fillna(0)

        max_delay = df["delivery_delay"].max()

        if max_delay > 0:

            df["delivery_delay_risk"] = (
                df["delivery_delay"] /
                max_delay
            ).clip(0, 1)

            risk_factors["delivery_delay_risk"] = (
                df["delivery_delay_risk"]
            )

            risk_weights["delivery_delay_risk"] = 0.20
    # --------------------------------------------------
    # ADAPTIVE WEIGHT NORMALIZATION
    # --------------------------------------------------

    if not risk_factors:

        df["combined_risk_score"] = 0.0

    else:

        total_weight = sum(
            risk_weights.values()
        )

        df["combined_risk_score"] = 0.0

        for factor, values in risk_factors.items():

            normalized_weight = (
                risk_weights[factor] /
                total_weight
            )

            df["combined_risk_score"] += (
                normalized_weight * values
            )

    # --------------------------------------------------
    # FINAL RISK SCORE
    # --------------------------------------------------

    df["predicted_risk_score"] = (
        df["combined_risk_score"]
        .clip(0, 1)
    )

    # --------------------------------------------------
    # RISK CATEGORY
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

    df["predicted_risk_category"] = (
        df["predicted_risk_score"]
        .apply(classify_risk)
    )

    return df