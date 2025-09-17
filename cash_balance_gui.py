#!/usr/bin/env python3
"""
Cash Balance Tracker GUI

A simple graphical interface for analyzing trading data with 10% dynamic position sizing.
Supports CSV, Excel (.xlsx, .xls) files.

Usage: python cash_balance_gui.py
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import os
import sys
import platform
from datetime import datetime
import threading

# Import our cash balance functions
from cash_balance_tracker import (
    load_csv_trade_data, 
    load_excel_trade_data,
    convert_trade_data_format,
    calculate_dynamic_cash_balance, 
    recalculate_trade_metrics
)

class CashBalanceGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Cash Balance Tracker - 10% Dynamic Position Sizing")
        
        # Detect platform for better compatibility
        self.is_macos = platform.system() == "Darwin"
        self.is_windows = platform.system() == "Windows"
        self.is_linux = platform.system() == "Linux"
        
        # Platform-specific sizing
        if self.is_macos:
            self.root.geometry("850x750")  # Slightly larger on macOS
        else:
            self.root.geometry("800x700")
        
        # Variables
        self.file_path = tk.StringVar()
        self.starting_cash = tk.StringVar(value="1000000")
        self.daily_balances = None
        self.updated_trades = None
        
        # Configure for macOS if needed
        if self.is_macos:
            self.setup_macos_specific()
        
        self.setup_gui()
        
    def setup_macos_specific(self):
        """Configure macOS-specific settings"""
        try:
            # Use native macOS menu bar if available
            self.root.createcommand('tk::mac::ShowPreferences', self.show_preferences)
            
            # Better macOS integration
            self.root.tk.call('tk::unsupported::MacWindowStyle', 'style', self.root._w, 'document')
            
        except (tk.TclError, AttributeError):
            # Fallback if macOS-specific features aren't available
            pass
    
    def show_preferences(self):
        """Show preferences dialog (macOS menu integration)"""
        messagebox.showinfo("Preferences", 
                           "Cash Balance Tracker v1.0\n\n"
                           "Adjust starting cash in the main window.\n"
                           "Supported formats: CSV, Excel (.xlsx, .xls)")
        
    def setup_gui(self):
        """Setup the GUI components"""
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Cash Balance Tracker", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # File selection section
        file_frame = ttk.LabelFrame(main_frame, text="Select Trading Data File", padding="10")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        ttk.Label(file_frame, text="File:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.file_entry = ttk.Entry(file_frame, textvariable=self.file_path, width=60)
        self.file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.browse_button = ttk.Button(file_frame, text="Browse...", command=self.browse_file)
        self.browse_button.grid(row=0, column=2)
        
        # Supported formats info
        formats_label = ttk.Label(file_frame, text="Supported formats: CSV (recommended), Excel (.xlsx, .xls)", 
                                 font=("Arial", 9), foreground="gray")
        formats_label.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))
        
        # Excel note
        excel_note = ttk.Label(file_frame, text="Note: Excel files require 'openpyxl' package", 
                              font=("Arial", 8), foreground="orange")
        excel_note.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(2, 0))
        
        # Settings section
        settings_frame = ttk.LabelFrame(main_frame, text="Settings", padding="10")
        settings_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(settings_frame, text="Starting Cash ($):").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        cash_entry = ttk.Entry(settings_frame, textvariable=self.starting_cash, width=15)
        cash_entry.grid(row=0, column=1, sticky=tk.W)
        
        # Column mapping section
        mapping_frame = ttk.LabelFrame(main_frame, text="Column Mapping (Auto-detected)", padding="10")
        mapping_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        mapping_frame.columnconfigure(1, weight=1)
        
        # Expected columns info
        expected_text = ("Expected columns: EntryTime, ExitTime, EntryPrice, ExitPrice, Ticker\n"
                        "The script will automatically detect and map your column names.")
        ttk.Label(mapping_frame, text=expected_text, font=("Arial", 9), 
                 foreground="blue").grid(row=0, column=0, columnspan=2, sticky=tk.W)
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=(0, 10))
        
        self.analyze_button = ttk.Button(button_frame, text="Analyze Trading Data", 
                                        command=self.analyze_data, style="Accent.TButton")
        self.analyze_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.save_button = ttk.Button(button_frame, text="Save Results", 
                                     command=self.save_results, state="disabled")
        self.save_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_button = ttk.Button(button_frame, text="Clear", command=self.clear_results)
        self.clear_button.pack(side=tk.LEFT)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Status label
        self.status_var = tk.StringVar(value="Ready to analyze trading data...")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var, 
                                     font=("Arial", 9), foreground="green")
        self.status_label.grid(row=6, column=0, columnspan=3, sticky=tk.W)
        
        # Results section
        results_frame = ttk.LabelFrame(main_frame, text="Analysis Results", padding="10")
        results_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(7, weight=1)
        
        # Results text area with scrollbar
        self.results_text = scrolledtext.ScrolledText(results_frame, height=20, width=80, 
                                                     font=("Consolas", 9))
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Initial message
        initial_msg = """Welcome to Cash Balance Tracker!

