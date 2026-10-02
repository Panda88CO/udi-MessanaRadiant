#!/usr/bin/env python3
"""
Unit tests for Messana API communication classes:
- messana_control (Messana_Info.py)
- messana_node (Messana_Node.py)
- messana_system (Messana_System.py)
"""

import unittest
from unittest.mock import MagicMock, patch

# Ensure mock helper is imported first to stub dependencies
import tests.mock_helper  # noqa: F401
from tests.mock_helper import create_mock_response, sample_messana_info
from Messana_Info import messana_control
from Messana_Node import messana_node
from Messana_System import messana_system


class TestMessanaControl(unittest.TestCase):
    """Test suite for messana_control base class in Messana_Info.py."""

    def setUp(self):
        self.ip = "192.168.1.100"
        self.api_key = "test_key_123"
        with patch.object(messana_control, "GET_system_data", return_value="Celsius"):
            self.control = messana_control(self.ip, self.api_key)

    @patch("requests.get")
    def test_get_system_data_success(self, mock_get):
        """Test GET_system_data successfully extracts value on 200 OK."""
        mock_get.return_value = create_mock_response(
            status_code=200,
            json_data={"tempUnit": "Celsius"},
        )
        result = self.control.GET_system_data("tempUnit")
        self.assertEqual(result, "Celsius")
        mock_get.assert_called_once_with(
            f"http://{self.ip}/api/system/tempUnit?apikey={self.api_key}"
        )

    @patch("requests.get")
    def test_get_system_data_nan_handling(self, mock_get):
        """Test GET_system_data converts NaN indicators (-32768, -3276.8) to None."""
        for nan_val in (-32768, -3276.8):
            mock_get.return_value = create_mock_response(
                status_code=200,
                json_data={"rawTemp": nan_val},
            )
            result = self.control.GET_system_data("rawTemp")
            self.assertIsNone(result)

    @patch("requests.get")
    def test_get_system_data_error_status(self, mock_get):
        """Test GET_system_data returns None when response status is not 200."""
        for code in (400, 404, 500):
            mock_get.return_value = create_mock_response(status_code=code)
            result = self.control.GET_system_data("status")
            self.assertIsNone(result)

    @patch("requests.get")
    def test_get_system_data_exception(self, mock_get):
        """Test GET_system_data returns None and catches connection exceptions."""
        mock_get.side_effect = Exception("Connection refused")
        result = self.control.GET_system_data("status")
        self.assertIsNone(result)

    @patch("requests.put")
    def test_put_system_data_success(self, mock_put):
        """Test PUT_system_data returns True on 200 OK."""
        mock_put.return_value = create_mock_response(status_code=200)
        result = self.control.PUT_system_data("status", 1)
        self.assertTrue(result)
        mock_put.assert_called_once_with(
            f"http://{self.ip}/api/system/status?apikey={self.api_key}",
            json={"value": 1},
        )

    @patch("requests.put")
    def test_put_system_data_failure(self, mock_put):
        """Test PUT_system_data handles non-200 responses."""
        mock_put.return_value = create_mock_response(status_code=500)
        result = self.control.PUT_system_data("status", 1)
        self.assertFalse(result)

    @patch("requests.get")
    def test_get_node_data_success(self, mock_get):
        """Test GET_node_data successfully retrieves node property value."""
        mock_get.return_value = create_mock_response(
            status_code=200,
            json_data={"airTemperature": 22.5},
        )
        result = self.control.GET_node_data("airTemperature", "zone", 1)
        self.assertEqual(result, 22.5)
        mock_get.assert_called_once_with(
            f"http://{self.ip}/api/zone/airTemperature/1?apikey={self.api_key}"
        )

    @patch("requests.get")
    def test_get_node_data_unsupported_or_nan(self, mock_get):
        """Test GET_node_data returns None for NaN values or '<Response [400]>'."""
        mock_get.return_value = create_mock_response(
            status_code=200,
            json_data={"airQuality": "<Response [400]>"},
        )
        result = self.control.GET_node_data("airQuality", "zone", 1)
        self.assertIsNone(result)

    @patch("requests.put")
    def test_put_node_data(self, mock_put):
        """Test PUT_node_data returns True on 200 and False on failure/error."""
        mock_put.return_value = create_mock_response(status_code=200)
        self.assertTrue(self.control.PUT_node_data("setpoint", 21.0, "zone", 1))

        mock_put.return_value = create_mock_response(status_code=500)
        self.assertFalse(self.control.PUT_node_data("setpoint", 21.0, "zone", 1))

        mock_put.side_effect = Exception("Network timeout")
        self.assertFalse(self.control.PUT_node_data("setpoint", 21.0, "zone", 1))

    @patch("requests.get")
    def test_system_connected(self, mock_get):
        """Test system_connected checks apiVersion endpoint."""
        mock_get.return_value = create_mock_response(status_code=200)
        self.assertTrue(self.control.system_connected())

        mock_get.return_value = create_mock_response(status_code=404)
        self.assertFalse(self.control.system_connected())


