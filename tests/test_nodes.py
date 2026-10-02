#!/usr/bin/env python3
"""
Unit tests for all ISY/IoX Node classes in udi-MessanaRadiant:
- udi_messana_zone (VOC, TIME updates, offline handling)
- udi_messana_macrozone
- udi_messana_atu
- udi_messana_buffertank
- udi_messana_hc_co
- udi_messana_fancoil
- udi_messana_energy_source
- udi_messana_hot_water
- MessanaController

Verifies that:
1. Valid API responses update node drivers and record a Unix timestamp on TIME (UOM 151).
2. API errors or None data set running status (GV2 or ST) to 0 and do NOT update TIME.
3. Zone VOC Level driver (GV7) uses UOM 96 when valid, or 98/25 when unsupported.
"""

import unittest
from unittest.mock import MagicMock, patch

import tests.mock_helper  # noqa: F401
from tests.mock_helper import create_mock_polyglot, sample_messana_info
from udi_MessanaZone import udi_messana_zone
from udi_MessanaMacrozone import udi_messana_macrozone
from udi_MessanaATU import udi_messana_atu
from udi_MessanaBuffertank import udi_messana_buffertank
from udi_MessanaHCCO import udi_messana_hc_co
from udi_MessanaFancoil import udi_messana_fancoil
from udi_MessanaEnergySource import udi_messana_energy_source
from udi_MessanaHotWater import udi_messana_hot_water
from udi_MessanaController import MessanaController