This tool analyzes your trading data with 10% dynamic position sizing.

Instructions:
1. Click 'Browse...' to select your trading data file (CSV or Excel)
2. Set your starting cash amount
3. Click 'Analyze Trading Data' to process your file
4. View results and save them if needed

Expected file format:
- EntryTime: Date of trade entry (YYYY-MM-DD format)
- ExitTime: Date of trade exit  
- EntryPrice: Price at entry
- ExitPrice: Price at exit
- Ticker: Stock symbol

The tool will automatically:
✓ Calculate 10% position sizing based on available cash
✓ Track daily cash balances for every day
✓ Recalculate all trades with realistic position sizes
✓ Provide comprehensive trading statistics
"""
        self.results_text.insert(tk.END, initial_msg)
        
    def browse_file(self):
        """Open file dialog to select trading data file"""
        filetypes = [
            ("All Supported", "*.csv *.xlsx *.xls"),
            ("CSV files", "*.csv"),
            ("Excel files", "*.xlsx *.xls"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select Trading Data File",
            filetypes=filetypes
        )
        
        if filename:
            self.file_path.set(filename)
            self.status_var.set(f"Selected: {os.path.basename(filename)}")
            
    def update_status(self, message, color="black"):
        """Update status message"""
        self.status_var.set(message)
        self.status_label.config(foreground=color)
        self.root.update_idletasks()
        
    def analyze_data(self):
        """Analyze the selected trading data file"""
        if not self.file_path.get():
            messagebox.showerror("Error", "Please select a trading data file first.")
            return
            
        if not os.path.exists(self.file_path.get()):
            messagebox.showerror("Error", "Selected file does not exist.")
            return
            
        try:
            starting_cash = float(self.starting_cash.get().replace(",", ""))
            if starting_cash <= 0:
                raise ValueError("Starting cash must be positive")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid starting cash amount: {e}")
            return
            
        # Disable button and start progress
        self.analyze_button.config(state="disabled")
        self.progress.start()
        self.update_status("Loading and analyzing data...", "blue")
        
        # Run analysis in separate thread to prevent GUI freezing
        thread = threading.Thread(target=self._run_analysis, args=(starting_cash,))
        thread.daemon = True
        thread.start()
        
    def _run_analysis(self, starting_cash):
        """Run the actual analysis in a separate thread"""
        try:
            file_path = self.file_path.get()
            file_ext = os.path.splitext(file_path)[1].lower()
            
            # Load data based on file type
            self.update_status("Loading file...", "blue")
            
            if file_ext == '.csv':
                trades_df = load_csv_trade_data(file_path)
            elif file_ext in ['.xlsx', '.xls']:
                trades_df = load_excel_trade_data(
                    file_path,
                    entry_time_col='EntryTime',
                    exit_time_col='ExitTime', 
                    entry_price_col='EntryPrice',
                    exit_price_col='ExitPrice',
                    ticker_col='Ticker'
                )
            else:
                raise ValueError(f"Unsupported file format: {file_ext}. Please use CSV, .xlsx, or .xls files.")
                
            self.update_status("Calculating daily cash balances...", "blue")
            
            # Calculate daily cash balances
            self.daily_balances, final_positions = calculate_dynamic_cash_balance(
                trades_df, starting_cash
            )
            
            self.update_status("Recalculating trade metrics...", "blue")
            
            # Recalculate trade metrics
            self.updated_trades = recalculate_trade_metrics(trades_df, self.daily_balances)
            
            # Display results on main thread
            self.root.after(0, self._display_results, starting_cash)
            
        except ImportError as e:
            if "openpyxl" in str(e).lower():
                error_msg = ("Excel file support not available. Please install openpyxl:\n\n"
                           "pip install openpyxl\n\n"
                           "Or save your Excel file as CSV format instead.")
            else:
                error_msg = f"Missing required library: {str(e)}"
            self.root.after(0, self._show_error, error_msg)
            
        except Exception as e:
            error_msg = f"Error analyzing data: {str(e)}"
            self.root.after(0, self._show_error, error_msg)
            
    def _show_error(self, error_msg):
        """Show error message on main thread"""
        self.progress.stop()
        self.analyze_button.config(state="normal")
        self.update_status("Error occurred", "red")
        messagebox.showerror("Analysis Error", error_msg)
        
    def _display_results(self, starting_cash):
        """Display analysis results on main thread"""
        try:
            # Stop progress and re-enable button
            self.progress.stop()
            self.analyze_button.config(state="normal")
            self.save_button.config(state="normal")
            
            # Clear previous results
            self.results_text.delete(1.0, tk.END)
            
            # Calculate summary statistics
            total_trades = len(self.updated_trades)
            winning_trades = len(self.updated_trades[self.updated_trades['ActualPnL'] > 0])
            win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
            total_pnl = self.updated_trades['ActualPnL'].sum()
            final_portfolio_value = self.daily_balances['TotalPortfolio'].iloc[-1]
            total_return = ((final_portfolio_value - starting_cash) / starting_cash) * 100
            avg_pnl = total_pnl / total_trades if total_trades > 0 else 0
            
            # Format results
            results = f"""=== CASH BALANCE TRACKING ANALYSIS COMPLETE ===

