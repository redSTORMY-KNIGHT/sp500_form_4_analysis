import streamlit as st
import pandas as pd

# Page config must be the first Streamlit command
st.set_page_config(page_title="Insider Trading Analysis", layout="wide")

# Load the data
@st.cache_data
def load_data():
    transactions_df = pd.read_csv("transactions_with_returns_and_relatives.csv")
    investor_analysis_df = pd.read_csv("investor_weighted_returns.csv")
    
    # Convert all return and performance columns to numeric
    return_columns = [
        'Weighted_Return_6M', 'Weighted_Return_1Y', 'Weighted_Return_18M',
        'Weighted_SP500_6M', 'Weighted_SP500_1Y', 'Weighted_SP500_18M',
        'Weighted_Sector_6M', 'Weighted_Sector_1Y', 'Weighted_Sector_18M',
        'Return_vs_SP500_6M', 'Return_vs_SP500_1Y', 'Return_vs_SP500_18M',
        'Return_vs_Sector_6M', 'Return_vs_Sector_1Y', 'Return_vs_Sector_18M'
    ]
    
    # Only convert columns that exist
    for col in return_columns:
        if col in investor_analysis_df.columns:
            investor_analysis_df[col] = pd.to_numeric(investor_analysis_df[col], errors='coerce')
    
    # Convert monetary values
    monetary_columns = ['Min_Transaction_Value', 'Avg_Transaction_Value', 'Total_Transaction_Value']
    for col in monetary_columns:
        if col in investor_analysis_df.columns:
            investor_analysis_df[col] = pd.to_numeric(investor_analysis_df[col], errors='coerce')
    
    return transactions_df, investor_analysis_df

transactions_df, investor_analysis_df = load_data()

st.title("Insider Trading Analysis Dashboard")

# Filters section
st.subheader("Filter Investors")

# Returns vs Market Filters
with st.expander("Returns vs Market Filters"):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Min Returns**")
        min_return_sp500_6m = st.number_input("6 Month Min vs S&P500 (%)", value=5.0, format="%.1f") / 100
        min_return_sp500_1y = st.number_input("1 Year Min vs S&P500 (%)", value=5.0, format="%.1f") / 100
        min_return_sp500_18m = st.number_input("18 Month Min vs S&P500 (%)", value=5.0, format="%.1f") / 100
        min_return_sector_6m = st.number_input("6 Month Min vs Sector (%)", value=5.0, format="%.1f") / 100
        min_return_sector_1y = st.number_input("1 Year Min vs Sector (%)", value=5.0, format="%.1f") / 100
        min_return_sector_18m = st.number_input("18 Month Min vs Sector (%)", value=5.0, format="%.1f") / 100

    with col2:
        st.markdown("**Max Returns**")
        max_return_sp500_6m = st.number_input("6 Month Max vs S&P500 (%)", value=500.0, format="%.1f") / 100
        max_return_sp500_1y = st.number_input("1 Year Max vs S&P500 (%)", value=500.0, format="%.1f") / 100
        max_return_sp500_18m = st.number_input("18 Month Max vs S&P500 (%)", value=500.0, format="%.1f") / 100
        max_return_sector_6m = st.number_input("6 Month Max vs Sector (%)", value=500.0, format="%.1f") / 100
        max_return_sector_1y = st.number_input("1 Year Max vs Sector (%)", value=500.0, format="%.1f") / 100
        max_return_sector_18m = st.number_input("18 Month Max vs Sector (%)", value=500.0, format="%.1f") / 100

# Transaction Pattern Filters
with st.expander("Transaction Pattern Filters"):
    col1, col2 = st.columns(2)
    with col1:
        min_transaction_count = st.number_input("Min Transaction Count", value=0)
        min_unique_years = st.number_input("Min Unique Transaction Years", value=0)
        min_companies = st.number_input("Min Number of Companies", value=0)
    with col2:
        min_transaction_value = st.number_input("Min Transaction Value ($M)", value=0.0)
        min_avg_transaction_value = st.number_input("Min Avg Transaction Value ($M)", value=0.0)
        max_days_between = st.number_input("Max Avg Days Between Transactions", value=10000)

# Company/Sector Filters
with st.expander("Company/Sector Filters"):
    col1, col2 = st.columns(2)
    with col1:
        selected_sectors = st.multiselect(
            "Filter by Most Active Sector",
            options=investor_analysis_df['Most_Active_Sector'].unique()
        )
    with col2:
        selected_cap_categories = st.multiselect(
            "Filter by Market Cap Category",
            options=investor_analysis_df['Most_Common_Company_Cap_Category'].unique()
        )

