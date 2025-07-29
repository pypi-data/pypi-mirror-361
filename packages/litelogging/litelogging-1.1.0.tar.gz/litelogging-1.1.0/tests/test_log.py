import unittest
from unittest.mock import patch
import sys
import io
from lite_logging.lite_logging import log, LOGGING_ENABLED, DEBUG_MODE, LOG_LEVEL

class TestLog(unittest.TestCase):
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_info_log(self, mock_stdout):
        log("This is an info message", level="INFO")
        self.assertIn("[INFO] This is an info message", mock_stdout.getvalue())
        self.assertIn("\033[92m", mock_stdout.getvalue())  # Green color
        
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_warning_log(self, mock_stdout):
        log("This is a warning", level="WARNING")
        self.assertIn("[WARNING] This is a warning", mock_stdout.getvalue())
        self.assertIn("\033[93m", mock_stdout.getvalue())  # Yellow color
        
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_error_log(self, mock_stdout):
        log("This is an error", level="ERROR")
        self.assertIn("[ERROR] This is an error", mock_stdout.getvalue())
        self.assertIn("\033[91m", mock_stdout.getvalue())  # Red color
        
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_debug_log(self, mock_stdout):
        log("This is a debug message", level="DEBUG")
        self.assertIn("[DEBUG] This is a debug message", mock_stdout.getvalue())
        self.assertIn("\033[96m", mock_stdout.getvalue())  # Cyan color
        
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_multiple_args(self, mock_stdout):
        log("Value:", 42, "Status:", True, level="INFO")
        self.assertIn("[INFO] Value: 42 Status: True", mock_stdout.getvalue())
        
    @patch('lite_logging.lite_logging.LOGGING_ENABLED', False)
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_disabled_logging(self, mock_stdout):
        log("This should not be logged", level="INFO")
        self.assertEqual("", mock_stdout.getvalue())
        
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_invalid_level(self, mock_stdout):
        log("Invalid level message", level="INVALID")
        self.assertEqual("", mock_stdout.getvalue())

if __name__ == '__main__':
    unittest.main()