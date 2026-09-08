import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

from src.industry.data_validator import validate_csv
from src.industry.risk_engine import calculate_risk_scores
from src.industry.column_mapper import (
    detect_columns,
    apply_column_mapping
)
from src.industry.ml_predictor import predict_ml_risk
from src.industry.hybrid_risk import calculate_hybrid_risk


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Supply Chain Risk Dashboard",
    page_icon="📦",
    layout="wide"
)


# ============================================================
# SIDEBAR - COMPANY CONFIGURATION
# ============================================================

st.sidebar.header("🏢 Company Configuration")

company_name = st.sidebar.text_input(
    "Company Name",
    placeholder="Enter company name"
)

industry = st.sidebar.text_input(
    "Industry",
    placeholder="e.g. Automotive, Manufacturing"
)

risk_tolerance = st.sidebar.slider(
    "Risk Tolerance",
    min_value=0.0,
    max_value=1.0,
    value=0.50,
    step=0.05
)


# ============================================================
# SIDEBAR - RISK CONFIGURATION
# ============================================================

st.sidebar.subheader("⚙️ Risk Configuration")

immediate_threshold = st.sidebar.slider(
    "Immediate Action Threshold",
    min_value=0.50,
    max_value=0.95,
    value=0.75,
    step=0.05
)

high_threshold = st.sidebar.slider(
    "High Priority Threshold",
    min_value=0.25,
    max_value=0.75,
    value=0.50,
    step=0.05
)

monitor_threshold = st.sidebar.slider(
    "Monitor Threshold",
    min_value=0.10,
    max_value=0.50,
    value=0.25,
    step=0.05
)


# ============================================================
# THRESHOLD VALIDATION
# ============================================================

if not (
    monitor_threshold
    < high_threshold
    < immediate_threshold
):
    st.sidebar.error(
        "Thresholds must follow: "
        "Monitor < High Priority < Immediate Action"
    )
    st.stop()


# ============================================================
# LOAD DEFAULT DATA
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_PATH = (
    BASE_DIR
    / "data"
    / "final_risk_predictions.csv"
)

try:

    df = pd.read_csv(DATA_PATH)

except FileNotFoundError:

    st.error(
        f"Default data file not found: {DATA_PATH}"
    )

    st.stop()


# ============================================================
# TITLE
# ============================================================

st.title(
    "📦 Intelligent Supply Chain Risk & Demand Analytics"
)

if company_name.strip():

    st.caption(
        f"🏢 {company_name.strip()} | "
        f"Industry: {industry if industry else 'Not specified'} | "
        f"Risk Tolerance: {risk_tolerance:.2f}"
    )

st.markdown(
    "### AI-Based Part and Supplier Risk Monitoring Dashboard"
)

st.divider()


# ============================================================
# COMPANY DATA TEMPLATE
# ============================================================

st.header("📋 Company Data Format")

st.write(
    "Upload your company's supply-chain data as a CSV file. "
    "The system automatically detects and maps common column names."
)

st.markdown(
    """
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
"""
)


template_data = pd.DataFrame({

    "Material_Code": [
        "MAT001",
        "MAT002"
    ],

    "Vendor_ID": [
        "VEN01",
        "VEN02"
    ],

    "Stock_On_Hand": [
        500,
        250
    ],

    "Monthly_Demand": [
        450,
        300
    ],

    "Supplier_Lead_Time": [
        10,
        25
    ],

    "Backorders": [
        5,
        20
    ],

    "Defect_Rate": [
        0.02,
        0.05
    ],

    "Delivery_Delay": [
        2,
        7
    ]
})


template_csv = template_data.to_csv(
    index=False
)


st.download_button(
    label="📥 Download Company CSV Template",
    data=template_csv,
    file_name="company_supply_chain_template.csv",
    mime="text/csv"
)


st.divider()


# ============================================================
# COMPANY DATA UPLOAD
# ============================================================

st.header("📂 Upload Company Supply Chain Data")

uploaded_file = st.file_uploader(
    "Upload a CSV file",
    type=["csv"]
)


# ============================================================
# PROCESS UPLOADED DATA
# ============================================================