# Apply filters
filtered_investors = investor_analysis_df[
    (investor_analysis_df['Return_vs_SP500_6M'].fillna(-100) >= min_return_sp500_6m) &
    (investor_analysis_df['Return_vs_SP500_6M'].fillna(100) <= max_return_sp500_6m) &
    (investor_analysis_df['Return_vs_SP500_1Y'].fillna(-100) >= min_return_sp500_1y) &
    (investor_analysis_df['Return_vs_SP500_1Y'].fillna(100) <= max_return_sp500_1y) &
    (investor_analysis_df['Return_vs_SP500_18M'].fillna(-100) >= min_return_sp500_18m) &
    (investor_analysis_df['Return_vs_SP500_18M'].fillna(100) <= max_return_sp500_18m) &
    (investor_analysis_df['Return_vs_Sector_6M'].fillna(-100) >= min_return_sector_6m) &
    (investor_analysis_df['Return_vs_Sector_1Y'].fillna(-100) >= min_return_sector_1y) &
    (investor_analysis_df['Return_vs_Sector_18M'].fillna(-100) >= min_return_sector_18m) &
    (investor_analysis_df['Transaction_Count'].fillna(0) >= min_transaction_count) &
    (investor_analysis_df['Unique_Transaction_Years'].fillna(0) >= min_unique_years) &
    (investor_analysis_df['Number_of_Companies'].fillna(0) >= min_companies) &
    (investor_analysis_df['Min_Transaction_Value'].fillna(0) >= min_transaction_value * 1_000_000) &
    (investor_analysis_df['Avg_Transaction_Value'].fillna(0) >= min_avg_transaction_value * 1_000_000) &
    (investor_analysis_df['Avg_Days_Between_Transactions'].fillna(365000) <= max_days_between)
]

# Add debug information
st.write("Total rows before filtering:", len(investor_analysis_df))
st.write("Total rows after filtering:", len(filtered_investors))

# Apply sector and market cap filters if selected
if selected_sectors:
    filtered_investors = filtered_investors[filtered_investors['Most_Active_Sector'].isin(selected_sectors)]
if selected_cap_categories:
    filtered_investors = filtered_investors[filtered_investors['Most_Common_Company_Cap_Category'].isin(selected_cap_categories)]

# Display results without the index
st.subheader(f"All Investors Overview ({len(filtered_investors)} investors)")
cols_to_show = [
    'OWNER_NAME', 'Transaction_Count', 'Earliest_Transaction_Year', 'Most_Recent_Transaction_Year',
    'Weighted_Return_6M', 'Return_vs_SP500_6M', 'Return_vs_Sector_6M',
    'Weighted_Return_1Y', 'Return_vs_SP500_1Y', 'Return_vs_Sector_1Y',
    'Weighted_Return_18M', 'Return_vs_SP500_18M', 'Return_vs_Sector_18M',
    'Pct_Positive_vs_SP500_6M', 'Pct_Positive_vs_SP500_1Y',
    'Avg_Transaction_Value', 'Total_Transaction_Value',
    'Number_of_Companies', 'Most_Common_Company', 'Most_Active_Sector',
    'Most_Common_Company_Cap_Category'
]

filtered_display = filtered_investors[cols_to_show].copy()

st.dataframe(
    filtered_display
    .sort_values('Return_vs_SP500_6M', ascending=False)
    .style.format({
        'Transaction_Count': '{:.0f}',  # Whole number, no decimals
        'Number_of_Companies': '{:.0f}',  # Whole number, no decimals
        'Earliest_Transaction_Year': '{:.0f}',  # Just year, no commas
        'Most_Recent_Transaction_Year': '{:.0f}',  # Just year, no commas
        'Weighted_Return_6M': '{:.1%}',
        'Return_vs_SP500_6M': '{:.1%}',
        'Return_vs_Sector_6M': '{:.1%}',
        'Weighted_Return_1Y': '{:.1%}',
        'Return_vs_SP500_1Y': '{:.1%}',
        'Return_vs_Sector_1Y': '{:.1%}',
        'Weighted_Return_18M': '{:.1%}',
        'Return_vs_SP500_18M': '{:.1%}',
        'Return_vs_Sector_18M': '{:.1%}',
        'Pct_Positive_vs_SP500_6M': '{:.1%}',
        'Pct_Positive_vs_SP500_1Y': '{:.1%}',
        'Avg_Transaction_Value': '${:,.0f}',
        'Total_Transaction_Value': '${:,.0f}'
    }),
    hide_index=True
)

# Individual investor details section
st.subheader("Individual Investor Details")
selected_investor = st.selectbox(
    "Select an investor to see their transactions",
    options=filtered_investors['OWNER_NAME'].tolist()
)

