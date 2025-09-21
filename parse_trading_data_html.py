#!/usr/bin/env python3
"""
Trading Data HTML Parser
Converts LibreOffice XHTML table data to clean CSV format for trading analysis
"""

import pandas as pd
import re
from datetime import datetime
import os
from bs4 import BeautifulSoup

def parse_trading_data_html(html_file_path):
    """
    Parse trading data from LibreOffice XHTML file
    
    Parameters:
    html_file_path: Path to the XHTML file containing trading data
    
    Returns:
    DataFrame with columns: EntryTime, ExitTime, EntryPrice, ExitPrice, Ticker, etc.
    """
    
    print(f"📊 Parsing trading data from: {html_file_path}")
    
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
    
    if len(rows) < 2:
        print("❌ No data rows found")
        return pd.DataFrame()
    
    # Extract header row
    header_row = rows[0]
    header_cells = header_row.find_all('td')
    headers = []
    
    for cell in header_cells:
        p_tag = cell.find('p')
        if p_tag:
            headers.append(p_tag.get_text().strip())
        else:
            headers.append(cell.get_text().strip())
    
    print(f"📋 Found headers: {headers}")
    
    # Extract data rows
    data_rows = []
    
    for row in rows[1:]:  # Skip header row
        cells = row.find_all('td')
        
        if len(cells) >= len(headers):
            row_data = []
            
            for i, cell in enumerate(cells[:len(headers)]):
                p_tag = cell.find('p')
                if p_tag:
                    text = p_tag.get_text().strip()
                else:
                    text = cell.get_text().strip()
                
                row_data.append(text)
            
            # Only add rows that have data in the first few columns
            if len(row_data) >= 5 and row_data[0] and row_data[0] != '':
                data_rows.append(row_data)
    
    if not data_rows:
        print("❌ No data rows found")
        return pd.DataFrame()
    
    # Create DataFrame
    df = pd.DataFrame(data_rows, columns=headers)
    
    # Clean and convert data types
    print(f"📊 Parsed {len(df)} trading records")
    
    # Convert date columns
    date_columns = ['EntryTime', 'ExitTime']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Convert numeric columns
    numeric_columns = ['EntryPrice', 'ExitPrice', 'PnL', 'ReturnPct', 'Duration']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Remove rows with invalid dates or prices
    if 'EntryTime' in df.columns and 'ExitTime' in df.columns:
        df = df.dropna(subset=['EntryTime', 'ExitTime'])
    
    if 'EntryPrice' in df.columns and 'ExitPrice' in df.columns:
        df = df.dropna(subset=['EntryPrice', 'ExitPrice'])
    
    # Sort by entry time
    if 'EntryTime' in df.columns:
        df = df.sort_values('EntryTime').reset_index(drop=True)
    
    print(f"✅ Cleaned data: {len(df)} valid trading records")
    if len(df) > 0:
        print(f"📅 Date range: {df['EntryTime'].min().date()} to {df['ExitTime'].max().date()}")
        print(f"💰 Price range: ${df['EntryPrice'].min():.2f} to ${df['EntryPrice'].max():.2f}")
    
    return df

def save_trading_data_to_csv(df, output_file='trading_data_parsed.csv'):
    """
    Save parsed trading data to CSV file
    
    Parameters:
    df: Parsed trading DataFrame
    output_file: Output CSV file path
    """
    
    df.to_csv(output_file, index=False)
    print(f"💾 Saved trading data to: {output_file}")
    
    return output_file

def load_trading_data_from_csv(csv_file='trading_data_parsed.csv'):
    """
    Load trading data from CSV file
    
    Parameters:
    csv_file: Path to CSV file
    
    Returns:
    DataFrame with trading data
    """
    
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"Trading data file not found: {csv_file}")
    
    df = pd.read_csv(csv_file)
    df['EntryTime'] = pd.to_datetime(df['EntryTime'])
    df['ExitTime'] = pd.to_datetime(df['ExitTime'])
    
    print(f"📊 Loaded trading data: {len(df)} records")
    print(f"📅 Date range: {df['EntryTime'].min().date()} to {df['ExitTime'].max().date()}")
    
    return df

if __name__ == "__main__":
    # Parse the HTML file and save to CSV
    html_file = "V1_DVO_SP500_TICKERS_DAILY_10_MAX_NO_EXTRA_FILTER_FINAL_2025_09.html"
    
    if os.path.exists(html_file):
        try:
            # Parse trading data
            trading_df = parse_trading_data_html(html_file)
            
            if not trading_df.empty:
                # Save to CSV
                csv_file = save_trading_data_to_csv(trading_df)
                
                # Show sample data
                print("\n📋 Sample trading data:")
                print(trading_df.head(10))
                
                print(f"\n✅ Trading data parsing complete!")
                print(f"📁 CSV file: {csv_file}")
                
                # Show column info
                print(f"\n📊 Columns available:")
                for i, col in enumerate(trading_df.columns):
                    print(f"  {i+1:2d}. {col}")
            else:
                print("❌ No data found in HTML file")
                
        except Exception as e:
            print(f"❌ Error parsing trading data: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"❌ HTML file not found: {html_file}")