class TestZoneNode(unittest.TestCase):
    """Test suite for udi_messana_zone."""

    def setUp(self):
        self.poly = create_mock_polyglot()
        self.info = sample_messana_info(temp_unit=0)

        # Mock the underlying messana_zone
        self.mock_zone_api = MagicMock()
        self.mock_zone_api.messana_temp_unit = "Celsius"
        self.mock_zone_api.get_name.return_value = "Living Room"

        with patch("udi_MessanaZone.messana_zone", return_value=self.mock_zone_api):
            self.zone_node = udi_messana_zone(
                self.poly,
                primary="controller",
                address="zone1",
                name="Living Room",
                zone_nbr=0,
                messana_info=self.info,
            )

    def test_shortpoll_success_updates_time_and_running(self):
        """Shortpoll with valid data sets GV2=1 and updates TIME (uom=151)."""
        self.mock_zone_api.get_status.return_value = 1
        self.mock_zone_api.get_air_temp.return_value = 21.5
        self.mock_zone_api.get_humidity.return_value = 45.0
        self.mock_zone_api.get_dewpoint.return_value = 10.0
        self.mock_zone_api.get_air_quality.return_value = 50
        self.mock_zone_api.get_alarmOn.return_value = 0

        self.zone_node.updateISY_shortpoll()

        self.assertEqual(self.zone_node.node.getDriver("GV2"), 1)
        time_driver = self.zone_node.node.drivers_values.get("TIME")
        self.assertIsNotNone(time_driver)
        self.assertGreater(time_driver["value"], 0)
        self.assertEqual(time_driver["uom"], 151)
        self.assertEqual(self.zone_node.node.getDriver("ST"), 21.5)
        self.assertEqual(self.zone_node.node.getDriver("CLIHUM"), 45.0)

    def test_shortpoll_api_error_leaves_time_untouched(self):
        """Shortpoll with None data sets GV2=0 and does NOT update TIME."""
        # Pre-set a known TIME value
        self.zone_node.node.setDriver("TIME", 1234567, True, True, 151)

        self.mock_zone_api.get_status.return_value = None
        self.mock_zone_api.get_air_temp.return_value = None
        self.mock_zone_api.get_humidity.return_value = None
        self.mock_zone_api.get_dewpoint.return_value = None
        self.mock_zone_api.get_air_quality.return_value = None
        self.mock_zone_api.get_alarmOn.return_value = None

        self.zone_node.updateISY_shortpoll()

        self.assertEqual(self.zone_node.node.getDriver("GV2"), 0)
        self.assertEqual(self.zone_node.node.getDriver("TIME"), 1234567)

    def test_longpoll_success_with_voc(self):
        """Longpoll with valid VOC updates GV7 with UOM 96 and sets TIME."""
        self.mock_zone_api.get_status.return_value = 1
        self.mock_zone_api.get_thermal_status.return_value = 2
        self.mock_zone_api.get_setpoint.return_value = 22.0
        self.mock_zone_api.get_air_temp.return_value = 21.0
        self.mock_zone_api.get_humidity.return_value = 40.0
        self.mock_zone_api.get_dewpoint.return_value = 9.0
        self.mock_zone_api.get_energy_saving.return_value = 0
        self.mock_zone_api.get_alarmOn.return_value = 0
        self.mock_zone_api.get_temp.return_value = 21.2
        self.mock_zone_api.get_air_quality.return_value = 80
        self.mock_zone_api.get_co2.return_value = 450
        self.mock_zone_api.get_voc.return_value = 125

        self.zone_node.updateISY_longpoll()

        self.assertEqual(self.zone_node.node.getDriver("GV2"), 1)
        # Verify VOC driver GV7
        voc_driver = self.zone_node.node.drivers_values.get("GV7")
        self.assertIsNotNone(voc_driver)
        self.assertEqual(voc_driver["value"], 125)
        self.assertEqual(voc_driver["uom"], 96)

        # Verify TIME driver
        time_driver = self.zone_node.node.drivers_values.get("TIME")
        self.assertIsNotNone(time_driver)
        self.assertGreater(time_driver["value"], 0)
        self.assertEqual(time_driver["uom"], 151)

    def test_longpoll_voc_unsupported(self):
        """Longpoll with unsupported VOC (-1) sets GV7 to 98 with UOM 25."""
        self.mock_zone_api.get_status.return_value = 1
        self.mock_zone_api.get_thermal_status.return_value = 1
        self.mock_zone_api.get_setpoint.return_value = 20.0
        self.mock_zone_api.get_air_temp.return_value = 20.0
        self.mock_zone_api.get_humidity.return_value = 50.0
        self.mock_zone_api.get_dewpoint.return_value = 9.0
        self.mock_zone_api.get_energy_saving.return_value = 0
        self.mock_zone_api.get_alarmOn.return_value = 0
        self.mock_zone_api.get_temp.return_value = 20.0
        self.mock_zone_api.get_air_quality.return_value = -1
        self.mock_zone_api.get_co2.return_value = -1
        self.mock_zone_api.get_voc.return_value = -1  # unsupported

        self.zone_node.updateISY_longpoll()

        voc_driver = self.zone_node.node.drivers_values.get("GV7")
        self.assertIsNotNone(voc_driver)
        self.assertEqual(voc_driver["value"], 98)
        self.assertEqual(voc_driver["uom"], 25)

    def test_longpoll_api_error_leaves_time_untouched(self):
        """Longpoll with None data sets GV2=0 and does NOT update TIME."""
        self.zone_node.node.setDriver("TIME", 999999, True, True, 151)

        self.mock_zone_api.get_status.return_value = None
        self.mock_zone_api.get_thermal_status.return_value = None
        self.mock_zone_api.get_setpoint.return_value = None
        self.mock_zone_api.get_air_temp.return_value = None
        self.mock_zone_api.get_humidity.return_value = None
        self.mock_zone_api.get_dewpoint.return_value = None
        self.mock_zone_api.get_energy_saving.return_value = None
        self.mock_zone_api.get_alarmOn.return_value = None
        self.mock_zone_api.get_temp.return_value = None

        self.zone_node.updateISY_longpoll()

        self.assertEqual(self.zone_node.node.getDriver("GV2"), 0)
        self.assertEqual(self.zone_node.node.getDriver("TIME"), 999999)

    def test_command_handlers(self):
        """Test zone commands: STATUS, DON, DOF, ENERGYSAVE, SETPOINT, UPDATE."""
        self.mock_zone_api.set_status.return_value = 1
        self.zone_node.set_status({"value": 1})
        self.assertEqual(self.zone_node.node.getDriver("GV0"), 1)

        # DON
        self.mock_zone_api.set_status.return_value = 1
        self.zone_node.set_on({"cmd": "DON"})
        self.assertEqual(self.zone_node.node.getDriver("GV0"), 1)
        self.mock_zone_api.set_status.assert_called_with(1)

        # DOF
        self.mock_zone_api.set_status.return_value = 0
        self.zone_node.set_off({"cmd": "DOF"})
        self.assertEqual(self.zone_node.node.getDriver("GV0"), 0)
        self.mock_zone_api.set_status.assert_called_with(0)

        # Commands mapping
        self.assertEqual(self.zone_node.commands["DON"], udi_messana_zone.set_on)
        self.assertEqual(self.zone_node.commands["DOF"], udi_messana_zone.set_off)

        self.mock_zone_api.set_energy_saving.return_value = 1
        self.zone_node.set_energy_save({"value": 1})
        self.assertEqual(self.zone_node.node.getDriver("GV8"), 1)

        self.mock_zone_api.set_setpoint.return_value = 21.5
        self.zone_node.set_setpoint({"value": 21.5})
        self.assertEqual(self.zone_node.node.getDriver("GV3"), 21.5)

    def test_zone_node_with_filtered_supported_props(self):
        """Zone node created with supported_props omits unsupported drivers and does not poll them."""
        # Zone without air quality, CO2, VOC, humidity, dewpoint
        supported = {'ST', 'GV0', 'GV1', 'GV2', 'GV3', 'GV8', 'GV9', 'GV10', 'TIME'}
        mock_api = MagicMock()
        mock_api.messana_temp_unit = "Celsius"
        mock_api.get_name.return_value = "Basic Room"

        with patch("udi_MessanaZone.messana_zone", return_value=mock_api):
            filtered_zone = udi_messana_zone(
                self.poly,
                primary="controller",
                address="zone2",
                name="Basic Room",
                zone_nbr=2,
                messana_info=self.info,
                supported_props=supported,
            )

        # Dynamic Node ID conforms to ZONE<nbr>
        self.assertEqual(filtered_zone.id, "ZONE2")

        # Unsupported drivers are omitted from drivers list
        driver_names = [d["driver"] for d in filtered_zone.drivers]
        self.assertNotIn("GV6", driver_names)
        self.assertNotIn("CO2LVL", driver_names)
        self.assertNotIn("GV7", driver_names)
        self.assertNotIn("CLIHUM", driver_names)
        self.assertNotIn("DEWPT", driver_names)
        self.assertIn("ST", driver_names)
        self.assertIn("GV0", driver_names)
        self.assertIn("GV3", driver_names)
        self.assertIn("GV10", driver_names)
        self.assertEqual(len(filtered_zone.drivers), 9)

        # Shortpoll: unsupported sensors are NOT polled
        mock_api.get_status.return_value = 1
        mock_api.get_air_temp.return_value = 22.0
        mock_api.get_alarmOn.return_value = 0
        filtered_zone.updateISY_shortpoll()

        mock_api.get_humidity.assert_not_called()
        mock_api.get_dewpoint.assert_not_called()
        mock_api.get_air_quality.assert_not_called()
        self.assertNotIn("GV6", filtered_zone.node.drivers_values)
        self.assertNotIn("CLIHUM", filtered_zone.node.drivers_values)

        # Longpoll: unsupported sensors are NOT polled and NO 98 is set
        mock_api.get_status.return_value = 1
        mock_api.get_thermal_status.return_value = 1
        mock_api.get_setpoint.return_value = 21.0
        mock_api.get_air_temp.return_value = 22.0
        mock_api.get_energy_saving.return_value = 0
        mock_api.get_alarmOn.return_value = 0
        mock_api.get_temp.return_value = 22.5
        filtered_zone.updateISY_longpoll()

        mock_api.get_humidity.assert_not_called()
        mock_api.get_dewpoint.assert_not_called()
        mock_api.get_air_quality.assert_not_called()
        mock_api.get_co2.assert_not_called()
        mock_api.get_voc.assert_not_called()
        self.assertNotIn("GV6", filtered_zone.node.drivers_values)
        self.assertNotIn("CO2LVL", filtered_zone.node.drivers_values)
        self.assertNotIn("GV7", filtered_zone.node.drivers_values)
        self.assertEqual(filtered_zone.node.getDriver("GV2"), 1)


