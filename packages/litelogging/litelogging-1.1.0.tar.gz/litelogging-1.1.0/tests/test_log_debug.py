import unittest
from unittest.mock import patch
import sys
import io
import os
from lite_logging.lite_logging import log_debug, LOGGING_ENABLED, DEBUG_MODE

class TestLogDebug(unittest.TestCase):
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_debug_log_info(self, mock_stdout):
        log_debug("This is a debug info message", level="INFO")
        output = mock_stdout.getvalue()
        
        # Check if file and line info is present
        self.assertIn("-> File:", output)
        self.assertIn("Line:", output)
        
        # Check if message content is present
        self.assertIn("[INFO] This is a debug info message", output)
        self.assertIn("\033[92m", output)  # Green color
        
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_debug_log_warning(self, mock_stdout):
        log_debug("This is a debug warning", level="WARNING")
        output = mock_stdout.getvalue()
        
        self.assertIn("-> File:", output)
        self.assertIn("Line:", output)
        self.assertIn("[WARNING] This is a debug warning", output)
        self.assertIn("\033[93m", output)  # Yellow color
        
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_debug_log_error(self, mock_stdout):
        log_debug("This is a debug error", level="ERROR")
        output = mock_stdout.getvalue()
        
        self.assertIn("-> File:", output)
        self.assertIn("Line:", output)
        self.assertIn("[ERROR] This is a debug error", output)
        self.assertIn("\033[91m", output)  # Red color
        
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_debug_log_debug(self, mock_stdout):
        log_debug("This is a debug debug message", level="DEBUG")
        output = mock_stdout.getvalue()
        
        self.assertIn("-> File:", output)
        self.assertIn("Line:", output)
        self.assertIn("[DEBUG] This is a debug debug message", output)
        self.assertIn("\033[96m", output)  # Cyan color
        
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_debug_multiple_args(self, mock_stdout):
        log_debug("Status:", "OK", "Code:", 200, level="INFO")
        output = mock_stdout.getvalue()
        
        self.assertIn("-> File:", output)
        self.assertIn("Line:", output)
        self.assertIn("[INFO] Status: OK Code: 200", output)
        
    @patch('lite_logging.lite_logging.LOGGING_ENABLED', False)
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_debug_disabled_logging(self, mock_stdout):
        log_debug("This should not be logged", level="INFO")
        self.assertEqual("", mock_stdout.getvalue())
        
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_debug_invalid_level(self, mock_stdout):
        log_debug("Invalid level message", level="INVALID")
        self.assertEqual("", mock_stdout.getvalue())

if __name__ == '__main__':
    unittest.main()