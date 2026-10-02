# udi-MessanaRadiant

[![Version](https://img.shields.io/badge/version-0.3.0-blue.svg)](server.json)
[![Tests](https://img.shields.io/badge/tests-51%20passed-brightgreen.svg)](tests/)

Universal Devices Polyglot v3 (PG3 / PG3x) Node Server for integrating the [Messana Radiant](https://www.radiantcooling.com) heating and cooling automation system with the Universal Devices eisy, Polisy, and ISY-994/IoX platforms.

---

## Overview

The Messana Radiant Node Server discovers and synchronizes all subsystems configured on your local Messana system:
* **Messana System Controller**: Overall status, energy saving mode, setback mode/difference, subsystem counts, alarms, and heartbeat.
* **Zones**: Room temperature, setpoints, relative humidity, dew point, air quality index, CO2 levels, **VOC concentration (ppb, UOM 96)**, thermal modes (heat/cool/both requests), and zone energy saving.
* **Macrozones**: Aggregated temperatures, setpoints, humidity, and dew point across multiple zones.
* **Air Treatment Units (ATUs)**: Supply air temperatures, airflow levels, Heat Recovery Ventilation (HRV), humidification, dehumidification, and convective integration.
* **Buffer Tanks**: Storage temperatures, operation modes (manual/automatic), temperature control modes (fixed, load-following, outdoor-reset), and alarm statuses.
* **Heat/Cool Changeover (HCCO)**: Adaptive comfort status, heating/cooling changeover mode, and executive season.
* **Fan Coils**: Heating and cooling fan speeds, fan coil type, and alarms.
* **Energy Sources**: Status, domestic hot water (DHW) production status, source type (boiler, heat pump), and alarms.
* **Domestic Hot Water (DHW)**: Current and target hot water temperatures.

---

## What's New in v0.3.0

* **VOC Sensor Integration**: Full support for zone VOC levels (`GV7`) reporting gas concentration in parts-per-billion (ppb) using UOM `96` from `/api/zone/voc/{id}`.
* **Dynamic Temperature Profile Selection**: Swappable temperature editors (`TEMPC` vs `TEMPF`, `SETTEMPC`/`SETTEMPF`, `TEMPOFFSETC`/`TEMPOFFSETF`) generated and published dynamically to IoX based on the `TEMP_UNIT` configuration setting (`C` or `F`).
* **Strict Uppercase Alphanumeric Naming**: All editor IDs, nodeDef IDs, property IDs, and command IDs strictly follow `^[A-Z0-9]+$` without underscores to comply with UDI profile specifications.
* **Guarded `TIME` Updates**: The `TIME` driver (UOM `151`) only updates when valid data is received from the Messana API. If an API request fails or returns no data, `TIME` remains untouched and the node's running state (`ST` or `GV2`) is set to `0` (Down).
* **Comprehensive Test Suite**: 51 standalone unit tests covering profile schemas, XML definitions, API communication, conversion routines, and node poll state transitions with zero external dependencies.
* **Unified Common Versioning**: Centralized `0.3.0` version definition synchronized across `version.py`, `version.txt`, `profile/version.txt`, and `server.json`.

---

## Configuration

In the PG3 Dashboard under **Configuration**, provide the following custom parameters:

| Parameter | Type | Required | Default | Description |
|:---|:---|:---:|:---:|:---|
| `IP_ADDRESS` | String | **Yes** | — | Local IP address of your Messana system (e.g. `192.168.1.100`) |
| `MESSANA_KEY` | String | **Yes** | — | API key provided by Messana / radiantcooling.com |
| `TEMP_UNIT` | String | No | `C` | Temperature display unit for ISY/IoX: `C` for Celsius or `F` for Fahrenheit |
| `NODE_DELAY` | Float | No | `1.0` | Startup serialization delay (seconds) between node creations to prevent high-volume errors |

### Polling Intervals

* **Short Poll** (default: `120` seconds): Sends a heartbeat toggle command (`DON` / `DOF`) and polls high-priority status, room temperatures, and alarm states.
* **Long Poll** (default: `600` seconds): Full system refresh including VOC, CO2, air quality, setpoints, thermal operations, and subsystem states.

---

## Running Tests

The test suite runs using standard Python with no extra dependencies needed:

```bash
python3 run_tests.py
```

Or using Python's standard `unittest` module:

```bash
python3 -m unittest discover tests
```

---

## Architecture & File Structure

```text
udi-MessanaRadiant/
├── server.json                 # Node server metadata & profile version
├── version.py                  # Single source of truth for version (__version__)
├── version.txt                 # Package version string
├── profile_def.py              # Dynamic JSON profile generator (C/F switching)
├── profile/                    # Static XML profile fallback
│   ├── version.txt             # Profile version string
│   ├── editor/editors.xml      # Editor definitions (TEMPC, TEMPF, VOC, TIMESTAMP, etc.)
│   ├── nodedef/nodedefs.xml    # NodeDef specifications (SYSTEM, ZONE, ATU, etc.)
│   └── nls/en_us.txt           # Natural Language Strings / labels
├── profile.zip                 # Packaged profile archive
├── udi_MessanaController.py    # Main PG3 Controller / System node
├── udi_MessanaZone.py          # Zone node (temperature, VOC, CO2, humidity, dew point)
├── udi_MessanaMacrozone.py     # Macrozone node
├── udi_MessanaATU.py           # Air Treatment Unit node
├── udi_MessanaBuffertank.py    # Buffer Tank node
├── udi_MessanaHCCO.py          # Heat/Cool Changeover node
├── udi_MessanaFancoil.py       # Fan Coil node
├── udi_MessanaEnergySource.py  # Energy Source node
├── udi_MessanaHotWater.py      # Domestic Hot Water node
├── Messana_Info.py             # HTTP client base class
├── Messana_Node.py             # Subsystem API data bindings
├── Messana_System.py           # System-level API data bindings
├── udiLib.py                   # Helper utilities and temperature conversion routines
├── run_tests.py                # Standalone test runner
└── tests/                      # 51 automated unit tests
    ├── test_profile.py         # Profile & XML schema tests
    ├── test_udilib.py          # Conversion & utility tests
    ├── test_messana_api.py     # API communication tests
    └── test_nodes.py           # Node polling and state tests
```

---

## References

* [Messana Radiant Cooling](https://www.radiantcooling.com)
* [Messana API Documentation (v0.9.1)](https://app.swaggerhub.com/apis-docs/radiantcooling/messana/0.9.1)
* [Universal Devices Polyglot v3 Documentation](https://github.com/UniversalDevicesInc/udi_interface)

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
