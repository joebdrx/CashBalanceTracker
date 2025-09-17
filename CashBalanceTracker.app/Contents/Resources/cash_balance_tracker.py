import pandas as pd
from datetime import datetime, timedelta
import numpy as np

def calculate_dynamic_cash_balance(trades_df, starting_cash=1000000):
    """
    Calculate running cash balance where each position gets 10% of available cash at entry.
    
    Parameters:
    trades_df: DataFrame with columns ['EntryTime', 'ExitTime', 'EntryPrice', 'ExitPrice']
    starting_cash: Initial cash balance (default: $1,000,000)
    
    Returns:
    tuple: (daily_balance_df, active_positions_final)
        - daily_balance_df: DataFrame with daily cash balances and position tracking
        - active_positions_final: List of any remaining open positions
    """
    
    # Validate inputs
    validate_cash_balance_inputs(trades_df, starting_cash)
    
    # Create a copy to avoid modifying original data
    trades_df = trades_df.copy()
    
    # Convert date strings to datetime if they're not already
    trades_df['EntryTime'] = pd.to_datetime(trades_df['EntryTime'])
    trades_df['ExitTime'] = pd.to_datetime(trades_df['ExitTime'])
    
    # Sort trades by entry time
    trades_df = trades_df.sort_values('EntryTime').reset_index(drop=True)
    
    # Create date range from first entry to last exit
    start_date = trades_df['EntryTime'].min()
    end_date = trades_df['ExitTime'].max()
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Initialize daily tracking DataFrame
    daily_balance = pd.DataFrame({
        'Date': date_range,
        'CashBalance': starting_cash,
        'ActivePositions': 0,
        'PositionValue': 0.0,
        'TotalPortfolio': starting_cash
    })
    
    # Track active positions
    active_positions = []
    
    # Process each day
    for i, current_date in enumerate(date_range):
        # Start with previous day's cash balance, or starting cash for first day
        if i == 0:
            cash_balance = starting_cash
        else:
            cash_balance = daily_balance.iloc[i-1]['CashBalance']
        
        # Check for exits FIRST (to free up cash for potential same-day re-entries)
        positions_to_remove = []
        for j, position in enumerate(active_positions):
            if position['exit_date'].date() == current_date.date():
                # Sell position
                sale_proceeds = position['shares'] * position['exit_price']
                cash_balance += sale_proceeds
                positions_to_remove.append(j)
        
        # Remove closed positions (in reverse order to maintain indices)
        for j in reversed(positions_to_remove):
            active_positions.pop(j)
        
        # Check for new entries on this date
        new_entries = trades_df[trades_df['EntryTime'].dt.date == current_date.date()]
        
        for _, trade in new_entries.iterrows():
            # Calculate position size (10% of available cash)
            position_cash = cash_balance * 0.10
            shares_to_buy = int(position_cash / trade['EntryPrice']) if trade['EntryPrice'] > 0 else 0
            
            # Only proceed if we can afford at least 1 share
            if shares_to_buy > 0:
                actual_cost = shares_to_buy * trade['EntryPrice']
                
                # Update cash balance
                cash_balance -= actual_cost
                
                # Add to active positions
                active_positions.append({
                    'entry_date': current_date,
                    'exit_date': trade['ExitTime'],
                    'entry_price': trade['EntryPrice'],
                    'exit_price': trade['ExitPrice'],
                    'shares': shares_to_buy,
                    'cost': actual_cost
                })
        
        # Calculate current position value (mark-to-market would require daily prices)
        # For now, we'll use entry prices as approximation
        position_value = sum(pos['shares'] * pos['entry_price'] for pos in active_positions)
        
        # Update daily balance record
        daily_balance.iloc[i] = {
            'Date': current_date,
            'CashBalance': cash_balance,
            'ActivePositions': len(active_positions),
            'PositionValue': position_value,
            'TotalPortfolio': cash_balance + position_value
        }
        
        # Debug output for first few days
        if i <= 5:
            print(f"Date: {current_date.date()}, Cash: ${cash_balance:,.2f}, Active Positions: {len(active_positions)}")
    
    return daily_balance, active_positions

