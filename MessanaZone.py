#!/usr/bin/env python3
import time
import os
try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    if (os.path.exists('./debug1.log')):
        os.remove('./debug1.log')
    import logging
    import sys
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] [%(threadName)s] %(message)s",
    handlers=[
        logging.FileHandler("debug1.log"),
        logging.StreamHandler(sys.stdout) ]
    )

from MessanaInfo import messana_system

#messana, controller, primary, address, name, nodeType, nodeNbr, messana
class messana_zone(messana_system):
    def __init__(self, zoneNbr):
        logging.info('init Zone:' )
        self.node_type = 'zone'
        self.node_nbr = zoneNbr
        self.name = self.get_name()
        self.stateList = [0,1]

        #self.get_all()


    def get_name(self):
        logging.debug('{} {} get_name'.format(self.node_type, self.node_nbr ))
        return(self.GET_node_data('name'))

    def get_status(self):
        logging.debug('{} {} get_status'.format(self.node_type, self.node_nbr))    
        return(self.GET_node_data('status'))

    def set_status(self, state):
        logging.debug('{} {} - set_status {}'.format(self.node_type, self.node_nbr, state ))
        if self.PUT_node_data('status', state ):
            time.sleep(0.5)
        return(self.get_status())

    def get_air_temp(self):
        logging.debug('{} {} - get_air_temp'.format(self.node_type, self.node_nbr))
        return(self.GET_node_data('airTemperature'))

    def get_setpoint(self):
        logging.debug('{} {} - get_setpoint'.format(self.node_type, self.node_nbr))
        return(self.GET_node_data( 'setpoint'))


    def set_setpoint(self, setpoint):
        logging.debug('{} {} set_setpoint: {}'.format(self.node_type, self.node_nbr, setpoint ))
        if self.PUT_node_data('setpoint', setpoint):
            time.sleep(0.5)
        return(self.get_setpoint())


    def get_temp(self):
        logging.debug('{} {} - get_temp'.format(self.node_type, self.node_nbr))
        return(self.GET_node_data('temperature'))


    def get_scheduleOn(self):
        logging.debug('{} {} - get_scheduleOn'.format(self.node_type, self.node_nbr))
        return(self.GET_node_data('scheduleOn'))



    def set_scheduleOn(self, state):
        logging.debug('{} {} set_scheduleOn {}'.format(self.node_type, self.node_nbr, state ))
        if self.PUT_node_data('scheduleOn', state):
            time.sleep(0.5)
        return(self.get_scheduleOn())



    def get_thermal_status(self):
        logging.debug('{} {} - get_thermal_status'.format(self.node_type, self.node_nbr))
        return( self.GET_node_data('thermalStatus'))



    def get_humidity(self):
        logging.debug('{} {} - get_humidity'.format(self.node_type, self.node_nbr))
        return( self.GET_node_data('humidity'))


    def get_air_quality(self):
        logging.debug('{} {} - get_air_quality'.format(self.node_type, self.node_nbr))
        val = self.GET_node_data('airQuality')
        if val not in self.NaNlist:
            return(val['category'])
        else:
            return None

    def get_setpointCO2(self):
        logging.debug('{} {} - get_setpointCO2'.format(self.node_type, self.node_nbr))
        return( self.GET_node_data('setpointCO2'))

    def set_setpointCO2(self, set_co2):
        logging.debug('{} {} set_setpointCO2: {}'.format(self.node_type, self.node_nbr, set_co2 ))
        if self.PUT_node_data('setpointCO2', set_co2):
            time.sleep(0.5)
        return(self.get_setpointCO2())


    def get_dewpoint(self):
        logging.debug('{} {} - get_dewpoint'.format(self.node_type, self.node_nbr))
        return( self.GET_node_data( 'dewpoint'))
  

    def get_energy_saving(self):
        logging.debug('{} {} - get_energy_saving'.format(self.node_type, self.node_nbr))
        return(self.GET_node_data('energySaving'))

       

    def set_energy_saving(self, energy_save):
        logging.debug('{} {} set_setpointCO2: {}'.format(self.node_type, self.node_nbr, energy_save ))
        if self.PUT_node_data('energySaving', energy_save ):
            time.sleep(0.5)
        return(self.get_energy_saving())

    def get_co2(self):
        logging.debug('{} {} - get_co2'.format(self.node_type, self.node_nbr))
        return(self.GET_node_data('co2'))


    def get_alarmOn(self):
        logging.debug('{} {} -get_alarmOn'.format(self.node_type, self.node_nbr))
        return(self.GET_node_data('alarmOn')) 


    def get_active(self):
        logging.debug('get_active: zone:{}'.format(self.node_nbr ))
        self.get_temp()
        self.get_air_temp()
        self.get_humidity()
        self.get_air_quality()
        self.get_status()
        self.get_co2()
        self.get_thermal_status()


    def get_all(self):
        logging.debug('get_all: zone:{}'.format(self.node_nbr ))
        self.get_active()
        self.get_name()
        self.get_setpointCO2()
        self.get_setpoint()
        self.get_energy_saving()
        self.get_scheduleOn()
        self.get_status()

    
