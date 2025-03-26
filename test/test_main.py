
import unittest
from unittest.mock import patch
import asyncio
import os
import sys 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from src.main import generate_game_from_api

class TestMainAPI(unittest.TestCase):

    @patch("src.main.main")
    def test_generate_game_from_api_delegates_to_main(self, mock_main):
        asyncio.run(generate_game_from_api("create a shooter", 2))
        mock_main.assert_called_once_with("create a shooter", 2)
