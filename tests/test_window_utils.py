
import unittest
from unittest.mock import patch, MagicMock
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from src.utils import window_utils



class TestWindowUtils(unittest.TestCase):

    @patch('src.utils.window_utils.gw.getWindowsWithTitle')
    def test_get_game_window_found(self, mock_get_windows):
        mock_window = MagicMock()
        mock_get_windows.return_value = [mock_window]

        result = window_utils.get_game_window("Test Game")
        self.assertEqual(result, mock_window)

    @patch('src.utils.window_utils.gw.getWindowsWithTitle')
    def test_get_game_window_not_found(self, mock_get_windows):
        mock_get_windows.return_value = []

        result = window_utils.get_game_window("Nonexistent Game")
        self.assertIsNone(result)

    def test_delete_screenshot_existing_file(self):
        path = "tests/temp_screenshot.png"
        with open(path, "w") as f:
            f.write("dummy")
        self.assertTrue(os.path.exists(path))

        window_utils.delete_screenshot(path)
        self.assertFalse(os.path.exists(path))

    def test_delete_screenshot_nonexistent_file(self):
        with patch('src.utils.window_utils.logging') as mock_log:
            window_utils.delete_screenshot("nonexistent_file.png")
            mock_log.error.assert_called_once()

if __name__ == '__main__':
    unittest.main()
