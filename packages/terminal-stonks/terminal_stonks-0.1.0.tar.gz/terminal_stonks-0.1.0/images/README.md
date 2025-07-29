# Images Directory

This directory contains example images for the Terminal Stonks project.

## example.png

This should contain a screenshot of the terminal showing a candlestick chart rendered by Terminal Stonks.

To generate this example image:

1. Run the screenshot-friendly example script:
   ```bash
   python scripts/generate_example.py
   ```
   This script generates realistic stock data and provides a countdown for taking screenshots.

2. Alternative - run the basic example:
   ```bash
   python example.py
   ```

3. Take a screenshot of your terminal showing the chart

4. Save the screenshot as `example.png` in this directory

## Requirements for the example image:

- Should show a colorful candlestick chart in the terminal
- Terminal should be large enough to display the chart clearly
- Include the chart title and axis labels
- PNG format with good contrast and readability

The image will be displayed in the main README.md file to showcase the library's capabilities. 