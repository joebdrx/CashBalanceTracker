import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import os

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

def detect_column_name(df, possible_names):
    """
    Detect the actual column name from a list of possible names.
    
    Parameters:
    df: DataFrame to search
    possible_names: List of possible column names
    
    Returns:
    The actual column name found, or None if not found
    """
    for name in possible_names:
        if name in df.columns:
            return name
    return None

def smart_column_detection(df):
    """
    Intelligent column detection with fuzzy matching and pattern recognition.
    
    Parameters:
    df: DataFrame to analyze
    
    Returns:
    Dictionary mapping actual column names to standard names
    """
    import re
    from difflib import get_close_matches
    
    column_mapping = {}
    
    # Define patterns for each required column type
    patterns = {
        'EntryTime': [
            r'entry.*time', r'entry.*date', r'entry_time', r'entry_date',
            r'entrytime', r'entrydate', r'Entry Time', r'Entry Date',
            r'buy.*time', r'buy.*date', r'purchase.*time', r'purchase.*date'
        ],
        'ExitTime': [
            r'exit.*time', r'exit.*date', r'exit_time', r'exit_date',
            r'exittime', r'exitdate', r'Exit Time', r'Exit Date',
            r'sell.*time', r'sell.*date', r'sale.*time', r'sale.*date'
        ],
        'EntryPrice': [
            r'entry.*price', r'entry_price', r'entryprice',
            r'Entry Price', r'buy.*price', r'purchase.*price',
            r'entry.*cost', r'entry_cost'
        ],
        'ExitPrice': [
            r'exit.*price', r'exit_price', r'exitprice',
            r'Exit Price', r'sell.*price', r'sale.*price',
            r'exit.*cost', r'exit_cost'
        ],
        'Ticker': [
            r'ticker', r'symbol', r'stock', r'instrument',
            r'Ticker', r'Symbol', r'Stock', r'Instrument',
            r'security', r'asset'
        ]
    }
    
    # Get all column names as strings
    available_columns = [str(col).strip() for col in df.columns]
    
    for target_col, pattern_list in patterns.items():
        found = False
        
        # First try exact matches (case-insensitive)
        for col in available_columns:
            if col.lower() in [p.lower() for p in pattern_list]:
                column_mapping[col] = target_col
                found = True
                break
        
        if not found:
            # Try regex pattern matching
            for pattern in pattern_list:
                for col in available_columns:
                    if re.search(pattern, col, re.IGNORECASE):
                        column_mapping[col] = target_col
                        found = True
                        break
                if found:
                    break
        
        if not found:
            # Try fuzzy matching
            for pattern in pattern_list:
                # Extract base words from pattern
                base_words = re.findall(r'[a-zA-Z]+', pattern)
                if base_words:
                    fuzzy_matches = get_close_matches(
                        ' '.join(base_words), 
                        available_columns, 
                        n=1, 
                        cutoff=0.6
                    )
                    if fuzzy_matches:
                        column_mapping[fuzzy_matches[0]] = target_col
                        found = True
                        break
    
    return column_mapping

def fuzzy_column_match(columns, target_pattern):
    """
    Use fuzzy matching to find the best column match.
    
    Parameters:
    columns: List of available column names
    target_pattern: Pattern to match against
    
    Returns:
    Best matching column name or None
    """
    from difflib import get_close_matches
    import re
    
    # Extract words from pattern
    words = re.findall(r'[a-zA-Z]+', target_pattern)
    if not words:
        return None
    
    # Try different combinations
    search_terms = [
        ' '.join(words),
        '_'.join(words),
        ''.join(words),
        words[0] if words else ''
    ]
    
    for term in search_terms:
        matches = get_close_matches(term, columns, n=1, cutoff=0.5)
        if matches:
            return matches[0]
    
    return None

