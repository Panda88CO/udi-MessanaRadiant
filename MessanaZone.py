#!/usr/bin/env python3
import time

try:
    import udi_interface
    logging = udi_interface.logging
    Custom = udi_interface.Custom

except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    #logging = logging.getlogging('testLOG')

#from subprocess import call
from MessanaInfo import messanaInfo

#messana, controller, primary, address, name, nodeType, nodeNbr, messana
class messanaZone(messanaInfo):
    def __init__(self, messanaIP, messanaKey, zoneNbr):
        super().__init__(messanaIP, messanaKey)
        logging.info('init Zone:' )
        
        self.node_type = 'zone'
        #self.IPaddress = IPaddress
        #self.apiKey = messanaKey
        self.node_nbr = zoneNbr
        self.stateList = [0,1]

        self.update_all()


    def update_active(self):
        logging.debug('update_active: zone:{}'.format(self.node_nbr ))
        self.update_temp()
        self.update_air_temp()
        self.update_humidity()
        self.update_air_quality()
        self.update_status()
        self.update_co2()
        self.update_thermal_status()


    def update_all(self):
        logging.debug('update_all: zone:{}'.format(self.node_nbr ))
        self.update_active()
        self.update_name()
        self.update_setpointCO2()
        self.update_setpoint()
        self.update_energy_saving()
        self.update_scheduleOn()
        self.update_status()


