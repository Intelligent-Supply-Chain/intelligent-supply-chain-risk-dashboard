# Intelligent Supply Chain Risk & Demand Analytics System

## Problem Statement

Supply chains are affected by demand fluctuations, inventory shortages, supplier delays, backorders, quality issues and long lead times. These factors can increase operational risk and negatively affect business performance.

The Intelligent Supply Chain Risk & Demand Analytics System is an AI and data-driven dashboard designed to identify, analyze and monitor supply-chain risks at part and supplier levels.

The system combines rule-based risk analysis with machine learning predictions to generate a Hybrid Risk Score for more comprehensive risk assessment.

---

## Key Features

- Company-specific supply-chain CSV upload
- Automatic column detection and mapping
- Data validation and quality checks
- Adaptive rule-based risk scoring
- Machine Learning based risk prediction
- Hybrid Risk Score combining rule-based and ML predictions
- Risk categorization into:
  - Normal
  - Monitor
  - High Priority
  - Immediate Action
- Part-level risk analysis
- Supplier-level risk analysis
- Identification of major risk drivers
- Dynamic business recommendations
- Interactive Streamlit dashboard
- Risk filtering by category and supplier
- Top high-risk parts identification
- Risk score distribution visualization
- CSV export of risk predictions

---

## Risk Factors

The system analyzes multiple supply-chain risk factors, including:

- Demand Risk
- Inventory Risk
- Backorder Risk
- Lead Time Risk
- Supplier Delivery Risk
- Quality Risk
- Stock Coverage Risk
- Delivery Delay Risk
- Criticality Risk
- Cost Risk

---

## Hybrid Risk Model

The final Hybrid Risk Score combines the rule-based risk score and the machine-learning risk score.

The current configuration uses:

- 40% Rule-Based Risk Score
- 60% Machine Learning Risk Score

The resulting Hybrid Risk Score is normalized between 0 and 1.

---

## Risk Categories

| Risk Score | Category |
|------------|----------|
| 0.00 - 0.24 | Normal |
| 0.25 - 0.49 | Monitor |
| 0.50 - 0.74 | High Priority |
| 0.75 - 1.00 | Immediate Action |

The dashboard also allows the user to customize these thresholds.

---

## Dataset

The system is designed to work with company supply-chain data provided in CSV format.

### Required Information

- Part / Material ID
- Supplier / Vendor ID
- Inventory / Stock on Hand
- Demand / Monthly Demand
- Supplier Lead Time

### Optional Information

- Backorders
- Defect Rate
- Delivery Delay
- Criticality
- Unit Cost

The dashboard automatically detects and maps common company-specific column names to standardized columns.

---

## Machine Learning

The system uses a trained machine-learning model to generate ML-based risk predictions.

The trained model and preprocessing objects are stored in the `models` directory.

Files include:

- `best_risk_model.pkl`
- `risk_scaler.pkl`
- `model_features.pkl`

The ML prediction pipeline:

1. Loads the trained model.
2. Converts available company data into numerical features.
3. Creates the required model features.
4. Applies the trained scaler.
5. Generates ML risk predictions.
6. Converts predictions into risk categories.

---

## Rule-Based Risk Engine

The rule-based risk engine evaluates available supply-chain risk factors and calculates an adaptive combined risk score.

The system dynamically normalizes risk-factor weights depending on which risk factors are available in the uploaded dataset.

This allows the dashboard to work with different company datasets without requiring every optional field.

---

## Hybrid Risk Analysis

The system combines:

```text
Rule-Based Risk Score
            +
Machine Learning Risk Score
            ↓
      Hybrid Risk Score
            ↓
       Risk Category