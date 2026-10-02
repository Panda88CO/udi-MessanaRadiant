#!/usr/bin/env python3
"""
Dynamic JSON Profile Definition for Messana Radiant Node Server on PG3 / PG3x.

All editor IDs, nodeDef IDs, property IDs, and command IDs are strictly UPPERCASE
alphanumeric ([A-Z0-9]+) without underscores or special characters.
"""

TEMP_C = 0
TEMP_F = 1


def build_profile_definition(temp_unit=TEMP_C) -> dict:
    """
    Build the dynamic JSON profile definition for PG3/PG3x.

    temp_unit can be 0/TEMP_C or 1/TEMP_F, or strings 'C' / 'F'.
    """
    is_f = False
    if temp_unit in (TEMP_F, 'F', 'f', 'FAHRENHEIT', 'fahrenheit', 1, '1', 17, '17'):
        is_f = True

    temp_editor = "TEMPF" if is_f else "TEMPC"
    settemp_editor = "SETTEMPF" if is_f else "SETTEMPC"
    tempoffset_editor = "TEMPOFFSETF" if is_f else "TEMPOFFSETC"
    settempos_editor = "SETTEMPOSF" if is_f else "SETTEMPOSC"

    if is_f:
        temp_ranges = [
            {"uom": "17", "min": -50, "max": 150, "step": 0.5, "prec": 1},
            {"uom": "25", "subset": "98-99", "names": {"98": "No Support", "99": "Unknown"}},
        ]
        settemp_ranges = [
            {"uom": "17", "min": 50, "max": 100, "step": 1, "prec": 1},
            {"uom": "25", "subset": "98-99", "names": {"98": "No Support", "99": "Unknown"}},
        ]
        tempoffset_ranges = [
            {"uom": "17", "min": 0, "max": 50, "step": 1, "prec": 1},
            {"uom": "25", "subset": "98-99", "names": {"98": "No Support", "99": "Unknown"}},
        ]
        settempos_ranges = [
            {"uom": "17", "min": 0, "max": 50, "step": 1, "prec": 1},
            {"uom": "25", "subset": "98-99", "names": {"98": "No Support", "99": "Unknown"}},
        ]
        temp_editors = [
            {"id": "TEMPF", "ranges": temp_ranges},
            {"id": "SETTEMPF", "ranges": settemp_ranges},
            {"id": "TEMPOFFSETF", "ranges": tempoffset_ranges},
            {"id": "SETTEMPOSF", "ranges": settempos_ranges},
        ]
    else:
        temp_ranges = [
            {"uom": "4", "min": -50, "max": 75, "step": 0.5, "prec": 1},
            {"uom": "25", "subset": "98-99", "names": {"98": "No Support", "99": "Unknown"}},
        ]
        settemp_ranges = [
            {"uom": "4", "min": 10, "max": 35, "step": 0.5, "prec": 1},
            {"uom": "25", "subset": "98-99", "names": {"98": "No Support", "99": "Unknown"}},
        ]
        tempoffset_ranges = [
            {"uom": "4", "min": 0, "max": 25, "step": 0.5, "prec": 1},
            {"uom": "25", "subset": "98-99", "names": {"98": "No Support", "99": "Unknown"}},
        ]
        settempos_ranges = [
            {"uom": "4", "min": 0, "max": 25, "step": 0.5, "prec": 1},
            {"uom": "25", "subset": "98-99", "names": {"98": "No Support", "99": "Unknown"}},
        ]
        temp_editors = [
            {"id": "TEMPC", "ranges": temp_ranges},
            {"id": "SETTEMPC", "ranges": settemp_ranges},
            {"id": "TEMPOFFSETC", "ranges": tempoffset_ranges},
            {"id": "SETTEMPOSC", "ranges": settempos_ranges},
        ]

    editors = temp_editors + [
        {
            "id": "ENABLE",
            "ranges": [
                {"uom": "25", "subset": "0-1,99", "names": {"0": "Disabled", "1": "Enabled", "99": "Unknown"}},
            ],
        },
        {
            "id": "SETENABLE",
            "ranges": [
                {"uom": "25", "subset": "0-1", "names": {"0": "Disable", "1": "Enable"}},
            ],
        },
        {
            "id": "BTENABLE",
            "ranges": [
                {"uom": "25", "subset": "0-2,99", "names": {"0": "Off", "1": "Disabled", "2": "On", "99": "Unknown"}},
            ],
        },
        {
            "id": "THERMALMODE",
            "ranges": [
                {
                    "uom": "25",
                    "subset": "0-3,99",
                    "names": {
                        "0": "No Request",
                        "1": "Heat Request",
                        "2": "Cool Request",
                        "3": "Heat&Cool Request",
                        "99": "Unknown",
                    },
                },
            ],
        },
        {
            "id": "STATUS",
            "ranges": [
                {"uom": "25", "subset": "0-1,99", "names": {"0": "Off", "1": "On", "99": "Unknown"}},
            ],
        },
        {
            "id": "SETSTATUS",
            "ranges": [
                {"uom": "25", "subset": "0-1", "names": {"0": "Off", "1": "On"}},
            ],
        },
        {
            "id": "HUMIDITY",
            "ranges": [
                {"uom": "21", "min": 0, "max": 100, "step": 0.5, "prec": 1},
                {"uom": "25", "subset": "98-99", "names": {"98": "No Support", "99": "Unknown"}},
            ],
        },
        {
            "id": "AIRQ",
            "ranges": [
                {"uom": "56", "min": 0, "max": 1000, "step": 1, "prec": 0},
                {"uom": "25", "subset": "98-99", "names": {"98": "No Support", "99": "Unknown"}},
            ],
        },
        {
            "id": "CO2",
            "ranges": [
                {"uom": "56", "min": 0, "max": 1000, "step": 1, "prec": 0},
                {"uom": "25", "subset": "98-99", "names": {"98": "No Support", "99": "Unknown"}},
            ],
        },
        {
            "id": "VOC",
            "ranges": [
                {"uom": "96", "min": 0, "max": 10000, "step": 1, "prec": 0},
                {"uom": "25", "subset": "98-99", "names": {"98": "No Support", "99": "Unknown"}},
            ],
        },
        {
            "id": "ALARM",
            "ranges": [
                {"uom": "25", "subset": "0-1,99", "names": {"0": "No Alarm", "1": "Alarm", "99": "Unknown"}},
            ],
        },
        {
            "id": "RUNNING",
            "ranges": [
                {"uom": "25", "subset": "0-1,99", "names": {"0": "Down", "1": "Up", "99": "Unknown"}},
            ],
        },
        {
            "id": "COUNT",
            "ranges": [
                {"uom": "107", "min": 0, "max": 127, "step": 1, "prec": 0},
                {"uom": "25", "subset": "98,99", "names": {"98": "Not Present", "99": "Unknown"}},
            ],
        },
        {
            "id": "ONOFF",
            "ranges": [
                {
                    "uom": "25",
                    "subset": "0-1,98,99",
                    "names": {"0": "Off", "1": "On", "98": "Not supported", "99": "Unknown"},
                },
            ],
        },
        {
            "id": "FLOWLVL",
            "ranges": [
                {"uom": "7", "min": 0, "max": 1000, "step": 10, "prec": 0},
                {"uom": "25", "subset": "98,99", "names": {"98": "No Support", "99": "Unknown"}},
            ],
        },
        {
            "id": "SETFLOWLVL",
            "ranges": [
                {"uom": "7", "min": 60, "max": 350, "step": 10, "prec": 0},
            ],
        },
        {
            "id": "BTMODE",
            "ranges": [
                {
                    "uom": "25",
                    "subset": "0-1,98,99",
                    "names": {"0": "Manual", "1": "Automatic", "98": "Not supported", "99": "Unknown"},
                },
            ],
        },
        {
            "id": "BTTEMPMODE",
            "ranges": [
                {
                    "uom": "25",
                    "subset": "0-2,98,99",
                    "names": {
                        "0": "Fixed Temperature",
                        "1": "Follow Heat/Cool loads",
                        "2": "Outdoor Temperature",
                        "98": "Not supported",
                        "99": "Unknown",
                    },
                },
            ],
        },
        {
            "id": "SETBTMODE",
            "ranges": [
                {"uom": "25", "subset": "0-1", "names": {"0": "Manual", "1": "Automatic"}},
            ],
        },
        {
            "id": "SETBTTEMPMODE",
            "ranges": [
                {
                    "uom": "25",
                    "subset": "0-2",
                    "names": {
                        "0": "Fixed Temperature",
                        "1": "Follow Heat/Cool loads",
                        "2": "Outdoor Temperature",
                    },
                },
            ],
        },
        {
            "id": "HCCOMODE",
            "ranges": [
                {
                    "uom": "25",
                    "subset": "0-2,98,99",
                    "names": {
                        "0": "Heating Mode",
                        "1": "Cooling Mode",
                        "2": "Auto Mode",
                        "98": "Not Supported",
                        "99": "Unknown",
                    },
                },
            ],
        },
        {
            "id": "SEASONMODE",
            "ranges": [
                {
                    "uom": "25",
                    "subset": "0-1,98,99",
                    "names": {"0": "Heating", "1": "Cooling", "98": "Not Supported", "99": "Unknown"},
                },
            ],
        },
        {
            "id": "SETHCCOMODE",
            "ranges": [
                {
                    "uom": "25",
                    "subset": "0-2",
                    "names": {"0": "Heating Mode", "1": "Cooling Mode", "2": "Auto Mode"},
                },
            ],
        },
        {
            "id": "FANSPEED",
            "ranges": [
                {"uom": "89", "min": 0, "max": 1000, "step": 1, "prec": 0},
                {"uom": "25", "subset": "98,99", "names": {"98": "Not Present", "99": "Unknown"}},
            ],
        },
        {
            "id": "SETSPEED",
            "ranges": [
                {"uom": "89", "min": 0, "max": 1000, "step": 1, "prec": 0},
            ],
        },
        {
            "id": "FCTYPE",
            "ranges": [
                {
                    "uom": "25",
                    "subset": "0-3,99",
                    "names": {"0": "Type 0", "1": "Type 1", "2": "Type 2", "3": "Type 3", "99": "Unknown"},
                },
            ],
        },
        {
            "id": "ESTYPE",
            "ranges": [
                {
                    "uom": "25",
                    "subset": "0-3,99",
                    "names": {
                        "0": "Boiler",
                        "1": "Heat Pump Cool",
                        "2": "Heat Pump Heat",
                        "3": "Heat Pump Heat/Cool",
                        "99": "Unknown",
                    },
                },
            ],
        },
        {
            "id": "TIMESTAMP",
            "ranges": [
                {"uom": "151", "min": 0, "max": 4294967295, "prec": 0},
            ],
        },
    ]

    nodedefs = [
        {
            "id": "SYSTEM",
            "name": "Messana System",
            "properties": [
                {"id": "ST", "name": "System Running", "editor": "RUNNING"},
                {"id": "GV0", "name": "System State", "editor": "STATUS"},
                {"id": "GV1", "name": "Setback Difference", "editor": tempoffset_editor},
                {"id": "GV2", "name": "Setback Mode", "editor": "ENABLE"},
                {"id": "GV12", "name": "Energy Saving", "editor": "ENABLE"},
                {"id": "GV3", "name": "Zones", "editor": "COUNT"},
                {"id": "GV4", "name": "Macrozones", "editor": "COUNT"},
                {"id": "GV5", "name": "ATUs", "editor": "COUNT"},
                {"id": "GV6", "name": "HC CO Controls", "editor": "COUNT"},
                {"id": "GV7", "name": "Fan Coils", "editor": "COUNT"},
                {"id": "GV8", "name": "DHWs", "editor": "COUNT"},
                {"id": "GV9", "name": "Buffer Tanks", "editor": "COUNT"},
                {"id": "GV10", "name": "Energy Sources", "editor": "COUNT"},
                {"id": "GV11", "name": "System Alarm", "editor": "ALARM"},
                {"id": "TIME", "name": "Last Update", "editor": "TIMESTAMP"},
            ],
            "cmds": {
                "accepts": [
                    {"id": "UPDATE", "name": "Force Update"},
                    {"id": "DON", "name": "System On"},
                    {"id": "DOF", "name": "System Off"},
                    {
                        "id": "STATUS",
                        "name": "Set Status",
                        "parameters": [
                            {"id": "", "name": "Status", "editor": "SETSTATUS", "init": "GV0"},
                        ],
                    },
                    {
                        "id": "ENERGYSAVE",
                        "name": "Set Energy Saving",
                        "parameters": [
                            {"id": "", "name": "Energy Saving", "editor": "SETENABLE", "init": "GV12"},
                        ],
                    },
                    {
                        "id": "SETBACK",
                        "name": "Set Setback Mode",
                        "parameters": [
                            {"id": "", "name": "Setback Mode", "editor": "SETENABLE", "init": "GV2"},
                        ],
                    },
                    {
                        "id": "SETBACKOFFSET",
                        "name": "Set Setback Difference",
                        "parameters": [
                            {"id": "", "name": "Setback Offset", "editor": settempos_editor, "init": "GV1"},
                        ],
                    },
                    {"id": "UPDATEPROFILE", "name": "Update Profile"},
                ],
                "sends": [
                    {"id": "DON"},
                    {"id": "DOF"},
                ],
            },
            "links": {"ctl": [], "rsp": []},
        },
        {
            "id": "ZONE",
            "name": "Messana Zone",
            "properties": [
                {"id": "ST", "name": "Room Temperature", "editor": temp_editor},
                {"id": "GV0", "name": "Zone Status", "editor": "ENABLE"},
                {"id": "GV1", "name": "Zone Thermal Operation", "editor": "THERMALMODE"},
                {"id": "GV2", "name": "System Running", "editor": "RUNNING"},
                {"id": "GV3", "name": "Zone Setpoint", "editor": temp_editor},
                {"id": "CLIHUM", "name": "Zone Humidity", "editor": "HUMIDITY"},
                {"id": "DEWPT", "name": "Zone Dew Point", "editor": temp_editor},
                {"id": "GV6", "name": "Zone Air Quality", "editor": "AIRQ"},
                {"id": "CO2LVL", "name": "Zone CO2 Level", "editor": "CO2"},
                {"id": "GV7", "name": "Zone VOC Level", "editor": "VOC"},
                {"id": "GV8", "name": "Zone Energy Saving", "editor": "ENABLE"},
                {"id": "GV9", "name": "Zone Alarm", "editor": "ALARM"},
                {"id": "GV10", "name": "Zone System Temperature", "editor": temp_editor},
                {"id": "TIME", "name": "Last Update", "editor": "TIMESTAMP"},
            ],
            "cmds": {
                "accepts": [
                    {"id": "UPDATE", "name": "Force Update"},
                    {"id": "DON", "name": "Zone On"},
                    {"id": "DOF", "name": "Zone Off"},
                    {
                        "id": "SETPOINT",
                        "name": "Set Point",
                        "parameters": [
                            {"id": "", "name": "Setpoint", "editor": settemp_editor, "init": "GV3"},
                        ],
                    },
                    {
                        "id": "STATUS",
                        "name": "Set Status",
                        "parameters": [
                            {"id": "", "name": "Status", "editor": "SETENABLE", "init": "GV0"},
                        ],
                    },
                    {
                        "id": "ENERGYSAVE",
                        "name": "Set Energy Saving",
                        "parameters": [
                            {"id": "", "name": "Energy Saving", "editor": "SETENABLE", "init": "GV8"},
                        ],
                    },
                ],
                "sends": [],
            },
            "links": {"ctl": [], "rsp": []},
        },
        {
            "id": "MACROZONE",
            "name": "Messana Macrozone",
            "properties": [
                {"id": "ST", "name": "Macrozone Temperature", "editor": temp_editor},
                {"id": "GV0", "name": "Macrozone Status", "editor": "ENABLE"},
                {"id": "GV2", "name": "System Running", "editor": "RUNNING"},
                {"id": "GV3", "name": "Macrozone Setpoint", "editor": temp_editor},
                {"id": "CLIHUM", "name": "Macrozone Humidity", "editor": "HUMIDITY"},
                {"id": "DEWPT", "name": "Macrozone Dew Point", "editor": temp_editor},
                {"id": "TIME", "name": "Last Update", "editor": "TIMESTAMP"},
            ],
            "cmds": {
                "accepts": [
                    {"id": "UPDATE", "name": "Force Update"},
                    {"id": "DON", "name": "Macrozone On"},
                    {"id": "DOF", "name": "Macrozone Off"},
                    {
                        "id": "SETPOINT",
                        "name": "Set Point",
                        "parameters": [
                            {"id": "", "name": "Setpoint", "editor": settemp_editor, "init": "GV3"},
                        ],
                    },
                    {
                        "id": "STATUS",
                        "name": "Set Status",
                        "parameters": [
                            {"id": "", "name": "Status", "editor": "SETENABLE", "init": "GV0"},
                        ],
                    },
                ],
                "sends": [],
            },
            "links": {"ctl": [], "rsp": []},
        },
        {
            "id": "ATU",
            "name": "Messana Air Treatment Unit",
            "properties": [
                {"id": "ST", "name": "System Running", "editor": "RUNNING"},
                {"id": "GV0", "name": "ATU Status", "editor": "ENABLE"},
                {"id": "CLITEMP", "name": "Air Temperature", "editor": temp_editor},
                {"id": "GV1", "name": "Flow Level", "editor": "FLOWLVL"},
                {"id": "GV2", "name": "Heat Recovery Status", "editor": "ENABLE"},
                {"id": "GV3", "name": "Heat Recovery Running", "editor": "ONOFF"},
                {"id": "GV4", "name": "Humidification Status", "editor": "ENABLE"},
                {"id": "GV5", "name": "Humidification Running", "editor": "ONOFF"},
                {"id": "GV6", "name": "Dehumidification Status", "editor": "ENABLE"},
                {"id": "GV7", "name": "Dehumidification Running", "editor": "ONOFF"},
                {"id": "GV8", "name": "Convection Status", "editor": "ENABLE"},
                {"id": "GV9", "name": "Convection Running", "editor": "ONOFF"},
                {"id": "GV11", "name": "Alarm", "editor": "ALARM"},
                {"id": "TIME", "name": "Last Update", "editor": "TIMESTAMP"},
            ],
            "cmds": {
                "accepts": [
                    {"id": "UPDATE", "name": "Force Update"},
                    {
                        "id": "STATUS",
                        "name": "Set Status",
                        "parameters": [
                            {"id": "", "name": "Status", "editor": "SETENABLE", "init": "GV0"},
                        ],
                    },
                    {
                        "id": "HRVEN",
                        "name": "Heat Recovery",
                        "parameters": [
                            {"id": "", "name": "Heat Recovery", "editor": "SETENABLE", "init": "GV2"},
                        ],
                    },
                    {
                        "id": "HUMEN",
                        "name": "Humidification",
                        "parameters": [
                            {"id": "", "name": "Humidification", "editor": "SETENABLE", "init": "GV4"},
                        ],
                    },
                    {
                        "id": "DEHUMEN",
                        "name": "Dehumidification",
                        "parameters": [
                            {"id": "", "name": "Dehumidification", "editor": "SETENABLE", "init": "GV6"},
                        ],
                    },
                    {
                        "id": "CONVEN",
                        "name": "Convection",
                        "parameters": [
                            {"id": "", "name": "Convection", "editor": "SETENABLE", "init": "GV8"},
                        ],
                    },
                    {
                        "id": "SETFLOW",
                        "name": "Set Flow Level",
                        "parameters": [
                            {"id": "", "name": "Flow Level", "editor": "SETFLOWLVL", "init": "GV1"},
                        ],
                    },
                ],
                "sends": [],
            },
            "links": {"ctl": [], "rsp": []},
        },
        {
            "id": "BUFFERTANK",
            "name": "Messana Buffer Tank",
            "properties": [
                {"id": "ST", "name": "System Running", "editor": "RUNNING"},
                {"id": "GV0", "name": "Buffer Tank Status", "editor": "BTENABLE"},
                {"id": "CLITEMP", "name": "Temperature", "editor": temp_editor},
                {"id": "GV1", "name": "Buffer Tank Mode", "editor": "BTMODE"},
                {"id": "GV2", "name": "Buffer Tank Temperature Mode", "editor": "BTTEMPMODE"},
                {"id": "GV3", "name": "Alarm", "editor": "ALARM"},
                {"id": "TIME", "name": "Last Update", "editor": "TIMESTAMP"},
            ],
            "cmds": {
                "accepts": [
                    {"id": "UPDATE", "name": "Force Update"},
                    {
                        "id": "STATUS",
                        "name": "Set Status",
                        "parameters": [
                            {"id": "", "name": "Status", "editor": "SETENABLE", "init": "GV0"},
                        ],
                    },
                    {
                        "id": "MODE",
                        "name": "Mode",
                        "parameters": [
                            {"id": "", "name": "Mode", "editor": "SETBTMODE", "init": "GV1"},
                        ],
                    },
                    {
                        "id": "TEMPMODE",
                        "name": "Temperature Mode",
                        "parameters": [
                            {"id": "", "name": "Temp Mode", "editor": "SETBTTEMPMODE", "init": "GV2"},
                        ],
                    },
                ],
                "sends": [],
            },
            "links": {"ctl": [], "rsp": []},
        },
        {
            "id": "HCCO",
            "name": "Messana Heat/Cool Changeover",
            "properties": [
                {"id": "ST", "name": "System Running", "editor": "RUNNING"},
                {"id": "GV0", "name": "Adaptive Comfort", "editor": "ENABLE"},
                {"id": "GV1", "name": "Heat/Cool Mode", "editor": "HCCOMODE"},
                {"id": "GV2", "name": "Executive Season", "editor": "SEASONMODE"},
                {"id": "TIME", "name": "Last Update", "editor": "TIMESTAMP"},
            ],
            "cmds": {
                "accepts": [
                    {"id": "UPDATE", "name": "Force Update"},
                    {
                        "id": "STATUS",
                        "name": "Set Adaptive Comfort",
                        "parameters": [
                            {"id": "", "name": "Status", "editor": "SETENABLE", "init": "GV0"},
                        ],
                    },
                    {
                        "id": "MODE",
                        "name": "Mode",
                        "parameters": [
                            {"id": "", "name": "Mode", "editor": "SETHCCOMODE", "init": "GV1"},
                        ],
                    },
                ],
                "sends": [],
            },
            "links": {"ctl": [], "rsp": []},
        },
        {
            "id": "FANCOIL",
            "name": "Messana Fan Coil",
            "properties": [
                {"id": "ST", "name": "System Running", "editor": "RUNNING"},
                {"id": "GV0", "name": "Fan Coil Status", "editor": "ENABLE"},
                {"id": "GV1", "name": "Fan Coil Cool Speed", "editor": "FANSPEED"},
                {"id": "GV2", "name": "Fan Coil Heat Speed", "editor": "FANSPEED"},
                {"id": "GV3", "name": "Fan Coil Type", "editor": "FCTYPE"},
                {"id": "GV4", "name": "Alarm", "editor": "ALARM"},
                {"id": "TIME", "name": "Last Update", "editor": "TIMESTAMP"},
            ],
            "cmds": {
                "accepts": [
                    {"id": "UPDATE", "name": "Force Update"},
                    {
                        "id": "STATUS",
                        "name": "Set Status",
                        "parameters": [
                            {"id": "", "name": "Status", "editor": "SETENABLE", "init": "GV0"},
                        ],
                    },
                    {
                        "id": "HEATSPEED",
                        "name": "Set Heat Speed",
                        "parameters": [
                            {"id": "", "name": "Speed", "editor": "SETSPEED", "init": "GV2"},
                        ],
                    },
                    {
                        "id": "COOLSPEED",
                        "name": "Set Cool Speed",
                        "parameters": [
                            {"id": "", "name": "Speed", "editor": "SETSPEED", "init": "GV1"},
                        ],
                    },
                ],
                "sends": [],
            },
            "links": {"ctl": [], "rsp": []},
        },
        {
            "id": "ENERGY",
            "name": "Messana Energy Source",
            "properties": [
                {"id": "ST", "name": "System Running", "editor": "RUNNING"},
                {"id": "GV0", "name": "Energy Source Status", "editor": "ENABLE"},
                {"id": "GV1", "name": "Energy Source DHW Status", "editor": "ONOFF"},
                {"id": "GV2", "name": "Energy Source Type", "editor": "ESTYPE"},
                {"id": "GV3", "name": "Alarm", "editor": "ALARM"},
                {"id": "TIME", "name": "Last Update", "editor": "TIMESTAMP"},
            ],
            "cmds": {
                "accepts": [
                    {"id": "UPDATE", "name": "Force Update"},
                ],
                "sends": [],
            },
            "links": {"ctl": [], "rsp": []},
        },
        {
            "id": "DHW",
            "name": "Messana Domestic Hot Water",
            "properties": [
                {"id": "ST", "name": "System Running", "editor": "RUNNING"},
                {"id": "GV0", "name": "DHW Status", "editor": "ENABLE"},
                {"id": "CLITEMP", "name": "Current Temperature", "editor": temp_editor},
                {"id": "GV1", "name": "Target Temperature", "editor": temp_editor},
                {"id": "TIME", "name": "Last Update", "editor": "TIMESTAMP"},
            ],
            "cmds": {
                "accepts": [
                    {"id": "UPDATE", "name": "Force Update"},
                    {
                        "id": "STATUS",
                        "name": "Set Status",
                        "parameters": [
                            {"id": "", "name": "Status", "editor": "SETENABLE", "init": "GV0"},
                        ],
                    },
                    {
                        "id": "TARGETTEMP",
                        "name": "Target Temperature",
                        "parameters": [
                            {"id": "", "name": "Target Temp", "editor": settemp_editor, "init": "GV1"},
                        ],
                    },
                ],
                "sends": [],
            },
            "links": {"ctl": [], "rsp": []},
        },
    ]

    return {
        "editors": editors,
        "nodedefs": nodedefs,
        "linkdefs": [],
    }

