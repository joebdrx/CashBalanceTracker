# Cash Balance Tracker GUI

A simple graphical interface for analyzing trading data with 10% dynamic position sizing.

## Quick Start

### Option 1: Double-click to run
1. Double-click `run_gui.py` to start the application
2. The GUI will open automatically

### Option 2: Run from command line
```bash
python cash_balance_gui.py
```

## How to Use the GUI

### 1. **Select Your Trading Data File**
- Click the "Browse..." button
- Select your trading data file (CSV, Excel .xlsx, or .xls)
- Supported formats are automatically detected

### 2. **Set Starting Cash**
- Enter your starting cash amount (default: $1,000,000)
- Use numbers only (commas will be automatically removed)

### 3. **Analyze Your Data**
- Click "Analyze Trading Data"
- The application will process your file and show a progress bar
- Results will appear in the text area below

### 4. **View Results**
The analysis provides:
- **Summary Statistics**: Total return, win rate, P&L, etc.
- **Daily Cash Balances**: Your exact cash position every day
- **Updated Trades**: Recalculated with 10% position sizing
- **Key Insights**: Date ranges, maximum positions, etc.

### 5. **Save Results**
- Click "Save Results" to export your analysis
- Choose a directory to save the files
- Three files will be created:
  - Daily cash balances (CSV)
  - Updated trades with 10% sizing (CSV)  
  - Complete analysis summary (TXT)

## Required File Format

Your spreadsheet should contain these columns:

| Column Name | Required | Description |
|-------------|----------|-------------|
| **EntryTime** | ✅ Yes | Entry date (YYYY-MM-DD format) |
| **ExitTime** | ✅ Yes | Exit date (YYYY-MM-DD format) |
| **EntryPrice** | ✅ Yes | Price at entry |
| **ExitPrice** | ✅ Yes | Price at exit |
| **Ticker** | ✅ Yes | Stock symbol |

Additional columns (optional):
- Shares Purchased, PnL, ReturnPct, Duration, etc.

## Features

### ✅ **Easy File Upload**
- Drag & drop support for files
- Supports CSV, Excel (.xlsx, .xls) formats
- Automatic file format detection

### ✅ **10% Dynamic Position Sizing**
- Each position gets exactly 10% of available cash
- No more fixed amounts per trade
- Realistic whole-share constraints

### ✅ **Comprehensive Analysis**
- Daily cash balance tracking
- Trade-by-trade results with actual position sizes
- Summary statistics and insights
- Date range analysis

### ✅ **Export Results**
- Save all results to CSV files
- Timestamped filenames
- Complete analysis summary

### ✅ **User-Friendly Interface**
- Progress indicators
- Status messages
- Error handling and validation
- Clear instructions

## Example Workflow

1. **Prepare your data**: Export trading data to CSV or Excel
2. **Open the GUI**: Double-click `run_gui.py`
3. **Load file**: Click "Browse..." and select your file
4. **Set parameters**: Enter starting cash amount
5. **Analyze**: Click "Analyze Trading Data"
6. **Review results**: Check the summary statistics and daily balances
7. **Save**: Click "Save Results" to export everything

## Sample Output

```
=== SUMMARY STATISTICS ===
Starting Cash:           $1,000,000.00
Final Portfolio Value:   $1,125,450.32
Total Return:            12.55%
Total P&L:              $125,450.32
Total Trades:           150
Winning Trades:         95
Win Rate:               63.3%
Average P&L per Trade:  $836.34

=== ADDITIONAL INSIGHTS ===
Date Range:             2017-01-11 to 2018-12-28
Number of Days:         716
Maximum Cash Balance:   $1,050,200.15
Minimum Cash Balance:   $815,325.40
Maximum Active Positions: 8
```

## Troubleshooting

### **"Module not found" error**
- Make sure all files are in the same directory:
  - `cash_balance_gui.py`
  - `cash_balance_tracker.py`
  - `run_gui.py`

### **"File format not supported"**
- Check that your file is CSV, .xlsx, or .xls format
- Make sure the file isn't corrupted
- Try saving as CSV from Excel if having issues
- Ensure the file selector shows "All Supported" files

### **"Invalid column names"**
- Verify your file has the required columns: EntryTime, ExitTime, EntryPrice, ExitPrice, Ticker
- Column names are case-sensitive
- Use the exact names shown in the requirements

### **"Invalid starting cash"**
- Enter numbers only (no $ symbols)
- Use positive amounts only
- Commas are automatically handled

### **GUI won't start**
- Make sure Python is installed
- Try running from command line: `python cash_balance_gui.py`
- Check that tkinter is available (usually included with Python)

## System Requirements

- **Python 3.6+** (Python 3.8+ recommended)
- **Required packages**: pandas, tkinter (usually included)
- **Optional packages**: openpyxl (for Excel support)

### Install missing packages:
```bash
pip install pandas openpyxl
```

## Features vs Command Line

| Feature | GUI | Command Line |
|---------|-----|--------------|
| File selection | ✅ Browse button | ❌ Manual typing |
| Progress tracking | ✅ Progress bar | ❌ Text only |
| Results viewing | ✅ Formatted display | ❌ Console output |
| Save results | ✅ One-click save | ❌ Manual export |
| Error handling | ✅ User-friendly | ❌ Technical errors |
| Ease of use | ✅ Point & click | ❌ Requires coding |

## File Organization

After running the GUI and saving results, you'll have:

```
your_project_folder/
├── cash_balance_gui.py          # Main GUI application
├── cash_balance_tracker.py      # Core analysis functions
├── run_gui.py                   # Simple launcher
├── your_data_file.csv           # Your trading data
└── results/                     # Saved results folder
    ├── your_data_daily_cash_balances_20241217_143022.csv
    ├── your_data_updated_trades_10percent_20241217_143022.csv
    └── your_data_analysis_summary_20241217_143022.txt
```

The GUI makes it easy to analyze your trading performance with professional-grade 10% dynamic position sizing - no coding required!
