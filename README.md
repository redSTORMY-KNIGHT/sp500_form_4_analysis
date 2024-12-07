# S&P 500 Insider Trading Analysis Pipeline

## Live Dashboard
🔗 [View Live Dashboard](https://interactivedashboardpy-6goxggemzjcqrccyx9xb2b.streamlit.app/)

## Overview
A data processing and analysis pipeline that tracks insider trading activities for S&P 500 companies, calculating returns and comparing them against market and sector benchmarks.

## Features

### Data Processing Pipeline
1. **Basic Return Calculations** (`transactions_with_calculated_returns.py`)
   - Processes raw transaction data
   - Adjusts for stock splits
   - Calculates 6-month, 1-year, and 18-month returns

2. **Market Benchmark Integration** (`transactions_combined_with_SP500_sector_performance.py`)
   - Adds S&P 500 index performance data
   - Incorporates sector-specific benchmarks
   - Calculates relative performance metrics

3. **Investor Performance Analysis** (`transactions_with_weighted_returns.py`)
   - Calculates weighted returns by investor
   - Aggregates transaction data
   - Generates investor-level performance metrics

### Key Metrics
- Transaction-level returns (6M, 1Y, 18M)
- Relative performance vs S&P 500
- Sector-relative performance
- Transaction value weighted returns
- Split-adjusted calculations

## Data Files

### Input Data
- Raw transaction data
- S&P 500 historical performance
- Sector performance data

### Output Data
- `investor_weighted_returns.csv`: Aggregated investor-level performance
- `transactions_with_returns.csv`: Transaction-level analysis
- `transactions_with_market_performance.csv`: Benchmark-relative performance

## Usage

1. **Data Preparation**
python
python transactions_with_calculated_returns.py


2. **Market Analysis**
python
python transactions_combined_with_SP500_sector_performance.py


3. **Investor Analysis**
python
python transactions_with_weighted_returns.py


## Requirements
- Python 3.x
- pandas
- numpy
- warnings
- datetime

## Installation
1. Clone the repository
2. Install required packages:
bash
pip install pandas numpy


## Data Structure
The pipeline processes Form 4 filings and related market data to track:
- Transaction details
- Price movements
- Market comparisons
- Investor behaviors

## License
[TBD]

## Contributing
[TBD]
