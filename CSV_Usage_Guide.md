# CSV Cash Balance Tracking - Usage Guide

## Quick Start with Your CSV Data

Your script is now updated to work perfectly with CSV files containing your trading data with the correct column names.

### Expected CSV Column Structure

Based on your data format, the CSV should contain these columns:

| Column Name | Description |
|-------------|-------------|
| **Shares Purchased** | Number of shares (original - will be recalculated) |
| **EntryBar** | Entry bar number |
| **ExitBar** | Exit bar number |
| **EntryPrice** | ✅ **Required**: Entry price per share |
| **ExitPrice** | ✅ **Required**: Exit price per share |
| **SL** | Stop Loss level |
| **TP** | Take Profit level |
| **PnL** | Original P&L (will be recalculated) |
| **ReturnPct** | Original return % (will be recalculated) |
| **EntryTime** | ✅ **Required**: Entry date (YYYY-MM-DD format) |
| **ExitTime** | ✅ **Required**: Exit date (YYYY-MM-DD format) |
| **Duration** | Trade duration in days |
| **Tag** | Trade tag/label |
| **Ticker** | ✅ **Required**: Stock symbol |
| **Is Winner** | TRUE/FALSE for winning trades |
| **Entry Money** | Original entry amount |
| **Exit Money** | Original exit amount |

**Required columns for cash tracking:** EntryTime, ExitTime, EntryPrice, ExitPrice, Ticker

## How to Use with Your CSV File

### Method 1: Simple CSV Loading (Recommended)

```python
from cash_balance_tracker import run_csv_cash_tracking_example

# Run complete analysis with your CSV file
daily_balances, updated_trades = run_csv_cash_tracking_example(
    csv_file_path='your_trading_data.csv',
    starting_cash=1000000
)

# Save results
daily_balances.to_csv('daily_cash_balances.csv', index=False)
updated_trades.to_csv('updated_trades_10percent.csv', index=False)
```

### Method 2: Manual Step-by-Step

```python
from cash_balance_tracker import load_csv_trade_data, calculate_dynamic_cash_balance, recalculate_trade_metrics

# Load your CSV data
trades_df = load_csv_trade_data('your_trading_data.csv')

# Calculate daily cash balances with 10% position sizing
daily_balances, final_positions = calculate_dynamic_cash_balance(
    trades_df, 
    starting_cash=1000000
)

# Get updated trade results with actual position sizes
updated_trades = recalculate_trade_metrics(trades_df, daily_balances)

# View results
print("Daily Cash Balances:")
print(daily_balances.head(10))

print("\nUpdated Trade Results:")
print(updated_trades.head(10))
```

### Method 3: Custom Column Names

If your CSV has different column names, specify them:

```python
from cash_balance_tracker import load_csv_trade_data

# Load with custom column names
trades_df = load_csv_trade_data(
    csv_file_path='your_file.csv',
    entry_time_col='Entry_Date',      # Your column name for entry dates
    exit_time_col='Exit_Date',        # Your column name for exit dates
    entry_price_col='Buy_Price',      # Your column name for entry prices
    exit_price_col='Sell_Price',      # Your column name for exit prices
    ticker_col='Symbol'               # Your column name for stock symbols
)
```

## What You Get as Output

### 1. Daily Cash Balance DataFrame

Shows your exact cash position every single day:

```
        Date  CashBalance  ActivePositions  PositionValue  TotalPortfolio
2017-01-11   900050.40                1       99949.60       1000000.00
2017-01-12   900050.40                1       99949.60       1000000.00
2017-01-13   900050.40                1       99949.60       1000000.00
...
```

**Columns:**
- `Date`: Every calendar day from first trade to last exit
- `CashBalance`: Exact cash available on that day  
- `ActivePositions`: Number of open positions
- `PositionValue`: Total value of open positions (at entry prices)
- `TotalPortfolio`: Cash + Position Value

### 2. Updated Trades DataFrame

Shows actual trade results with 10% position sizing:

```
EntryDate   ExitDate   Ticker  EntryPrice  ExitPrice  CashAvailable  PositionSize  ActualShares  ActualCost  ActualProceeds  ActualPnL  ReturnPct
2017-01-11  2017-03-14  AAPL      98.96     109.07      1000000.0     100000.0          1010      99949.60      110160.70    10211.10     10.22
```

**Columns:**
- `CashAvailable`: Cash you had when entering the trade
- `PositionSize`: 10% of available cash allocated
- `ActualShares`: Shares purchased (rounded down to whole shares)
- `ActualCost`: Actual amount spent
- `ActualProceeds`: Actual proceeds from sale
- `ActualPnL`: Real profit/loss with 10% sizing
- `ReturnPct`: Actual return percentage

## Key Features

### ✅ **10% Dynamic Position Sizing**
- No more fixed $100K per trade!
- Each position gets exactly 10% of available cash
- Automatically calculates shares based on available funds
- Accounts for cash availability as it changes

### ✅ **Daily Cash Tracking**
- Every single day tracked from first entry to last exit
- Shows exact cash balance available each day
- Tracks number of active positions
- Calculates total portfolio value

### ✅ **Realistic Constraints**
- Only whole shares purchased
- Can't spend more cash than available
- Handles same-day exits and entries correctly
- Processes exits before entries (cash becomes available)

## Summary Statistics You'll Get

```
=== SUMMARY STATISTICS ===
Starting Cash: $1,000,000.00
Final Portfolio Value: $1,125,450.32
Total Return: 12.55%
Total P&L: $125,450.32
Total Trades: 150
Winning Trades: 95
Win Rate: 63.3%
Average P&L per Trade: $836.34

=== ADDITIONAL INSIGHTS ===
Date Range: 2017-01-11 to 2018-12-28
Number of Days: 716
Maximum Cash Balance: $1,050,200.15
Minimum Cash Balance: $815,325.40
Maximum Active Positions: 8
```

## Common File Formats

### If your CSV is from Excel:
```
# Save as CSV from Excel, then:
daily_balances, updated_trades = run_csv_cash_tracking_example('your_file.csv')
```

### If you have different date formats:
The script automatically handles common date formats:
- `2017-01-11` (YYYY-MM-DD)
- `01/11/2017` (MM/DD/YYYY)  
- `11-Jan-2017` (DD-Mon-YYYY)

### If you have missing data:
The script will:
- Skip trades with invalid/missing dates
- Skip trades with non-positive prices
- Show warnings for problematic data
- Continue processing valid trades

## Sample Usage

```python
# Basic usage - just run this one line!
daily_balances, updated_trades = run_csv_cash_tracking_example(
    'V1_DVO_SP500_TICKERS_DAILY_10_MAX_NO_EXTRA_FILTER_FINAL_2025_09.csv'
)
```

This will:
1. Load your CSV data
2. Show you the first few trades loaded
3. Calculate daily cash balances with 10% allocation
4. Show daily balance progression
5. Recalculate all trades with actual position sizes
6. Display comprehensive summary statistics
7. Return both DataFrames for further analysis

## Export Results

```python
# Save daily cash balances
daily_balances.to_csv('my_daily_cash_balances.csv', index=False)

# Save updated trade results  
updated_trades.to_csv('my_updated_trades.csv', index=False)

# Save summary to Excel with multiple sheets
with pd.ExcelWriter('my_trading_analysis.xlsx') as writer:
    daily_balances.to_excel(writer, sheet_name='Daily_Cash', index=False)
    updated_trades.to_excel(writer, sheet_name='Updated_Trades', index=False)
```

The script is now perfectly configured for your CSV data format and will give you accurate daily cash balance tracking with 10% dynamic position sizing!
