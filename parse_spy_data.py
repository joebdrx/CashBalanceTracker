#!/usr/bin/env python3
"""
SPY Data Parser
Converts HTML table data to clean CSV format for benchmark analysis
"""

import pandas as pd
import re
from datetime import datetime
import os
from bs4 import BeautifulSoup

def parse_spy_html_data(html_file_path):
    """
    Parse SPY OHLC data from HTML file exported from spreadsheet
    
    Parameters:
    html_file_path: Path to the HTML file containing SPY data
    
    Returns:
    DataFrame with columns: Date, Symbol, Open, High, Low, Close, Adjusted_Close, Volume
    """
    
    print(f"📊 Parsing SPY data from: {html_file_path}")
    
    # Read the HTML file
    with open(html_file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(content, 'html.parser')
    
    # Find the table
    table = soup.find('table')
    if not table:
        print("❌ No table found in HTML file")
        return pd.DataFrame()
    
    # Extract all rows
    rows = table.find_all('tr')
    
    data_rows = []
    header_found = False
    
    for row in rows:
        cells = row.find_all('td')
        
        if len(cells) >= 7:  # Need at least 7 columns for OHLC data
            row_data = []
            
            for i, cell in enumerate(cells[:7]):  # Take first 7 columns
                # Check if this is the header row
                if i == 0 and 'date' in cell.get_text().lower():
                    header_found = True
                    break
                
                # Extract text content
                text = cell.get_text().strip()
                
                # Check for data-sheets-value attribute for more accurate parsing
                data_attr = cell.get('data-sheets-value')
                if data_attr:
                    # Parse JSON-like data-sheets-value
                    try:
                        # Extract numeric values
                        if '"3":' in data_attr:  # Numeric value
                            num_match = re.search(r'"3":\s*(\d+(?:\.\d+)?)', data_attr)
                            if num_match:
                                value = float(num_match.group(1))
                                # Check if this is a date (Excel serial number)
                                if i == 0 and 40000 < value < 50000:  # Date column with Excel serial number
                                    # Convert Excel serial number to date
                                    from datetime import datetime, timedelta
                                    excel_epoch = datetime(1900, 1, 1)
                                    # Excel serial numbers start from 1900-01-01, but Excel has a bug with 1900 being a leap year
                                    if value > 59:  # Account for Excel's 1900 leap year bug
                                        value = value - 1
                                    date = excel_epoch + timedelta(days=value - 2)
                                    text = date.strftime('%Y-%m-%d')
                                else:
                                    text = value
                        elif '"2":' in data_attr:  # String value
                            str_match = re.search(r'"2":\s*"([^"]*)"', data_attr)
                            if str_match:
                                text = str_match.group(1)
                    except:
                        pass  # Use text content as fallback
                
                row_data.append(text)
            
            # Skip header row
            if header_found and len(row_data) >= 7 and row_data[0] is not None:
                # Skip if first column contains 'date' (header)
                if not str(row_data[0]).lower().startswith('date'):
                    data_rows.append(row_data)
    
    if not data_rows:
        print("❌ No data rows found")
        return pd.DataFrame()
    
    # Create DataFrame
    columns = ['Date', 'Symbol', 'Open', 'High', 'Low', 'Close', 'Adjusted_Close']
    df = pd.DataFrame(data_rows, columns=columns)
    
    # Clean and convert data types
    df = df.dropna(subset=['Date', 'Close'])
    
    # Convert date column - handle different date formats
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    
    # Convert numeric columns
    numeric_columns = ['Open', 'High', 'Low', 'Close', 'Adjusted_Close']
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Remove rows with invalid dates or prices
    df = df.dropna(subset=['Date', 'Close'])
    
    # Sort by date
    df = df.sort_values('Date').reset_index(drop=True)
    
    print(f"✅ Parsed {len(df)} SPY data points")
    if len(df) > 0:
        print(f"📅 Date range: {df['Date'].min().date()} to {df['Date'].max().date()}")
        print(f"💰 Price range: ${df['Close'].min():.2f} to ${df['Close'].max():.2f}")
    
    return df

def save_spy_data_to_csv(df, output_file='spy_benchmark_data.csv'):
    """
    Save parsed SPY data to CSV file
    
    Parameters:
    df: Parsed SPY DataFrame
    output_file: Output CSV file path
    """
    
    df.to_csv(output_file, index=False)
    print(f"💾 Saved SPY data to: {output_file}")
    
    return output_file

def load_spy_data_from_csv(csv_file='spy_benchmark_data.csv'):
    """
    Load SPY data from CSV file
    
    Parameters:
    csv_file: Path to CSV file
    
    Returns:
    DataFrame with SPY data
    """
    
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"SPY data file not found: {csv_file}")
    
    df = pd.read_csv(csv_file)
    df['Date'] = pd.to_datetime(df['Date'])
    
    print(f"📊 Loaded SPY data: {len(df)} records")
    print(f"📅 Date range: {df['Date'].min().date()} to {df['Date'].max().date()}")
    
    return df

if __name__ == "__main__":
    # Parse the HTML file and save to CSV
    html_file = "70dbab46-7ddf-4a8e-90bd-7d4bfa80e842.html"
    
    if os.path.exists(html_file):
        try:
            # Parse SPY data
            spy_df = parse_spy_html_data(html_file)
            
            # Save to CSV
            csv_file = save_spy_data_to_csv(spy_df)
            
            # Show sample data
            print("\n📋 Sample SPY data:")
            print(spy_df.head(10))
            
            print(f"\n✅ SPY data parsing complete!")
            print(f"📁 CSV file: {csv_file}")
            
        except Exception as e:
            print(f"❌ Error parsing SPY data: {e}")
    else:
        print(f"❌ HTML file not found: {html_file}")