if uploaded_file is not None:

    # --------------------------------------------------------
    # COMPANY NAME VALIDATION
    # --------------------------------------------------------

    if not company_name.strip():

        st.warning(
            "Please enter your company name before uploading data."
        )

        st.stop()


    # --------------------------------------------------------
    # VALIDATE CSV
    # --------------------------------------------------------

    df_uploaded, validation_messages = validate_csv(
        uploaded_file
    )


    if df_uploaded is None:

        st.error(
            "❌ Unable to process the uploaded CSV file."
        )

        st.stop()


    # --------------------------------------------------------
    # USE UPLOADED DATA
    # --------------------------------------------------------

    df = df_uploaded.copy()

    st.success(
        "✅ CSV file uploaded successfully!"
    )


    # ========================================================
    # UPLOADED DATASET
    # ========================================================

    st.subheader("📊 Uploaded Dataset")

    st.write(
        f"Rows: {df.shape[0]} | "
        f"Columns: {df.shape[1]}"
    )

    st.dataframe(
        df.head(10),
        use_container_width=True
    )


    # ========================================================
    # DATA VALIDATION
    # ========================================================

    st.subheader("⚠️ Data Validation Results")

    if validation_messages:

        for message in validation_messages:

            if "duplicate" in message.lower():

                st.warning(message)

            elif "missing" in message.lower():

                st.warning(message)

            else:

                st.info(message)

    else:

        st.success(
            "✅ No data quality issues detected."
        )


    # ========================================================
    # COLUMN MAPPING
    # ========================================================

    st.subheader("🔗 Column Mapping")

    detected_mapping = detect_columns(df)


    if not detected_mapping:

        st.error(
            "❌ Unable to detect compatible columns "
            "in the uploaded dataset."
        )

        st.stop()


    mapping_display = pd.DataFrame(
        [
            {
                "Company Column": original,
                "Standard Column": standard
            }

            for standard, original
            in detected_mapping.items()
        ]
    )


    st.dataframe(
        mapping_display,
        use_container_width=True,
        hide_index=True
    )


    # --------------------------------------------------------
    # APPLY MAPPING
    # --------------------------------------------------------

    df = apply_column_mapping(
        df,
        detected_mapping
    )


    st.success(
        "✅ Company columns successfully standardized."
    )


# ============================================================
# RISK ENGINE
# ============================================================

try:

    df = calculate_risk_scores(df)

except Exception as e:

    st.error(
        f"❌ Risk calculation failed: {e}"
    )

    st.stop()


# ============================================================
# ML RISK PREDICTION
# ============================================================

try:

    df = predict_ml_risk(df)

except Exception as e:

    st.error(
        f"❌ ML risk prediction failed: {e}"
    )

    st.stop()


# ============================================================
# HYBRID RISK ANALYSIS
# ============================================================

try:

    df = calculate_hybrid_risk(df)

except Exception as e:

    st.error(
        f"❌ Hybrid risk calculation failed: {e}"
    )

    st.stop()


# ============================================================
# VERIFY HYBRID RISK SCORE
# ============================================================

if "hybrid_risk_score" not in df.columns:

    st.error(
        "❌ Hybrid risk score was not generated."
    )

    st.write(
        "Available columns:"
    )

    st.write(
        list(df.columns)
    )

    st.stop()


# ============================================================
# CLEAN HYBRID RISK SCORE
# ============================================================

df["hybrid_risk_score"] = pd.to_numeric(
    df["hybrid_risk_score"],
    errors="coerce"
)

df["hybrid_risk_score"] = (
    df["hybrid_risk_score"]
    .fillna(0)
    .clip(0, 1)
)


# ============================================================
# USE HYBRID RISK AS FINAL PREDICTION
# ============================================================

df["predicted_risk_score"] = (
    df["hybrid_risk_score"]
)


# ============================================================
# HYBRID RISK CATEGORY
# ============================================================

def classify_company_risk(score):

    if pd.isna(score):
        return "Normal"

    if score >= immediate_threshold:
        return "Immediate Action"

    elif score >= high_threshold:
        return "High Priority"

    elif score >= monitor_threshold:
        return "Monitor"

    else:
        return "Normal"