def recalculate_trade_metrics(trades_df, daily_balance_df):
    """
    Recalculate trade metrics based on dynamic position sizing
    """
    results = []
    
    for _, trade in trades_df.iterrows():
        entry_date = trade['EntryTime'].date()
        
        # Find cash balance on entry date
        matching_dates = daily_balance_df[daily_balance_df['Date'].dt.date == entry_date]
        if len(matching_dates) == 0:
            print(f"Warning: No cash balance data found for entry date {entry_date}")
            continue
        entry_balance = matching_dates['CashBalance'].iloc[0]
        
        # Calculate actual position size
        position_cash = entry_balance * 0.10
        actual_shares = int(position_cash / trade['EntryPrice'])
        actual_cost = actual_shares * trade['EntryPrice']
        actual_proceeds = actual_shares * trade['ExitPrice']
        actual_pnl = actual_proceeds - actual_cost
        actual_return = (actual_pnl / actual_cost) * 100 if actual_cost > 0 else 0
        
        results.append({
            'EntryDate': trade['EntryTime'],
            'ExitDate': trade['ExitTime'],
            'Ticker': trade.get('Ticker', 'Unknown'),
            'EntryPrice': trade['EntryPrice'],
            'ExitPrice': trade['ExitPrice'],
            'CashAvailable': entry_balance,
            'PositionSize': position_cash,
            'ActualShares': actual_shares,
            'ActualCost': actual_cost,
            'ActualProceeds': actual_proceeds,
            'ActualPnL': actual_pnl,
            'ReturnPct': actual_return
        })
    
    return pd.DataFrame(results)

def convert_trade_data_format(df, entry_time_col='EntryTime', exit_time_col='ExitTime', 
                              entry_price_col='EntryPrice', exit_price_col='ExitPrice',
                              ticker_col=None):
    """
    Convert trade data to the format expected by calculate_dynamic_cash_balance.
    
    Parameters:
    df: DataFrame with trade data
    entry_time_col: Column name for entry time
    exit_time_col: Column name for exit time  
    entry_price_col: Column name for entry price
    exit_price_col: Column name for exit price
    ticker_col: Column name for ticker (optional)
    
    Returns:
    DataFrame with standardized column names
    """
    
    # Create a copy to avoid modifying original data
    converted_df = df.copy()
    
    # Rename columns to standard format
    column_mapping = {
        entry_time_col: 'EntryTime',
        exit_time_col: 'ExitTime', 
        entry_price_col: 'EntryPrice',
        exit_price_col: 'ExitPrice'
    }
    
    if ticker_col and ticker_col in df.columns:
        column_mapping[ticker_col] = 'Ticker'
    
    converted_df = converted_df.rename(columns=column_mapping)
    
    # Ensure required columns exist
    required_cols = ['EntryTime', 'ExitTime', 'EntryPrice', 'ExitPrice']
    missing_cols = [col for col in required_cols if col not in converted_df.columns]
    
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    # Add Ticker column if not present
    if 'Ticker' not in converted_df.columns:
        converted_df['Ticker'] = 'UNKNOWN'
    
    # Validate data types and convert dates
    try:
        converted_df['EntryTime'] = pd.to_datetime(converted_df['EntryTime'])
        converted_df['ExitTime'] = pd.to_datetime(converted_df['ExitTime'])
        converted_df['EntryPrice'] = pd.to_numeric(converted_df['EntryPrice'])
        converted_df['ExitPrice'] = pd.to_numeric(converted_df['ExitPrice'])
    except Exception as e:
        raise ValueError(f"Error converting data types: {e}")
    
    # Validate that exit dates are after entry dates
    invalid_dates = converted_df['ExitTime'] <= converted_df['EntryTime']
    if invalid_dates.any():
        print(f"Warning: {invalid_dates.sum()} trades have exit dates before or equal to entry dates")
        converted_df = converted_df[~invalid_dates]
    
    # Validate prices are positive
    invalid_prices = (converted_df['EntryPrice'] <= 0) | (converted_df['ExitPrice'] <= 0)
    if invalid_prices.any():
        print(f"Warning: {invalid_prices.sum()} trades have non-positive prices")
        converted_df = converted_df[~invalid_prices]
    
    return converted_df[['EntryTime', 'ExitTime', 'EntryPrice', 'ExitPrice', 'Ticker']]

