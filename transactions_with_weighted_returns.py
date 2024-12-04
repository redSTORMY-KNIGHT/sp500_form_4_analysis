import pandas as pd
import numpy as np
from datetime import datetime
import warnings

# Suppress warnings
warnings.filterwarnings('ignore', category=RuntimeWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)

# Read the CSV file
df = pd.read_csv(r"C:\Users\Riot\OneDrive\Business\SP500_form4_analysis\transactions_with_returns.csv")

# Convert TRANS_DATE to datetime
df['TRANS_DATE'] = pd.to_datetime(df['TRANS_DATE'])

# Function to clean return values
def clean_return_value(x):
    try:
        return float(x) / 100  # Divide by 100 to convert percentage to decimal
    except (ValueError, TypeError):
        return 0.0  # Replace any non-numeric values with 0

# List of return columns to clean
return_columns = [
    'RETURN_6M', 'RETURN_1Y', 'RETURN_18M',
    'SP500_RETURN_6M', 'SP500_RETURN_1Y', 'SP500_RETURN_18M',
    'SECTOR_RETURN_6M', 'SECTOR_RETURN_1Y', 'SECTOR_RETURN_18M',
    'SP500_6M', 'SP500_1Y', 'SP500_18M',
    'SECTOR_6M', 'SECTOR_1Y', 'SECTOR_18M'
]

# Convert all return columns to numeric
for col in return_columns:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Convert Market Cap to numeric, replacing any non-numeric values with NaN
df['Market Cap'] = pd.to_numeric(df['Market Cap'], errors='coerce')

# Define bull/bear markets based on SP500 returns
# A common definition is that a bear market is when prices fall by 20% or more
def classify_market_condition(row):
    if row['SP500_RETURN_6M'] <= -0.10:  # Bear market (using 10% for 6-month window)
        return 'Bear'
    elif row['SP500_RETURN_6M'] >= 0.10:  # Bull market
        return 'Bull'
    else:
        return 'Neutral'

df['Market_Condition'] = df.apply(classify_market_condition, axis=1)

# Add market cap categorization function
def categorize_market_cap(cap_value):
    if cap_value >= 200e9:  # $200B+
        return 'Mega Cap'
    elif cap_value >= 10e9:  # $10B-$200B
        return 'Large Cap'
    elif cap_value >= 2e9:   # $2B-$10B
        return 'Mid Cap'
    elif cap_value >= 300e6: # $300M-$2B
        return 'Small Cap'
    else:
        return 'Micro Cap'

# Add to main code before the groupby
df['Market_Cap_Category'] = df['Market Cap'].apply(categorize_market_cap)

def safe_mode(series):
    """Safely get mode of a series, returning None if empty or no mode exists"""
    if series.empty:
        return None
    mode_result = series.mode()
    return mode_result.iloc[0] if not mode_result.empty else None

def validate_returns(group, owner_name):
    """Validate return values are within reasonable bounds"""
    return_cols = [
        'RETURN_6M', 'RETURN_1Y', 'RETURN_18M',
        'SP500_RETURN_6M', 'SP500_RETURN_1Y', 'SP500_RETURN_18M',
        'SECTOR_RETURN_6M', 'SECTOR_RETURN_1Y', 'SECTOR_RETURN_18M'
    ]
    
    for col in return_cols:
        # Convert to numeric, forcing non-numeric values to NaN
        group[col] = pd.to_numeric(group[col], errors='coerce')
        
        # Add null check
        null_count = group[col].isnull().sum()
        if null_count > 0:
            print(f"Warning: {null_count} null values in {col} for {owner_name}")
        
        # Check for invalid values (now safe to use abs() since values are numeric)
        invalid_values = group[col][(group[col].abs() > 5) | (group[col] == 0)].count()
        if invalid_values > 0:
            print(f"Warning: {invalid_values} suspicious {col} values for {owner_name}")

def weighted_return_calc(group, return_col, value_col, total_value):
    """Calculate weighted return using transaction values as weights"""
    if total_value == 0:
        return 0
    
    # Filter out only null values
    valid_mask = (
        group[return_col].notna() & 
        group[value_col].notna() &
        (group[value_col] > 0)
    )
    
    filtered_group = group[valid_mask]
    
    # Calculate weights for each transaction
    weights = filtered_group[value_col] / total_value
    
    # Calculate weighted return
    weighted_return = (filtered_group[return_col] * weights).sum()
    
    return weighted_return