def smart_date_parser(date_value):
    """
    Handle multiple date formats intelligently.
    
    Parameters:
    date_value: Date value in various formats
    
    Returns:
    Parsed datetime object or None if parsing fails
    """
    import re
    from datetime import datetime, timedelta
    
    if pd.isna(date_value) or date_value is None:
        return None
    
    # Handle Excel serial numbers
    if isinstance(date_value, (int, float)):
        if 20000 < date_value < 50000:  # Excel serial range
            try:
                excel_epoch = datetime(1900, 1, 1)
                if date_value > 59:  # Account for Excel's 1900 leap year bug
                    date_value = date_value - 1
                return excel_epoch + timedelta(days=date_value - 2)
            except:
                pass
    
    # Convert to string for pattern matching
    date_str = str(date_value).strip()
    
    # Remove common prefixes/suffixes
    date_str = re.sub(r'^[^\d]*', '', date_str)  # Remove leading non-digits
    date_str = re.sub(r'[^\d]*$', '', date_str)  # Remove trailing non-digits
    
    # Common date formats to try
    date_formats = [
        '%Y-%m-%d',           # 2023-01-01
        '%m/%d/%Y',           # 01/01/2023
        '%d/%m/%Y',           # 01/01/2023
        '%Y-%m-%d %H:%M:%S',  # 2023-01-01 12:00:00
        '%m/%d/%Y %H:%M:%S',  # 01/01/2023 12:00:00
        '%d/%m/%Y %H:%M:%S',  # 01/01/2023 12:00:00
        '%Y%m%d',             # 20230101
        '%m-%d-%Y',           # 01-01-2023
        '%d-%m-%Y',           # 01-01-2023
        '%B %d, %Y',          # January 1, 2023
        '%b %d, %Y',          # Jan 1, 2023
        '%d %B %Y',           # 1 January 2023
        '%d %b %Y'            # 1 Jan 2023
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    # Try pandas auto-detection as fallback
    try:
        return pd.to_datetime(date_value, errors='coerce')
    except:
        return None

def clean_dataframe(df):
    """
    Comprehensive data cleaning pipeline.
    
    Parameters:
    df: Raw DataFrame
    
    Returns:
    Cleaned DataFrame
    """
    import re
    
    cleaned_df = df.copy()
    
    print(f"Cleaning DataFrame with {len(cleaned_df)} rows and {len(cleaned_df.columns)} columns")
    
    # Remove HTML tags from all string columns
    for col in cleaned_df.columns:
        if cleaned_df[col].dtype == 'object':
            # Remove HTML tags
            cleaned_df[col] = cleaned_df[col].astype(str).str.replace(r'<[^>]+>', '', regex=True)
            # Remove extra whitespace
            cleaned_df[col] = cleaned_df[col].str.strip()
            # Replace empty strings with NaN
            cleaned_df[col] = cleaned_df[col].replace('', pd.NA)
    
    # Remove completely empty rows
    cleaned_df = cleaned_df.dropna(how='all')
    
    # Remove rows where all required columns are missing
    required_cols = ['EntryTime', 'ExitTime', 'EntryPrice', 'ExitPrice']
    if all(col in cleaned_df.columns for col in required_cols):
        cleaned_df = cleaned_df.dropna(subset=required_cols, how='all')
    
    # Convert numeric columns
    numeric_cols = ['EntryPrice', 'ExitPrice']
    for col in numeric_cols:
        if col in cleaned_df.columns:
            # Remove non-numeric characters except decimal points and minus signs
            cleaned_df[col] = cleaned_df[col].astype(str).str.replace(r'[^\d.-]', '', regex=True)
            cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='coerce')
    
    # Clean date columns
    date_cols = ['EntryTime', 'ExitTime']
    for col in date_cols:
        if col in cleaned_df.columns:
            cleaned_df[col] = cleaned_df[col].apply(smart_date_parser)
    
    print(f"After cleaning: {len(cleaned_df)} rows and {len(cleaned_df.columns)} columns")
    
    return cleaned_df

def validate_required_columns(df, data_type='trading'):
    """
    Check if DataFrame has the minimum required columns.
    Uses smart detection to find equivalent column names.
    
    Parameters:
    df: DataFrame to validate
    data_type: 'trading' for trading data, 'benchmark' for benchmark data
    
    Returns:
    Boolean indicating if validation passed
    """
    if data_type == 'benchmark':
        # For benchmark data, we need Date and Close/Adjusted_Close columns
        # Check for common variations
        date_variations = ['Date', 'date', 'DATE', 'Date_Time', 'date_time', 'datetime']
        close_variations = ['Close', 'close', 'CLOSE', 'Close_Price', 'close_price', 'Adjusted_Close', 'adjusted_close', 'Adj_Close']
        
        # Check if any column matches date patterns
        has_date = any(any(variation.lower() in col.lower() for variation in date_variations) for col in df.columns)
        has_close = any(any(variation.lower() in col.lower() for variation in close_variations) for col in df.columns)
        
        print(f"Benchmark validation: Date={has_date}, Close={has_close}")
        print(f"Available columns: {list(df.columns)}")
        return has_date and has_close
    
    else:
        # For trading data, use smart column detection
        smart_mapping = smart_column_detection(df)
        
        # Check if we found the required column types
        required_types = ['EntryTime', 'ExitTime', 'EntryPrice', 'ExitPrice']
        found_types = list(smart_mapping.values())
        
        # Count how many required types we found
        found_count = sum(1 for req_type in required_types if req_type in found_types)
        
        print(f"Trading validation: Found {found_count}/4 required column types")
        print(f"Smart mapping: {smart_mapping}")
        
        return found_count >= 4