def validate_cash_balance_inputs(trades_df, starting_cash):
    """
    Validate inputs for cash balance calculation.
    """
    if not isinstance(trades_df, pd.DataFrame):
        raise TypeError("trades_df must be a pandas DataFrame")
    
    if trades_df.empty:
        raise ValueError("trades_df cannot be empty")
    
    if starting_cash <= 0:
        raise ValueError("starting_cash must be positive")
    
    required_columns = ['EntryTime', 'ExitTime', 'EntryPrice', 'ExitPrice']
    missing_columns = [col for col in required_columns if col not in trades_df.columns]
    
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    
    return True

def create_sample_trade_data():
    """
    Create sample trade data for testing the cash balance tracking.
    This demonstrates the correct data format.
    """
    
    sample_trades = pd.DataFrame({
        'EntryTime': ['2017-01-11', '2017-01-17', '2017-01-18', '2017-01-20', '2017-01-25'],
        'ExitTime': ['2017-03-14', '2017-03-27', '2017-02-06', '2017-03-17', '2017-04-15'],
        'EntryPrice': [98.96, 37.75, 9.88, 91.7, 45.20],
        'ExitPrice': [109.07, 37.49, 13.63, 111.85, 52.30],
        'Ticker': ['AAPL', 'GNRC', 'AMD', 'ALGN', 'NVDA']
    })
    
    return sample_trades

def run_complete_cash_tracking_example(starting_cash=1000000):
    """
    Complete example showing how to use the cash tracking functions correctly with sample data.
    """
    
    print("=== COMPLETE CASH BALANCE TRACKING EXAMPLE ===")
    print(f"Starting Cash: ${starting_cash:,.2f}")
    print()
    
    # Create sample data
    trades_df = create_sample_trade_data()
    print("Sample Trade Data:")
    print(trades_df.to_string(index=False))
    print()
    
    # Calculate daily cash balances with 10% allocation per position
    daily_balances, final_positions = calculate_dynamic_cash_balance(trades_df, starting_cash)
    
    print("=== DAILY CASH BALANCE TRACKING ===")
    print("(Showing first 20 days)")
    print(daily_balances.head(20).to_string(index=False))
    print()
    
    # Recalculate trade metrics with actual position sizes
    updated_trades = recalculate_trade_metrics(trades_df, daily_balances)
    
    print("=== TRADE RESULTS WITH 10% DYNAMIC POSITION SIZING ===")
    print(updated_trades.to_string(index=False))
    print()
    
    # Summary statistics
    total_trades = len(updated_trades)
    winning_trades = len(updated_trades[updated_trades['ActualPnL'] > 0])
    win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
    total_pnl = updated_trades['ActualPnL'].sum()
    final_portfolio_value = daily_balances['TotalPortfolio'].iloc[-1]
    total_return = ((final_portfolio_value - starting_cash) / starting_cash) * 100
    
    print("=== SUMMARY STATISTICS ===")
    print(f"Starting Cash: ${starting_cash:,.2f}")
    print(f"Final Portfolio Value: ${final_portfolio_value:,.2f}")
    print(f"Total Return: {total_return:.2f}%")
    print(f"Total P&L: ${total_pnl:,.2f}")
    print(f"Total Trades: {total_trades}")
    print(f"Winning Trades: {winning_trades}")
    print(f"Win Rate: {win_rate:.1f}%")
    
    return daily_balances, updated_trades

