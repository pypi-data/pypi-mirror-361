import unittest
import pandas as pd
from unittest.mock import patch
from terminal_stonks import KChart


class TestKChart(unittest.TestCase):
    def setUp(self):
        """Set up test data."""
        self.sample_data = pd.DataFrame({
            'Open': [100.0, 102.0, 101.0, 103.0],
            'High': [105.0, 106.0, 104.0, 107.0],
            'Low': [99.0, 101.0, 100.0, 102.0],
            'Close': [102.0, 101.0, 103.0, 105.0]
        }, index=pd.date_range('2024-01-01', periods=4, freq='D'))

    def test_init_with_valid_data(self):
        """Test initialization with valid DataFrame."""
        chart = KChart(self.sample_data)
        self.assertIsInstance(chart, KChart)
        self.assertTrue(chart.data.equals(self.sample_data))

    def test_init_with_invalid_index(self):
        """Test initialization with invalid index type."""
        invalid_data = pd.DataFrame({
            'Open': [100.0, 102.0],
            'High': [105.0, 106.0],
            'Low': [99.0, 101.0],
            'Close': [102.0, 101.0]
        })  # No DatetimeIndex
        
        with self.assertRaises(TypeError):
            KChart(invalid_data)

    @patch('terminal_stonks.k_chart.shutil.get_terminal_size')
    @patch('terminal_stonks.k_chart.Console')
    def test_render_basic(self, mock_console, mock_terminal_size):
        """Test basic render functionality."""
        mock_terminal_size.return_value = (80, 24)  # width, height
        
        chart = KChart(self.sample_data)
        chart.render("Test Chart")
        
        # Verify console methods were called
        mock_console.return_value.clear.assert_called_once()
        mock_console.return_value.print.assert_called()

    @patch('terminal_stonks.k_chart.shutil.get_terminal_size')
    @patch('terminal_stonks.k_chart.Console')
    def test_render_small_terminal(self, mock_console, mock_terminal_size):
        """Test render with very small terminal."""
        mock_terminal_size.return_value = (10, 5)  # very small
        
        chart = KChart(self.sample_data)
        chart.render()
        
        # Should handle small terminal gracefully
        mock_console.return_value.clear.assert_called_once()

    def test_scale_price(self):
        """Test price scaling function."""
        chart = KChart(self.sample_data)
        
        # Test price scaling
        max_price = 110.0
        price_per_row = 1.0
        chart_height = 20
        
        # Price at top should map to 0
        result = chart._scale_price(max_price, max_price, price_per_row, chart_height)
        self.assertEqual(result, 0)
        
        # Price at bottom should map to chart_height - 1
        result = chart._scale_price(90.0, max_price, price_per_row, chart_height)
        self.assertEqual(result, 19)  # chart_height - 1

    def test_empty_data(self):
        """Test with empty DataFrame."""
        empty_data = pd.DataFrame({
            'Open': [],
            'High': [],
            'Low': [],
            'Close': []
        }, index=pd.DatetimeIndex([]))
        
        # Should not raise an error
        chart = KChart(empty_data)
        self.assertIsInstance(chart, KChart)


if __name__ == '__main__':
    unittest.main() 