df["hybrid_risk_category"] = (
    df["hybrid_risk_score"]
    .apply(classify_company_risk)
)


st.success(
    "✅ ML + Hybrid risk analysis completed successfully."
)


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.header("🎛️ Dashboard Filters")


risk_categories = sorted(
    df[
        "hybrid_risk_category"
    ]
    .dropna()
    .unique()
)


selected_risk = st.sidebar.multiselect(
    "Select Risk Category",
    risk_categories,
    default=risk_categories
)


if "supplier_id_primary" in df.columns:

    suppliers = sorted(
        df[
            "supplier_id_primary"
        ]
        .dropna()
        .unique()
    )

    selected_suppliers = st.sidebar.multiselect(
        "Select Supplier",
        suppliers,
        default=suppliers
    )

else:

    selected_suppliers = []


# ============================================================
# CURRENT THRESHOLDS
# ============================================================

st.sidebar.write(
    "Current thresholds:"
)

st.sidebar.write(
    f"Monitor: {monitor_threshold:.2f}"
)

st.sidebar.write(
    f"High Priority: {high_threshold:.2f}"
)

st.sidebar.write(
    f"Immediate Action: {immediate_threshold:.2f}"
)


# ============================================================
# APPLY FILTERS
# ============================================================

filtered_df = df[
    df[
        "hybrid_risk_category"
    ].isin(selected_risk)
]


if "supplier_id_primary" in df.columns:

    filtered_df = filtered_df[
        filtered_df[
            "supplier_id_primary"
        ].isin(selected_suppliers)
    ]


# ============================================================
# KPI CALCULATIONS
# ============================================================

total_parts = len(filtered_df)


immediate_action_count = len(
    filtered_df[
        filtered_df[
            "hybrid_risk_category"
        ] == "Immediate Action"
    ]
)


high_priority_count = len(
    filtered_df[
        filtered_df[
            "hybrid_risk_category"
        ] == "High Priority"
    ]
)


monitor_count = len(
    filtered_df[
        filtered_df[
            "hybrid_risk_category"
        ] == "Monitor"
    ]
)


normal_count = len(
    filtered_df[
        filtered_df[
            "hybrid_risk_category"
        ] == "Normal"
    ]
)


if len(filtered_df) > 0:

    average_risk = (
        filtered_df[
            "hybrid_risk_score"
        ].mean()
    )

else:

    average_risk = 0


# ============================================================
# KPI CARDS
# ============================================================

st.subheader("📊 Risk Overview")


col1, col2, col3, col4, col5 = st.columns(5)


col1.metric(
    "Total Parts",
    total_parts
)


col2.metric(
    "Immediate Action",
    immediate_action_count
)


col3.metric(
    "High Priority",
    high_priority_count
)


col4.metric(
    "Monitor",
    monitor_count
)


col5.metric(
    "Average Risk",
    f"{average_risk:.3f}"
)


st.divider()


# ============================================================
# RISK DISTRIBUTION
# ============================================================

col1, col2 = st.columns(2)


