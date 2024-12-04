import pandas as pd

# Read the CSV file
df = pd.read_csv(r"C:\Users\Riot\OneDrive\Business\SP500_form4_analysis\transactions_split_adjusted.csv")

# Convert price columns to numeric, handling any non-numeric values as NaN
df['6 Month Price'] = pd.to_numeric(df['6 Month Price'], errors='coerce')
df['1 Year Price'] = pd.to_numeric(df['1 Year Price'], errors='coerce')
df['18 Month Price'] = pd.to_numeric(df['18 Month Price'], errors='coerce')
df['ADJUSTED_TRANS_PRICEPERSHARE'] = pd.to_numeric(df['ADJUSTED_TRANS_PRICEPERSHARE'], errors='coerce')

# Calculate total transaction values
df['TOTAL_TRANS_VALUE'] = df['TRANS_SHARES'] * df['TRANS_PRICEPERSHARE']
df['ADJUSTED_TOTAL_TRANS_VALUE'] = df['ADJUSTED_TRANS_SHARES'] * df['ADJUSTED_TRANS_PRICEPERSHARE']

# Calculate stock returns at different intervals
df['RETURN_6M'] = (df['6 Month Price'] - df['ADJUSTED_TRANS_PRICEPERSHARE']) / df['ADJUSTED_TRANS_PRICEPERSHARE']

df['RETURN_1Y'] = (df['1 Year Price'] - df['ADJUSTED_TRANS_PRICEPERSHARE']) / df['ADJUSTED_TRANS_PRICEPERSHARE']

df['RETURN_18M'] = (df['18 Month Price'] - df['ADJUSTED_TRANS_PRICEPERSHARE']) / df['ADJUSTED_TRANS_PRICEPERSHARE']

# Reorder columns - first get the list of all columns
cols = df.columns.tolist()

# Find the position after '18 Month Price'
insert_position = cols.index('18 Month Price') + 1

# Move the return columns to their new positions
cols.remove('RETURN_6M')
cols.remove('RETURN_1Y')
cols.remove('RETURN_18M')
cols.insert(insert_position, 'RETURN_6M')
cols.insert(insert_position + 1, 'RETURN_1Y')
cols.insert(insert_position + 2, 'RETURN_18M')

# Find the position after TRANS_PRICEPERSHARE
insert_position = cols.index('TRANS_PRICEPERSHARE') + 1

# Add TOTAL_TRANS_VALUE after TRANS_PRICEPERSHARE
cols.remove('TOTAL_TRANS_VALUE')
cols.insert(insert_position, 'TOTAL_TRANS_VALUE')

# Find the position after ADJUSTED_TRANS_PRICEPERSHARE
insert_position = cols.index('ADJUSTED_TRANS_PRICEPERSHARE') + 1

# Add ADJUSTED_TOTAL_TRANS_VALUE after ADJUSTED_TRANS_PRICEPERSHARE
cols.remove('ADJUSTED_TOTAL_TRANS_VALUE')
cols.insert(insert_position, 'ADJUSTED_TOTAL_TRANS_VALUE')

# Reorder the dataframe columns
df = df[cols]

# Save the updated dataframe to a new CSV
output_path = r"C:\Users\Riot\OneDrive\Business\SP500_form4_analysis\transactions_with_returns.csv"
df.to_csv(output_path, index=False) 