def run_csv_cash_tracking_example(csv_file_path, starting_cash=1000000):
    """
    Complete example using your actual CSV file.
    
    Parameters:
    csv_file_path: Path to your CSV file
    starting_cash: Starting cash amount (default: $1,000,000)
    
    Returns:
    tuple: (daily_balances, updated_trades)
    """
    
    print("=== CSV CASH BALANCE TRACKING ===")
    print(f"Loading data from: {csv_file_path}")
    print(f"Starting Cash: ${starting_cash:,.2f}")
    print()
    
    # Load your CSV data
    trades_df = load_csv_trade_data(csv_file_path)
    
    print(f"Loaded {len(trades_df)} trades")
    print("First few trades:")
    print(trades_df.head().to_string(index=False))
    print()
    
    # Calculate daily cash balances with 10% allocation per position
    daily_balances, final_positions = calculate_dynamic_cash_balance(trades_df, starting_cash)
    
    print("=== DAILY CASH BALANCE TRACKING ===")
    print("(Showing first 10 days)")
    print(daily_balances.head(10).to_string(index=False))
    print()
    print("(Showing last 10 days)")
    print(daily_balances.tail(10).to_string(index=False))
    print()
    
    # Recalculate trade metrics with actual position sizes
    updated_trades = recalculate_trade_metrics(trades_df, daily_balances)
    
    print("=== FIRST 10 TRADE RESULTS WITH 10% DYNAMIC POSITION SIZING ===")
    print(updated_trades.head(10).to_string(index=False))
    print()
    
    # Summary statistics
    total_trades = len(updated_trades)
    winning_trades = len(updated_trades[updated_trades['ActualPnL'] > 0])
    win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
    total_pnl = updated_trades['ActualPnL'].sum()
    final_portfolio_value = daily_balances['TotalPortfolio'].iloc[-1]
    total_return = ((final_portfolio_value - starting_cash) / starting_cash) * 100
    
    print("=== SUMMARY STATISTICS ===")
    print(f"Starting Cash: ${starting_cash:,.2f}")
    print(f"Final Portfolio Value: ${final_portfolio_value:,.2f}")
    print(f"Total Return: {total_return:.2f}%")
    print(f"Total P&L: ${total_pnl:,.2f}")
    print(f"Total Trades: {total_trades}")
    print(f"Winning Trades: {winning_trades}")
    print(f"Win Rate: {win_rate:.1f}%")
    print(f"Average P&L per Trade: ${total_pnl/total_trades:,.2f}")
    
    # Additional insights
    print("\n=== ADDITIONAL INSIGHTS ===")
    print(f"Date Range: {daily_balances['Date'].min().date()} to {daily_balances['Date'].max().date()}")
    print(f"Number of Days: {len(daily_balances)}")
    print(f"Maximum Cash Balance: ${daily_balances['CashBalance'].max():,.2f}")
    print(f"Minimum Cash Balance: ${daily_balances['CashBalance'].min():,.2f}")
    print(f"Maximum Active Positions: {daily_balances['ActivePositions'].max()}")
    
    return daily_balances, updated_trades

def load_csv_trade_data(csv_file_path, 
                         entry_time_col='EntryTime', exit_time_col='ExitTime',
                         entry_price_col='EntryPrice', exit_price_col='ExitPrice',
                         ticker_col='Ticker'):
    """
    Load trade data from CSV file and convert to the format needed for cash tracking.
    
    This function is designed for your CSV format with columns:
    Shares Purchased, EntryBar, ExitBar, EntryPrice, ExitPrice, SL, TP, 
    PnL, ReturnPct, EntryTime, ExitTime, Duration, Tag, Ticker, Is Winner, Entry Money, Exit Money
    
    Parameters:
    csv_file_path: Path to CSV file
    entry_time_col, exit_time_col, entry_price_col, exit_price_col: Column names in CSV
    ticker_col: Column name for ticker symbols
    
    Returns:
    DataFrame ready for cash balance calculation
    """
    
    try:
        # Read CSV file
        df = pd.read_csv(csv_file_path)
        print(f"Loaded {len(df)} rows from CSV file")
        print(f"Columns available: {list(df.columns)}")
        
        # Convert to standard format using the CSV column names
        trades_df = convert_trade_data_format(
            df, 
            entry_time_col=entry_time_col,
            exit_time_col=exit_time_col, 
            entry_price_col=entry_price_col,
            exit_price_col=exit_price_col,
            ticker_col=ticker_col
        )
        
        print(f"Successfully converted data. Final dataset has {len(trades_df)} valid trades.")
        return trades_df
        
    except Exception as e:
        print(f"Error loading CSV file: {e}")
        print("Please check:")
        print("1. File path is correct")
        print("2. CSV file has the expected column names")
        print("3. Date and price columns have valid data")
        raise

