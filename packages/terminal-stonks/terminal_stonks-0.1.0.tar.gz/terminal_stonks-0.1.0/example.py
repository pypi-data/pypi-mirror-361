#!/usr/bin/env python3
"""
Simple example of using terminal-stonks package
"""

import pandas as pd
from terminal_stonks import KChart

def main():
    # Create sample OHLC data
    data = pd.DataFrame({
        'Open': [100.0, 102.0, 101.0, 103.0, 105.0, 104.0, 106.0, 108.0, 107.0, 109.0],
        'High': [105.0, 106.0, 104.0, 107.0, 108.0, 107.0, 109.0, 110.0, 109.0, 111.0],
        'Low': [99.0, 101.0, 100.0, 102.0, 104.0, 103.0, 105.0, 107.0, 106.0, 108.0],
        'Close': [102.0, 101.0, 103.0, 105.0, 107.0, 106.0, 108.0, 107.0, 109.0, 110.0]
    }, index=pd.date_range('2024-01-01', periods=10, freq='D'))
    
    print("Terminal Stonks Example")
    print("======================")
    print(f"Sample data shape: {data.shape}")
    print(f"Date range: {data.index[0].strftime('%Y-%m-%d')} to {data.index[-1].strftime('%Y-%m-%d')}")
    print()
    
    # Create and display chart
    chart = KChart(data)
    chart.render("Sample Stock Chart - Terminal Stonks Demo")

if __name__ == "__main__":
    main() 