def robust_data_loading(file_path):
    """
    Try multiple parsing methods with error recovery.
    
    Parameters:
    file_path: Path to the data file
    
    Returns:
    Loaded and cleaned DataFrame
    
    Raises:
    ValueError: If all parsing methods fail
    """
    import os
    from pathlib import Path
    
    file_ext = Path(file_path).suffix.lower()
    file_name = os.path.basename(file_path)
    
    print(f"🔄 Attempting to load: {file_name}")
    
    # Define parsing methods based on file extension
    methods = []
    
    if file_ext == '.csv':
        methods = [
            ('CSV Standard', lambda: pd.read_csv(file_path)),
            ('CSV Latin-1', lambda: pd.read_csv(file_path, encoding='latin-1')),
            ('CSV CP1252', lambda: pd.read_csv(file_path, encoding='cp1252')),
            ('CSV UTF-16', lambda: pd.read_csv(file_path, encoding='utf-16'))
        ]
    elif file_ext in ['.xlsx', '.xls']:
        methods = [
            ('Excel', lambda: pd.read_excel(file_path)),
            ('Excel Engine Openpyxl', lambda: pd.read_excel(file_path, engine='openpyxl')),
            ('Excel Engine Xlrd', lambda: pd.read_excel(file_path, engine='xlrd'))
        ]
    elif file_ext == '.html':
        # Import HTML parsers if available
        try:
            from parse_trading_data_html import parse_trading_data_html
            from parse_spy_data import parse_spy_html_data
            methods = [
                ('HTML Trading Data', lambda: parse_trading_data_html(file_path)),
                ('HTML SPY Data', lambda: parse_spy_html_data(file_path)),
                ('HTML Generic', lambda: pd.read_html(file_path)[0])
            ]
        except ImportError:
            methods = [
                ('HTML Generic', lambda: pd.read_html(file_path)[0])
            ]
    else:
        # Try all methods for unknown extensions
        try:
            from parse_trading_data_html import parse_trading_data_html
            from parse_spy_data import parse_spy_html_data
            methods = [
                ('CSV Standard', lambda: pd.read_csv(file_path)),
                ('Excel', lambda: pd.read_excel(file_path)),
                ('HTML Trading Data', lambda: parse_trading_data_html(file_path)),
                ('HTML SPY Data', lambda: parse_spy_html_data(file_path))
            ]
        except ImportError:
            methods = [
                ('CSV Standard', lambda: pd.read_csv(file_path)),
                ('Excel', lambda: pd.read_excel(file_path))
            ]
    
    # Try each method
    for method_name, method_func in methods:
        try:
            print(f"  Trying {method_name}...")
            df = method_func()
            
            if df is None or df.empty:
                print(f"    ❌ {method_name}: Empty result")
                continue
            
            print(f"    ✅ {method_name}: Loaded {len(df)} rows, {len(df.columns)} columns")
            
            # Clean the data
            cleaned_df = clean_dataframe(df)
            
            # Detect data type first
            is_benchmark = any(keyword in file_name.lower() for keyword in ['spy', 'qqq', 'benchmark', 'index'])
            data_type = 'benchmark' if is_benchmark else 'trading'
            
            print(f"    🔍 Data type detection: {data_type} (file: {file_name})")
            
            # Apply smart column detection and mapping only for trading data
            if data_type == 'trading':
                smart_mapping = smart_column_detection(cleaned_df)
                if smart_mapping:
                    print(f"    🔄 {method_name}: Applying smart column mapping...")
                    cleaned_df = cleaned_df.rename(columns=smart_mapping)
            else:
                print(f"    🔄 {method_name}: Skipping smart mapping for {data_type} data")
            
            # Validate required columns
            if validate_required_columns(cleaned_df, data_type):
                print(f"    ✅ {method_name}: Validation passed ({data_type} data)")
                return cleaned_df
            else:
                print(f"    ⚠️  {method_name}: Missing required columns ({data_type} data), trying next method")
                continue
                
        except Exception as e:
            print(f"    ❌ {method_name}: {str(e)[:100]}...")
            continue
    
    # If all methods failed, provide helpful error message
    available_cols = []
    try:
        # Try to get column info from the first method that doesn't crash
        for method_name, method_func in methods[:2]:  # Try first 2 methods
            try:
                df = method_func()
                if df is not None and not df.empty:
                    available_cols = list(df.columns)
                    break
            except:
                continue
    except:
        pass
    
    error_msg = f"""
    ❌ All parsing methods failed for: {file_name}
    
    Available columns found: {available_cols}
    
    Please ensure your file has columns containing:
    - Entry time/date information
    - Exit time/date information  
    - Entry price information
    - Exit price information
    
    Supported formats: CSV, Excel (.xlsx, .xls), HTML
    """
    
    raise ValueError(error_msg)

