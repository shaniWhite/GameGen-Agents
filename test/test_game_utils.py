
import unittest
from unittest.mock import patch, MagicMock
import subprocess
import asyncio
from src.utils import game_utils

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
        self.assertNotEqual(process.poll(), None)  # Process should be terminated

    def test_stop_game_does_nothing_if_already_stopped(self):
        process = subprocess.Popen(["python", "-c", "print('done')"])
        process.wait()  # Let it finish immediately

        # Should not raise or try to terminate again
        game_utils.stop_game(process)
        self.assertNotEqual(process.poll(), None)
        
    @patch("src.utils.game_utils.pyautogui")
    @patch("src.utils.game_utils.keyboard")
    def test_simulate_input_keyboard_keys(self, mock_keyboard, mock_pyautogui):
        game_utils.simulate_input("left")
        mock_pyautogui.keyDown.assert_called_with("left")
        mock_pyautogui.keyUp.assert_called_with("left")

        game_utils.simulate_input("space")
        mock_keyboard.press.assert_called_with("space")
        mock_keyboard.release.assert_called_with("space")

    @patch("src.utils.game_utils.pyautogui")
    def test_simulate_input_mouse_actions(self, mock_pyautogui):
        # Return width and height for screen size
        mock_pyautogui.size.return_value = (1920, 1080)

        game_utils.simulate_input("move mouse")
        mock_pyautogui.moveTo.assert_called_with(960, 540, duration=0.5)

        game_utils.simulate_input("double click")
        mock_pyautogui.doubleClick.assert_called_once()

        game_utils.simulate_input("right click")
        mock_pyautogui.rightClick.assert_called_once()

        game_utils.simulate_input("move mouse")
        mock_pyautogui.size.return_value = (1920, 1080)
        game_utils.simulate_input("move mouse")
        mock_pyautogui.moveTo.assert_called_with(960, 540, duration=0.5)

    @patch("src.utils.game_utils.logging")
    def test_simulate_input_unknown_action(self, mock_log):
        game_utils.simulate_input("fly")
        mock_log.error.assert_called_with("⚠ Unknown action: fly")
    

    def test_run_game_process_finishes_cleanly(self):
        asyncio.run(self._test_run_game_process_finishes_cleanly())

    @patch("src.utils.game_utils.subprocess.Popen")
    @patch("src.utils.game_utils.keyboard")
    async def _test_run_game_process_finishes_cleanly(self, mock_keyboard, mock_popen):
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

    @patch("src.utils.game_utils.subprocess.Popen")
    @patch("src.utils.game_utils.keyboard")
    async def _test_run_game_with_error_output(self, mock_keyboard, mock_popen):
        mock_process = MagicMock()
        mock_process.poll.side_effect = [None, None, 0]
        mock_process.communicate.return_value = ("", "Runtime Error Here")
        mock_process.returncode = 1
        mock_popen.return_value = mock_process

        result = await game_utils.run_game()
        self.assertIn("Runtime errors", result)


if __name__ == "__main__":
    unittest.main()
