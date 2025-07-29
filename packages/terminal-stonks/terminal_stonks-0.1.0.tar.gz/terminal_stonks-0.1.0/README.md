# Terminal Stonks 📈

[![PyPI version](https://badge.fury.io/py/terminal-stonks.svg)](https://badge.fury.io/py/terminal-stonks)
[![Python Versions](https://img.shields.io/pypi/pyversions/terminal-stonks.svg)](https://pypi.org/project/terminal-stonks/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python library for rendering beautiful stock candlestick charts directly in your terminal using ASCII art and colors.

## Preview

![Terminal Stonks Example](images/example.png)
*Example of a candlestick chart rendered in the terminal*

## Features

- 🎨 **Beautiful ASCII charts** - Render K-line/candlestick charts in your terminal
- 🌈 **Color-coded candles** - Red for bullish, green for bearish movements
- 📏 **Auto-scaling** - Charts automatically scale to fit your terminal size
- 📅 **Date labels** - X-axis shows relevant dates for better context
- 💰 **Price labels** - Y-axis displays price levels
- 🔄 **Real-time compatible** - Perfect for live data visualization

## Installation

Install from PyPI:

```bash
pip install terminal-stonks
```

Or install from source:

```bash
git clone https://github.com/yourusername/terminal-stonks.git
cd terminal-stonks
pip install -e .
```

## Quick Start

```python
import pandas as pd
from terminal_stonks import KChart

# Create sample data
data = pd.DataFrame({
    'Open': [100, 102, 101, 103, 105],
    'High': [105, 106, 104, 107, 108],
    'Low': [99, 101, 100, 102, 104],
    'Close': [102, 101, 103, 105, 107]
}, index=pd.date_range('2024-01-01', periods=5, freq='D'))

# Create and render chart
chart = KChart(data)
chart.render(title="My Stock Chart")
```

## API Reference

### KChart Class

#### `__init__(data: pd.DataFrame)`

Initialize a KChart with stock data.

**Parameters:**
- `data` (pd.DataFrame): DataFrame with columns 'Open', 'High', 'Low', 'Close' and a DatetimeIndex

**Raises:**
- `TypeError`: If the index is not a DatetimeIndex

#### `render(title: str = "")`

Render the chart to the terminal.

**Parameters:**
- `title` (str, optional): Chart title to display at the top

## Data Format

Your DataFrame should have the following structure:

```python
import pandas as pd

data = pd.DataFrame({
    'Open': [float],    # Opening prices
    'High': [float],    # Highest prices
    'Low': [float],     # Lowest prices
    'Close': [float]    # Closing prices
}, index=pd.DatetimeIndex)  # Must be a DatetimeIndex
```

## Examples

### Basic Usage

```python
from terminal_stonks import KChart
import pandas as pd

# Sample OHLC data
data = pd.DataFrame({
    'Open': [150.0, 152.0, 151.0, 153.0],
    'High': [155.0, 156.0, 154.0, 157.0],
    'Low': [149.0, 151.0, 150.0, 152.0],
    'Close': [152.0, 151.0, 153.0, 155.0]
}, index=pd.date_range('2024-01-01', periods=4))

chart = KChart(data)
chart.render("AAPL Stock Chart")
```

### With Yahoo Finance Data

```python
import yfinance as yf
from terminal_stonks import KChart

# Fetch real data
ticker = yf.Ticker("AAPL")
data = ticker.history(period="1mo")

# Render chart
chart = KChart(data)
chart.render("Apple Inc. (AAPL) - Last 30 Days")
```

**Example Output:**
![Terminal Chart Example](images/example.png)

## Chart Components

- **Candlestick Body**: Represented by `█` characters
  - Red: Bullish (Close > Open)
  - Green: Bearish (Close < Open)
- **Shadows/Wicks**: Represented by `│` characters
- **Price Scale**: Left side Y-axis with price levels
- **Date Labels**: Bottom X-axis with date information

## Requirements

- Python 3.8+
- pandas >= 1.3.0
- rich >= 10.0.0

## Development

To set up for development:

```bash
git clone https://github.com/yourusername/terminal-stonks.git
cd terminal-stonks
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

Format code:

```bash
black terminal_stonks/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Generating Example Screenshots

To update the example image (`images/example.png`):

```bash
# Run the screenshot-friendly script
python scripts/generate_example.py

# Take a screenshot when the chart appears
# Save as images/example.png
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Rich](https://github.com/Textualize/rich) for beautiful terminal output
- Inspired by the need for simple, terminal-based financial data visualization

## Changelog

### 0.1.0 (Initial Release)
- Basic candlestick chart rendering
- Auto-scaling charts
- Color-coded bullish/bearish candles
- Date and price axis labels

## Author

**Sun Jiaxuan**  
Email: [sunjiaxuan@hotmail.com](mailto:sunjiaxuan@hotmail.com) 