def user_friendly_error_handling(error, file_path):
    """
    Provide helpful error messages with suggestions.
    
    Parameters:
    error: The exception that occurred
    file_path: Path to the file that caused the error
    
    Returns:
    User-friendly error message
    """
    error_str = str(error)
    
    if "Missing required columns" in error_str:
        try:
            # Try to get available columns
            df = pd.read_csv(file_path, nrows=1)
            available_cols = list(df.columns)
        except:
            available_cols = ["Unable to read file"]
        
        return f"""
        ❌ Column Mapping Error
        
        The program couldn't find the required columns in your file.
        
        Required columns:
        - EntryTime or EntryDate (for entry dates)
        - ExitTime or ExitDate (for exit dates)  
        - EntryPrice (for entry prices)
        - ExitPrice (for exit prices)
        
        Available columns in your file:
        {available_cols}
        
        💡 Suggestions:
        1. Rename your columns to match the required names
        2. Check if your file has the correct data
        3. Try saving as CSV format
        """
    
    elif "UnicodeDecodeError" in error_str:
        return f"""
        ❌ File Encoding Error
        
        The file couldn't be read due to encoding issues.
        
        💡 Try:
        1. Save your file as UTF-8 CSV
        2. Open in Excel and save as .xlsx
        3. Check if the file is corrupted
        """
    
    elif "No module named" in error_str:
        return f"""
        ❌ Missing Dependencies
        
        {error_str}
        
        💡 Install missing packages:
        pip install pandas openpyxl xlrd beautifulsoup4
        """
    
    else:
        return f"""
        ❌ Unexpected Error
        
        {error_str}
        
        💡 Try:
        1. Check if the file is not corrupted
        2. Ensure the file format is supported (CSV, Excel, HTML)
        3. Contact support if the issue persists
        """

def convert_trade_data_format(df, entry_time_col=None, exit_time_col=None, 
                              entry_price_col='EntryPrice', exit_price_col='ExitPrice',
                              ticker_col='Ticker'):
    """
    Convert trade data to the format expected by calculate_dynamic_cash_balance.
    Uses intelligent column detection with fuzzy matching and pattern recognition.
    
    Parameters:
    df: DataFrame with trade data
    entry_time_col: Column name for entry time (auto-detected if None)
    exit_time_col: Column name for exit time (auto-detected if None)
    entry_price_col: Column name for entry price
    exit_price_col: Column name for exit price
    ticker_col: Column name for ticker (auto-detected if None)
    
    Returns:
    DataFrame with standardized column names
    """
    
    # Create a copy to avoid modifying original data
    converted_df = df.copy()
    
    # Use smart column detection if specific columns not provided
    if any(col is None for col in [entry_time_col, exit_time_col, ticker_col]):
        print("Using smart column detection...")
        smart_mapping = smart_column_detection(converted_df)
        print(f"Smart detection found: {smart_mapping}")
        
        # Apply smart mapping
        converted_df = converted_df.rename(columns=smart_mapping)
        
        # Update column variables
        entry_time_col = smart_mapping.get(entry_time_col, 'EntryTime')
        exit_time_col = smart_mapping.get(exit_time_col, 'ExitTime')
        ticker_col = smart_mapping.get(ticker_col, 'Ticker')
    
    # Fallback to basic detection if smart detection didn't find everything
    if entry_time_col is None:
        entry_time_col = detect_column_name(converted_df, ['EntryTime', 'EntryDate', 'entry_time', 'entry_date'])
    if exit_time_col is None:
        exit_time_col = detect_column_name(converted_df, ['ExitTime', 'ExitDate', 'exit_time', 'exit_date'])
    if ticker_col is None:
        ticker_col = detect_column_name(converted_df, ['Ticker', 'Symbol', 'ticker', 'symbol'])
    
    print(f"Final column mapping: Entry={entry_time_col}, Exit={exit_time_col}, Ticker={ticker_col}")
    
    # Rename columns to standard format
    column_mapping = {}
    
    if entry_time_col and entry_time_col in converted_df.columns:
        column_mapping[entry_time_col] = 'EntryTime'
    if exit_time_col and exit_time_col in converted_df.columns:
        column_mapping[exit_time_col] = 'ExitTime'
    if entry_price_col and entry_price_col in converted_df.columns:
        column_mapping[entry_price_col] = 'EntryPrice'
    if exit_price_col and exit_price_col in converted_df.columns:
        column_mapping[exit_price_col] = 'ExitPrice'
    if ticker_col and ticker_col in converted_df.columns:
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
                         entry_time_col=None, exit_time_col=None,
                         entry_price_col='EntryPrice', exit_price_col='ExitPrice',
                         ticker_col=None):
    """
    Load trade data from CSV file and convert to the format needed for cash tracking.
    
    Supports various column name formats with auto-detection:
    - EntryTime/EntryDate, ExitTime/ExitDate
    - EntryPrice, ExitPrice  
    - Ticker/Symbol
    
    Parameters:
    csv_file_path: Path to CSV file
    entry_time_col, exit_time_col, entry_price_col, exit_price_col: Column names (auto-detected if None)
    ticker_col: Column name for ticker symbols (auto-detected if None)
    
    Returns:
    DataFrame ready for cash balance calculation
    """
    
    try:
        # Use robust loading system
        df = robust_data_loading(csv_file_path)
        
        # Convert to standard format
        trades_df = convert_trade_data_format(
            df, 
            entry_time_col=entry_time_col,
            exit_time_col=exit_time_col, 
            entry_price_col=entry_price_col,
            exit_price_col=exit_price_col,
            ticker_col=ticker_col
        )
        
        print(f"✅ Successfully loaded and converted {len(trades_df)} trades from CSV")
        return trades_df
        
    except Exception as e:
        error_msg = user_friendly_error_handling(e, csv_file_path)
        print(error_msg)
        return pd.DataFrame()

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
        # Use robust loading system
        df = robust_data_loading(excel_file_path)
        
        # Convert to standard format
        trades_df = convert_trade_data_format(
            df, 
            entry_time_col=entry_time_col,
            exit_time_col=exit_time_col, 
            entry_price_col=entry_price_col,
            exit_price_col=exit_price_col,
            ticker_col=ticker_col
        )
        
        print(f"✅ Successfully loaded and converted {len(trades_df)} trades from Excel")
        return trades_df
        
    except Exception as e:
        error_msg = user_friendly_error_handling(e, excel_file_path)
        print(error_msg)
        return pd.DataFrame()

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

