#!/usr/bin/env python3
"""
Unit tests for udi-MessanaRadiant profile definitions.

Validates dynamic profile generation in profile_def.py and static XML files
in profile/editor/editors.xml, profile/nodedef/nodedefs.xml, and profile/nls/en_us.txt.
Ensures naming conventions (strictly uppercase alphanumeric without underscores),
temperature editor switching (TEMPC vs TEMPF), VOC UOM 96, and TIME UOM 151.
"""

import os
import re
import unittest
import xml.etree.ElementTree as ET

from profile_def import TEMP_C, TEMP_F, build_profile_definition


class TestProfileDef(unittest.TestCase):
    """Tests for dynamic profile generation in profile_def.py."""

    ID_REGEX = re.compile(r"^[A-Z0-9]+$")

    def test_build_profile_celsius(self):
        """Test profile generation for Celsius."""
        profile = build_profile_definition(TEMP_C)
        self.assertIn("editors", profile)
        self.assertIn("nodedefs", profile)

        # Check editor IDs
        editor_ids = {e["id"] for e in profile["editors"]}
        self.assertIn("TEMPC", editor_ids)
        self.assertIn("TEMPF", editor_ids)
        self.assertIn("VOC", editor_ids)
        self.assertIn("TIMESTAMP", editor_ids)

        # Verify Celsius editors assigned to ZONE node properties
        zone_node = next(n for n in profile["nodedefs"] if n["id"] == "ZONE")
        prop_editors = {p["id"]: p["editor"] for p in zone_node["properties"]}
        self.assertEqual(prop_editors["ST"], "TEMPC")
        self.assertEqual(prop_editors["GV3"], "TEMPC")
        self.assertEqual(prop_editors["DEWPT"], "TEMPC")
        self.assertEqual(prop_editors["GV10"], "TEMPC")
        self.assertEqual(prop_editors["GV7"], "VOC")
        self.assertEqual(prop_editors["TIME"], "TIMESTAMP")

    def test_build_profile_fahrenheit(self):
        """Test profile generation for Fahrenheit with various parameter formats."""
        for f_param in (TEMP_F, "F", "f", "FAHRENHEIT", 1, "1", 17, "17"):
            profile = build_profile_definition(f_param)
            zone_node = next(n for n in profile["nodedefs"] if n["id"] == "ZONE")
            prop_editors = {p["id"]: p["editor"] for p in zone_node["properties"]}
            self.assertEqual(
                prop_editors["ST"],
                "TEMPF",
                f"Failed for param {f_param}",
            )
            self.assertEqual(prop_editors["GV3"], "TEMPF")
            self.assertEqual(prop_editors["DEWPT"], "TEMPF")
            self.assertEqual(prop_editors["GV10"], "TEMPF")

            # Check commands in ZONE
            cmd_params = {
                c["id"]: c["parameters"][0]["editor"]
                for c in zone_node["cmds"]["accepts"]
                if "parameters" in c
            }
            self.assertEqual(cmd_params["SETPOINT"], "SETTEMPF")

    def test_all_ids_uppercase_alphanumeric(self):
        """Verify all editor IDs, nodeDef IDs, property IDs, and cmd IDs follow ^[A-Z0-9]+$."""
        for temp_unit in (TEMP_C, TEMP_F):
            profile = build_profile_definition(temp_unit)
            for editor in profile["editors"]:
                self.assertTrue(
                    self.ID_REGEX.match(editor["id"]),
                    f"Editor ID '{editor['id']}' does not match ^[A-Z0-9]+$",
                )

            editor_id_set = {e["id"] for e in profile["editors"]}

            for nodedef in profile["nodedefs"]:
                self.assertTrue(
                    self.ID_REGEX.match(nodedef["id"]),
                    f"NodeDef ID '{nodedef['id']}' does not match ^[A-Z0-9]+$",
                )
                for prop in nodedef["properties"]:
                    self.assertTrue(
                        self.ID_REGEX.match(prop["id"]),
                        f"Property ID '{prop['id']}' in node '{nodedef['id']}' does not match ^[A-Z0-9]+$",
                    )
                    self.assertIn(
                        prop["editor"],
                        editor_id_set,
                        f"Editor '{prop['editor']}' for property '{prop['id']}' not in editors",
                    )

                for cmd in nodedef.get("cmds", {}).get("accepts", []):
                    self.assertTrue(
                        self.ID_REGEX.match(cmd["id"]),
                        f"Cmd ID '{cmd['id']}' in node '{nodedef['id']}' does not match ^[A-Z0-9]+$",
                    )
                    for param in cmd.get("parameters", []):
                        if param["id"]:  # default/unnamed params may have empty id ""
                            self.assertTrue(
                                self.ID_REGEX.match(param["id"]),
                                f"Param ID '{param['id']}' in cmd '{cmd['id']}' does not match ^[A-Z0-9]+$",
                            )
                        self.assertIn(
                            param["editor"],
                            editor_id_set,
                            f"Editor '{param['editor']}' for param in '{cmd['id']}' not in editors",
                        )

    def test_voc_editor_uom_and_range(self):
        """Verify VOC editor uses UOM 96 and valid range."""
        profile = build_profile_definition(TEMP_C)
        voc_editor = next(e for e in profile["editors"] if e["id"] == "VOC")
        primary_range = voc_editor["ranges"][0]
        self.assertEqual(primary_range["uom"], "96")
        self.assertEqual(primary_range["min"], 0)
        self.assertEqual(primary_range["max"], 10000)

    def test_time_editor_uom_and_range(self):
        """Verify TIMESTAMP editor uses UOM 151."""
        profile = build_profile_definition(TEMP_C)
        time_editor = next(e for e in profile["editors"] if e["id"] == "TIMESTAMP")
        primary_range = time_editor["ranges"][0]
        self.assertEqual(primary_range["uom"], "151")

    def test_no_destructive_delete(self):
        """Verify dynamic profile does not include destructive delete block."""
        profile = build_profile_definition(TEMP_C)
        self.assertNotIn("delete", profile)

    def test_don_dof_in_dynamic_profile(self):
        """Verify DON and DOF are defined in accepts and sends for SYSTEM, and accepts for ZONE/MACROZONE."""
        profile = build_profile_definition(TEMP_C)
        nodes_by_id = {n["id"]: n for n in profile["nodedefs"]}

        # SYSTEM: accepts and sends
        system_node = nodes_by_id["SYSTEM"]
        system_accepts = {cmd["id"] for cmd in system_node.get("cmds", {}).get("accepts", [])}
        system_sends = {cmd["id"] for cmd in system_node.get("cmds", {}).get("sends", [])}
        self.assertIn("DON", system_accepts)
        self.assertIn("DOF", system_accepts)
        self.assertIn("DON", system_sends)
        self.assertIn("DOF", system_sends)

        # ZONE: accepts
        zone_node = nodes_by_id["ZONE"]
        zone_accepts = {cmd["id"] for cmd in zone_node.get("cmds", {}).get("accepts", [])}
        self.assertIn("DON", zone_accepts)
        self.assertIn("DOF", zone_accepts)

        # MACROZONE: accepts
        macrozone_node = nodes_by_id["MACROZONE"]
        macrozone_accepts = {cmd["id"] for cmd in macrozone_node.get("cmds", {}).get("accepts", [])}
        self.assertIn("DON", macrozone_accepts)
        self.assertIn("DOF", macrozone_accepts)


