"""
Mock helper for testing udi-MessanaRadiant.

Sets up mocks for udi_interface and requests if not already present in the environment.
Provides helper factories for Polyglot interfaces, nodes, and HTTP responses.
"""

import sys
from unittest.mock import MagicMock

# 1. Stub udi_interface if not installed
if "udi_interface" not in sys.modules:
    try:
        import udi_interface
    except ImportError:
        udi_mock = MagicMock()

        class MockNode:
            def __init__(self, polyglot, primary, address, name):
                self.poly = polyglot
                self.primary = primary
                self.address = address
                self.name = name
                self.drivers_values = {}

            def setDriver(self, driver, value, report=True, force=False, uom=None):
                self.drivers_values[driver] = {"value": value, "uom": uom}

            def getDriver(self, driver):
                if driver in self.drivers_values:
                    return self.drivers_values[driver]["value"]
                return None

            def reportCmd(self, cmd, value=None):
                pass

        udi_mock.Node = MockNode
        udi_mock.LOGGER = MagicMock()

        class MockCustom:
            def __init__(self, poly, name):
                self.poly = poly
                self.name = name
                self._data = {}

            def __getitem__(self, key):
                return self._data.get(key)

            def __setitem__(self, key, val):
                self._data[key] = val

            def __contains__(self, key):
                return key in self._data

            def load(self, params):
                self._data.update(params)

            def clear(self):
                self._data.clear()

            def delete(self, key):
                self._data.pop(key, None)

        udi_mock.Custom = MockCustom
        udi_mock.Interface = MagicMock
        sys.modules["udi_interface"] = udi_mock


# 2. Stub requests if not installed
if "requests" not in sys.modules:
    try:
        import requests
    except ImportError:
        requests_mock = MagicMock()
        sys.modules["requests"] = requests_mock


def create_mock_polyglot():
    """Create a mock polyglot controller instance."""
    poly = MagicMock()
    poly.START = "start"
    poly.STOP = "stop"
    poly.LOGLEVEL = "loglevel"
    poly.CUSTOMPARAMS = "customparams"
    poly.POLL = "poll"
    poly.ADDNODEDONE = "addnodedone"
    poly.CONFIGDONE = "configdone"

    nodes_dict = {}

    def addNode(node, conn_status=None):
        nodes_dict[node.address] = node
        # simulate node_queue callback
        if hasattr(node, "node_queue"):
            node.node_queue({"address": node.address})
        return node

    poly.addNode.side_effect = addNode
    poly.getNode.side_effect = lambda addr: nodes_dict.get(addr)
    poly.getNodes.side_effect = lambda: dict(nodes_dict)
    poly.getValidAddress.side_effect = lambda addr: addr[:14]
    poly.getValidName.side_effect = lambda name: name
    poly.Notices = MagicMock()

    return poly


def create_mock_response(status_code=200, json_data=None):
    """Create a mock requests.Response object."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.__str__.return_value = f"<Response [{status_code}]>"
    if json_data is not None:
        resp.json.return_value = json_data
    else:
        resp.json.return_value = {}
    return resp


def sample_messana_info(temp_unit=0):
    """Return standard test messana_info dict."""
    return {
        "ip_address": "192.168.1.100",
        "api_key": "test_api_key_12345",
        "isy_temp_unit": temp_unit,
    }