# =============================================================================
# BENCHMARK COMPARISON FUNCTIONS
# =============================================================================

def load_benchmark_data(benchmark_file_path):
    """
    Load benchmark data (SPY/QQQ) from CSV file using robust loading
    
    Parameters:
    benchmark_file_path: Path to CSV file with benchmark OHLC data
    
    Returns:
    DataFrame with columns: Date, Price
    """
    try:
        # Try robust loading system first
        df = robust_data_loading(benchmark_file_path)
        
        if df.empty:
            print("⚠️ Robust loading failed, trying fallback methods...")
            
            # Fallback 1: Direct CSV loading
            try:
                df = pd.read_csv(benchmark_file_path)
                print("✅ Fallback 1: Direct CSV loading successful")
            except Exception as e1:
                print(f"❌ Fallback 1 failed: {e1}")
                
                # Fallback 2: Try different encodings
                try:
                    df = pd.read_csv(benchmark_file_path, encoding='latin-1')
                    print("✅ Fallback 2: Latin-1 encoding successful")
                except Exception as e2:
                    print(f"❌ Fallback 2 failed: {e2}")
                    
                    # Fallback 3: Try Excel format
                    try:
                        df = pd.read_excel(benchmark_file_path)
                        print("✅ Fallback 3: Excel format successful")
                    except Exception as e3:
                        print(f"❌ All fallback methods failed: {e3}")
                        return pd.DataFrame()
        
        if df.empty:
            print("❌ All loading methods failed")
            return pd.DataFrame()
        
        # Ensure Date column exists and is properly formatted
        if 'Date' not in df.columns:
            # Try to find date column with variations
            date_cols = [col for col in df.columns if any(variation in col.lower() for variation in ['date', 'time', 'datetime'])]
            if date_cols:
                df = df.rename(columns={date_cols[0]: 'Date'})
                print(f"🔄 Renamed column '{date_cols[0]}' to 'Date'")
            else:
                print("❌ No date column found in benchmark data")
                return pd.DataFrame()
        
        # Convert Date to datetime if not already
        if not pd.api.types.is_datetime64_any_dtype(df['Date']):
            df['Date'] = pd.to_datetime(df['Date'])
        
        # Find price column (Close or Adjusted_Close)
        price_col = None
        if 'Adjusted_Close' in df.columns:
            price_col = 'Adjusted_Close'
        elif 'Close' in df.columns:
            price_col = 'Close'
        else:
            # Try to find price column with variations
            price_cols = [col for col in df.columns if any(variation in col.lower() for variation in ['close', 'price', 'adj'])]
            if price_cols:
                price_col = price_cols[0]
                print(f"🔄 Using price column: '{price_col}'")
            else:
                print("❌ No price column found in benchmark data")
                return pd.DataFrame()
        
        # Create standardized DataFrame
        benchmark_df = df[['Date', price_col]].copy()
        benchmark_df = benchmark_df.rename(columns={price_col: 'Price'})
        benchmark_df = benchmark_df.sort_values('Date').reset_index(drop=True)
        
        # Validate the final DataFrame
        is_valid, issues, suggestions = validate_benchmark_data(benchmark_df)
        
        if not is_valid:
            print("⚠️ Benchmark data validation issues found:")
            for issue in issues:
                print(f"   - {issue}")
            print("💡 Suggestions:")
            for suggestion in suggestions:
                print(f"   - {suggestion}")
        
        print(f"📊 Loaded benchmark data: {len(benchmark_df)} records")
        print(f"📅 Date range: {benchmark_df['Date'].min().date()} to {benchmark_df['Date'].max().date()}")
        
        return benchmark_df
        
    except Exception as e:
        print(f"❌ Error loading benchmark data: {e}")
        print(f"Error type: {type(e).__name__}")
        
        # Debug information
        if 'df' in locals() and not df.empty:
            print(f"Available columns: {list(df.columns)}")
            print(f"DataFrame shape: {df.shape}")
            print(f"First few rows:")
            print(df.head())
        else:
            print("No DataFrame available for debugging")
        
        # Try to provide specific guidance
        if "Date" in str(e):
            print("💡 Date column issue detected. Possible solutions:")
            print("   1. Check if your file has a date column")
            print("   2. Try renaming your date column to 'Date'")
            print("   3. Ensure date format is recognizable")
        elif "encoding" in str(e).lower():
            print("💡 Encoding issue detected. Try saving as UTF-8 CSV")
        elif "file not found" in str(e).lower():
            print("💡 File not found. Check the file path")
        
        return pd.DataFrame()

