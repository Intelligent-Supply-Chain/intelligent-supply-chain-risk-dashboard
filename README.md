# Intelligent Supply Chain Risk & Demand Analytics System

An end-to-end data analytics and machine learning project designed to identify supply chain risks at the part and supplier level.

The system analyzes demand, inventory, backorders, supplier performance, lead times, quality incidents, and part criticality to calculate risk scores and classify parts into different risk categories.

## 🚀 Live Dashboard

Access the deployed Streamlit dashboard here:

https://intelligent-supply-chain-risk-dashboard-nc8rodv4utmpbtl5e3pp4q.streamlit.app

---

## 📌 Project Objective

The main objective of this project is to build an intelligent supply chain risk monitoring system that helps organizations:

- Identify high-risk parts
- Detect parts requiring immediate action
- Monitor supplier performance
- Analyze inventory and demand risks
- Identify potential supply chain disruptions
- Support data-driven business decisions

---

## 🏗️ Project Architecture

The project follows an end-to-end data analytics and machine learning workflow:

Raw Data
↓
Data Cleaning & Preprocessing
↓
Feature Engineering
↓
Risk Feature Calculation
↓
Machine Learning Model
↓
Risk Prediction
↓
Final Risk Analysis
↓
Streamlit Dashboard

---

## 📊 Datasets

The project uses multiple supply chain datasets, including:

### Parts Master Data

Contains information about:

- Part ID
- Part family
- Criticality class
- Unit cost
- Lead time
- Primary supplier
- Supplier risk class
- Repairability
- Shelf life

### Demand & Forecast Data

Contains:

- Demand history
- Forecast information
- Site information
- Forecast type
- Consumption patterns

### Purchase Order Data

Contains:

- Purchase order information
- Order dates
- Supplier information
- Delivery performance
- Delay information

### Quality Incident Data

Contains:

- Quality incidents
- Defect severity
- Scrap information
- Incident dates

---

## ⚙️ Key Features

### 1. Demand Risk Analysis

Analyzes demand patterns using:

- Average demand
- Demand standard deviation
- Total demand
- Maximum demand

### 2. Inventory Risk Analysis

Evaluates:

- Average inventory
- Backorders
- Blocked inventory
- Inventory coverage

### 3. Supplier Risk Analysis

Evaluates supplier performance using:

- Delivery delays
- Late delivery rate
- Fill rate
- Supplier risk score

### 4. Quality Risk Analysis

Considers:

- Number of quality incidents
- Scrap quantity
- Defect severity

### 5. Part Risk Analysis

Combines multiple risk factors including:

- Demand risk
- Inventory risk
- Backorder risk
- Supplier delivery risk
- Lead-time risk
- Quality risk
- Criticality risk
- Cost risk

### 6. Machine Learning Risk Prediction

A trained machine learning model predicts the risk score for each part.

The prediction system classifies parts into:

- Normal
- Monitor
- High Priority
- Immediate Action

---

## 📈 Final Risk Distribution

The final prediction dataset contains 300 parts.

| Risk Category | Number of Parts |
|---|---:|
| Normal | 40 |
| Monitor | 176 |
| High Priority | 82 |
| Immediate Action | 2 |

The system identifies **2 parts requiring Immediate Action** and **82 High Priority parts**.

---

## 🚨 Immediate Action Parts

The current analysis identifies:

| Part ID | Supplier | Predicted Risk |
|---|---|---:|
| P00264 | SUP033 | 0.7805 |
| P00294 | SUP033 | 0.7625 |

These parts should receive immediate attention during supply chain risk assessment.

---

## 🏭 Supplier Risk Analysis

The system also performs supplier-wise risk analysis.

Important supplier-level metrics include:

- Total parts supplied
- Average risk
- Maximum risk
- Immediate Action parts
- High Priority parts

For example, supplier `SUP033` has the highest average risk among the analyzed suppliers and is associated with both Immediate Action parts.

---

## 💡 Business Recommendations

### Immediate Action

Review high-risk parts and their associated suppliers immediately.

### High Priority

Increase safety stock and closely monitor supplier delivery performance.

### Monitor

Continue monitoring demand, inventory, quality, and supplier performance.

### Normal

Continue normal inventory and supplier monitoring.

---

## 🛠️ Technologies Used

- Python
- Pandas
- NumPy
- Scikit-learn
- Plotly
- Streamlit
- Jupyter Notebook
- Git & GitHub

---

## 📁 Project Structure

```text
Intelligent_supply_chain/
│
├── app.py
│
├── data/
│   └── final_risk_predictions.csv
│
├── models/
│   ├── trained_model
│   ├── scaler
│   └── feature_list
│
├── src/
│   ├── data preprocessing
│   ├── feature engineering
│   ├── risk analysis
│   └── model inference
│
├── sql/
│   └── SQL scripts
│
├── requirements.txt
│
├── .gitignore
│
└── README.md