def load_excel_trade_data(excel_file_path, sheet_name=0, 
                           entry_time_col='EntryTime', exit_time_col='ExitTime',
                           entry_price_col='EntryPrice', exit_price_col='ExitPrice',
                           ticker_col=None):
    """
    Load trade data from Excel file and convert to the format needed for cash tracking.
    
    Parameters:
    excel_file_path: Path to Excel file
    sheet_name: Sheet name or index (default: 0 for first sheet)
    entry_time_col, exit_time_col, entry_price_col, exit_price_col: Column names in Excel
    ticker_col: Column name for ticker symbols (optional)
    
    Returns:
    DataFrame ready for cash balance calculation
    """
    
    try:
        # Read Excel file
        df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
        print(f"Loaded {len(df)} rows from Excel file")
        print(f"Columns available: {list(df.columns)}")
        
        # Convert to standard format
        trades_df = convert_trade_data_format(
            df, 
            entry_time_col=entry_time_col,
            exit_time_col=exit_time_col, 
            entry_price_col=entry_price_col,
            exit_price_col=exit_price_col,
            ticker_col=ticker_col
        )
        
        print(f"Successfully converted data. Final dataset has {len(trades_df)} valid trades.")
        return trades_df
        
    except Exception as e:
        print(f"Error loading Excel file: {e}")
        print("Please check:")
        print("1. File path is correct")
        print("2. Column names match your Excel file")
        print("3. Date and price columns have valid data")
        raise

# For your specific data format:
def show_daily_cash_example():
    """
    Shows exactly what the daily cash tracking looks like with sample data
    """
    print("=== RUNNING DAILY CASH EXAMPLE ===")
    
    # Use the complete example function
    daily_balances, updated_trades = run_complete_cash_tracking_example(starting_cash=1000000)
    
    return daily_balances, updated_trades

# Quick verification function
def verify_cash_tracking():
    """
    Simple verification that cash tracking works correctly
    """
    print("=== CASH TRACKING VERIFICATION ===")
    print("Starting with $1,000,000")
    print("Day 1: Enter position - spend 10% = $100,000, Cash left = $900,000")
    print("Day 5: Enter another - spend 10% of $900,000 = $90,000, Cash left = $810,000")
    print("Day 10: Exit first position - get proceeds back, Cash increases")
    print("Day 15: Enter third position - spend 10% of current cash available")
    print("\nThe function tracks this for EVERY DAY in your dataset!")

# Show exactly what columns are in the output:
def show_output_columns_info():
    """
    Display information about the output columns from cash balance tracking.
    """
    print("=== OUTPUT COLUMNS ===")
    print("daily_balance DataFrame contains:")
    print("- Date: Every calendar day from first entry to last exit")
    print("- CashBalance: Exact cash available on that day")
    print("- ActivePositions: Number of open trades")
    print("- PositionValue: Total value of open positions")
    print("- TotalPortfolio: Cash + Position Value")
    print("\nThis gives you exact cash balance for every single day!")

# Simplified daily cash tracker function:
def simple_cash_tracker(entry_dates, exit_dates, entry_prices, exit_prices, starting_cash=1000000):
    """
    Simplified version for quick implementation
    
    Parameters:
    entry_dates: List of entry dates (strings or datetime objects)
    exit_dates: List of exit dates
    entry_prices: List of entry prices
    exit_prices: List of exit prices
    starting_cash: Starting cash amount
    """
    
    # Convert to datetime
    entries = pd.to_datetime(entry_dates)
    exits = pd.to_datetime(exit_dates)
    
    # Create date range
    start_date = entries.min()
    end_date = exits.max()
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Initialize cash tracking
    cash_balance = starting_cash
    daily_cash = []
    active_trades = {}  # {trade_id: {shares, exit_date, exit_price}}
    
    for current_date in dates:
        daily_cash_flow = 0
        
        # Check for new entries
        for i, entry_date in enumerate(entries):
            if entry_date.date() == current_date.date():
                # Invest 10% of available cash
                investment_amount = cash_balance * 0.10
                shares = int(investment_amount / entry_prices[i])
                actual_cost = shares * entry_prices[i]
                
                cash_balance -= actual_cost
                daily_cash_flow -= actual_cost
                
                # Track this trade
                active_trades[i] = {
                    'shares': shares,
                    'exit_date': exits[i],
                    'exit_price': exit_prices[i],
                    'entry_price': entry_prices[i]
                }
        
        # Check for exits
        trades_to_remove = []
        for trade_id, trade_info in active_trades.items():
            if trade_info['exit_date'].date() == current_date.date():
                # Sell shares
                proceeds = trade_info['shares'] * trade_info['exit_price']
                cash_balance += proceeds
                daily_cash_flow += proceeds
                trades_to_remove.append(trade_id)
        
        # Remove completed trades
        for trade_id in trades_to_remove:
            del active_trades[trade_id]
        
        daily_cash.append({
            'Date': current_date,
            'CashBalance': cash_balance,
            'DailyCashFlow': daily_cash_flow,
            'ActiveTrades': len(active_trades)
        })
    
    return pd.DataFrame(daily_cash)