def validate_benchmark_data(df):
    """
    Validate benchmark data and provide detailed feedback
    
    Parameters:
    df: DataFrame to validate
    
    Returns:
    Tuple: (is_valid, issues, suggestions)
    """
    issues = []
    suggestions = []
    
    # Check for required columns
    required_cols = ['Date', 'Close', 'Adjusted_Close']
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        issues.append(f"Missing columns: {missing_cols}")
        
        # Check for variations
        date_variations = [col for col in df.columns if 'date' in col.lower()]
        close_variations = [col for col in df.columns if 'close' in col.lower()]
        
        if date_variations:
            suggestions.append(f"Found date-like columns: {date_variations}")
        if close_variations:
            suggestions.append(f"Found close-like columns: {close_variations}")
    
    # Check data types
    if 'Date' in df.columns:
        if not pd.api.types.is_datetime64_any_dtype(df['Date']):
            issues.append("Date column is not datetime type")
            suggestions.append("Convert Date column to datetime format")
    
    # Check for empty data
    if df.empty:
        issues.append("DataFrame is empty")
        suggestions.append("Check if file contains data")
    
    # Check for missing values
    if not df.empty:
        missing_dates = df['Date'].isna().sum() if 'Date' in df.columns else 0
        if missing_dates > 0:
            issues.append(f"Found {missing_dates} missing dates")
            suggestions.append("Remove rows with missing dates")
    
    is_valid = len(issues) == 0
    return is_valid, issues, suggestions

def calculate_buy_and_hold_performance(benchmark_df, start_date, end_date, initial_cash):
    """
    Calculate buy-and-hold performance for benchmark
    
    Parameters:
    benchmark_df: DataFrame with Date and Price columns
    start_date: Start date for analysis
    end_date: End date for analysis
    initial_cash: Starting cash amount
    
    Returns:
    DataFrame with daily portfolio values for buy-and-hold strategy
    """
    # Filter benchmark data to analysis period
    mask = (benchmark_df['Date'] >= start_date) & (benchmark_df['Date'] <= end_date)
    period_data = benchmark_df[mask].copy()
    
    if len(period_data) == 0:
        print("❌ No benchmark data found for the analysis period")
        return pd.DataFrame()
    
    # Calculate shares purchased on start date
    start_price = period_data.iloc[0]['Price']
    shares_purchased = int(initial_cash / start_price)
    actual_cost = shares_purchased * start_price
    remaining_cash = initial_cash - actual_cost
    
    # Calculate daily portfolio values
    period_data['Shares'] = shares_purchased
    period_data['CashBalance'] = remaining_cash
    period_data['PositionValue'] = period_data['Shares'] * period_data['Price']
    period_data['TotalPortfolio'] = period_data['CashBalance'] + period_data['PositionValue']
    
    print(f"📈 Buy-and-hold performance calculated:")
    print(f"   Shares purchased: {shares_purchased:,}")
    print(f"   Start price: ${start_price:.2f}")
    print(f"   End price: ${period_data.iloc[-1]['Price']:.2f}")
    print(f"   Final value: ${period_data.iloc[-1]['TotalPortfolio']:,.2f}")
    
    return period_data[['Date', 'CashBalance', 'PositionValue', 'TotalPortfolio', 'Price']]