FILE ANALYZED: {os.path.basename(self.file_path.get())}
ANALYSIS DATE: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

=== SUMMARY STATISTICS ===
Starting Cash:           ${starting_cash:,.2f}
Final Portfolio Value:   ${final_portfolio_value:,.2f}
Total Return:            {total_return:.2f}%
Total P&L:              ${total_pnl:,.2f}
Total Trades:           {total_trades:,}
Winning Trades:         {winning_trades:,}
Win Rate:               {win_rate:.1f}%
Average P&L per Trade:  ${avg_pnl:,.2f}

=== ADDITIONAL INSIGHTS ===
Date Range:             {self.daily_balances['Date'].min().date()} to {self.daily_balances['Date'].max().date()}
Number of Days:         {len(self.daily_balances):,}
Maximum Cash Balance:   ${self.daily_balances['CashBalance'].max():,.2f}
Minimum Cash Balance:   ${self.daily_balances['CashBalance'].min():,.2f}
Maximum Active Positions: {self.daily_balances['ActivePositions'].max()}

=== FIRST 10 DAILY CASH BALANCES ===
{self.daily_balances.head(10).to_string(index=False)}

=== LAST 10 DAILY CASH BALANCES ===
{self.daily_balances.tail(10).to_string(index=False)}

=== FIRST 10 UPDATED TRADES (with 10% Position Sizing) ===
{self.updated_trades[['EntryDate', 'Ticker', 'CashAvailable', 'PositionSize', 'ActualShares', 'ActualCost', 'ActualPnL', 'ReturnPct']].head(10).to_string(index=False)}

=== ANALYSIS COMPLETE ===
✓ Each position allocated exactly 10% of available cash
✓ Daily cash balance tracked for every day
✓ Realistic trade results with whole share constraints
✓ Ready to save results to files