class TestMessanaNode(unittest.TestCase):
    """Test suite for messana_node in Messana_Node.py."""

    def setUp(self):
        self.info = sample_messana_info()
        with patch.object(messana_control, "GET_system_data", return_value="Celsius"), \
             patch.object(messana_control, "GET_node_data", return_value="Living Room"):
            self.node = messana_node(self.info, "zone", 1)

    @patch.object(messana_control, "GET_node_data")
    def test_get_voc_valid_and_unsupported(self, mock_get_node):
        """Test get_voc returns value when supported and -1 when unsupported or None."""
        # Valid VOC value
        mock_get_node.return_value = 150
        self.assertEqual(self.node.get_voc(), 150)
        mock_get_node.assert_called_with("voc", "zone", 1)

        # None -> -1
        mock_get_node.return_value = None
        self.assertEqual(self.node.get_voc(), -1)

        # "<Response [400]>" -> -1
        mock_get_node.return_value = "<Response [400]>"
        self.assertEqual(self.node.get_voc(), -1)

    @patch.object(messana_control, "GET_node_data")
    def test_get_co2_valid_and_unsupported(self, mock_get_node):
        """Test get_co2 returns value when supported and -1 when unsupported or None."""
        mock_get_node.return_value = 600
        self.assertEqual(self.node.get_co2(), 600)

        mock_get_node.return_value = None
        self.assertEqual(self.node.get_co2(), -1)

    @patch.object(messana_control, "GET_node_data")
    def test_get_alarm_on_handling(self, mock_get_node):
        """Test get_alarmOn logic checking secondary alarms array."""
        # Alarm is 0 -> returns 0 without checking alarms
        mock_get_node.return_value = 0
        self.assertEqual(self.node.get_alarmOn(), 0)

        # Alarm != 0, but alarms array is empty -> cleared to 0
        def side_effect(mKey, nType, nNbr):
            if mKey == "alarmOn":
                return 1
            if mKey == "alarms":
                return []
            return None

        mock_get_node.side_effect = side_effect
        self.assertEqual(self.node.get_alarmOn(), 0)

        # Alarm != 0, alarms array has error codes -> returns alarm
        def side_effect_active(mKey, nType, nNbr):
            if mKey == "alarmOn":
                return 1
            if mKey == "alarms":
                return ["ERR_FREEZE"]
            return None

        mock_get_node.side_effect = side_effect_active
        self.assertEqual(self.node.get_alarmOn(), 1)


class TestMessanaSystem(unittest.TestCase):
    """Test suite for messana_system in Messana_System.py."""

    @patch.object(messana_control, "GET_system_data")
    def test_system_initialization(self, mock_get_sys):
        """Test messana_system collects system properties on __init__."""
        data_map = {
            "tempUnit": "Celsius",
            "status": 1,
            "zoneCount": 4,
            "atuCount": 1,
            "bufferTankCount": 1,
            "energySourceCount": 1,
            "fancoilCount": 2,
            "HCgroupCount": 1,
            "macroZoneCount": 1,
            "dhwCount": 1,
            "name": "Main System",
        }
        mock_get_sys.side_effect = lambda key: data_map.get(key)

        info = sample_messana_info()
        sys_obj = messana_system(info)

        self.assertEqual(sys_obj.status, 1)
        self.assertEqual(sys_obj.temp_unit, "Celsius")
        self.assertEqual(sys_obj.nbr_zones, 4)
        self.assertEqual(sys_obj.nbr_atus, 1)
        self.assertEqual(sys_obj.name, "Main System")


if __name__ == "__main__":
    unittest.main()

