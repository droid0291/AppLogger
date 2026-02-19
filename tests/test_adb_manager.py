import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import subprocess

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.adb_manager import ADBManager

class TestADBManager(unittest.TestCase):
    @patch('subprocess.run')
    def test_get_connected_devices(self, mock_run):
        # Mock successful output
        mock_run.return_value.stdout = "List of devices attached\nserial1\tdevice\nserial2\tdevice\n"
        mock_run.return_value.returncode = 0
        
        manager = ADBManager()
        devices = manager.get_connected_devices()
        self.assertEqual(devices, ["serial1", "serial2"])

    @patch('subprocess.run')
    def test_run_command_failure(self, mock_run):
        # Mock failure
        mock_run.side_effect = subprocess.CalledProcessError(1, ["adb", "test"], stderr="error")
        
        manager = ADBManager()
        result = manager.run_command(["test"])
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
