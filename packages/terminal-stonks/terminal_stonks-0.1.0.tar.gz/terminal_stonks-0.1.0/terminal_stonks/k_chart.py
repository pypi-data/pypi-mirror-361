import shutil
import pandas as pd
from rich.console import Console
from rich.text import Text

class KChart:
    """
    A class to render K-line charts in the terminal.
    """
    def __init__(self, data: pd.DataFrame):
        """
        Initializes the KChart with stock data.

        Args:
            data (pd.DataFrame): A DataFrame with 'Open', 'High', 'Low', 'Close' columns.
                                 The index should be a DatetimeIndex.
        """
        if not isinstance(data.index, pd.DatetimeIndex):
            raise TypeError("Data index must be a DatetimeIndex.")
        self.data = data
        self.console = Console()

    def render(self, title=""):
        """
        Renders the K-line chart to the console.
        """
        self.console.clear()
        terminal_width, terminal_height = shutil.get_terminal_size()

        # Define margins and calculate chart dimensions
        y_axis_width = 10  # Space for price labels
        x_axis_height = 2  # Space for date labels
        top_margin = 1
        bottom_margin = 1

        chart_height = terminal_height - x_axis_height - top_margin - bottom_margin
        chart_width = terminal_width - y_axis_width

        if chart_height <= 0 or chart_width <= 0:
            self.console.print("Terminal too small.", style="bold red")
            return

        # Slice data to fit the chart width
        data_to_display = self.data.iloc[-chart_width:]
        if data_to_display.empty:
            return

        max_price = data_to_display['High'].max()
        min_price = data_to_display['Low'].min()
        price_range = max_price - min_price
        if price_range == 0:
            price_range = 1 # Avoid division by zero

        price_per_row = price_range / chart_height

        # Initialize canvas as a list of Text objects
        canvas = [Text(" " * terminal_width) for _ in range(chart_height)]

        # Draw components
        self._draw_y_axis(canvas, chart_height, max_price, min_price, y_axis_width)
        self._draw_candlesticks(canvas, data_to_display, chart_height, chart_width, max_price, price_per_row, y_axis_width)
        
        # Print title and chart
        self.console.print(f"[bold]{title}[/bold]", justify="center")
        for row_text in canvas:
            self.console.print(row_text)
            
        # Draw and print X-axis separately
        x_axis = self._draw_x_axis(data_to_display, chart_width, y_axis_width)
        self.console.print(x_axis)

    def _draw_y_axis(self, canvas, height, max_p, min_p, y_axis_width):
        if height <= 1:
            return
        price_step = (max_p - min_p) / (height - 1)
        for i in range(height):
            price = max_p - (i * price_step)
            label = f"{price:>{y_axis_width - 2}.2f} -"
            label_text = Text(label, style="dim")
            canvas[i] = label_text + canvas[i][len(label):]

    def _scale_price(self, price, max_price, price_per_row, chart_height):
        scaled = int((max_price - price) / price_per_row) if price_per_row > 0 else 0
        return max(0, min(chart_height - 1, scaled))

    def _draw_candlesticks(self, canvas, data, height, width, max_p, price_per_row, y_axis_offset):
        for i, (timestamp, row) in enumerate(data.iterrows()):
            x_pos = y_axis_offset + i
            if x_pos >= y_axis_offset + width:
                continue

            is_positive = row['Close'] >= row['Open']
            color = "red" if is_positive else "green"

            high_y = self._scale_price(row['High'], max_p, price_per_row, height)
            low_y = self._scale_price(row['Low'], max_p, price_per_row, height)
            open_y = self._scale_price(row['Open'], max_p, price_per_row, height)
            close_y = self._scale_price(row['Close'], max_p, price_per_row, height)
            
            body_top_y = min(open_y, close_y)
            body_bottom_y = max(open_y, close_y)

            # Draw upper shadow
            for y in range(high_y, body_top_y):
                canvas[y] = canvas[y][:x_pos] + Text("│", style=color) + canvas[y][x_pos+1:]

            # Draw body
            for y in range(body_top_y, body_bottom_y + 1):
                canvas[y] = canvas[y][:x_pos] + Text("█", style=color) + canvas[y][x_pos+1:]
            
            # Draw lower shadow
            for y in range(body_bottom_y + 1, low_y + 1):
                canvas[y] = canvas[y][:x_pos] + Text("│", style=color) + canvas[y][x_pos+1:]

    def _draw_x_axis(self, data, width, y_axis_offset):
        x_axis = Text(" " * (y_axis_offset -1) + "└", style="default")
        x_axis.append("-" * (width))

        # Add date labels
        num_labels = width // 15 # one label every 15 chars
        if num_labels < 2:
            num_labels = 2
        
        step = len(data) // (num_labels -1) if num_labels > 1 else 0
        
        labels = {}

        if len(data) > 0:
            # First label
            labels[0] = data.index[0].strftime('%Y-%m-%d')
            # Last label
            if len(data) - 1 > 0:
                labels[len(data) - 1] = data.index[-1].strftime('%Y-%m-%d')

        if step > 0:
            for i in range(1, num_labels - 1):
                idx = i * step
                if 0 < idx < len(data):
                    labels[idx] = data.index[idx].strftime('%m-%d')
        
        last_pos = 0
        sorted_indices = sorted(labels.keys())
        
        final_x_axis = Text(" " * (y_axis_offset))
        for idx in sorted_indices:
            label_text = labels[idx]
            position = idx
            if position > last_pos:
                final_x_axis.append(" " * (position - last_pos))
            final_x_axis.append(label_text, style="dim")
            last_pos = position + len(label_text)

        return final_x_axis 