import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Supply Chain Risk Dashboard",
    page_icon="📦",
    layout="wide"
)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "final_risk_predictions.csv"

try:
    df = pd.read_csv(DATA_PATH)
except FileNotFoundError:
    st.error(f"File not found: {DATA_PATH}")
    st.stop()

# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("📦 Intelligent Supply Chain Risk & Demand Analytics")
st.markdown(
    "### AI-Based Part and Supplier Risk Monitoring Dashboard"
)

st.divider()

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.header("Dashboard Filters")

# Risk category filter
risk_categories = sorted(df["predicted_risk_category"].dropna().unique())

selected_risk = st.sidebar.multiselect(
    "Select Risk Category",
    risk_categories,
    default=risk_categories
)

# Supplier filter
suppliers = sorted(df["supplier_id_primary"].dropna().unique())

selected_suppliers = st.sidebar.multiselect(
    "Select Supplier",
    suppliers,
    default=suppliers
)

# Apply filters
filtered_df = df[
    (df["predicted_risk_category"].isin(selected_risk)) &
    (df["supplier_id_primary"].isin(selected_suppliers))
]

# --------------------------------------------------
# KPI CALCULATIONS
# --------------------------------------------------

total_parts = len(filtered_df)

immediate_action = len(
    filtered_df[
        filtered_df["predicted_risk_category"] == "Immediate Action"
    ]
)

high_priority = len(
    filtered_df[
        filtered_df["predicted_risk_category"] == "High Priority"
    ]
)

monitor = len(
    filtered_df[
        filtered_df["predicted_risk_category"] == "Monitor"
    ]
)

normal = len(
    filtered_df[
        filtered_df["predicted_risk_category"] == "Normal"
    ]
)

average_risk = filtered_df["predicted_risk_score"].mean()

# --------------------------------------------------
# KPI CARDS
# --------------------------------------------------

st.subheader("📊 Risk Overview")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Total Parts",
    total_parts
)

col2.metric(
    "Immediate Action",
    immediate_action
)

col3.metric(
    "High Priority",
    high_priority
)

col4.metric(
    "Monitor",
    monitor
)

col5.metric(
    "Average Risk",
    f"{average_risk:.3f}"
)

st.divider()

