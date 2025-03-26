
import unittest
import os
import sqlite3
from datetime import datetime
from src.utils import game_database  # adjust path if needed

class TestGameDatabase(unittest.TestCase):
    TEST_DB = "test_games.db"

    def setUp(self):
        # Override the DB_FILE for tests
        game_database.DB_FILE = self.TEST_DB
        game_database.init_db()

    def tearDown(self):
        if os.path.exists(self.TEST_DB):
            os.remove(self.TEST_DB)

    def test_init_db_creates_table(self):
        conn = sqlite3.connect(self.TEST_DB)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='games'")
        table_exists = c.fetchone()
        conn.close()
        self.assertIsNotNone(table_exists)

    def test_save_game_inserts_record(self):
        game_database.save_game("Test Game")

        conn = sqlite3.connect(self.TEST_DB)
        c = conn.cursor()
        c.execute("SELECT game_name, created_at FROM games WHERE game_name=?", ("Test Game",))
        row = c.fetchone()
        conn.close()

        self.assertIsNotNone(row)
        self.assertEqual(row[0], "Test Game")
        self.assertTrue(datetime.fromisoformat(row[1]))  # check ISO format

    def test_save_game_replaces_existing(self):
        game_database.save_game("Same Game")
        conn = sqlite3.connect(self.TEST_DB)
        c = conn.cursor()
        c.execute("SELECT created_at FROM games WHERE game_name='Same Game'")
        first_timestamp = c.fetchone()[0]
        conn.close()

        # Save again with same name
        game_database.save_game("Same Game")
        conn = sqlite3.connect(self.TEST_DB)
        c = conn.cursor()
        c.execute("SELECT created_at FROM games WHERE game_name='Same Game'")
        second_timestamp = c.fetchone()[0]
        conn.close()

        self.assertNotEqual(first_timestamp, second_timestamp)