with col1:

    st.subheader(
        "Risk Category Distribution"
    )


    if not filtered_df.empty:

        risk_distribution = (
            filtered_df[
                "hybrid_risk_category"
            ]
            .value_counts()
            .reset_index()
        )


        risk_distribution.columns = [
            "Risk Category",
            "Count"
        ]


        fig = px.bar(
            risk_distribution,
            x="Risk Category",
            y="Count",
            title="Parts by Hybrid Risk Category",
            text="Count"
        )


        fig.update_traces(
            textposition="outside"
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.info(
            "No data available for the selected filters."
        )


with col2:

    st.subheader(
        "Risk Category Share"
    )


    if not filtered_df.empty:

        risk_distribution = (
            filtered_df[
                "hybrid_risk_category"
            ]
            .value_counts()
            .reset_index()
        )


        risk_distribution.columns = [
            "Risk Category",
            "Count"
        ]


        fig_pie = px.pie(
            risk_distribution,
            names="Risk Category",
            values="Count",
            title="Hybrid Risk Distribution"
        )


        st.plotly_chart(
            fig_pie,
            use_container_width=True
        )

    else:

        st.info(
            "No data available for the selected filters."
        )


# ============================================================
# TOP HIGH-RISK PARTS
# ============================================================

st.divider()

st.subheader(
    "🚨 Top 20 Highest Risk Parts"
)


top_risk = (
    filtered_df
    .sort_values(
        "hybrid_risk_score",
        ascending=False
    )
    .head(20)
)


display_columns = [
    "part_id",
    "supplier_id_primary",
    "ml_risk_score",
    "hybrid_risk_score",
    "hybrid_risk_category"
]


available_display_columns = [
    column
    for column in display_columns
    if column in top_risk.columns
]


if not top_risk.empty:

    st.dataframe(
        top_risk[
            available_display_columns
        ],
        use_container_width=True,
        hide_index=True
    )

else:

    st.info(
        "No high-risk parts available for the selected filters."
    )


# ============================================================
# IMMEDIATE ACTION REQUIRED
# ============================================================

st.subheader(
    "🚨 Immediate Action Required"
)


immediate_action_df = df[
    df[
        "hybrid_risk_category"
    ]
    .astype(str)
    .str.strip()
    == "Immediate Action"
]


if immediate_action_df.empty:

    st.success(
        "✅ No immediate action required."
    )

else:

    st.error(
        f"{len(immediate_action_df)} "
        "part(s) require immediate action."
    )


    immediate_columns = [
        "part_id",
        "supplier_id_primary",
        "ml_risk_score",
        "hybrid_risk_score",
        "hybrid_risk_category"
    ]


    immediate_columns = [
        column
        for column in immediate_columns
        if column in immediate_action_df.columns
    ]


    st.dataframe(
        immediate_action_df[
            immediate_columns
        ]
        .sort_values(
            "hybrid_risk_score",
            ascending=False
        ),
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# HIGH PRIORITY PARTS
# ============================================================

st.divider()

st.subheader(
    "🟠 High Priority Parts"
)


high_df = filtered_df[
    filtered_df[
        "hybrid_risk_category"
    ] == "High Priority"
].sort_values(
    "hybrid_risk_score",
    ascending=False
)


high_display_columns = [
    column
    for column in display_columns
    if column in high_df.columns
]


if not high_df.empty:

    st.dataframe(
        high_df[
            high_display_columns
        ],
        use_container_width=True,
        hide_index=True
    )

else:

    st.info(
        "No high-priority parts available for the selected filters."
    )


# ============================================================
# SUPPLIER RISK ANALYSIS
# ============================================================

st.divider()

st.subheader(
    "🏭 Supplier Risk Analysis"
)


if "supplier_id_primary" in filtered_df.columns:

    supplier_aggregation = {
        "part_id": "count",
        "hybrid_risk_score": ["mean", "max"]
    }


    supplier_analysis = (
        filtered_df
        .groupby(
            "supplier_id_primary"
        )
        .agg(
            total_parts=(
                "part_id",
                "count"
            ),

            average_hybrid_risk=(
                "hybrid_risk_score",
                "mean"
            ),

            maximum_hybrid_risk=(
                "hybrid_risk_score",
                "max"
            )
        )
        .reset_index()
    )


    supplier_analysis = (
        supplier_analysis
        .sort_values(
            "average_hybrid_risk",
            ascending=False
        )
    )


    col1, col2 = st.columns(2)


    with col1:

        fig_supplier = px.bar(
            supplier_analysis.head(15),
            x="supplier_id_primary",
            y="average_hybrid_risk",
            title="Top Suppliers by Average Hybrid Risk",
            text_auto=".3f"
        )


        st.plotly_chart(
            fig_supplier,
            use_container_width=True
        )


    with col2:

        fig_supplier_max = px.bar(
            supplier_analysis.head(15),
            x="supplier_id_primary",
            y="maximum_hybrid_risk",
            title="Maximum Hybrid Risk by Supplier",
            text_auto=".3f"
        )


        st.plotly_chart(
            fig_supplier_max,
            use_container_width=True
        )


    st.dataframe(
        supplier_analysis,
        use_container_width=True,
        hide_index=True
    )


else:

    st.info(
        "Supplier information was not provided "
        "in the uploaded dataset."
    )


# ============================================================
# RISK SCORE DISTRIBUTION
# ============================================================

st.divider()

st.subheader(
    "📈 Hybrid Risk Score Distribution"
)


if not filtered_df.empty:

    fig_hist = px.histogram(
        filtered_df,
        x="hybrid_risk_score",
        nbins=20,
        title="Distribution of Hybrid Risk Scores"
    )


    st.plotly_chart(
        fig_hist,
        use_container_width=True
    )

else:

    st.info(
        "No data available for the selected filters."
    )


# ============================================================
# BUSINESS RECOMMENDATIONS
# ============================================================

st.divider()

st.subheader(
    "💡 Business Recommendations"
)


st.markdown(
    """
### 🔴 Immediate Action

- Review the affected parts immediately.
- Investigate the associated suppliers.
- Check inventory and backorder conditions.
- Consider increasing safety stock.
- Review supplier delivery performance.

### 🟠 High Priority

- Closely monitor supplier performance.
- Increase safety stock where required.
- Review demand and inventory trends.
- Investigate repeated delays or quality problems.

### 🟡 Monitor

- Continue regular monitoring.
- Track changes in demand and inventory.
- Watch supplier performance.

### 🟢 Normal

- Continue normal inventory management.
- No immediate intervention is required.
"""
)


# ============================================================
# DETAILED PART RISK ANALYSIS
# ============================================================

st.markdown("---")

st.header(
    "🔎 Detailed Part Risk Analysis"
)


st.write(
    "Use the filters below to investigate individual parts, "
    "their suppliers, risk scores and risk categories."
)


# ============================================================
# PART SELECTOR
# ============================================================

if "part_id" in df.columns and not df.empty:

    selected_part = st.selectbox(
        "Select Part",
        sorted(
            df[
                "part_id"
            ].dropna().unique()
        )
    )


    part_data = df[
        df["part_id"] == selected_part
    ].iloc[0]


    # ========================================================
    # SELECTED PART INFORMATION
    # ========================================================

    col1, col2, col3, col4, col5 = st.columns(5)


    with col1:

        st.metric(
            "Supplier",
            part_data.get(
                "supplier_id_primary",
                "N/A"
            )
        )


    with col2:

        ml_score = part_data.get(
            "ml_risk_score",
            0
        )

        try:
            ml_score = float(ml_score)
        except (TypeError, ValueError):
            ml_score = 0

        st.metric(
            "ML Risk Score",
            f"{ml_score:.3f}"
        )


    with col3:

        hybrid_score = part_data.get(
            "hybrid_risk_score",
            0
        )

        try:
            hybrid_score = float(hybrid_score)
        except (TypeError, ValueError):
            hybrid_score = 0

        st.metric(
            "Hybrid Risk Score",
            f"{hybrid_score:.3f}"
        )


    with col4:

        st.metric(
            "Risk Category",
            part_data.get(
                "hybrid_risk_category",
                "N/A"
            )
        )


    with col5:

        combined_score = part_data.get(
            "combined_risk_score",
            hybrid_score
        )

        try:
            combined_score = float(combined_score)
        except (TypeError, ValueError):
            combined_score = hybrid_score

        st.metric(
            "Combined Risk",
            f"{combined_score:.3f}"
        )


    # ========================================================
    # RISK FACTORS
    # ========================================================

    st.subheader(
        "Risk Factors"
    )


    risk_columns = [

        "demand_risk",

        "inventory_risk",

        "backorder_risk",

        "supplier_delivery_risk",

        "lead_time_risk",

        "quality_risk",

        "defect_rate_risk",

        "stock_coverage_risk",

        "delivery_delay_risk",

        "criticality_risk",

        "cost_risk"
    ]


    available_risk_columns = [

        column

        for column in risk_columns

        if column in df.columns
    ]


    if available_risk_columns:

        risk_factor_data = pd.DataFrame({

            "Risk Factor":
                available_risk_columns,

            "Risk Score": [

                part_data[column]

                for column
                in available_risk_columns

            ]
        })


        st.dataframe(
            risk_factor_data,
            use_container_width=True,
            hide_index=True
        )


    else:

        st.info(
            "No detailed risk-factor information "
            "is available for this dataset."
        )


    # ========================================================
    # MAIN RISK DRIVERS
    # ========================================================

    st.subheader(
        "🚨 Main Risk Drivers"
    )


    risk_driver_columns = {

        "demand_risk":
            "Demand Risk",

        "inventory_risk":
            "Inventory Risk",

        "lead_time_risk":
            "Lead Time Risk",

        "stock_coverage_risk":
            "Stock Coverage Risk",

        "backorder_risk":
            "Backorder Risk",

        "quality_risk":
            "Quality Risk",

        "defect_rate_risk":
            "Quality Risk",

        "delivery_delay_risk":
            "Delivery Delay Risk",

        "criticality_risk":
            "Criticality Risk",

        "cost_risk":
            "Cost Risk"
    }


    available_drivers = []


    for column, label in risk_driver_columns.items():

        if column in part_data.index:

            value = part_data[column]

            if pd.notna(value):

                try:

                    available_drivers.append({

                        "Risk Driver": label,

                        "Score": float(value)

                    })

                except (TypeError, ValueError):

                    pass


    if available_drivers:

        driver_df = (

            pd.DataFrame(
                available_drivers
            )

            .sort_values(
                "Score",
                ascending=False
            )
        )


        st.dataframe(
            driver_df,
            use_container_width=True,
            hide_index=True
        )


        top_driver = driver_df.iloc[0]


        st.warning(
            f"⚠️ Main risk driver: "
            f"**{top_driver['Risk Driver']}** "
            f"(score: {top_driver['Score']:.3f})"
        )


        # ====================================================
        # DYNAMIC BUSINESS RECOMMENDATION
        # ====================================================

        st.subheader(
            "💡 Recommended Action"
        )


        top_driver_name = (
            top_driver["Risk Driver"]
        )


        if top_driver_name == "Backorder Risk":

            st.error(
                "🔴 High backorder risk detected. "
                "Prioritize pending orders, review replenishment "
                "levels and investigate the cause of the backlog."
            )


        elif top_driver_name == "Lead Time Risk":

            st.warning(
                "🟠 High lead-time risk detected. "
                "Review supplier lead times, improve order planning "
                "and consider alternate suppliers."
            )


        elif top_driver_name == "Inventory Risk":

            st.warning(
                "🟡 High inventory risk detected. "
                "Review stock levels and consider increasing "
                "safety-stock coverage."
            )


        elif top_driver_name == "Demand Risk":

            st.warning(
                "🟠 High demand risk detected. "
                "Review demand forecasts and adjust inventory "
                "planning accordingly."
            )


        elif top_driver_name == "Delivery Delay Risk":

            st.error(
                "🔴 High delivery-delay risk detected. "
                "Investigate supplier delivery performance "
                "and consider corrective action."
            )


        elif top_driver_name == "Quality Risk":

            st.error(
                "🔴 High quality risk detected. "
                "Investigate supplier defects and strengthen "
                "quality-control procedures."
            )


        else:

            st.info(
                f"ℹ️ The primary risk driver is "
                f"**{top_driver_name}**. "
                "Review this factor and monitor the part closely."
            )


    else:

        st.info(
            "Detailed risk-driver information is not available "
            "for this dataset."
        )


else:

    st.info(
        "No part-level information is available."
    )


# ============================================================
# DOWNLOAD RISK PREDICTIONS
# ============================================================

st.markdown("---")

st.subheader(
    "📥 Download Risk Predictions"
)


csv_data = filtered_df.to_csv(
    index=False
)


st.download_button(
    label="Download Current Risk Data as CSV",
    data=csv_data,
    file_name="filtered_risk_predictions.csv",
    mime="text/csv"
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Intelligent Supply Chain Risk & Demand Analytics System | "
    "AI & Data Science Project"
)