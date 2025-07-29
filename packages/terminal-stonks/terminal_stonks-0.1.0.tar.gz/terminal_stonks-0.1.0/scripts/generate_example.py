#!/usr/bin/env python3
"""
Generate example chart for screenshot
This script creates a more realistic example for taking screenshots
"""

import pandas as pd
import numpy as np
from terminal_stonks.k_chart import KChart
import time

def generate_realistic_data(days=30):
    """Generate realistic-looking stock data"""
    np.random.seed(42)  # For reproducible results
    
    # Start with a base price
    start_price = 100.0
    dates = pd.date_range('2024-01-01', periods=days, freq='D')
    
    # Generate price movements using random walk
    returns = np.random.normal(0.001, 0.02, days)  # Small daily returns with volatility
    prices = [start_price]
    
    for ret in returns[1:]:
        new_price = prices[-1] * (1 + ret)
        prices.append(new_price)
    
    # Generate OHLC data
    data = []
    for i, price in enumerate(prices):
        # Add some intraday volatility
        volatility = abs(np.random.normal(0, 0.015))
        high = price * (1 + volatility)
        low = price * (1 - volatility)
        
        # Open is previous close with some gap
        if i == 0:
            open_price = price
        else:
            gap = np.random.normal(0, 0.005)
            open_price = data[i-1]['Close'] * (1 + gap)
        
        close_price = price
        
        data.append({
            'Open': open_price,
            'High': max(open_price, high, close_price),
            'Low': min(open_price, low, close_price),
            'Close': close_price
        })
    
    return pd.DataFrame(data, index=dates)

def main():
    print("🚀 Terminal Stonks - Example Chart Generator")
    print("=" * 50)
    print()
    
    # Generate realistic data
    print("📊 Generating realistic stock data...")
    data = generate_realistic_data(25)
    
    print(f"📈 Data range: {data.index[0].strftime('%Y-%m-%d')} to {data.index[-1].strftime('%Y-%m-%d')}")
    print(f"💰 Price range: ${data['Low'].min():.2f} - ${data['High'].max():.2f}")
    print()
    
    print("⏳ Rendering chart in 3 seconds... (Perfect time to take a screenshot!)")
    time.sleep(3)
    
    # Create and render the chart
    chart = KChart(data)
    chart.render("📈 EXAMPLE STOCK (EXPL) - Terminal Stonks Demo 🚀")
    
    print()
    print("✨ Chart rendered! This is perfect for taking a screenshot.")
    print("💡 To save this as example.png:")
    print("   1. Take a screenshot of your terminal")
    print("   2. Crop to show just the chart area")
    print("   3. Save as 'images/example.png'")

if __name__ == "__main__":
    main() 