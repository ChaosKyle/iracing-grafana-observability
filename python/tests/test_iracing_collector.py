import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import logging
from datetime import datetime

# Add parent directory to path to import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from collectors.iracing_collector import iRacingCollector

# Disable logging during tests
logging.disable(logging.CRITICAL)

class TestiRacingCollector(unittest.TestCase):
    """Test cases for the iRacingCollector class"""
    
    @patch('collectors.iracing_collector.InfluxConnector')
    @patch('collectors.iracing_collector.PostgresConnector')
    @patch('os.getenv')
    def setUp(self, mock_getenv, mock_postgres, mock_influx):
        """Set up the test environment"""
        # Mock environment variables
        mock_getenv.side_effect = lambda key, default=None: {
            'IRACING_USERNAME': 'test_user',
            'IRACING_PASSWORD': 'test_pass'
        }.get(key, default)
        
        # Mock database connectors
        self.mock_postgres = mock_postgres.return_value
        self.mock_influx = mock_influx.return_value
        
        # Skip the actual pyracing client initialization
        with patch('collectors.iracing_collector.Client'):
            self.collector = iRacingCollector()
            self.collector.ir = MagicMock()
    
    @patch('collectors.iracing_collector.asyncio.run')
    def test_run_collection(self, mock_run):
        """Test the run_collection method"""
        # Configure mock to make main() return True
        mock_run.return_value = True
        
        # Call method
        result = self.collector.run_collection()
        
        # Verify result
        self.assertTrue(result)
        mock_run.assert_called_once()
    
    # Test async methods
    # These would typically use the unittest.IsolatedAsyncioTestCase in Python 3.8+
    # but for simplicity we'll just test the method signatures here
    
    def test_authenticate_method_exists(self):
        """Test that the authenticate method exists"""
        self.assertTrue(hasattr(self.collector, 'authenticate'))
        self.assertTrue(callable(self.collector.authenticate))
    
    def test_collect_career_stats_method_exists(self):
        """Test that the collect_career_stats method exists"""
        self.assertTrue(hasattr(self.collector, 'collect_career_stats'))
        self.assertTrue(callable(self.collector.collect_career_stats))
    
    def test_collect_recent_races_method_exists(self):
        """Test that the collect_recent_races method exists"""
        self.assertTrue(hasattr(self.collector, 'collect_recent_races'))
        self.assertTrue(callable(self.collector.collect_recent_races))
    
    def test_collect_telemetry_method_exists(self):
        """Test that the collect_telemetry method exists"""
        self.assertTrue(hasattr(self.collector, 'collect_telemetry'))
        self.assertTrue(callable(self.collector.collect_telemetry))

if __name__ == '__main__':
    unittest.main()