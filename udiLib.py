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
import re
import numbers

TEMP_C = 0
TEMP_F = 1

def node_queue(self, data):
    self.n_queue.append(data['address'])

def wait_for_node_done(self):
    while len(self.n_queue) == 0:
        time.sleep(0.1)
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
