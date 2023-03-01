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


def node_queue(self, data):
    self.n_queue.append(data['address'])

def wait_for_node_done(self):
    while len(self.n_queue) == 0:
        time.sleep(0.1)
    self.n_queue.pop()

def getValidName(name):
    name = bytes(name, 'utf-8').decode('utf-8','ignore')
    return re.sub(r"[^A-Za-z0-9_ ]", "", name)

# remove all illegal characters from node address
def getValidAddress(name):
    name = bytes(name, 'utf-8').decode('utf-8','ignore')
    return re.sub(r"[^A-Za-z0-9_]", "", name.lower()[:14])

def isy_value(value):
    if value == None:
        return (99)
    else:
        return(value)

def handleLevelChange(level):
    logging.info('New log level: {}'.format(level))
    logging.setLevel(level['level'])

def handleParams (self, userParam ):
    logging.debug('handleParams')
    self.Parameters.load(userParam)
    self.poly.Notices.clear()

def send_rel_temp_to_isy(self, temperature, stateVar):
    logging.debug('send_rel_temp_to_isy - {} {}'.format(temperature, stateVar))
    logging.debug('ISYunit={}, Mess_unit={}'.format(self.ISY_temp_unit , self.messana_temp_unit ))
    if self.ISY_temp_unit == 0: # Celsius in ISY
        if self.messana_temp_unit == 'Celsius' or self.messana_temp_unit == 0:
            temp = round(temperature,1),
        else: # messana = Farenheit
            temp = round(temperature*5/9,1)
        logging.debug('Celsius : {}  = {}'.format( temperature, temp ))  
        self.node.setDriver(stateVar, temp, True, True, 4)
    elif  self.ISY_temp_unit == 1: # Farenheit in ISY
        if self.messana_temp_unit == 'Celsius' or self.messana_temp_unit == 0:
            temp =  round((temperature*9/5),1)
        else:
            temp =  round(temperature,1)
        logging.debug('Farenheit : {}  = {}'.format( temperature, temp ))
        self.node.setDriver(stateVar, temp, True, True, 17)
    else: # kelvin
        if self.messana_temp_unit == 'Celsius' or self.messana_temp_unit == 0:
            temp = round(temperature,1)
        else:
            temp = round((temperature)*9/5,1)
        logging.debug('Kelvin : {}  = {}'.format( temperature, temp ))
        self.node.setDriver(stateVar, temp , True, True, 26)


def send_temp_to_isy(self, temperature, stateVar):
    logging.debug('send_temp_to_isy -{} {}'.format(temperature, stateVar ))
    logging.debug('ISYunit={}, Mess_unit={}'.format(self.ISY_temp_unit , self.messana_temp_unit ))
    if self.ISY_temp_unit == 0: # Celsius in ISY
        if self.messana_temp_unit == 'Celsius' or self.messana_temp_unit == 0:
            temp = round(temperature,1)
        else: # messana = Farenheit
            temp = round((temperature-32)*5/9,1)
        logging.debug('Celsius : {}  = {}'.format( temperature, temp ))  
        self.node.setDriver(stateVar, temp, True, True, 4)
    elif  self.ISY_temp_unit == 1: # Farenheit in ISY
        if self.messana_temp_unit == 'Celsius' or self.messana_temp_unit == 0:
            temp = round((temperature*9/5+32),1)
        else:
            temp = round(temperature,1)
        logging.debug('Farenheit : {}  = {}'.format( temperature, temp ))            
        self.node.setDriver(stateVar,temp , True, True, 17)
    else: # kelvin
        if self.messana_temp_unit == 'Celsius' or self.messana_temp_unit == 0:
            temp = round(temperature+273.15,1)
        else:
             temp = round((temperature+273.15-32)*9/5,1)
        logging.debug('Kelvin : {}  = {}'.format( temperature, temp ))
        self.node.setDriver(stateVar, temp, True, True, 26)


def convert_temp_unit(self, tempStr):
    if tempStr.capitalize()[:1] == 'F':
        return(1)
    elif tempStr.capitalize()[:1] == 'K':
        return(2)
    else:
        return(0)