class TestMacrozoneNode(unittest.TestCase):
    """Test suite for udi_messana_macrozone."""

    def setUp(self):
        self.poly = create_mock_polyglot()
        self.info = sample_messana_info()
        self.mock_macro_api = MagicMock()
        self.mock_macro_api.messana_temp_unit = "Celsius"
        self.mock_macro_api.get_name.return_value = "Macro 1"

        with patch("udi_MessanaMacrozone.messana_macrozone", return_value=self.mock_macro_api):
            self.macro_node = udi_messana_macrozone(
                self.poly,
                primary="controller",
                address="macro1",
                name="Macro 1",
                macrozone_nbr=0,
                messana_info=self.info,
            )

    def test_macrozone_poll_success_and_failure(self):
        """Verify macrozone updates GV2/TIME on success and GV2=0/untouched on failure."""
        # Success
        self.mock_macro_api.get_status.return_value = 1
        self.mock_macro_api.get_temp.return_value = 21.0
        self.mock_macro_api.get_humidity.return_value = 50.0
        self.mock_macro_api.get_dewpoint.return_value = 10.0
        self.macro_node.updateISY_shortpoll()
        self.assertEqual(self.macro_node.node.getDriver("GV2"), 1)
        self.assertGreater(self.macro_node.node.getDriver("TIME"), 0)

        # Failure
        self.macro_node.node.setDriver("TIME", 88888, True, True, 151)
        self.mock_macro_api.get_status.return_value = None
        self.mock_macro_api.get_temp.return_value = None
        self.mock_macro_api.get_humidity.return_value = None
        self.mock_macro_api.get_dewpoint.return_value = None
        self.macro_node.updateISY_shortpoll()
        self.assertEqual(self.macro_node.node.getDriver("GV2"), 0)
        self.assertEqual(self.macro_node.node.getDriver("TIME"), 88888)

    def test_macrozone_command_handlers(self):
        """Test macrozone commands: DON, DOF, STATUS."""
        self.mock_macro_api.set_status.return_value = 1
        self.macro_node.set_on({"cmd": "DON"})
        self.assertEqual(self.macro_node.node.getDriver("GV0"), 1)
        self.mock_macro_api.set_status.assert_called_with(1)

        self.mock_macro_api.set_status.return_value = 0
        self.macro_node.set_off({"cmd": "DOF"})
        self.assertEqual(self.macro_node.node.getDriver("GV0"), 0)
        self.mock_macro_api.set_status.assert_called_with(0)

        self.assertEqual(self.macro_node.commands["DON"], udi_messana_macrozone.set_on)
        self.assertEqual(self.macro_node.commands["DOF"], udi_messana_macrozone.set_off)


