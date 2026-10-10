# Polyglot v3 Configuration Guide: Messana Radiant

This guide explains how to configure and operate the **Messana Radiant** node server in the Polyglot v3 (PG3 / PG3x) Web Dashboard for Universal Devices **eisy** and **Polisy**.

---

## 1. Quick Start Checklist

Before configuring the node server, ensure you have:
1. **Messana Controller (mBox) on your Local Network**:
   - The mBox must be powered on and connected to the same local area network as your eisy or Polisy.
   - Note the local IPv4 address (e.g., `192.168.1.100`).
   - *(Recommendation: Assign a permanent DHCP reservation in your router so the IP never changes).*
2. **Messana API Key**:
   - An active API key provided by your Messana radiant heating & cooling installer or generated via [radiantcooling.com](https://www.radiantcooling.com).

---

## 2. Configuration in the PG3 Web Dashboard

1. Log into your Polyglot v3 dashboard (`https://<eisy-ip>:8043`).
2. Navigate to **Node Servers** &rarr; **Messana Radiant**.
3. Click on the **Configuration** tab.
4. Under **Custom Configuration Parameters**, enter the following keys and values:

| Parameter Key | Required | Default | Example Value | Description |
|:---|:---:|:---:|:---|:---|
| `IP_ADDRESS` | **Yes** | — | `192.168.1.100` | The local IPv4 address of your Messana controller. Do not include `http://` or trailing slashes. |
| `MESSANA_KEY` | **Yes** | — | `a1b2c3d4-e5f6...` | Your secret Messana API key. |
| `TEMP_UNIT` | No | `C` | `F` | Preferred temperature unit for display and setpoint control in IoX / UD Mobile: enter `F` for Fahrenheit or `C` for Celsius. |

5. Click **Save Changes**.
6. Click **Restart Node Server**.

> **Note on Temperature Units**:  
> When `TEMP_UNIT` is set to `F`, setpoints entered in UD Mobile or the Admin Console in Fahrenheit are automatically converted to Celsius before sending to your Messana controller. Measured temperatures received from the controller in Celsius are converted to Fahrenheit for display.

---

## 3. Polling Intervals

The node server uses two polling cycles to keep your system responsive without placing unnecessary load on your controller or home network:

* **Short Poll** (Default: `120` seconds / 2 minutes):
  - Sends a periodic heartbeat toggle (`DON` / `DOF`) to indicate live communication.
  - Updates current room temperatures, relative humidity, active thermal calls (heating vs cooling requests), and system alarms.
* **Long Poll** (Default: `600` seconds / 10 minutes):
  - Performs a comprehensive environmental refresh: Indoor Air Quality index, Volatile Organic Compounds (`VOC` in ppb), Carbon Dioxide (`CO2` in ppm), and all mechanical subsystem states (ATU, Buffer Tanks, Fan Coils).

*You can adjust these intervals under the **Details** tab in the PG3 dashboard if desired, though the default values are ideal for most homes.*

---

## 4. Understanding Your Discovered Nodes in IoX

Once connected, the node server automatically discovers and creates nodes in your Admin Console and UD Mobile app:

### System Controller Node
* **Online Status (`ST`)**: `1` = Online and communicating with the Messana system; `0` = Offline or communication error.
* **Last Update (`TIME`)**: Shows the exact date and timestamp of the last successful data update received from the Messana controller. If network communication drops, this timestamp freezes.
* **Energy Saving Mode (`GV3`)**: Master Whole-House Away / Energy Saving state. Turning this On sets energy-saving mode across all zones.
* **Setback Mode (`GV0`) & Offset (`GV1`)**: Shows active setback status and differential temperature offset.
* **Active Alarms (`GV4`)**: Indicates any active system alarms.
* **Subsystem Counts**: Reports the total number of connected zones, macrozones, ATUs, buffer tanks, fan coils, and energy sources.

### Zone (Room) Nodes
* **Temperature (`ST`)**: Current room temperature.
* **Setpoint (`CLISPC`)**: Target temperature setpoint for the zone.
* **Humidity (`CLIHUM`)**: Relative humidity percentage (%).
* **Dew Point (`GV4`)**: Calculated dew point temperature (vital for radiant cooling condensation management).
* **Thermal Request (`GV1`)**: Current operational call (`0` = Idle, `1` = Heating, `2` = Cooling, `3` = Heating & Cooling).
* **Air Quality Index (`GV6`)**: Current IAQ category (Good, Moderate, Poor).
* **VOC Concentration (`GV7`)**: Total Volatile Organic Compounds measured in parts-per-billion (`ppb`).
* **CO2 Concentration (`GV5`)**: Carbon dioxide concentration measured in parts-per-million (`ppm`).
* **Zone Energy Saving (`GV3`)**: Individual room Eco / Energy Saving toggle.

### Mechanical Equipment Nodes
* **Air Treatment Units (ATUs)**: Supply air temperatures, airflow rates, Heat Recovery Ventilation (`HRV`) status, humidification status, and convective integration.
* **Buffer Tanks**: Hot and cold water thermal storage temperatures, operation modes (Manual/Auto), and temperature control modes (Fixed, Load-Following, Outdoor-Reset).
* **Heat/Cool Changeover (HCCO)**: Adaptive comfort status, active seasonal mode (Heating, Cooling, Auto), and executive season.
* **Fan Coils**: Fan coil operational status and heating/cooling fan speed levels.
* **Energy Sources**: Heat pump and boiler status, DHW production status, and alarms.
* **Domestic Hot Water (DHW)**: Hot water supply temperatures and target setpoint.

---

## 5. Controlling Your System from UD Mobile & Admin Console

* **Changing Setpoints**: Adjust sliders or type new temperatures directly in UD Mobile or the Admin Console. Supports precision decimals (e.g. `71.5` °F).
* **Toggling Away / Energy Saving Mode**: Use the **Energy Saving** switch on the System Controller to set the whole home to Away mode, or toggle individual zones as needed.
* **Ventilation Boost**: Turn HRV on or off directly from the ATU node or automate it using IoX programs when VOC or CO2 rises.

---

## 6. Troubleshooting Checklist

| Issue | Cause & Resolution |
|:---|:---|
| **Node server shows "Disconnected" or "Failed"** | Verify your eisy has network access to the Messana controller's IP address. Confirm that the IP address in configuration matches your mBox. |
| **Log displays `Response [401]`** | The API key entered under `MESSANA_KEY` is incorrect or has expired. Verify your API key with Messana or your installer. |
| **Log displays `Response [404]`** | A requested subsystem or endpoint is not enabled on your specific Messana controller hardware configuration. The node server automatically handles this cleanly. |
| **Temperatures show in Celsius but I prefer Fahrenheit** | Ensure `TEMP_UNIT` is set to `F` in PG3 Configuration. After saving and restarting the node server, restart your Admin Console so IoX loads the Fahrenheit profile definitions. |
| **`TIME` driver is not advancing** | The node server protects against stale data: `TIME` only advances when fresh data is received from the Messana controller. If network communication is interrupted, `TIME` stays frozen and `ST` drops to `0`. |

---

## 7. Additional Documentation

* **[User Guide & Automation Examples (README.md)](README.md)**: Full overview, benefits, and practical IoX program automation recipes.
* **[Developer & Architecture Guide (DEVELOPER.html)](DEVELOPER.html)**: Internal architecture, REST API mapping tables, unit test runner instructions, and developer documentation.
* **[Messana Radiant Cooling](https://www.radiantcooling.com)**: Official manufacturer website and documentation.
