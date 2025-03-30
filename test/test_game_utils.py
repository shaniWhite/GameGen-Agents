import unittest
from unittest.mock import patch, MagicMock
import subprocess
import asyncio
import platform
from src.utils import game_utils
import os

class TestGameUtils(unittest.TestCase):

    @patch("subprocess.Popen")
    def test_start_game_returns_process(self, mock_popen):
        mock_process = MagicMock()
        mock_popen.return_value = mock_process

        process = game_utils.start_game()
        self.assertEqual(process, mock_process)
        mock_popen.assert_called_once_with([game_utils.sys.executable, "game/main.py"])

    def test_stop_game_kills_active_process(self):
        process = subprocess.Popen(["python", "-c", "import time; time.sleep(5)"])
        game_utils.stop_game(process)
        self.assertNotEqual(process.poll(), None)

    def test_stop_game_does_nothing_if_already_stopped(self):
        process = subprocess.Popen(["python", "-c", "print('done')"])
        process.wait()
        game_utils.stop_game(process)
        self.assertNotEqual(process.poll(), None)

    @unittest.skipIf(
        platform.system() != "Windows" or os.environ.get("CI") == "true",
        "Skipping GUI-dependent test in CI or on non-Windows"
    )
    @patch("pyautogui.keyDown")
    @patch("pyautogui.keyUp")
    @patch("keyboard.press")
    @patch("keyboard.release")
    def test_simulate_input_keyboard_keys(self, mock_release, mock_press, mock_keyup, mock_keydown):
        game_utils.simulate_input("left")
        mock_keydown.assert_called_with("left")
        mock_keyup.assert_called_with("left")

        game_utils.simulate_input("space")
        mock_press.assert_called_with("space")
        mock_release.assert_called_with("space")

    @unittest.skipIf(
        platform.system() != "Windows" or os.environ.get("CI") == "true",
        "Skipping GUI-dependent test in CI or on non-Windows"
    )
    @patch("pyautogui.size", return_value=(1920, 1080))
    @patch("pyautogui.moveTo")
    @patch("pyautogui.doubleClick")
    @patch("pyautogui.rightClick")
    def test_simulate_input_mouse_actions(self, mock_right_click, mock_double_click, mock_move_to, mock_size):
        game_utils.simulate_input("move mouse")
        mock_move_to.assert_called_with(960, 540, duration=0.5)

        game_utils.simulate_input("double click")
        mock_double_click.assert_called_once()

        game_utils.simulate_input("right click")
        mock_right_click.assert_called_once()

        game_utils.simulate_input("move mouse")
        mock_move_to.assert_called_with(960, 540, duration=0.5)
        
    @unittest.skipIf(
    platform.system() != "Windows" or os.environ.get("CI") == "true",
    "Skipped GUI-related test in CI or on non-Windows"
    )

    @patch("logging.error")
    def test_simulate_input_unknown_action(self, mock_log):
        game_utils.simulate_input("fly")
        mock_log.assert_called_with("⚠ Unknown action: fly")

    def test_run_game_process_finishes_cleanly(self):
        asyncio.run(self._test_run_game_process_finishes_cleanly())

    @patch("subprocess.Popen")
    @patch("keyboard.press")
    @patch("keyboard.release")
    async def _test_run_game_process_finishes_cleanly(self, mock_release, mock_press, mock_popen):
        mock_process = MagicMock()
        mock_process.poll.side_effect = [None, None, 0]
        mock_process.communicate.return_value = ("Game output", "")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        result = await game_utils.run_game()
        self.assertIsNone(result)
        mock_popen.assert_called()

    def test_run_game_with_error_output(self):
        asyncio.run(self._test_run_game_with_error_output())

    @patch("subprocess.Popen")
    @patch("keyboard.press")
    @patch("keyboard.release")
    async def _test_run_game_with_error_output(self, mock_release, mock_press, mock_popen):
        mock_process = MagicMock()
        mock_process.poll.side_effect = [None, None, 0]
        mock_process.communicate.return_value = ("", "Runtime Error Here")
        mock_process.returncode = 1
        mock_popen.return_value = mock_process

        result = await game_utils.run_game()
        self.assertIn("Runtime errors", result)

if __name__ == "__main__":
    unittest.main()