class TestOtherSubsystemNodes(unittest.TestCase):
    """Test suite for ATU, Buffer Tank, HCCO, Fan Coil, Energy Source, Hot Water."""

    def setUp(self):
        self.poly = create_mock_polyglot()
        self.info = sample_messana_info()

    def test_atu_time_and_running_status(self):
        """ATU updates ST=1 and TIME on success, ST=0 and untouched TIME on failure."""
        mock_atu = MagicMock()
        mock_atu.messana_temp_unit = "Celsius"
        mock_atu.get_name.return_value = "ATU 1"

        with patch("udi_MessanaATU.messana_atu", return_value=mock_atu):
            node = udi_messana_atu(self.poly, "controller", "atu1", "ATU 1", 0, self.info)

        # Success
        mock_atu.get_status.return_value = 1
        mock_atu.get_air_temp.return_value = 20.0
        mock_atu.get_flow_level.return_value = 150
        mock_atu.get_HRV_status.return_value = 1
        mock_atu.get_humidification_status.return_value = 0
        mock_atu.get_dehumidification_status.return_value = 0
        mock_atu.get_convection_status.return_value = 0
        mock_atu.get_alarmOn.return_value = 0
        node.updateISY_shortpoll()
        self.assertEqual(node.node.getDriver("ST"), 1)
        self.assertGreater(node.node.getDriver("TIME"), 0)

        # Failure
        node.node.setDriver("TIME", 11111, True, True, 151)
        mock_atu.get_status.return_value = None
        mock_atu.get_air_temp.return_value = None
        mock_atu.get_flow_level.return_value = None
        mock_atu.get_HRV_status.return_value = None
        mock_atu.get_humidification_status.return_value = None
        mock_atu.get_dehumidification_status.return_value = None
        mock_atu.get_convection_status.return_value = None
        mock_atu.get_alarmOn.return_value = None
        node.updateISY_shortpoll()
        self.assertEqual(node.node.getDriver("ST"), 0)
        self.assertEqual(node.node.getDriver("TIME"), 11111)

    def test_buffertank_time_and_running_status(self):
        """Buffer Tank updates ST=1 and TIME on success, ST=0 on failure."""
        mock_bt = MagicMock()
        mock_bt.messana_temp_unit = "Celsius"
        mock_bt.get_name.return_value = "BT 1"

        with patch("udi_MessanaBuffertank.messana_buffertank", return_value=mock_bt):
            node = udi_messana_buffertank(self.poly, "controller", "bt1", "BT 1", 0, self.info)

        # Success
        mock_bt.get_status.return_value = 1
        mock_bt.get_temp.return_value = 45.0
        mock_bt.get_buffertank_mode.return_value = 1
        mock_bt.get_buffertank_temp_mode.return_value = 0
        mock_bt.get_alarmOn.return_value = 0
        node.updateISY_shortpoll()
        self.assertEqual(node.node.getDriver("ST"), 1)
        self.assertGreater(node.node.getDriver("TIME"), 0)

        # Failure
        node.node.setDriver("TIME", 22222, True, True, 151)
        mock_bt.get_status.return_value = None
        mock_bt.get_temp.return_value = None
        mock_bt.get_buffertank_mode.return_value = None
        mock_bt.get_buffertank_temp_mode.return_value = None
        mock_bt.get_alarmOn.return_value = None
        node.updateISY_shortpoll()
        self.assertEqual(node.node.getDriver("ST"), 0)
        self.assertEqual(node.node.getDriver("TIME"), 22222)

    def test_hcco_time_and_running_status(self):
        """HCCO updates ST=1 and TIME on success, ST=0 on failure."""
        mock_hc = MagicMock()
        mock_hc.get_name.return_value = "HC 1"

        with patch("udi_MessanaHCCO.messana_hc_co", return_value=mock_hc):
            node = udi_messana_hc_co(self.poly, "controller", "hc1", "HC 1", 0, self.info)

        # Success
        mock_hc.get_status.return_value = 1
        mock_hc.get_adaptive_comf_status.return_value = 1
        mock_hc.get_hc_co_mode.return_value = 2
        mock_hc.get_hc_co_season_mode.return_value = 0
        node.updateISY_shortpoll()
        self.assertEqual(node.node.getDriver("ST"), 1)
        self.assertGreater(node.node.getDriver("TIME"), 0)

        # Failure
        node.node.setDriver("TIME", 33333, True, True, 151)
        mock_hc.get_status.return_value = None
        mock_hc.get_adaptive_comf_status.return_value = None
        mock_hc.get_hc_co_mode.return_value = None
        mock_hc.get_hc_co_season_mode.return_value = None
        node.updateISY_shortpoll()
        self.assertEqual(node.node.getDriver("ST"), 0)
        self.assertEqual(node.node.getDriver("TIME"), 33333)

    def test_fancoil_time_and_running_status(self):
        """Fan Coil updates ST=1 and TIME on success, ST=0 on failure."""
        mock_fc = MagicMock()
        mock_fc.get_name.return_value = "FC 1"
        del mock_fc.get_cool_speed
        del mock_fc.get_heat_speed

        with patch("udi_MessanaFancoil.messana_fancoil", return_value=mock_fc):
            node = udi_messana_fancoil(self.poly, "controller", "fc1", "FC 1", 0, self.info)

        # Success
        mock_fc.get_status.return_value = 1
        mock_fc.get_fancoil_cool_speed.return_value = 200
        mock_fc.get_fancoil_heat_speed.return_value = 200
        mock_fc.get_fctype.return_value = 1
        mock_fc.get_alarmOn.return_value = 0
        node.updateISY_shortpoll()
        self.assertEqual(node.node.getDriver("ST"), 1)
        self.assertGreater(node.node.getDriver("TIME"), 0)

        # Failure
        node.node.setDriver("TIME", 44444, True, True, 151)
        mock_fc.get_status.return_value = None
        mock_fc.get_fancoil_cool_speed.return_value = None
        mock_fc.get_fancoil_heat_speed.return_value = None
        mock_fc.get_fctype.return_value = None
        mock_fc.get_alarmOn.return_value = None
        node.updateISY_shortpoll()
        self.assertEqual(node.node.getDriver("ST"), 0)
        self.assertEqual(node.node.getDriver("TIME"), 44444)

    def test_energy_source_time_and_running_status(self):
        """Energy Source updates ST=1 and TIME on success, ST=0 on failure."""
        mock_es = MagicMock()
        mock_es.get_name.return_value = "ES 1"

        with patch("udi_MessanaEnergySource.messana_energy_source", return_value=mock_es):
            node = udi_messana_energy_source(self.poly, "controller", "es1", "ES 1", 0, self.info)

        # Success
        mock_es.get_status.return_value = 1
        mock_es.get_energy_source_dhwStatus.return_value = 1
        mock_es.get_energy_source_type.return_value = 2
        mock_es.get_alarmOn.return_value = 0
        node.updateISY_shortpoll()
        self.assertEqual(node.node.getDriver("ST"), 1)
        self.assertGreater(node.node.getDriver("TIME"), 0)

        # Failure
        node.node.setDriver("TIME", 55555, True, True, 151)
        mock_es.get_status.return_value = None
        mock_es.get_energy_source_dhwStatus.return_value = None
        mock_es.get_energy_source_type.return_value = None
        mock_es.get_alarmOn.return_value = None
        node.updateISY_shortpoll()
        self.assertEqual(node.node.getDriver("ST"), 0)
        self.assertEqual(node.node.getDriver("TIME"), 55555)

    def test_hotwater_time_and_running_status(self):
        """Hot Water updates ST=1 and TIME on success, ST=0 on failure."""
        mock_hw = MagicMock()
        mock_hw.messana_temp_unit = "Celsius"
        mock_hw.get_name.return_value = "DHW 1"

        with patch("udi_MessanaHotWater.messana_hot_water", return_value=mock_hw):
            node = udi_messana_hot_water(self.poly, "controller", "dhw1", "DHW 1", 0, self.info)

        # Success
        mock_hw.get_status.return_value = 1
        mock_hw.get_temp.return_value = 55.0
        mock_hw.get_target_temp.return_value = 60.0
        node.updateISY_shortpoll()
        self.assertEqual(node.node.getDriver("ST"), 1)
        self.assertGreater(node.node.getDriver("TIME"), 0)

        # Failure
        node.node.setDriver("TIME", 66666, True, True, 151)
        mock_hw.get_status.return_value = None
        mock_hw.get_temp.return_value = None
        mock_hw.get_target_temp.return_value = None
        node.updateISY_shortpoll()
        self.assertEqual(node.node.getDriver("ST"), 0)
        self.assertEqual(node.node.getDriver("TIME"), 66666)


