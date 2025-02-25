import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import logging
from datetime import datetime

# Add parent directory to path to import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.influx_connector import InfluxConnector

# Disable logging during tests
logging.disable(logging.CRITICAL)

class TestInfluxConnector(unittest.TestCase):
    """Test cases for the InfluxConnector class"""
    
    @patch('influxdb_client.InfluxDBClient')
    @patch('os.getenv')
    def setUp(self, mock_getenv, mock_client):
        """Set up the test environment"""
        # Mock environment variables
        mock_getenv.side_effect = lambda key, default=None: {
            'INFLUXDB_URL': 'http://localhost:8086',
            'INFLUXDB_TOKEN': 'test_token',
            'INFLUXDB_ORG': 'test_org',
            'INFLUXDB_BUCKET': 'test_bucket'
        }.get(key, default)
        
        # Mock InfluxDB client
        self.mock_client = mock_client
        self.mock_write_api = MagicMock()
        self.mock_query_api = MagicMock()
        self.mock_client.return_value.write_api.return_value = self.mock_write_api
        self.mock_client.return_value.query_api.return_value = self.mock_query_api
        
        # Create test instance
        self.connector = InfluxConnector()
    
    def test_write_telemetry_points(self):
        """Test writing telemetry points to InfluxDB"""
        # Sample telemetry data
        telemetry_data = [
            {
                "timestamp": datetime(2025, 2, 1, 12, 0, 0),
                "lap": 1,
                "speed": 200.5,
                "rpm": 8500,
                "throttle": 0.75,
                "brake": 0.0,
                "gear": 4
            },
            {
                "timestamp": datetime(2025, 2, 1, 12, 0, 1),
                "lap": 1,
                "speed": 210.2,
                "rpm": 9000,
                "throttle": 1.0,
                "brake": 0.0,
                "gear": 5
            }
        ]
        
        # Call the method
        result = self.connector.write_telemetry_points(telemetry_data)
        
        # Verify result
        self.assertTrue(result)
        self.mock_write_api.write.assert_called_once()
        
        # Check that we passed the correct arguments
        args, kwargs = self.mock_write_api.write.call_args
        self.assertEqual(kwargs['bucket'], 'test_bucket')
        self.assertEqual(len(kwargs['record']), 2)  # Two points
    
    def test_query_recent_telemetry(self):
        """Test querying recent telemetry"""
        # Mock query result
        mock_table = MagicMock()
        mock_record1 = MagicMock()
        mock_record1.values = {'speed': 200.5, 'rpm': 8500}
        mock_record2 = MagicMock()
        mock_record2.values = {'speed': 210.2, 'rpm': 9000}
        mock_table.records = [mock_record1, mock_record2]
        
        self.mock_query_api.query.return_value = [mock_table]
        
        # Call the method
        result = self.connector.query_recent_telemetry(minutes=30)
        
        # Verify result
        self.assertEqual(len(result), 2)
        self.mock_query_api.query.assert_called_once()
        
        # Check that the data was processed correctly
        self.assertEqual(result[0], {'speed': 200.5, 'rpm': 8500})
        self.assertEqual(result[1], {'speed': 210.2, 'rpm': 9000})
    
    def test_query_lap_telemetry(self):
        """Test querying telemetry for a specific lap"""
        # Mock query result
        mock_table = MagicMock()
        mock_record1 = MagicMock()
        mock_record1.values = {'speed': 200.5, 'rpm': 8500, 'lap': 3}
        mock_record2 = MagicMock()
        mock_record2.values = {'speed': 210.2, 'rpm': 9000, 'lap': 3}
        mock_table.records = [mock_record1, mock_record2]
        
        self.mock_query_api.query.return_value = [mock_table]
        
        # Call the method
        result = self.connector.query_lap_telemetry(lap_number=3)
        
        # Verify result
        self.assertEqual(len(result), 2)
        self.mock_query_api.query.assert_called_once()
        
        # Check that the data was processed correctly
        self.assertEqual(result[0], {'speed': 200.5, 'rpm': 8500, 'lap': 3})
        self.assertEqual(result[1], {'speed': 210.2, 'rpm': 9000, 'lap': 3})

if __name__ == '__main__':
    unittest.main()