# --------------------------------------------------
# RISK DISTRIBUTION
# --------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    st.subheader("Risk Category Distribution")

    risk_distribution = (
        filtered_df["predicted_risk_category"]
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
        title="Parts by Risk Category",
        text="Count"
    )

    fig.update_traces(
        textposition="outside"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with col2:

    st.subheader("Risk Category Share")

    fig_pie = px.pie(
        risk_distribution,
        names="Risk Category",
        values="Count",
        title="Risk Distribution"
    )

    st.plotly_chart(
        fig_pie,
        use_container_width=True
    )

# --------------------------------------------------
# TOP HIGH-RISK PARTS
# --------------------------------------------------

st.divider()

st.subheader("🚨 Top 20 Highest Risk Parts")

top_risk = (
    filtered_df
    .sort_values(
        "predicted_risk_score",
        ascending=False
    )
    .head(20)
)

display_columns = [
    "part_id",
    "supplier_id_primary",
    "combined_risk_score",
    "predicted_risk_score",
    "predicted_risk_category"
]

st.dataframe(
    top_risk[display_columns],
    use_container_width=True,
    hide_index=True
)

# ============================================================
# IMMEDIATE ACTION REQUIRED
# ============================================================

st.subheader("🚨 Immediate Action Required")

immediate_action = df[
    df["predicted_risk_category"].astype(str).str.strip() == "Immediate Action"
]

if immediate_action.empty:
    st.warning("No immediate action required.")
else:
    st.error(
        f"{len(immediate_action)} part(s) require immediate action."
    )

    st.dataframe(
        immediate_action[
            [
                "part_id",
                "supplier_id_primary",
                "combined_risk_score",
                "predicted_risk_score",
                "predicted_risk_category"
            ]
        ].sort_values(
            "predicted_risk_score",
            ascending=False
        ),
        use_container_width=True,
        hide_index=True
    )

# --------------------------------------------------
# HIGH PRIORITY PARTS
# --------------------------------------------------

st.divider()

st.subheader("🟠 High Priority Parts")

high_df = filtered_df[
    filtered_df["predicted_risk_category"]
    == "High Priority"
].sort_values(
    "predicted_risk_score",
    ascending=False
)

st.dataframe(
    high_df[display_columns],
    use_container_width=True,
    hide_index=True
)

# --------------------------------------------------
# SUPPLIER RISK ANALYSIS
# --------------------------------------------------

st.divider()

st.subheader("🏭 Supplier Risk Analysis")

supplier_analysis = (
    filtered_df
    .groupby("supplier_id_primary")
    .agg(
        total_parts=("part_id", "count"),
        average_risk=("predicted_risk_score", "mean"),
        maximum_risk=("predicted_risk_score", "max")
    )
    .reset_index()
)

supplier_analysis = supplier_analysis.sort_values(
    "average_risk",
    ascending=False
)

col1, col2 = st.columns(2)

with col1:

    fig_supplier = px.bar(
        supplier_analysis.head(15),
        x="supplier_id_primary",
        y="average_risk",
        title="Top Suppliers by Average Risk",
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
        y="maximum_risk",
        title="Maximum Risk by Supplier",
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

# --------------------------------------------------
# RISK SCORE DISTRIBUTION
# --------------------------------------------------

st.divider()

st.subheader("📈 Predicted Risk Score Distribution")

fig_hist = px.histogram(
    filtered_df,
    x="predicted_risk_score",
    nbins=20,
    title="Distribution of Predicted Risk Scores"
)

st.plotly_chart(
    fig_hist,
    use_container_width=True
)

# --------------------------------------------------
# BUSINESS RECOMMENDATIONS
# --------------------------------------------------

st.divider()

st.subheader("💡 Business Recommendations")

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

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "Intelligent Supply Chain Risk & Demand Analytics System | "
    "AI & Data Science Project"
)

# ============================================================
# DETAILED PART RISK ANALYSIS
# ============================================================

st.markdown("---")

st.header("🔎 Detailed Part Risk Analysis")

st.write(
    "Use the filters below to investigate individual parts, "
    "their suppliers, risk scores and risk categories."
)

# Part selector
selected_part = st.selectbox(
    "Select Part",
    sorted(df["part_id"].unique())
)

# Get selected part
part_data = df[df["part_id"] == selected_part].iloc[0]

# Display selected part information
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Supplier",
        part_data["supplier_id_primary"]
    )

with col2:
    st.metric(
        "Risk Score",
        f"{part_data['predicted_risk_score']:.3f}"
    )

with col3:
    st.metric(
        "Risk Category",
        part_data["predicted_risk_category"]
    )

with col4:
    st.metric(
        "Combined Risk",
        f"{part_data['combined_risk_score']:.3f}"
    )


# Detailed feature information
st.subheader("Risk Factors")

risk_columns = [
    "demand_risk",
    "inventory_risk",
    "backorder_risk",
    "supplier_delivery_risk",
    "lead_time_risk",
    "quality_risk",
    "criticality_risk",
    "cost_risk"
]

available_risk_columns = [
    col for col in risk_columns if col in df.columns
]

if available_risk_columns:
    risk_factor_data = pd.DataFrame({
        "Risk Factor": available_risk_columns,
        "Risk Score": [
            part_data[col] for col in available_risk_columns
        ]
    })

    st.dataframe(
        risk_factor_data,
        use_container_width=True,
        hide_index=True
    )


# Download filtered data
st.markdown("---")

st.subheader("📥 Download Risk Predictions")

csv_data = filtered_df.to_csv(index=False)

st.download_button(
    label="Download Current Risk Data as CSV",
    data=csv_data,
    file_name="filtered_risk_predictions.csv",
    mime="text/csv"
)