# Messana Radiant Node Server Configuration

This node server integrates the [Messana Radiant](https://www.radiantcooling.com) heating and cooling automation system with Universal Devices eisy, Polisy, and IoX platforms.

---

## 1. Prerequisites

1. **Messana System on Local Network**: Locate the local IP address of your Messana controller (e.g. `192.168.1.100`).
2. **Messana API Key**: Obtain your API key from Messana ([radiantcooling.com](https://www.radiantcooling.com)).

---

## 2. Custom Configuration Parameters

In the Polyglot Web Dashboard, go to your **Messana Radiant** node server details, select **Configuration**, and configure the following parameters:

| Parameter Key | Required | Default | Description |
|:---|:---:|:---:|:---|
| `IP_ADDRESS` | **Yes** | — | The local IPv4 address of your Messana system (e.g., `192.168.1.100`). |
| `MESSANA_KEY` | **Yes** | — | The API key required to authenticate with your Messana controller. |
| `TEMP_UNIT` | No | `C` | Preferred temperature unit for ISY/IoX display: enter `C` for Celsius or `F` for Fahrenheit. Changing this automatically publishes the corresponding dynamic profile (`TEMPC` or `TEMPF`). |

Click **Save Changes** and restart the node server if prompted.

---

## 3. Polling Intervals

* **shortPoll** (Default: `120` seconds):
  - Sends a periodic heartbeat toggle (`DON` / `DOF`) to indicate live communication.
  - Polls high-priority status, room temperatures, humidity, and alarms.
* **longPoll** (Default: `600` seconds):
  - Full system refresh: VOC levels (ppb), CO2 levels (ppm), air quality, setpoints, thermal operations, and subsystem states.

---

## 4. Node Status Indicators

* **System Running** (`ST` on Controller and Subsystems; `GV2` on Zones and Macrozones):
  - `1` = Up (Online and communicating with Messana API).
  - `0` = Down (Offline, API error, or no data received).
* **Last Update** (`TIME`):
  - Unix epoch timestamp (UOM 151) of the last successful data reception from the Messana system.
  - **Guarded**: If communication fails or no data is returned, `TIME` will **not** update, providing a clear indication of stale data.
* **VOC Level** (`GV7` on Zones):
  - Reports volatile organic compound concentration in parts-per-billion (ppb) using UOM `96`.

---

## 5. Subsystem Nodes Discovered

Upon successful connection, the node server automatically discovers and creates:
* **Zones**: Individual climate and air quality zones.
* **Macrozones**: Grouped climate zones.
* **Air Treatment Units (ATUs)**: Ventilation, HRV, and humidity controls.
* **Buffer Tanks**: Hot/cold storage tanks with mode and setpoint control.
* **Heat/Cool Changeover (HCCO)**: Seasonal and adaptive comfort changeover.
* **Fan Coils**: Auxiliary convective units with speed controls.
* **Energy Sources**: Boilers and heat pumps.
* **Domestic Hot Water (DHW)**: Hot water supply temperatures.

---

## 6. Documentation & References

* [Messana Official Site](https://www.radiantcooling.com)
* [Messana SwaggerHub API Docs (v0.9.1)](https://app.swaggerhub.com/apis-docs/radiantcooling/messana/0.9.1)