if selected_investor:
    investor_cik = investor_analysis_df[investor_analysis_df['OWNER_NAME'] == selected_investor]['OWNER_CIK'].iloc[0]
    investor_transactions = transactions_df[transactions_df['OWNER_CIK'] == investor_cik].copy()
    
    # Restore original toggle text
    aggregate_transactions = st.toggle("Combine transactions within 30 days", value=False)
    
    if aggregate_transactions:
        # Sort by date first
        investor_transactions['TRANS_DATE'] = pd.to_datetime(investor_transactions['TRANS_DATE'])
        investor_transactions = investor_transactions.sort_values('TRANS_DATE')
        
        # Create monthly groups (restored from 6M)
        investor_transactions['GROUP_DATE'] = investor_transactions['TRANS_DATE'].dt.to_period('M')
        
        # Aggregate the transactions
        aggregated_transactions = investor_transactions.groupby(['GROUP_DATE', 'ISSUERNAME', 'ISSUERTRADINGSYMBOL', 'GICS_SECTOR', 'GICS_SUB_INDUSTRY']).agg({
            'TRANS_DATE': 'first',  # Keep the first date in the group
            'ADJUSTED_TRANS_SHARES': 'sum',
            'ADJUSTED_TOTAL_TRANS_VALUE': 'sum',
            'RETURN_6M': lambda x: pd.to_numeric(x, errors='coerce').mean(),
            'RETURN_1Y': lambda x: pd.to_numeric(x, errors='coerce').mean(),
            'RETURN_18M': lambda x: pd.to_numeric(x, errors='coerce').mean(),
            'Vs_SP500_6M': lambda x: pd.to_numeric(x, errors='coerce').mean(),
            'Vs_SP500_1Y': lambda x: pd.to_numeric(x, errors='coerce').mean(),
            'Vs_SP500_18M': lambda x: pd.to_numeric(x, errors='coerce').mean(),
            'Vs_Sector_6M': lambda x: pd.to_numeric(x, errors='coerce').mean(),
            'Vs_Sector_1Y': lambda x: pd.to_numeric(x, errors='coerce').mean(),
            'Vs_Sector_18M': lambda x: pd.to_numeric(x, errors='coerce').mean(),
            '6 Month Price': 'last',
            '1 Year Price': 'last',
            '18 Month Price': 'last'
        }).reset_index()
        
        # Calculate new price per share
        aggregated_transactions['ADJUSTED_TRANS_PRICEPERSHARE'] = (
            aggregated_transactions['ADJUSTED_TOTAL_TRANS_VALUE'] / 
            aggregated_transactions['ADJUSTED_TRANS_SHARES']
        )
        
        display_transactions = aggregated_transactions
    else:
        display_transactions = investor_transactions.copy()
        # Convert percentage columns to numeric for non-aggregated view
        percentage_cols = [
            'RETURN_6M', 'RETURN_1Y', 'RETURN_18M',
            'Vs_SP500_6M', 'Vs_SP500_1Y', 'Vs_SP500_18M',
            'Vs_Sector_6M', 'Vs_Sector_1Y', 'Vs_Sector_18M'
        ]
        for col in percentage_cols:
            display_transactions[col] = pd.to_numeric(display_transactions[col], errors='coerce')

    # Modify the columns shown based on aggregation
    display_cols = [
        'ISSUERNAME', 'ISSUERTRADINGSYMBOL', 'GICS_SECTOR', 'GICS_SUB_INDUSTRY',
        'TRANS_DATE', 'ADJUSTED_TRANS_SHARES', 'ADJUSTED_TRANS_PRICEPERSHARE', 
        'ADJUSTED_TOTAL_TRANS_VALUE', '6 Month Price', '1 Year Price', '18 Month Price',
        'RETURN_6M', 'Vs_SP500_6M', 'Vs_Sector_6M',
        'RETURN_1Y', 'Vs_SP500_1Y', 'Vs_Sector_1Y',
        'RETURN_18M', 'Vs_SP500_18M', 'Vs_Sector_18M'
    ]
    
    # Create a formatter dictionary that checks for numeric columns
    format_dict = {
        'ADJUSTED_TRANS_SHARES': '{:.2f}',
        'ADJUSTED_TRANS_PRICEPERSHARE': '${:.2f}',
        'ADJUSTED_TOTAL_TRANS_VALUE': '${:,.0f}',
        '6 Month Price': '${:.2f}',
        '1 Year Price': '${:.2f}',
        '18 Month Price': '${:.2f}'
    }
    
    # Only add percentage formatting for columns that exist and are numeric
    percentage_cols = [
        'RETURN_6M', 'RETURN_1Y', 'RETURN_18M',
        'Vs_SP500_6M', 'Vs_SP500_1Y', 'Vs_SP500_18M',
        'Vs_Sector_6M', 'Vs_Sector_1Y', 'Vs_Sector_18M'
    ]
    
    for col in percentage_cols:
        if col in display_transactions.columns:
            if pd.api.types.is_numeric_dtype(display_transactions[col]):
                format_dict[col] = '{:.1%}'
    
    st.dataframe(
        display_transactions[display_cols]
        .sort_values('TRANS_DATE', ascending=False)
        .style.format(format_dict),
        hide_index=True
    )
