#!/usr/bin/env python3
"""
Unit tests for udiLib utility functions and temperature conversion routines.
"""

import unittest
from unittest.mock import MagicMock

# Import mock_helper first to stub udi_interface / requests if not installed
import tests.mock_helper  # noqa: F401
import udiLib
from udiLib import TEMP_C, TEMP_F


class DummyNodeOwner:
    """Mock container representing a node instance using udiLib functions."""

    def __init__(self, isy_temp_unit=TEMP_C, messana_temp_unit=TEMP_C):
        self.ISY_temp_unit = isy_temp_unit
        self.messana_temp_unit = messana_temp_unit
        self.node = MagicMock()
        self.n_queue = []

    # Bind methods from udiLib
    isy_value = udiLib.isy_value
    convert_temp_unit = udiLib.convert_temp_unit
    getValidName = udiLib.getValidName
    getValidAddress = udiLib.getValidAddress
    send_temp_to_isy = udiLib.send_temp_to_isy
    send_rel_temp_to_isy = udiLib.send_rel_temp_to_isy
    node_queue = udiLib.node_queue
    wait_for_node_done = udiLib.wait_for_node_done


class TestUdiLib(unittest.TestCase):
    """Test suite for udiLib utility methods."""

    def setUp(self):
        self.helper = DummyNodeOwner()

    def test_isy_value(self):
        """Test isy_value returns correct code for None, non-numbers, and valid numbers."""
        # None -> 99
        self.assertEqual(self.helper.isy_value(None), 99)
        # Non-numeric -> 98
        self.assertEqual(self.helper.isy_value("invalid"), 98)
        self.assertEqual(self.helper.isy_value([1, 2]), 98)
        self.assertEqual(self.helper.isy_value({"val": 1}), 98)
        # Numbers preserved
        self.assertEqual(self.helper.isy_value(0), 0)
        self.assertEqual(self.helper.isy_value(1), 1)
        self.assertEqual(self.helper.isy_value(21.5), 21.5)
        self.assertEqual(self.helper.isy_value(-5), -5)

    def test_convert_temp_unit(self):
        """Test convert_temp_unit parsing strings to TEMP_C or TEMP_F."""
        self.assertEqual(self.helper.convert_temp_unit("F"), TEMP_F)
        self.assertEqual(self.helper.convert_temp_unit("f"), TEMP_F)
        self.assertEqual(self.helper.convert_temp_unit("Fahrenheit"), TEMP_F)
        self.assertEqual(self.helper.convert_temp_unit("fahrenheit"), TEMP_F)
        self.assertEqual(self.helper.convert_temp_unit("C"), TEMP_C)
        self.assertEqual(self.helper.convert_temp_unit("c"), TEMP_C)
        self.assertEqual(self.helper.convert_temp_unit("Celsius"), TEMP_C)

    def test_get_valid_name(self):
        """Test getValidName sanitizes illegal characters."""
        self.assertEqual(self.helper.getValidName("Living Room!"), "Living Room")
        self.assertEqual(self.helper.getValidName("Zone #1 (Upstairs)"), "Zone 1 Upstairs")
        self.assertEqual(self.helper.getValidName("Zone_2-A"), "Zone_2A")

    def test_get_valid_address(self):
        """Test getValidAddress produces clean lowercase address <= 14 characters."""
        self.assertEqual(self.helper.getValidAddress("Zone 1 Main"), "zone1main")
        # Slices to 14 characters before regex cleaning
        self.assertEqual(self.helper.getValidAddress("Zone-Special#12"), "zonespecial1")
        long_name = "VeryLongZoneNameHere12345"
        addr = self.helper.getValidAddress(long_name)
        self.assertLessEqual(len(addr), 14)
        self.assertEqual(addr, "verylongzonena")

    def test_node_queue(self):
        """Test node_queue and wait_for_node_done handling."""
        self.helper.node_queue({"address": "testaddr"})
        self.assertEqual(self.helper.n_queue, ["testaddr"])
        self.helper.wait_for_node_done()
        self.assertEqual(self.helper.n_queue, [])

    def test_send_temp_to_isy_none(self):
        """Verify send_temp_to_isy handles None without crashing and returns False."""
        result = self.helper.send_temp_to_isy(None, "ST")
        self.assertFalse(result)
        self.helper.node.setDriver.assert_not_called()

    def test_send_temp_to_isy_c_to_c(self):
        """Test send_temp_to_isy with Celsius ISY and Celsius Messana."""
        owner = DummyNodeOwner(isy_temp_unit=TEMP_C, messana_temp_unit="Celsius")
        result = owner.send_temp_to_isy(21.46, "ST")
        self.assertTrue(result)
        owner.node.setDriver.assert_called_once_with("ST", 21.5, True, True, 4)

    def test_send_temp_to_isy_f_to_c(self):
        """Test send_temp_to_isy converting Messana F to ISY C."""
        owner = DummyNodeOwner(isy_temp_unit=TEMP_C, messana_temp_unit="Fahrenheit")
        # 68 F = 20.0 C
        result = owner.send_temp_to_isy(68.0, "ST")
        self.assertTrue(result)
        owner.node.setDriver.assert_called_once_with("ST", 20.0, True, True, 4)

    def test_send_temp_to_isy_c_to_f(self):
        """Test send_temp_to_isy converting Messana C to ISY F."""
        owner = DummyNodeOwner(isy_temp_unit=TEMP_F, messana_temp_unit="Celsius")
        # 20.0 C = 68.0 F
        result = owner.send_temp_to_isy(20.0, "ST")
        self.assertTrue(result)
        owner.node.setDriver.assert_called_once_with("ST", 68.0, True, True, 17)

    def test_send_temp_to_isy_f_to_f(self):
        """Test send_temp_to_isy with Fahrenheit ISY and Fahrenheit Messana."""
        owner = DummyNodeOwner(isy_temp_unit=TEMP_F, messana_temp_unit="Fahrenheit")
        result = owner.send_temp_to_isy(72.54, "ST")
        self.assertTrue(result)
        owner.node.setDriver.assert_called_once_with("ST", 72.5, True, True, 17)

    def test_send_temp_to_isy_invalid_unit(self):
        """Test send_temp_to_isy with invalid ISY temp unit returns False."""
        owner = DummyNodeOwner(isy_temp_unit=99, messana_temp_unit=TEMP_C)
        result = owner.send_temp_to_isy(21.0, "ST")
        self.assertFalse(result)
        owner.node.setDriver.assert_not_called()

    def test_send_rel_temp_to_isy_none(self):
        """Verify send_rel_temp_to_isy handles None without crashing and returns False."""
        result = self.helper.send_rel_temp_to_isy(None, "GV1")
        self.assertFalse(result)
        self.helper.node.setDriver.assert_not_called()

    def test_send_rel_temp_to_isy_conversions(self):
        """Test relative temperature offset calculations (differential, no 32 degree bias)."""
        # C to C
        owner_cc = DummyNodeOwner(isy_temp_unit=TEMP_C, messana_temp_unit="Celsius")
        self.assertTrue(owner_cc.send_rel_temp_to_isy(2.5, "GV1"))
        owner_cc.node.setDriver.assert_called_once_with("GV1", 2.5, True, True, 4)

        # Messana F to ISY C delta: 9 F diff = 5 C diff
        owner_fc = DummyNodeOwner(isy_temp_unit=TEMP_C, messana_temp_unit="Fahrenheit")
        self.assertTrue(owner_fc.send_rel_temp_to_isy(9.0, "GV1"))
        owner_fc.node.setDriver.assert_called_once_with("GV1", 5.0, True, True, 4)

        # Messana C to ISY F delta: 5 C diff = 9 F diff
        owner_cf = DummyNodeOwner(isy_temp_unit=TEMP_F, messana_temp_unit="Celsius")
        self.assertTrue(owner_cf.send_rel_temp_to_isy(5.0, "GV1"))
        owner_cf.node.setDriver.assert_called_once_with("GV1", 9.0, True, True, 17)

        # F to F
        owner_ff = DummyNodeOwner(isy_temp_unit=TEMP_F, messana_temp_unit="Fahrenheit")
        self.assertTrue(owner_ff.send_rel_temp_to_isy(3.5, "GV1"))
        owner_ff.node.setDriver.assert_called_once_with("GV1", 3.5, True, True, 17)


if __name__ == "__main__":
    unittest.main()