Click 'Save Results' to export data to CSV files.
"""
            
            self.results_text.insert(tk.END, results)
            self.update_status(f"Analysis complete! Processed {total_trades:,} trades over {len(self.daily_balances):,} days.", "green")
            
        except Exception as e:
            self._show_error(f"Error displaying results: {str(e)}")
            
    def save_results(self):
        """Save analysis results to CSV files"""
        if self.daily_balances is None or self.updated_trades is None:
            messagebox.showerror("Error", "No results to save. Please run analysis first.")
            return
            
        # Ask user for save directory
        save_dir = filedialog.askdirectory(title="Select Directory to Save Results")
        if not save_dir:
            return
            
        try:
            # Generate filename prefix
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = os.path.splitext(os.path.basename(self.file_path.get()))[0]
            
            # Save daily balances
            daily_file = os.path.join(save_dir, f"{base_name}_daily_cash_balances_{timestamp}.csv")
            self.daily_balances.to_csv(daily_file, index=False)
            
            # Save updated trades
            trades_file = os.path.join(save_dir, f"{base_name}_updated_trades_10percent_{timestamp}.csv")
            self.updated_trades.to_csv(trades_file, index=False)
            
            # Save summary report
            summary_file = os.path.join(save_dir, f"{base_name}_analysis_summary_{timestamp}.txt")
            with open(summary_file, 'w') as f:
                f.write(self.results_text.get(1.0, tk.END))
                
            success_msg = f"""Results saved successfully!

Files created:
1. Daily Cash Balances: {os.path.basename(daily_file)}
2. Updated Trades: {os.path.basename(trades_file)}
3. Analysis Summary: {os.path.basename(summary_file)}

Location: {save_dir}"""
            
            messagebox.showinfo("Save Complete", success_msg)
            self.update_status(f"Results saved to {save_dir}", "green")
            
        except Exception as e:
            messagebox.showerror("Save Error", f"Error saving results: {str(e)}")
            
    def clear_results(self):
        """Clear all results and reset the interface"""
        self.file_path.set("")
        self.starting_cash.set("1000000")
        self.daily_balances = None
        self.updated_trades = None
        self.save_button.config(state="disabled")
        
        # Clear results text
        self.results_text.delete(1.0, tk.END)
        initial_msg = """Results cleared. Ready for new analysis.

Select a trading data file and click 'Analyze Trading Data' to begin."""
        self.results_text.insert(tk.END, initial_msg)
        
        self.update_status("Ready to analyze trading data...", "green")

def main():
    """Main function to run the GUI application"""
    root = tk.Tk()
    
    # Detect platform
    is_macos = platform.system() == "Darwin"
    is_windows = platform.system() == "Windows"
    
    # Set up platform-appropriate styling
    style = ttk.Style()
    
    # Choose the best theme for each platform
    if is_macos:
        # macOS looks best with aqua theme if available
        try:
            style.theme_use('aqua')
        except tk.TclError:
            try:
                style.theme_use('clam')
            except tk.TclError:
                style.theme_use('default')
    elif is_windows:
        # Windows looks good with vista or xpnative
        try:
            style.theme_use('vista')
        except tk.TclError:
            try:
                style.theme_use('winnative')
            except tk.TclError:
                style.theme_use('clam')
    else:
        # Linux/Unix - use clam or alt
        try:
            style.theme_use('clam')
        except tk.TclError:
            style.theme_use('alt')
    
    # Configure custom styles with platform-appropriate colors
    if is_macos:
        style.configure('Accent.TButton', 
                       foreground='white', 
                       background='#007AFF')  # macOS blue
    else:
        style.configure('Accent.TButton', 
                       foreground='white', 
                       background='#0078d4')  # Windows blue
    
    app = CashBalanceGUI(root)
    
    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")
    
    # macOS-specific window setup
    if is_macos:
        # Bring window to front on macOS
        root.lift()
        root.attributes('-topmost', True)
        root.after_idle(root.attributes, '-topmost', False)
    
    root.mainloop()

if __name__ == "__main__":
    main()
