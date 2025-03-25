
import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from src.utils import window_utils
import cv2




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

    @patch('src.utils.window_utils.get_game_window')
    @patch('src.utils.window_utils.pyautogui.screenshot')
    def test_capture_screenshot_success(self, mock_screenshot, mock_get_window):
        mock_window = MagicMock()
        mock_window.left = 50
        mock_window.top = 100
        mock_window.width = 640
        mock_window.height = 480
        mock_get_window.return_value = mock_window

        mock_image = MagicMock()
        mock_screenshot.return_value = mock_image

        game_name = "My Game"
        index = 2
        folder = "tests/screens"
        expected_path = os.path.join(folder, "screenshot_2.png")

        # Make sure the folder exists for testing
        os.makedirs(folder, exist_ok=True)

        result = window_utils.capture_screenshot(game_name, index, folder)

        mock_get_window.assert_called_once_with(game_name)
        mock_screenshot.assert_called_once_with(region=(50, 100, 640, 480))
        mock_image.save.assert_called_once_with(expected_path)
        self.assertEqual(result, expected_path)

    @patch('src.utils.window_utils.get_game_window', return_value=None)
    def test_capture_screenshot_no_window(self, mock_get_window):
        result = window_utils.capture_screenshot("Missing Game", 0, "tests/screens")
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


class TestVideoUtils(unittest.TestCase):

    def setUp(self):
        self.before_path = "tests/before.png"
        self.after_path = "tests/after.png"
        self.output_path = "tests/movement_result.png"

        os.makedirs("tests", exist_ok=True)

        # Create two dummy grayscale images with a shifted square
        before_img = np.zeros((100, 100), dtype=np.uint8)
        after_img = np.zeros((100, 100), dtype=np.uint8)
        cv2.rectangle(before_img, (20, 20), (40, 40), 255, -1)  # original square
        cv2.rectangle(after_img, (30, 30), (50, 50), 255, -1)   # moved square

        cv2.imwrite(self.before_path, before_img)
        cv2.imwrite(self.after_path, after_img)

    def tearDown(self):
        for f in [self.before_path, self.after_path, self.output_path]:
            if os.path.exists(f):
                os.remove(f)

    def test_detect_and_mark_movement(self):
        result_path = window_utils.detect_and_mark_movement(self.before_path, self.after_path, self.output_path)
        self.assertEqual(result_path, self.output_path)
        self.assertTrue(os.path.exists(self.output_path))

if __name__ == '__main__':
    unittest.main()