def calculate_weighted_returns(group):
    if group.empty:
        # Return empty row (keep existing empty return structure)
        return pd.DataFrame([{...}])
    
    # Get owner name from the group index
    owner_name = group.name[1] if isinstance(group.name, tuple) else "Unknown"
    
    # Calculate transaction metrics
    transaction_dates = pd.to_datetime(group['TRANS_DATE'])
    date_diffs = transaction_dates.sort_values().diff()
    avg_days_between = date_diffs.mean().days if len(date_diffs) > 1 else 0
    
    # Filter out rows with invalid transaction values
    group = group[group['ADJUSTED_TOTAL_TRANS_VALUE'] > 0]
    total_trans_value = group['ADJUSTED_TOTAL_TRANS_VALUE'].sum()
    
    if total_trans_value <= 0:
        print(f"Warning: No valid transactions for {owner_name}")
        return pd.DataFrame([{...}])  # Return empty row
    
    # First calculate all weighted returns
    metrics = {
        'Weighted_Return_6M': weighted_return_calc(group, 'RETURN_6M', 'ADJUSTED_TOTAL_TRANS_VALUE', total_trans_value),
        'Weighted_Return_1Y': weighted_return_calc(group, 'RETURN_1Y', 'ADJUSTED_TOTAL_TRANS_VALUE', total_trans_value),
        'Weighted_Return_18M': weighted_return_calc(group, 'RETURN_18M', 'ADJUSTED_TOTAL_TRANS_VALUE', total_trans_value),
        
        'Weighted_SP500_6M': weighted_return_calc(group, 'SP500_RETURN_6M', 'ADJUSTED_TOTAL_TRANS_VALUE', total_trans_value),
        'Weighted_SP500_1Y': weighted_return_calc(group, 'SP500_RETURN_1Y', 'ADJUSTED_TOTAL_TRANS_VALUE', total_trans_value),
        'Weighted_SP500_18M': weighted_return_calc(group, 'SP500_RETURN_18M', 'ADJUSTED_TOTAL_TRANS_VALUE', total_trans_value),
        
        'Weighted_Sector_6M': weighted_return_calc(group, 'SECTOR_RETURN_6M', 'ADJUSTED_TOTAL_TRANS_VALUE', total_trans_value),
        'Weighted_Sector_1Y': weighted_return_calc(group, 'SECTOR_RETURN_1Y', 'ADJUSTED_TOTAL_TRANS_VALUE', total_trans_value),
        'Weighted_Sector_18M': weighted_return_calc(group, 'SECTOR_RETURN_18M', 'ADJUSTED_TOTAL_TRANS_VALUE', total_trans_value),
    }
    
    # Calculate relative performance
    metrics.update({
        'Return_vs_SP500_6M': metrics['Weighted_Return_6M'] - metrics['Weighted_SP500_6M'],
        'Return_vs_SP500_1Y': metrics['Weighted_Return_1Y'] - metrics['Weighted_SP500_1Y'],
        'Return_vs_SP500_18M': metrics['Weighted_Return_18M'] - metrics['Weighted_SP500_18M'],
        'Return_vs_Sector_6M': metrics['Weighted_Return_6M'] - metrics['Weighted_Sector_6M'],
        'Return_vs_Sector_1Y': metrics['Weighted_Return_1Y'] - metrics['Weighted_Sector_1Y'],
        'Return_vs_Sector_18M': metrics['Weighted_Return_18M'] - metrics['Weighted_Sector_18M']
    })
    
    # Now calculate individual transaction relative returns for win rates
    group['Return_vs_SP500_6M'] = group['RETURN_6M'] - group['SP500_RETURN_6M']
    group['Return_vs_SP500_1Y'] = group['RETURN_1Y'] - group['SP500_RETURN_1Y']
    group['Return_vs_Sector_6M'] = group['RETURN_6M'] - group['SECTOR_RETURN_6M']
    
    # Calculate win rates
    metrics.update({
        'Pct_Positive_vs_SP500_6M': (group['Return_vs_SP500_6M'] > 0).mean(),
        'Pct_Positive_vs_SP500_1Y': (group['Return_vs_SP500_1Y'] > 0).mean(),
        'Pct_Positive_vs_Sector_6M': (group['Return_vs_Sector_6M'] > 0).mean(),
    })
    
    # Add transaction pattern metrics
    metrics.update({
        'Transaction_Count': len(group),
        'Min_Transaction_Value': group['ADJUSTED_TOTAL_TRANS_VALUE'].min(),
        'Avg_Transaction_Value': group['ADJUSTED_TOTAL_TRANS_VALUE'].mean(),
        'Total_Transaction_Value': total_trans_value,
        'Avg_Days_Between_Transactions': avg_days_between,
        'Number_of_Companies': group['ISSUERTRADINGSYMBOL'].nunique(),
        'Earliest_Transaction_Year': transaction_dates.dt.year.min(),
        'Most_Recent_Transaction_Year': transaction_dates.dt.year.max(),
        'Unique_Transaction_Years': transaction_dates.dt.year.nunique(),
    })
    
    # Add company/sector info
    metrics.update({
        'Most_Common_Company': safe_mode(group['ISSUERTRADINGSYMBOL']),
        'Most_Active_Sector': safe_mode(group['GICS_SECTOR'])
    })
    
    # Add market cap category
    most_common_company = metrics['Most_Common_Company']
    if most_common_company:
        company_data = group[group['ISSUERTRADINGSYMBOL'] == most_common_company].iloc[0]
        metrics['Most_Common_Company_Cap_Category'] = categorize_market_cap(company_data['Market Cap'])
    else:
        metrics['Most_Common_Company_Cap_Category'] = ''
    
    return pd.DataFrame([metrics])

# Main execution
if __name__ == "__main__":
    print("Starting analysis...")
    
    # Read the CSV file
    df = pd.read_csv(r"C:\Users\Riot\OneDrive\Business\SP500_form4_analysis\transactions_with_returns_and_relatives.csv")
    print(f"Loaded {len(df)} transactions")
    
    # Convert return columns to numeric
    for col in return_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Basic data validation
    print("\nData validation:")
    print("Return columns range:")
    for col in ['RETURN_6M', 'RETURN_1Y', 'RETURN_18M']:
        print(f"{col}: Min={df[col].min():.2%}, Max={df[col].max():.2%}, Mean={df[col].mean():.2%}")
    
    # Calculate weighted returns
    investor_returns = df.groupby(['OWNER_CIK', 'OWNER_NAME']).apply(
        calculate_weighted_returns
    ).reset_index(level=[0,1]).drop('level_2', axis=1, errors='ignore')
    
    # Save results
    output_path = r"C:\Users\Riot\OneDrive\Business\SP500_form4_analysis\investor_weighted_returns.csv"
    investor_returns.to_csv(output_path, index=False)
    print(f"\nAnalysis complete. Results saved to {output_path}")
