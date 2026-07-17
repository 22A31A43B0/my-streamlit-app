import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration & Styling
st.set_page_config(page_title="Power BU Operations Dashboard", layout="wide")

st.title("📊 Power BU Live Operations Dashboard")
st.markdown("---")

# 2. Complete Data Loading Pipeline
@st.cache_data
def load_all_data():
    # --- SALES DATA ---
    df_sales_raw = pd.read_excel("Copy of Power BU July Plan - Revised 1st July.xlsx", sheet_name="Summary")
    df_sales = df_sales_raw.iloc[2:5, 1:3].copy()
    df_sales.columns = ["Product Line", "Sales Value (K$)"]
    df_sales["Sales Value (K$)"] = pd.to_numeric(df_sales["Sales Value (K$)"])
    
    # --- HEADCOUNT DETAILED DATA ---
    df_hc_raw = pd.read_excel("Copy of July 26.xlsx", sheet_name="Summary-HC")
    
    # Extract specific rows exactly as they are in the sheet
    bk_cable = df_hc_raw.iloc[1, [1, 2, 3]].values
    acwhip = df_hc_raw.iloc[2, [1, 2, 3]].values
    connector = df_hc_raw.iloc[3, [1, 2, 3]].values
    bench = df_hc_raw.iloc[4, [1, 2, 3]].values
    ev = df_hc_raw.iloc[5, [1, 2, 3]].values
    qa = df_hc_raw.iloc[10, [1, 2, 3]].values
    npi = df_hc_raw.iloc[11, [1, 2, 3]].values
    
    # Create clean detailed table
    raw_data = [
        ["BK Cable Assembly", bk_cable[1], bk_cable[2]],
        ["ACWHIP", acwhip[1], acwhip[2]],
        ["Connector", connector[1], connector[2]],
        ["Bench", bench[1], bench[2]],
        ["EV (Plant 2 & 3)", ev[1], ev[2]],
        ["QA", qa[1], qa[2]],
        ["NPI", npi[1], npi[2]]
    ]
    
    df_hc_details = pd.DataFrame(raw_data, columns=["Department", "HC Allocation", "HC Physically Required @ Line"])
    df_hc_details["HC Allocation"] = pd.to_numeric(df_hc_details["HC Allocation"]).fillna(0)
    df_hc_details["HC Physically Required @ Line"] = pd.to_numeric(df_hc_details["HC Physically Required @ Line"]).fillna(0)

    # Grab exact Totals and Gaps from the Excel
    total_mfg_req = df_hc_raw.iloc[7, 2] # 2241.87
    total_mfg_actual = df_hc_raw.iloc[8, 2] # 2103
    mfg_gap = df_hc_raw.iloc[9, 2] # -138.87
    grand_total_req = df_hc_raw.iloc[12, 2] # 2499.87 (Total required for July 26)
    
    # --- REVENUE VS HC COMPARISON TABLE (from bottom right of Summary-HC) ---
    comparison_data = {
        "Metric": ["Revenue ($K)", "Headcount", "Revenue/HC ($K)"],
        "June 26 Plan": [35200, 2012.04, 17.49],
        "July 26 Plan": [42211, 2241.87, 18.82],
        "Change (%)": ["+16.6%", "+10.3%", "+7.1%"]
    }
    df_comparison = pd.DataFrame(comparison_data)

    return df_sales, df_hc_details, total_mfg_req, total_mfg_actual, mfg_gap, grand_total_req, df_comparison

try:
    df_sales, df_hc_details, total_mfg_req, total_mfg_actual, mfg_gap, grand_total_req, df_comparison = load_all_data()

    # 3. KPI Cards Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Total Sales Plan", value="$42.21M")
    with col2:
        st.metric(label="Total Required (Mfg + QA + NPI)", value=f"{grand_total_req:,.2f}")
    with col3:
        st.metric(label="Actual Mfg HC (June 25)", value=f"{total_mfg_actual:,}")
    with col4:
        st.metric(label="Mfg Staffing Deficit", value=f"{mfg_gap:.2f}", delta=f"{mfg_gap:.2f}", delta_color="inverse")

    st.markdown("---")

    # 4. Two Column Layout for Graphics
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("💰 Sales Target Value ($K)")
        fig_sales = px.bar(df_sales, x="Product Line", y="Sales Value (K$)", text="Sales Value (K$)", color="Product Line")
        fig_sales.update_traces(texttemplate='%{text:,.2f}', textposition='outside')
        st.plotly_chart(fig_sales, use_container_width=True)

    with c2:
        st.subheader("👷 Headcount Needs by Area")
        fig_hc = px.bar(
            df_hc_details, 
            x="Department", 
            y=["HC Allocation", "HC Physically Required @ Line"],
            barmode="group",
            labels={"value": "People Count", "variable": "Allocation Type"}
        )
        st.plotly_chart(fig_hc, use_container_width=True)

    st.markdown("---")

    # 5. Exact Tables
    t1, t2 = st.columns([3, 2])
    with t1:
        st.subheader("📋 Complete HC Allocation Detail (From Sheet)")
        st.dataframe(df_hc_details, use_container_width=True)
    with t2:
        st.subheader("📈 June vs July Efficiency Comparison")
        st.dataframe(df_comparison, use_container_width=True)

except Exception as e:
    st.error(f"Error parsing data: {e}")