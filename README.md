# Messana Radiant Integration for Universal Devices

[![Version](https://img.shields.io/badge/version-0.4.0-blue.svg)](server.json)
[![Platform](https://img.shields.io/badge/platform-eisy%20%7C%20Polisy%20%7C%20IoX-orange.svg)](https://www.universal-devices.com)
[![Polyglot](https://img.shields.io/badge/polyglot-PG3%20%2F%20PG3x-purple.svg)](https://github.com/UniversalDevicesInc/udi_interface)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Developer Guide](https://img.shields.io/badge/developer-DEVELOPER.html-teal.svg)](DEVELOPER.html)

Bring the power, luxury, and efficiency of your **[Messana Radiant Cooling & Heating System](https://www.radiantcooling.com)** directly into your **Universal Devices eisy, Polisy, or IoX** smart home platform.

Control room temperatures, monitor indoor air quality (VOC and CO2), track dew points to prevent condensation, activate whole-house Away / Energy Saving modes, and automate your entire climate system alongside your lighting, shading, and security systems.

---

## Why Connect Messana to Universal Devices?

* **Unified Smart Home Control**: Monitor and control every radiant zone directly from the **UD Mobile** app (iOS/Android) or the **IoX Admin Console** without jumping between different apps.
* **Complete Thermal & Air Quality Monitoring**: In addition to room temperature, view relative humidity, calculated dew point, air quality status, CO2 levels (ppm), and volatile organic compound (VOC) levels in parts-per-billion (ppb).
* **Smart Home Automations**: Trigger energy-saving setback modes automatically when your alarm is armed away, adjust nighttime sleeping temperatures on a schedule, or boost ventilation when air quality dips.
* **Whole-House or Room-by-Room Control**: Adjust setpoints individually per room, or command the master controller to set whole-house Energy Saving mode with a single button press.
* **Full Mechanical Equipment Visibility**: Keep an eye on your Air Treatment Units (ATUs), Heat Recovery Ventilation (HRV), buffer storage tanks, fan coils, heat pumps/boilers, and domestic hot water.
* **Fahrenheit & Celsius Support**: Seamlessly use your preferred temperature unit. If you use Fahrenheit in IoX, setpoints you enter in UD Mobile are automatically converted to Celsius for the Messana system, and temperatures are converted to Fahrenheit for display.

---

## Supported Subsystems & What You Can Control

| Subsystem | What You Can Monitor | What You Can Control |
|:---|:---|:---|
| **System Controller** | Overall system status, active alarm flags, subsystem counts, communication heartbeat | Master Energy Saving (Away mode) toggle, Night Setback mode & differential offset |
| **Zones (Rooms)** | Room temperature, current setpoint, relative humidity, dew point, thermal request (heat/cool/idle), VOC (ppb), CO2 (ppm), Air Quality category | Room temperature setpoint, individual Zone Energy Saving toggle |
| **Macrozones** | Grouped zone average temperatures, humidity, dew point, and setpoints | Group temperature setpoint |
| **Air Treatment Units (ATU)** | Supply air temperatures, airflow levels, operational status | Heat Recovery Ventilation (HRV) toggle, Humidification toggle, Convective Integration toggle |
| **Buffer Tanks** | Hot and cold thermal storage water temperatures, alarm states | Operation mode (Off, Manual, Automatic), Temperature control mode (Fixed, Load-Following, Outdoor-Reset) |
| **Heat/Cool Changeover (HCCO)** | Active season (Heating vs Cooling), Adaptive Comfort state | Mode selection (Heating, Cooling, Auto), Adaptive Comfort toggle |
| **Fan Coils** | Fan coil status, unit type, alarms | Heating fan speed, Cooling fan speed |
| **Energy Sources** | Boiler/Heat pump status, Domestic Hot Water (DHW) production status, alarms | Operating state |
| **Domestic Hot Water (DHW)** | Current water temperature, target temperature | Hot water setpoint |

---

## Quick Start Setup Guide

Setting up the Messana Radiant node server takes less than five minutes:

### 1. Gather Your Information
Before starting, make sure you have:
* The **Local IP Address** of your Messana controller (mBox) on your home network (e.g., `192.168.1.100`). *(Tip: Reserve a static IP for your mBox in your home router).*
* Your **Messana API Key**, provided by your Messana installer or obtained through your account on [radiantcooling.com](https://www.radiantcooling.com).

### 2. Install from the PG3 Node Server Store
1. Open your Polyglot v3 web dashboard (`https://<your-eisy-ip>:8043`).
2. Go to **Node Server Store**.
3. Search for **Messana Radiant** and click **Install**.
4. Choose an available slot and confirm.

### 3. Enter Configuration Settings
In the PG3 dashboard under **Node Servers** &rarr; **Messana Radiant** &rarr; **Configuration**, enter the following under **Custom Configuration Parameters**:

| Key | Value Example | Description |
|:---|:---|:---|
| `IP_ADDRESS` | `192.168.1.100` | Local IP address of your Messana controller |
| `MESSANA_KEY` | `your-api-key-here` | Your Messana system API key |
| `TEMP_UNIT` | `F` (or `C`) | Enter `F` for Fahrenheit or `C` for Celsius (defaults to `C`) |
| `NODE_DELAY` | `1.0` | Startup serialization delay (seconds) between node creations |

Click **Save Changes** and **Restart** the node server.

### 4. Automatic Discovery
Once restarted, the node server connects to your Messana controller and automatically creates all your configured zones, macrozones, ATUs, buffer tanks, and equipment in IoX. Open your **IoX Admin Console** or **UD Mobile** app to see your new devices!

---

## Everyday Use with UD Mobile & Admin Console

### Adjusting Temperature Setpoints
* In **UD Mobile** or the **Admin Console**, open any Zone.
* Move the setpoint slider or type your desired temperature (e.g., `72.0` °F or `21.5` °C).
* The command is immediately delivered to the Messana controller.

### Using Energy Saving / Away Mode
* **Whole-House Away Mode**: Open the **Messana System Controller** node and turn **Energy Saving** to **On**. This activates energy-saving mode across all zones in the house.
* **Single-Room Eco Mode**: Open an individual **Zone** node and toggle its specific **Energy Saving** switch (ideal for guest rooms or unused spaces).

### Checking Online Status & Fresh Data
* **Online Status (`ST` / `GV2`)**: Shows `1` (Online) when communicating normally, or `0` (Offline) if network communication is interrupted.
* **Last Updated (`TIME`)**: Shows the exact date and time when live readings were last fetched from your Messana controller. If communication is lost, this timestamp remains frozen so you always know your data is fresh.

---

## Helpful IoX Automation Examples

Here are common ways homeowners automate their Messana system using Universal Devices IoX programs:

### Automation 1: Whole-House Away Mode
*Automatically put the radiant system into Energy Saving mode when you leave home.*

```text
If
   Folder 'Occupancy' is False
   (or Security System status is Armed Away)

Then
   Set 'Messana Controller' Energy Saving On

Else
   Set 'Messana Controller' Energy Saving Off
```

### Automation 2: Scheduled Night Setback
*Lower bedroom temperatures slightly at night for deeper sleep, and warm up before sunrise.*

```text
If
   Time is 10:30:00PM

Then
   Set 'Master Bedroom Zone' Setpoint 67.0°F

Else
   ---
```

```text
If
   Time is 6:00:00AM

Then
   Set 'Master Bedroom Zone' Setpoint 71.0°F

Else
   ---
```

### Automation 3: High VOC / Indoor Air Quality Ventilation Boost
*Automatically boost fresh air ventilation when indoor VOC or CO2 levels elevate.*

```text
If
   'Living Room Zone' VOC > 450 ppb
   or 'Living Room Zone' CO2 > 1000 ppm

Then
   Set 'Air Treatment Unit' HRV On
   Send Notification to Admin 'Elevated indoor air pollutants detected — fresh air ventilation enabled.'

Else
   ---
```

### Automation 4: Condensation Protection Watchdog
*Receive an alert if indoor humidity causes dew point to approach room temperature during summer radiant cooling.*

```text
If
   'Master Bedroom Zone' Dew Point >= 64.0°F
   and 'Master Bedroom Zone' Cooling Request is On

Then
   Send Notification to Admin 'Warning: High humidity detected in Master Bedroom during cooling. Check dehumidification.'

Else
   ---
```

---

## Understanding Polling Intervals

* **Short Poll (Every 2 minutes / 120 seconds)**:
  Checks room temperatures, live operating states (heating/cooling demand), alarms, and refreshes the system online heartbeat.
* **Long Poll (Every 10 minutes / 600 seconds)**:
  Performs a complete refresh of deep environmental sensors (VOC concentration, CO2 ppm, air quality categories), macrozone aggregations, and mechanical subsystem details.

*(You can customize these intervals in the PG3 node server configuration page if desired).*

---

## Troubleshooting & FAQ

<details>
<summary><strong>My zones show up, but temperatures are displayed in Celsius instead of Fahrenheit.</strong></summary>

1. In the PG3 dashboard under **Configuration**, set `TEMP_UNIT` to `F`.
2. Click **Save Changes** and restart the node server.
3. In the IoX Admin Console, close and re-open the console (or clear Java cache) so IoX loads the Fahrenheit profile definitions.
</details>

<details>
<summary><strong>The node server shows "Offline" or nodes are not updating.</strong></summary>

1. Confirm that your Messana controller is powered on and connected to your local network.
2. In your web browser, verify you can reach `http://<your-messana-ip>` or ping its IP address.
3. Check that your `IP_ADDRESS` and `MESSANA_KEY` in the PG3 configuration are typed correctly with no accidental spaces.
4. Review the PG3 **Log** tab: if you see `Response [401]`, verify your API key; if you see connection timeouts, verify the IP address.
</details>

<details>
<summary><strong>Can I set fractional or decimal temperatures (e.g., 70.5°F or 21.5°C)?</strong></summary>

Yes! The node server supports precision decimal inputs from both the IoX Admin Console and the UD Mobile app.
</details>

<details>
<summary><strong>What does the VOC reading mean?</strong></summary>

VOC stands for Volatile Organic Compounds. The sensor measures total volatile organic pollutants in **ppb** (parts per billion). Lower numbers (under 250 ppb) represent clean, fresh indoor air. Readings above 500 ppb indicate elevated contaminants (cooking aromas, cleaning supplies, off-gassing) and suggest running ventilation.
</details>

---

## Technical & Developer Documentation

Are you a software developer, custom integrator, or contributing code to this node server? 

Detailed technical architecture, API endpoint routing tables, dynamic profile specifications, test suite details, and release workflows have been moved to the dedicated guide:

&rarr; **[Open the Developer & Architecture Guide (DEVELOPER.html)](DEVELOPER.html)**

---

## Helpful Links & Resources

* [Messana Radiant Cooling & Heating Official Website](https://www.radiantcooling.com)
* [Universal Devices Official Website](https://www.universal-devices.com)
* [Universal Devices Community Forum](https://forum.universal-devices.com/)
* [Polyglot v3 Documentation](https://github.com/UniversalDevicesInc/udi_interface)

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
