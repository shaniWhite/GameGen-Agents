
import unittest
from unittest.mock import patch, MagicMock
import subprocess

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

if __name__ == "__main__":
    unittest.main()
