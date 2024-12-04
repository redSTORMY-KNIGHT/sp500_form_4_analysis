import pandas as pd
from datetime import datetime, timedelta
from tqdm import tqdm  # For progress bar

print("Starting data processing...")

# Read the CSV files
transactions_df = pd.read_csv(r"C:\Users\Riot\OneDrive\Business\SP500_form4_analysis\insider_transactions_with_prices_final.csv")
sp500_sectors_df = pd.read_csv(r"C:\Users\Riot\OneDrive\Business\SP500_form4_analysis\S_P_500_and_Sectors_Ten_Yr_Performance.csv")

# Convert date columns to datetime, ensuring they're timezone-naive
transactions_df['TRANS_DATE'] = pd.to_datetime(transactions_df['TRANS_DATE']).dt.tz_localize(None)
sp500_sectors_df['Date'] = pd.to_datetime(sp500_sectors_df['Date']).dt.tz_localize(None)

def get_closest_date_value(target_date, sp500_df, column_name):
    if hasattr(target_date, 'tz'):
        target_date = target_date.tz_localize(None)
    closest_date = sp500_df['Date'].iloc[(sp500_df['Date'] - target_date).abs().argsort()[0]]
    return sp500_df.loc[sp500_df['Date'] == closest_date, column_name].iloc[0]

# Initialize new columns for SP500 and sector performance
periods = [('', 0), ('_6M', 180), ('_1Y', 365), ('_18M', 547)]

print("Processing market data...")
# Use tqdm for progress tracking
for period_suffix, days_offset in tqdm(periods, desc="Processing time periods"):
    # Add SP500 columns
    transactions_df[f'SP500{period_suffix}'] = transactions_df['TRANS_DATE'].apply(
        lambda x: get_closest_date_value(x + timedelta(days=days_offset), sp500_sectors_df, 'S&P 500')
    )
    
    # Add sector-specific columns
    transactions_df[f'SECTOR{period_suffix}'] = transactions_df.apply(
        lambda row: get_closest_date_value(
            row['TRANS_DATE'] + timedelta(days=days_offset), 
            sp500_sectors_df, 
            row['GICS_SECTOR']
        ),
        axis=1
    )

print("Calculating returns...")
# Calculate returns and embed context for zero returns
for period_suffix, days in periods[1:]:  # Skip the initial period
    # Calculate SP500 returns
    transactions_df[f'SP500_RETURN{period_suffix}'] = transactions_df.apply(
        lambda row: (
            (row[f'SP500{period_suffix}'] / row['SP500'] - 1)
            if (row['TRANS_DATE'] + timedelta(days=days) <= sp500_sectors_df['Date'].max() and 
                row['TRANS_DATE'] >= sp500_sectors_df['Date'].min())
            else 'Future data not available'
            if row['TRANS_DATE'] + timedelta(days=days) > sp500_sectors_df['Date'].max()
            else 'Historical data not available'
            if row['TRANS_DATE'] < sp500_sectors_df['Date'].min()
            else 'No price change'
        ),
        axis=1
    )
    
    # Calculate sector returns
    transactions_df[f'SECTOR_RETURN{period_suffix}'] = transactions_df.apply(
        lambda row: (
            (row[f'SECTOR{period_suffix}'] / row['SECTOR'] - 1)
            if (row['TRANS_DATE'] + timedelta(days=days) <= sp500_sectors_df['Date'].max() and 
                row['TRANS_DATE'] >= sp500_sectors_df['Date'].min())
            else 'Future data not available'
            if row['TRANS_DATE'] + timedelta(days=days) > sp500_sectors_df['Date'].max()
            else 'Historical data not available'
            if row['TRANS_DATE'] < sp500_sectors_df['Date'].min()
            else 'No price change'
        ),
        axis=1
    )

# Save the results
output_path = r"C:\Users\Riot\OneDrive\Business\SP500_form4_analysis\transactions_with_market_performance.csv"
transactions_df.to_csv(output_path, index=False)

print(f"\nProcess complete! Output file saved to:\n{output_path}")
