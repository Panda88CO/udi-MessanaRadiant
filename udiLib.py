#!/usr/bin/env python3
try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom

except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    #logging = logging.getlogging('testLOG')
import time
import os
import re
import numbers
import xml.etree.ElementTree as ET

TEMP_C = 0
TEMP_F = 1

def node_queue(self, data):
    self.n_queue.append(data['address'])

def wait_for_node_done(self):
    count = 0
    while len(self.n_queue) == 0 and count < 50:
        time.sleep(0.1)
        count += 1
    if len(self.n_queue) > 0:
        self.n_queue.pop()

def getValidName(self, name):
    name = bytes(name, 'utf-8').decode('utf-8','ignore')
    return re.sub(r"[^A-Za-z0-9_ ]", "", name)

# remove all illegal characters from node address
def getValidAddress(self, name):
    name = bytes(name, 'utf-8').decode('utf-8','ignore')
    return re.sub(r"[^A-Za-z0-9_]", "", name.lower()[:14])

def isy_value(self, value):
    if value == None:
        return (99)
    elif not (isinstance (value, numbers.Number)):
        return(98)
    else:
        return(value)

def handleLevelChange(self, level):
    logging.info('New log level: {}'.format(level))
    logging.setLevel(level['level'])

def handleParams (self, userParam ):
    logging.debug('handleParams')
    self.Parameters.load(userParam)
    self.poly.Notices.clear()

def send_rel_temp_to_isy(self, temperature, stateVar):
    logging.debug('send_rel_temp_to_isy - {} {}'.format(temperature, stateVar))
    logging.debug('ISYunit={}, Mess_unit={}'.format(self.ISY_temp_unit , self.messana_temp_unit ))
    if temperature is None:
        return False
    if self.ISY_temp_unit == TEMP_C: # Celsius in ISY
        if self.messana_temp_unit == 'Celsius' or self.messana_temp_unit == TEMP_C:
            temp = round(temperature, 1)
        else: # messana = Farenheit
            temp = round(temperature*5/9,1)
        logging.debug('Celsius : {}  = {}'.format( temperature, temp ))  
        self.node.setDriver(stateVar, temp, True, True, 4)
        return True
    elif  self.ISY_temp_unit == TEMP_F: # Farenheit in ISY
        if self.messana_temp_unit == 'Celsius' or self.messana_temp_unit == TEMP_C:
            temp =  round((temperature*9/5),1)
        else:
            temp =  round(temperature,1)
        logging.debug('Farenheit : {}  = {}'.format( temperature, temp ))
        self.node.setDriver(stateVar, temp, True, True, 17)
        return True
    else:
        logging.error('Wring temp unit: {}'.format(self.ISY_temp_unit))
        return False


def send_temp_to_isy(self, temperature, stateVar):
    logging.debug('send_temp_to_isy -{} {}'.format(temperature, stateVar ))
    logging.debug('ISYunit={}, Mess_unit={}'.format(self.ISY_temp_unit , self.messana_temp_unit ))
    if temperature is None:
        return False
    if self.ISY_temp_unit == TEMP_C: # Celsius in ISY
        if self.messana_temp_unit == 'Celsius' or self.messana_temp_unit == TEMP_C:
            temp = round(temperature,1)
        else: # messana = Farenheit
            temp = round((temperature-32)*5/9,1)
        logging.debug('Celsius : {}  = {}'.format( temperature, temp ))  
        self.node.setDriver(stateVar, temp, True, True, 4)
        return True
    elif  self.ISY_temp_unit == TEMP_F: # Farenheit in ISY
        if self.messana_temp_unit == 'Celsius' or self.messana_temp_unit == TEMP_C:
            temp = round((temperature*9/5+32),1)
        else:
            temp = round(temperature,1)
        logging.debug('Farenheit : {}  = {}'.format( temperature, temp ))            
        self.node.setDriver(stateVar,temp , True, True, 17)
        return True
    else:
        logging.error('Wring temp unit: {}'.format(self.ISY_temp_unit))
        return False

def convert_temp_unit(self, tempStr):
    if tempStr.capitalize()[:1] == 'F':
        return(TEMP_F)
    else:
        return(TEMP_C)

def get_command_value(*args):
    """Safely extract parameter value from a PG3 command dictionary."""
    if not args:
        return None
    command = args[-1]
    if not isinstance(command, dict):
        return None
    val = command.get('value')
    if val is not None:
        logging.debug('get_command_value extracted value {} from {}'.format(val, command))
        return val
    query = command.get('query')
    if isinstance(query, dict) and query:
        val = query.get('')
        if val is not None:
            logging.debug('get_command_value extracted query[""] {} from {}'.format(val, command))
            return val
        val = query.get('value')
        if val is not None:
            logging.debug('get_command_value extracted query["value"] {} from {}'.format(val, command))
            return val
        for k, v in query.items():
            if v is not None:
                logging.debug('get_command_value extracted query[{}] {} from {}'.format(k, v, command))
                return v
    logging.debug('get_command_value found no value in {}'.format(command))
    return None