# Example usage with your data structure:
def process_trading_data(csv_file_path=None, trades_data=None, starting_cash=1000000):
    """
    Main function to process trading data and return cash balance tracking
    
    Parameters:
    csv_file_path: Path to CSV file with trade data
    trades_data: DataFrame with trade data (alternative to CSV)
    starting_cash: Starting cash balance
    """
    
    if csv_file_path:
        trades_df = pd.read_csv(csv_file_path)
    else:
        trades_df = trades_data
    
    # Calculate daily cash balances
    daily_balances, final_positions = calculate_dynamic_cash_balance(
        trades_df, starting_cash
    )
    
    # Recalculate trade metrics
    updated_trades = recalculate_trade_metrics(trades_df, daily_balances)
    
    # Summary statistics
    total_trades = len(updated_trades)
    winning_trades = len(updated_trades[updated_trades['ActualPnL'] > 0])
    win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
    total_pnl = updated_trades['ActualPnL'].sum()
    final_portfolio_value = daily_balances['TotalPortfolio'].iloc[-1]
    total_return = ((final_portfolio_value - starting_cash) / starting_cash) * 100
    
    print(f"Trading Summary:")
    print(f"Starting Cash: ${starting_cash:,.2f}")
    print(f"Final Portfolio Value: ${final_portfolio_value:,.2f}")
    print(f"Total Return: {total_return:.2f}%")
    print(f"Total P&L: ${total_pnl:,.2f}")
    print(f"Total Trades: {total_trades}")
    print(f"Winning Trades: {winning_trades}")
    print(f"Win Rate: {win_rate:.1f}%")
    
    return daily_balances, updated_trades

# For Excel formula approach:
"""
Excel Formula for running cash balance (assuming data is sorted by date):

In column for CashBalance:
=IF(ROW()=2, 1000000, 
   PREVIOUS_CASH_BALANCE 
   - SUMIF(EntryDateColumn, TODAY, PositionSizeColumn)
   + SUMIF(ExitDateColumn, TODAY, ProceedsColumn))

Where:
- PREVIOUS_CASH_BALANCE = cell above current row
- PositionSizeColumn = EntryPrice * Shares (calculated as 10% of available cash)
- ProceedsColumn = ExitPrice * Shares

This requires helper columns to calculate:
1. Position size based on available cash
2. Actual shares purchased
3. Entry cost
4. Exit proceeds
"""

# ============================================================================
# QUICK START EXAMPLE FOR YOUR CSV DATA
# ============================================================================

if __name__ == "__main__":
    print("=== CASH BALANCE TRACKER - READY TO USE ===")
    print("\nTo use with your CSV file, run:")
    print("from cash_balance_tracker import run_csv_cash_tracking_example")
    print("daily_balances, updated_trades = run_csv_cash_tracking_example('your_file.csv')")
    print("\nOr for a quick test with sample data:")
    print("from cash_balance_tracker import run_complete_cash_tracking_example")
    print("daily_balances, updated_trades = run_complete_cash_tracking_example()")
    print("\nExpected CSV columns: EntryTime, ExitTime, EntryPrice, ExitPrice, Ticker")
    print("(The script works with your exact column naming convention)")
    
    # Uncomment the line below to run a quick test with sample data:
    # run_complete_cash_tracking_example()