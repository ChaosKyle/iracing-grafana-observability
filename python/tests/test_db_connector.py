import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import logging
from datetime import datetime

# Add parent directory to path to import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.db_connector import PostgresConnector

# Disable logging during tests
logging.disable(logging.CRITICAL)

class TestPostgresConnector(unittest.TestCase):
    """Test cases for the PostgresConnector class"""
    
    @patch('psycopg2.connect')
    def setUp(self, mock_connect):
        """Set up the test environment"""
        self.mock_connect = mock_connect
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_conn.cursor.return_value.__enter__.return_value = self.mock_cursor
        self.mock_connect.return_value = self.mock_conn
        
        # Create test instance
        self.connector = PostgresConnector()
    
    def test_session_exists_true(self):
        """Test session_exists when a session exists"""
        self.mock_cursor.fetchone.return_value = (1,)
        result = self.connector.session_exists(12345)
        self.assertTrue(result)
        self.mock_cursor.execute.assert_called_once()
    
    def test_session_exists_false(self):
        """Test session_exists when a session doesn't exist"""
        self.mock_cursor.fetchone.return_value = None
        result = self.connector.session_exists(12345)
        self.assertFalse(result)
        self.mock_cursor.execute.assert_called_once()
    
    def test_upsert_track_existing(self):
        """Test upsert_track for an existing track"""
        self.mock_cursor.fetchone.return_value = (1,)
        track_data = {
            "iracing_id": 123,
            "name": "Test Track",
            "config": "Test Config",
            "length_km": 5.2,
            "corners": 12
        }
        result = self.connector.upsert_track(track_data)
        self.assertEqual(result, 1)
        self.assertEqual(self.mock_cursor.execute.call_count, 2)
        self.mock_conn.commit.assert_called_once()
    
    def test_upsert_track_new(self):
        """Test upsert_track for a new track"""
        self.mock_cursor.fetchone.side_effect = [None, (2,)]
        track_data = {
            "iracing_id": 123,
            "name": "Test Track",
            "config": "Test Config",
            "length_km": 5.2,
            "corners": 12
        }
        result = self.connector.upsert_track(track_data)
        self.assertEqual(result, 2)
        self.assertEqual(self.mock_cursor.execute.call_count, 2)
        self.mock_conn.commit.assert_called_once()
    
    def test_get_driver_id(self):
        """Test get_driver_id"""
        self.mock_cursor.fetchone.return_value = (5,)
        result = self.connector.get_driver_id(98765)
        self.assertEqual(result, 5)
        self.mock_cursor.execute.assert_called_once()

    def test_get_driver_id_none(self):
        """Test get_driver_id when driver doesn't exist"""
        self.mock_cursor.fetchone.return_value = None
        result = self.connector.get_driver_id(98765)
        self.assertIsNone(result)
        self.mock_cursor.execute.assert_called_once()

if __name__ == '__main__':
    unittest.main()