def compare_strategy_vs_benchmark(strategy_daily_balances, benchmark_daily_balances):
    """
    Compare strategy performance vs benchmark
    
    Parameters:
    strategy_daily_balances: DataFrame with strategy daily balances
    benchmark_daily_balances: DataFrame with benchmark daily balances
    
    Returns:
    Dictionary with performance comparison metrics
    """
    # Ensure both DataFrames have the same date range
    strategy_df = strategy_daily_balances.copy()
    benchmark_df = benchmark_daily_balances.copy()
    
    # Merge on date to align the data
    merged = pd.merge(strategy_df, benchmark_df, on='Date', suffixes=('_strategy', '_benchmark'))
    
    if len(merged) == 0:
        print("❌ No overlapping dates between strategy and benchmark data")
        return {}
    
    # Calculate returns
    merged['Strategy_Return'] = merged['TotalPortfolio_strategy'].pct_change()
    merged['Benchmark_Return'] = merged['TotalPortfolio_benchmark'].pct_change()
    
    # Calculate cumulative returns
    merged['Strategy_CumReturn'] = (1 + merged['Strategy_Return'].fillna(0)).cumprod() - 1
    merged['Benchmark_CumReturn'] = (1 + merged['Benchmark_Return'].fillna(0)).cumprod() - 1
    
    # Calculate performance metrics
    strategy_total_return = merged['Strategy_CumReturn'].iloc[-1]
    benchmark_total_return = merged['Benchmark_CumReturn'].iloc[-1]
    alpha = strategy_total_return - benchmark_total_return
    
    # Calculate volatility (annualized)
    strategy_vol = merged['Strategy_Return'].std() * np.sqrt(252)
    benchmark_vol = merged['Benchmark_Return'].std() * np.sqrt(252)
    
    # Calculate Sharpe ratio (assuming 0% risk-free rate)
    strategy_sharpe = (strategy_total_return * 252) / (strategy_vol * np.sqrt(252)) if strategy_vol > 0 else 0
    benchmark_sharpe = (benchmark_total_return * 252) / (benchmark_vol * np.sqrt(252)) if benchmark_vol > 0 else 0
    
    # Calculate beta
    covariance = np.cov(merged['Strategy_Return'].fillna(0), merged['Benchmark_Return'].fillna(0))[0, 1]
    benchmark_variance = np.var(merged['Benchmark_Return'].fillna(0))
    beta = covariance / benchmark_variance if benchmark_variance > 0 else 0
    
    # Calculate maximum drawdown
    strategy_peak = merged['Strategy_CumReturn'].expanding().max()
    strategy_drawdown = (merged['Strategy_CumReturn'] - strategy_peak) / (1 + strategy_peak)
    strategy_max_drawdown = strategy_drawdown.min()
    
    benchmark_peak = merged['Benchmark_CumReturn'].expanding().max()
    benchmark_drawdown = (merged['Benchmark_CumReturn'] - benchmark_peak) / (1 + benchmark_peak)
    benchmark_max_drawdown = benchmark_drawdown.min()
    
    # Calculate win rate (days outperforming benchmark)
    outperforming_days = (merged['Strategy_Return'] > merged['Benchmark_Return']).sum()
    total_days = len(merged)
    win_rate = (outperforming_days / total_days) * 100 if total_days > 0 else 0
    
    # Compile results
    results = {
        'strategy_total_return': strategy_total_return * 100,
        'benchmark_total_return': benchmark_total_return * 100,
        'alpha': alpha * 100,
        'beta': beta,
        'strategy_volatility': strategy_vol * 100,
        'benchmark_volatility': benchmark_vol * 100,
        'strategy_sharpe': strategy_sharpe,
        'benchmark_sharpe': benchmark_sharpe,
        'strategy_max_drawdown': strategy_max_drawdown * 100,
        'benchmark_max_drawdown': benchmark_max_drawdown * 100,
        'win_rate': win_rate,
        'outperforming_days': outperforming_days,
        'total_days': total_days,
        'final_strategy_value': merged['TotalPortfolio_strategy'].iloc[-1],
        'final_benchmark_value': merged['TotalPortfolio_benchmark'].iloc[-1]
    }
    
    return results