def convert_temp_to_messana(self, isy_temp):
    """Convert a temperature from ISY units to Messana units."""
    if isy_temp is None:
        return None
    try:
        val = float(isy_temp)
    except (ValueError, TypeError):
        return None

    is_isy_c = (getattr(self, 'ISY_temp_unit', TEMP_C) == TEMP_C)
    mess_unit = getattr(self, 'messana_temp_unit', 'Celsius')
    is_mess_c = (mess_unit == 'Celsius' or mess_unit == TEMP_C)

    if is_isy_c and not is_mess_c:
        res = round(val * 9 / 5 + 32, 1)
    elif not is_isy_c and is_mess_c:
        res = round((val - 32) * 5 / 9, 1)
    else:
        res = round(val, 1)
    logging.debug('convert_temp_to_messana: {} (ISY unit: {}) -> {} (Messana unit: {})'.format(
        isy_temp, getattr(self, 'ISY_temp_unit', None), res, mess_unit
    ))
    return res

def convert_rel_temp_to_messana(self, isy_diff):
    """Convert a relative temperature difference from ISY units to Messana units."""
    if isy_diff is None:
        return None
    try:
        val = float(isy_diff)
    except (ValueError, TypeError):
        return None

    is_isy_c = (getattr(self, 'ISY_temp_unit', TEMP_C) == TEMP_C)
    mess_unit = getattr(self, 'messana_temp_unit', 'Celsius')
    is_mess_c = (mess_unit == 'Celsius' or mess_unit == TEMP_C)

    if is_isy_c and not is_mess_c:
        res = round(val * 9 / 5, 1)
    elif not is_isy_c and is_mess_c:
        res = round(val * 5 / 9, 1)
    else:
        res = round(val, 1)
    logging.debug('convert_rel_temp_to_messana: delta {} (ISY unit: {}) -> delta {} (Messana unit: {})'.format(
        isy_diff, getattr(self, 'ISY_temp_unit', None), res, mess_unit
    ))
    return res


_profile_driver_names = None


def clear_profile_driver_names_cache():
    """Clear the cached profile driver names mapping."""
    global _profile_driver_names
    _profile_driver_names = None


def get_profile_driver_names(temp_unit=None, force_refresh=False):
    """
    Extract the mapping of (nodeDefId, driver_id) -> display name.
    1. First tries dynamic profile definitions (profile_def.build_profile_definition).
    2. If dynamic profile is not available or does not contain the driver,
       falls back to the static profile directory (profile/nodedef/nodedefs.xml and profile/nls/en_us.txt).
    Cached after the first load.
    """
    global _profile_driver_names
    if _profile_driver_names is not None and not force_refresh:
        return _profile_driver_names

    _profile_driver_names = {}

    # 1. First try dynamic JSON profile definitions
    try:
        from profile_def import build_profile_definition
        dp = build_profile_definition(temp_unit if temp_unit is not None else TEMP_C)
        for nd in dp.get('nodedefs', []):
            nid = nd.get('id')
            for prop in nd.get('properties', []):
                driver_id = prop.get('id')
                name = prop.get('name')
                if nid and driver_id and name:
                    _profile_driver_names[(nid, driver_id)] = name
    except Exception as e:
        logging.debug(f'Could not load driver names from dynamic profile: {e}')

    # 2. If not available or missing definitions, fall back to profile directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    xml_path = os.path.join(base_dir, 'profile', 'nodedef', 'nodedefs.xml')
    nls_path = os.path.join(base_dir, 'profile', 'nls', 'en_us.txt')

    if os.path.exists(xml_path) and os.path.exists(nls_path):
        try:
            st_labels = {}
            with open(nls_path, 'r', encoding='utf-8') as f:
                for line in f:
                    m = re.match(r'^ST-([\w\-]+)-([\w\-]+)-NAME\s*=\s*(.+)', line.strip())
                    if m:
                        nls, driver, label = m.groups()
                        st_labels[(nls, driver)] = label.strip()

            tree = ET.parse(xml_path)
            root = tree.getroot()
            for node_def in root.findall('.//nodeDef'):
                node_id = node_def.get('id')
                nls = node_def.get('nls')
                if not node_id or not nls:
                    continue
                for st in node_def.findall('.//st'):
                    driver_id = st.get('id')
                    if driver_id and (nls, driver_id) in st_labels:
                        key = (node_id, driver_id)
                        if key not in _profile_driver_names:
                            _profile_driver_names[key] = st_labels[(nls, driver_id)]
        except Exception as e:
            logging.warning(f'Could not load driver names from static profile directory: {e}')

    return _profile_driver_names


def apply_profile_driver_names(self, node_id=None):
    """
    Populate or update 'name' in each driver dictionary of a node instance
    using definitions extracted from dynamic profiles or profile directory.
    Can be invoked as node.apply_profile_driver_names() or apply_profile_driver_names(node).
    """
    target_id = node_id or getattr(self, 'id', None)
    if not target_id:
        return
    drivers_list = getattr(self, 'drivers', None)
    if not drivers_list or not isinstance(drivers_list, list):
        return

    names = get_profile_driver_names()
    for d in drivers_list:
        if not isinstance(d, dict):
            continue
        driver_id = d.get('driver')
        if not driver_id:
            continue
        if (target_id, driver_id) in names:
            d['name'] = names[(target_id, driver_id)]
        elif str(target_id).startswith('ZONE') and ('ZONE', driver_id) in names:
            d['name'] = names[('ZONE', driver_id)]

