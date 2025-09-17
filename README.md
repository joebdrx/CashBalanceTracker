# Cash Balance Tracker

A professional trading analysis application with 10% dynamic position sizing.

## 🎯 Overview

Cash Balance Tracker analyzes your trading performance by implementing realistic 10% position sizing based on available cash. Instead of fixed position sizes, each trade gets exactly 10% of your available cash at the time of entry, providing accurate performance metrics.

## ✨ Features

- **10% Dynamic Position Sizing**: Each position gets exactly 10% of available cash
- **Daily Cash Balance Tracking**: Track your exact cash position every single day
- **Multiple File Formats**: Supports CSV, Excel (.xlsx, .xls) files
- **Cross-Platform GUI**: Native-looking interface on Windows, macOS, and Linux
- **Comprehensive Analysis**: Win rate, total return, P&L, and detailed trade metrics
- **Professional Export**: Save results to CSV files with timestamps

## 🚀 Quick Start

### Option 1: Use the GUI (Recommended)
```bash
# Double-click to run (all platforms)
python3 run_gui.py

# Or use platform-specific launchers
./start_gui.sh         # macOS/Linux
start_gui.bat          # Windows
```

### Option 2: macOS App Bundle
```bash
# Create native macOS app
python3 create_macos_app.py

# Then double-click CashBalanceTracker.app
```

### Option 3: Command Line
```python
from cash_balance_tracker import run_csv_cash_tracking_example

# Analyze your trading data
daily_balances, updated_trades = run_csv_cash_tracking_example('your_data.csv')
```

## 📊 What You Get

### Daily Cash Balance Tracking
```
        Date  CashBalance  ActivePositions  PositionValue  TotalPortfolio
2017-01-11   900,050.40                1       99,949.60       1,000,000.00
2017-01-12   900,050.40                1       99,949.60       1,000,000.00
...
```

### Updated Trade Results
```
EntryDate   Ticker  CashAvailable  PositionSize  ActualShares  ActualPnL  ReturnPct
2017-01-11  AAPL      1,000,000     100,000           1010     10,211.10     10.22
...
```

### Summary Statistics
```
Starting Cash:           $1,000,000.00
Final Portfolio Value:   $1,125,450.32
Total Return:            12.55%
Win Rate:               63.3%
Total Trades:           150
```

## 📋 Requirements

### Required Data Columns
Your CSV/Excel file should contain:
- **EntryTime**: Entry date (YYYY-MM-DD format)
- **ExitTime**: Exit date (YYYY-MM-DD format)  
- **EntryPrice**: Price per share at entry
- **ExitPrice**: Price per share at exit
- **Ticker**: Stock symbol

### System Requirements
- **Python 3.8+** (with tkinter for GUI)
- **Dependencies**: pandas, openpyxl (auto-installed)
- **Operating System**: Windows 7+, macOS 10.12+, Linux with X11

## 🛠️ Installation

### Easy Setup
```bash
# Clone repository
git clone https://github.com/yourusername/cash-balance-tracker.git
cd cash-balance-tracker

# Install dependencies
pip install -r requirements.txt

# Run the application
python3 cash_balance_gui.py
```

### For Development
```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run from source
python3 cash_balance_gui.py
```

## 📁 Project Structure

```
cash-balance-tracker/
├── cash_balance_gui.py          # Main GUI application
├── cash_balance_tracker.py      # Core analysis engine
├── requirements.txt             # Python dependencies
├── run_gui.py                   # Simple launcher
├── start_gui.sh/.bat           # Platform launchers
├── create_macos_app.py         # macOS app bundle creator
├── build_release.py            # Cross-platform build script
├── CashBalanceTracker.app/     # macOS app bundle
├── docs/                       # Documentation
│   ├── GUI_README.md
│   ├── CSV_Usage_Guide.md
│   └── RELEASE_GUIDE.md
└── README.md                   # This file
```

## 🎮 Usage Examples

### GUI Usage
1. Launch the application
2. Click "Browse..." to select your trading data file
3. Set starting cash amount (default: $1,000,000)
4. Click "Analyze Trading Data"
5. Review results and save if needed

### Python API
```python
from cash_balance_tracker import load_csv_trade_data, calculate_dynamic_cash_balance

# Load your data
trades_df = load_csv_trade_data('my_trades.csv')

# Calculate daily cash balances
daily_balances, positions = calculate_dynamic_cash_balance(trades_df, 1000000)

# Get updated trade results
updated_trades = recalculate_trade_metrics(trades_df, daily_balances)
```

## 🔧 Build for Distribution

### macOS App Bundle
```bash
python3 create_macos_app.py
# Creates: CashBalanceTracker.app
```

### Cross-Platform Executables
```bash
python3 build_release.py
# Creates platform-specific executables
```

### Create DMG (macOS)
```bash
hdiutil create -volname "Cash Balance Tracker" -srcfolder CashBalanceTracker.app -ov -format UDZO CashBalanceTracker.dmg
```

## 📈 Key Advantages

- **Realistic Position Sizing**: No more fixed $100K per trade - uses actual available cash
- **Daily Precision**: Tracks cash balance changes every single day
- **Professional Quality**: Export-ready results for further analysis
- **User-Friendly**: No coding required - point and click interface
- **Cross-Platform**: Works on Windows, macOS, and Linux

## 🐛 Troubleshooting

### Common Issues
- **Missing pandas**: Run `pip install pandas openpyxl`
- **GUI won't start**: Ensure Python 3.8+ with tkinter is installed
- **Excel files not opening**: Install `openpyxl` package
- **Permission denied**: Use virtual environment or user install

### Platform-Specific
- **macOS**: May need to allow app in Security & Privacy settings
- **Windows**: Windows Defender may flag unsigned executable
- **Linux**: Ensure python3-tk package is installed

## 📄 License

This project is provided as-is for trading analysis purposes. Use at your own discretion.

## 🤝 Contributing

Contributions welcome! Please feel free to submit issues and enhancement requests.

## 📞 Support

For questions or issues:
1. Check the documentation in the `docs/` folder
2. Review troubleshooting section above
3. Open an issue on GitHub

---

**Professional trading analysis made simple with 10% dynamic position sizing!** 📊