def run_benchmark_analysis(trades_file_path, benchmark_file_path, starting_cash=1000000):
    """
    Run complete analysis comparing strategy vs benchmark
    
    Parameters:
    trades_file_path: Path to trading data CSV/Excel file
    benchmark_file_path: Path to benchmark data CSV file
    starting_cash: Starting cash amount
    
    Returns:
    Tuple: (strategy_results, benchmark_results, comparison_metrics)
    """
    print("🚀 Starting Benchmark Analysis")
    print("=" * 50)
    
    # Load and analyze trading strategy
    print("\n📊 Analyzing Trading Strategy...")
    
    # Use robust loading system for trading data
    print(f"Loading trading data: {trades_file_path}")
    trades_df = robust_data_loading(trades_file_path)
    
    # Convert to standard format
    trades_df = convert_trade_data_format(trades_df)
    
    if trades_df.empty:
        print("❌ Failed to load trading data")
        return None, None, None
    
    # Calculate daily cash balances
    daily_balances, final_positions = calculate_dynamic_cash_balance(trades_df, starting_cash)
    
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
    
    # Load benchmark data
    print("\n📈 Loading Benchmark Data...")
    print(f"Benchmark file: {benchmark_file_path}")
    benchmark_df = load_benchmark_data(benchmark_file_path)
    
    if benchmark_df.empty:
        print("❌ Failed to load benchmark data")
        return None, None, None
    
    # Calculate benchmark performance
    print("\n📊 Calculating Benchmark Performance...")
    start_date = daily_balances['Date'].min()
    end_date = daily_balances['Date'].max()
    
    benchmark_daily_balances = calculate_buy_and_hold_performance(
        benchmark_df, start_date, end_date, starting_cash
    )
    
    if benchmark_daily_balances.empty:
        print("❌ Failed to calculate benchmark performance")
        return daily_balances, None, None
    
    # Compare strategies
    print("\n⚖️ Comparing Strategy vs Benchmark...")
    comparison_metrics = compare_strategy_vs_benchmark(daily_balances, benchmark_daily_balances)
    
    # Display results
    print("\n" + "=" * 60)
    print("📊 BENCHMARK COMPARISON RESULTS")
    print("=" * 60)
    
    if comparison_metrics:
        print(f"Strategy Total Return:     {comparison_metrics['strategy_total_return']:8.2f}%")
        print(f"Benchmark Total Return:    {comparison_metrics['benchmark_total_return']:8.2f}%")
        print(f"Alpha (Excess Return):     {comparison_metrics['alpha']:8.2f}%")
        print(f"Beta (Volatility):         {comparison_metrics['beta']:8.2f}")
        print(f"Strategy Sharpe Ratio:     {comparison_metrics['strategy_sharpe']:8.2f}")
        print(f"Benchmark Sharpe Ratio:    {comparison_metrics['benchmark_sharpe']:8.2f}")
        print(f"Strategy Max Drawdown:     {comparison_metrics['strategy_max_drawdown']:8.2f}%")
        print(f"Benchmark Max Drawdown:    {comparison_metrics['benchmark_max_drawdown']:8.2f}%")
        print(f"Win Rate:                  {comparison_metrics['win_rate']:8.1f}%")
        print(f"Outperforming Days:        {comparison_metrics['outperforming_days']:8.0f} / {comparison_metrics['total_days']}")
        print(f"Final Strategy Value:      ${comparison_metrics['final_strategy_value']:12,.2f}")
        print(f"Final Benchmark Value:     ${comparison_metrics['final_benchmark_value']:12,.2f}")
    
    return daily_balances, benchmark_daily_balances, comparison_metrics

if __name__ == "__main__":
    print("=== CASH BALANCE TRACKER - READY TO USE ===")
    print("\nTo use with your CSV file, run:")
    print("from cash_balance_tracker import run_csv_cash_tracking_example")
    print("daily_balances, updated_trades = run_csv_cash_tracking_example('your_file.csv')")
    print("\nOr for a quick test with sample data:")
    print("from cash_balance_tracker import run_complete_cash_tracking_example")
    print("daily_balances, updated_trades = run_complete_cash_tracking_example()")
    print("\nFor benchmark comparison:")
    print("from cash_balance_tracker import run_benchmark_analysis")
    print("strategy, benchmark, metrics = run_benchmark_analysis('trades.csv', 'spy_benchmark_data.csv')")
    print("\nExpected CSV columns: EntryTime, ExitTime, EntryPrice, ExitPrice, Ticker")
    print("(The script works with your exact column naming convention)")
    
    # Uncomment the line below to run a quick test with sample data:
    # run_complete_cash_tracking_example()