class TestControllerNode(unittest.TestCase):
    """Test suite for MessanaController."""

    def setUp(self):
        self.poly = create_mock_polyglot()
        self.controller = MessanaController(
            self.poly,
            primary="controller",
            address="controller",
            name="Messana Main",
        )
        self.controller.node = self.controller
        self.mock_sys_api = MagicMock()
        self.mock_sys_api.temp_unit = "Celsius"
        self.mock_sys_api.nbr_zones = 2
        self.mock_sys_api.nbr_macrozones = 1
        self.mock_sys_api.nbr_atus = 1
        self.mock_sys_api.nbr_HCgroup = 1
        self.mock_sys_api.nbr_fancoil = 1
        self.mock_sys_api.nbr_dhwater = 1
        self.mock_sys_api.nbr_buffer_tank = 1
        self.mock_sys_api.nbr_energy_source = 1
        self.controller.messana = self.mock_sys_api

    def test_controller_shortpoll_success_and_failure(self):
        """Controller shortpoll updates ST=1 and TIME on success, ST=0 on failure."""
        # Success
        self.mock_sys_api.get_status.return_value = 1
        self.mock_sys_api.get_external_alarm.return_value = 0
        self.controller.updateISY_shortpoll()
        self.assertEqual(self.controller.getDriver("ST"), 1)
        time_driver = self.controller.drivers_values.get("TIME")
        self.assertIsNotNone(time_driver)
        self.assertGreater(time_driver["value"], 0)
        self.assertEqual(time_driver["uom"], 151)

        # Failure
        self.controller.setDriver("TIME", 77777, True, True, 151)
        self.mock_sys_api.get_status.return_value = None
        self.mock_sys_api.get_external_alarm.return_value = None
        self.controller.updateISY_shortpoll()
        self.assertEqual(self.controller.getDriver("ST"), 0)
        self.assertEqual(self.controller.getDriver("TIME"), 77777)

    def test_controller_longpoll_success_and_failure(self):
        """Controller longpoll updates ST=1 and TIME on success, ST=0 on failure."""
        # Success
        self.mock_sys_api.get_status.return_value = 1
        self.mock_sys_api.get_setback_diff.return_value = 2.0
        self.mock_sys_api.get_setback.return_value = 1
        self.mock_sys_api.get_energy_saving.return_value = 0
        self.mock_sys_api.get_external_alarm.return_value = 0
        self.controller.updateISY_longpoll()
        self.assertEqual(self.controller.getDriver("ST"), 1)
        self.assertGreater(self.controller.getDriver("TIME"), 0)

        # Failure
        self.controller.setDriver("TIME", 88888, True, True, 151)
        self.mock_sys_api.get_status.return_value = None
        self.mock_sys_api.get_setback_diff.return_value = None
        self.mock_sys_api.get_setback.return_value = None
        self.mock_sys_api.get_energy_saving.return_value = None
        self.mock_sys_api.get_external_alarm.return_value = None
        self.controller.updateISY_longpoll()
        self.assertEqual(self.controller.getDriver("ST"), 0)
        self.assertEqual(self.controller.getDriver("TIME"), 88888)

    def test_controller_don_dof_commands(self):
        """Test controller commands: DON, DOF."""
        self.mock_sys_api.set_status.return_value = 1
        self.controller.setOn({"cmd": "DON"})
        self.assertEqual(self.controller.getDriver("GV0"), 1)
        self.mock_sys_api.set_status.assert_called_with(1)

        self.mock_sys_api.set_status.return_value = 0
        self.controller.setOff({"cmd": "DOF"})
        self.assertEqual(self.controller.getDriver("GV0"), 0)
        self.mock_sys_api.set_status.assert_called_with(0)

        self.assertEqual(self.controller.commands["DON"], MessanaController.setOn)
        self.assertEqual(self.controller.commands["DOF"], MessanaController.setOff)

    def test_controller_discover_zone_capabilities(self):
        """Controller probes zone hardware capabilities and excludes unsupported sensors."""
        self.controller.messana_info = sample_messana_info()
        self.mock_sys_api.nbr_zones = 2
        self.mock_sys_api.get_zone_name.side_effect = lambda nbr: f"Room {nbr}"

        # Mock probe API instances for Zone 0 and Zone 1
        mock_z0 = MagicMock()
        mock_z0.get_humidity.return_value = 45.0
        mock_z0.get_dewpoint.return_value = 11.0
        mock_z0.get_air_quality.return_value = 85
        mock_z0.get_co2.return_value = 500
        mock_z0.get_voc.return_value = 200

        mock_z1 = MagicMock()
        mock_z1.get_humidity.return_value = None  # Unsupported
        mock_z1.get_dewpoint.return_value = None  # Unsupported
        mock_z1.get_air_quality.return_value = None  # Unsupported
        mock_z1.get_co2.return_value = -1  # Unsupported
        mock_z1.get_voc.return_value = -1  # Unsupported

        def mock_zone_factory(nbr, info=None):
            return mock_z0 if nbr == 0 else mock_z1

        with patch("udi_MessanaController.messana_zone", side_effect=mock_zone_factory):
            caps = self.controller.discover_zone_capabilities()

        self.assertIn(0, caps)
        self.assertIn(1, caps)

        # Zone 0 supports all optional sensors
        z0_supp = caps[0]["supported"]
        self.assertIn("CLIHUM", z0_supp)
        self.assertIn("DEWPT", z0_supp)
        self.assertIn("GV6", z0_supp)
        self.assertIn("CO2LVL", z0_supp)
        self.assertIn("GV7", z0_supp)
        self.assertEqual(len(z0_supp), 14)

        # Zone 1 excludes unsupported sensors
        z1_supp = caps[1]["supported"]
        self.assertNotIn("CLIHUM", z1_supp)
        self.assertNotIn("DEWPT", z1_supp)
        self.assertNotIn("GV6", z1_supp)
        self.assertNotIn("CO2LVL", z1_supp)
        self.assertNotIn("GV7", z1_supp)
        self.assertEqual(len(z1_supp), 9)


if __name__ == "__main__":
    unittest.main()
