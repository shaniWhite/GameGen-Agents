
import unittest
from unittest.mock import mock_open, patch
from src.utils import file_utils

class TestFileUtils(unittest.TestCase):

    def test_parse_file_structure(self):
        xml = """
        <game>
            <game_name>Space Invaders</game_name>
            <window_size width="800" height="600" />
            <structure>
                <file>
                    <name>main.py</name>
                    <description>Main game loop</description>
                </file>
                <file>
                    <name>enemy.py</name>
                    <description>Enemy logic</description>
                </file>
            </structure>
            <actions>
                <action>Move left, key name: 'left arrow'</action>
                <action>Jump, key name: "space bar"</action>
            </actions>
        </game>
        """
        name, size, files, actions = file_utils.parse_file_structure(xml)
        
        self.assertEqual(name, "Space Invaders")
        self.assertEqual(size, (800, 600))
        self.assertEqual(len(files), 2)
        self.assertIn(("main.py", "Main game loop"), files)

        expected_actions = [
            ("Move left, key name: 'left arrow'", "left arrow"),
            ("Jump, key name: \"space bar\"", "space bar"),
        ]
        self.assertEqual(actions, expected_actions)


    def test_insert_message_separator(self):
        messages = [
            {"role": "user", "content": "First"},
            {"role": "user", "content": "Second"},
            {"role": "assistant", "content": "Reply"},
        ]
        result = file_utils.insert_message_separator(messages)
        self.assertEqual(len(result), 4)
        self.assertEqual(result[1], {"role": "assistant", "content": "--- Next Message ---"})

    @patch("builtins.open", new_callable=mock_open, read_data="game plan data")
    def test_load_game_plan_success(self, mock_file):
        content = file_utils.load_game_plan()
        self.assertEqual(content, "game plan data")

    @patch("builtins.open", side_effect=FileNotFoundError)
    @patch("src.utils.file_utils.logging")
    def test_load_game_plan_file_not_found(self, mock_log, mock_open_fn):
        result = file_utils.load_game_plan()
        self.assertIsNone(result)
        mock_log.warning.assert_called_once()


    def test_normalize_action_key(self):
        test_cases = [
            ("left arrow", "left"),
            ("right arrow", "right"),
            ("space bar", "space"),
            ("up arrow", "up"),
            ("down arrow", "down"),
            ("enter", "enter"),
            ("A", "A"),  # Not in mapping
            ("LEFT ARROW", "left"),  # Case-insensitive
        ]

        for input_key, expected_output in test_cases:
            with self.subTest(input_key=input_key):
                self.assertEqual(file_utils.normalize_action_key(input_key), expected_output)

if __name__ == "__main__":
    unittest.main()