class TestStaticXmlProfile(unittest.TestCase):
    """Tests for static XML profile files in profile/ directory."""

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    PROFILE_DIR = os.path.join(BASE_DIR, "profile")
    ID_REGEX = re.compile(r"^[A-Z0-9]+$")

    def test_editors_xml_validity_and_ids(self):
        """Test profile/editor/editors.xml parses cleanly and conforms to ID conventions."""
        editors_path = os.path.join(self.PROFILE_DIR, "editor", "editors.xml")
        self.assertTrue(os.path.exists(editors_path), f"File missing: {editors_path}")

        tree = ET.parse(editors_path)
        root = tree.getroot()
        self.assertEqual(root.tag, "editors")

        editor_ids = set()
        for editor in root.findall("editor"):
            ed_id = editor.get("id")
            self.assertIsNotNone(ed_id)
            self.assertTrue(
                self.ID_REGEX.match(ed_id),
                f"Static editor ID '{ed_id}' violates ^[A-Z0-9]+$",
            )
            editor_ids.add(ed_id)

        # Check required editors exist
        self.assertIn("TEMPC", editor_ids)
        self.assertIn("TEMPF", editor_ids)
        self.assertIn("VOC", editor_ids)
        self.assertIn("TIMESTAMP", editor_ids)

        # Check VOC has uom="96"
        voc_elem = root.find("./editor[@id='VOC']")
        self.assertIsNotNone(voc_elem)
        ranges = voc_elem.findall("range")
        voc_uoms = [r.get("uom") for r in ranges]
        self.assertIn("96", voc_uoms)

        # Check TIMESTAMP has uom="151"
        ts_elem = root.find("./editor[@id='TIMESTAMP']")
        self.assertIsNotNone(ts_elem)
        ts_ranges = ts_elem.findall("range")
        ts_uoms = [r.get("uom") for r in ts_ranges]
        self.assertIn("151", ts_uoms)

    def test_dual_uom_temperature_support(self):
        """Verify temperature editors in editors.xml support both Celsius (4) and Fahrenheit (17)."""
        editors_path = os.path.join(self.PROFILE_DIR, "editor", "editors.xml")
        tree = ET.parse(editors_path)
        root = tree.getroot()
        temp_editors = (
            "TEMPC", "TEMPF", "SETTEMPC", "SETTEMPF",
            "TEMPOFFSETC", "TEMPOFFSETF", "SETTEMPOSC", "SETTEMPOSF"
        )
        for ed_id in temp_editors:
            ed = root.find(f"./editor[@id='{ed_id}']")
            self.assertIsNotNone(ed, f"Editor {ed_id} missing")
            uoms = {r.get("uom") for r in ed.findall("range")}
            self.assertIn("4", uoms, f"Editor {ed_id} missing UOM 4")
            self.assertIn("17", uoms, f"Editor {ed_id} missing UOM 17")

    def test_nodedefs_xml_validity_and_references(self):
        """Test profile/nodedef/nodedefs.xml parses cleanly and all editor refs exist."""
        editors_path = os.path.join(self.PROFILE_DIR, "editor", "editors.xml")
        nodedefs_path = os.path.join(self.PROFILE_DIR, "nodedef", "nodedefs.xml")
        self.assertTrue(os.path.exists(nodedefs_path), f"File missing: {nodedefs_path}")

        editors_tree = ET.parse(editors_path)
        defined_editors = {e.get("id") for e in editors_tree.getroot().findall("editor")}

        tree = ET.parse(nodedefs_path)
        root = tree.getroot()
        self.assertEqual(root.tag, "nodeDefs")

        for node_def in root.findall("nodeDef"):
            node_id = node_def.get("id")
            self.assertTrue(
                self.ID_REGEX.match(node_id),
                f"NodeDef ID '{node_id}' violates ^[A-Z0-9]+$",
            )

            # Check status properties
            sts = node_def.find("sts")
            if sts is not None:
                for st in sts.findall("st"):
                    st_id = st.get("id")
                    st_editor = st.get("editor")
                    self.assertTrue(
                        self.ID_REGEX.match(st_id),
                        f"Property ID '{st_id}' in '{node_id}' violates ^[A-Z0-9]+$",
                    )
                    self.assertIn(
                        st_editor,
                        defined_editors,
                        f"Editor '{st_editor}' in node '{node_id}' property '{st_id}' not found in editors.xml",
                    )

            # Check commands
            cmds = node_def.find("cmds")
            if cmds is not None:
                accepts = cmds.find("accepts")
                if accepts is not None:
                    for cmd in accepts.findall("cmd"):
                        cmd_id = cmd.get("id")
                        self.assertTrue(
                            self.ID_REGEX.match(cmd_id),
                            f"Cmd ID '{cmd_id}' in '{node_id}' violates ^[A-Z0-9]+$",
                        )
                        for param in cmd.findall("p"):
                            param_editor = param.get("editor")
                            self.assertIn(
                                param_editor,
                                defined_editors,
                                f"Editor '{param_editor}' in cmd '{cmd_id}' not found in editors.xml",
                            )

        # Check ZONE has GV7 mapped to VOC
        zone_node = root.find("./nodeDef[@id='ZONE']")
        self.assertIsNotNone(zone_node)
        gv7 = zone_node.find("./sts/st[@id='GV7']")
        self.assertIsNotNone(gv7, "GV7 not found in ZONE nodeDef")
        self.assertEqual(gv7.get("editor"), "VOC")

    def test_nls_file_definitions(self):
        """Test profile/nls/en_us.txt has valid key=val format and includes VOC translation."""
        nls_path = os.path.join(self.PROFILE_DIR, "nls", "en_us.txt")
        self.assertTrue(os.path.exists(nls_path), f"File missing: {nls_path}")

        entries = {}
        with open(nls_path, "r", encoding="utf-8") as f:
            for line_no, raw_line in enumerate(f, 1):
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                self.assertIn("=", line, f"Line {line_no} is missing '=' delimiter: {line}")
                key, val = line.split("=", 1)
                entries[key.strip()] = val.strip()

        self.assertIn("ST-NLSZONE-GV7-NAME", entries)
        self.assertIn("VOC", entries["ST-NLSZONE-GV7-NAME"])

    def test_don_dof_in_static_xml_and_nls(self):
        """Verify DON and DOF are in nodedefs.xml and en_us.txt for SYSTEM, ZONE, and MACROZONE."""
        nodedefs_path = os.path.join(self.PROFILE_DIR, "nodedef", "nodedefs.xml")
        tree = ET.parse(nodedefs_path)
        root = tree.getroot()

        # SYSTEM: sends and accepts
        sys_node = root.find("./nodeDef[@id='SYSTEM']")
        self.assertIsNotNone(sys_node)
        sys_sends = {c.get("id") for c in sys_node.findall("./cmds/sends/cmd")}
        sys_accepts = {c.get("id") for c in sys_node.findall("./cmds/accepts/cmd")}
        self.assertIn("DON", sys_sends)
        self.assertIn("DOF", sys_sends)
        self.assertIn("DON", sys_accepts)
        self.assertIn("DOF", sys_accepts)

        # ZONE: accepts
        zone_node = root.find("./nodeDef[@id='ZONE']")
        self.assertIsNotNone(zone_node)
        zone_accepts = {c.get("id") for c in zone_node.findall("./cmds/accepts/cmd")}
        self.assertIn("DON", zone_accepts)
        self.assertIn("DOF", zone_accepts)

        # MACROZONE: accepts
        mz_node = root.find("./nodeDef[@id='MACROZONE']")
        self.assertIsNotNone(mz_node)
        mz_accepts = {c.get("id") for c in mz_node.findall("./cmds/accepts/cmd")}
        self.assertIn("DON", mz_accepts)
        self.assertIn("DOF", mz_accepts)

        # NLS labels
        nls_path = os.path.join(self.PROFILE_DIR, "nls", "en_us.txt")
        entries = {}
        with open(nls_path, "r", encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    entries[key.strip()] = val.strip()

        self.assertIn("CMD-NLSSYSTEM-DON-NAME", entries)
        self.assertIn("CMD-NLSSYSTEM-DOF-NAME", entries)
        self.assertIn("CMD-NLSZONE-DON-NAME", entries)
        self.assertIn("CMD-NLSZONE-DOF-NAME", entries)
        self.assertIn("CMD-NLSMACROZONE-DON-NAME", entries)
        self.assertIn("CMD-NLSMACROZONE-DOF-NAME", entries)

    def test_common_version_consistency(self):
        """Verify version.py, version.txt, profile/version.txt, and server.json are all in sync."""
        import json
        from version import __version__

        # 1. Check version.txt
        root_v_path = os.path.join(self.BASE_DIR, "version.txt")
        with open(root_v_path, "r", encoding="utf-8") as f:
            root_v = f.read().strip()
        self.assertEqual(
            root_v,
            __version__,
            f"version.txt ({root_v}) does not match version.py ({__version__})",
        )

        # 2. Check profile/version.txt
        prof_v_path = os.path.join(self.PROFILE_DIR, "version.txt")
        with open(prof_v_path, "r", encoding="utf-8") as f:
            prof_v = f.read().strip()
        self.assertEqual(
            prof_v,
            __version__,
            f"profile/version.txt ({prof_v}) does not match version.py ({__version__})",
        )

        # 3. Check server.json
        server_json_path = os.path.join(self.BASE_DIR, "server.json")
        with open(server_json_path, "r", encoding="utf-8") as f:
            server_data = json.load(f)
        self.assertEqual(
            server_data.get("profile_version"),
            __version__,
            f"server.json profile_version ({server_data.get('profile_version')}) does not match {__version__}",
        )
        self.assertEqual(
            server_data.get("credits", [{}])[0].get("version"),
            __version__,
            f"server.json credits version does not match {__version__}",
        )


if __name__ == "__main__":
    unittest.main()

