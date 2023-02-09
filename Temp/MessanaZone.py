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

#from MessanaInfo import messana_control

from Temp.MessanaNode import messana_node
#messana, controller, primary, address, name, nodeType, nodeNbr, messana
class messana_zone(messana_node):
    def __init__(self, zone_nbr, messana_info):
        super().__init__(messana_info, 'zone', zone_nbr)
        logging.info('init Zone:' )
        self.type = 'zone'
        self.nbr = zone_nbr
        self.name = self.get_name()
        #self.stateList = [0,1]
        self.messana_temp_unit = self.GET_system_data('tempUnit')
        #self.get_all()

    '''
    def __get_zone_data(self, mKey):
        logging.debug('{} {} get_zone_data'.format(self.type, self.nbr ))
        return(self.messana.GET_node_data(mKey, self.type, self.nbr))

    def __put_zone_data(self, mKey, value):
        logging.debug('{} {} get_name'.format(self.type, self.nbr ))
        return(self.messana.PUT_node_data(mKey, value, self.type, self.nbr))

    def get_name(self):
        logging.debug('{} {} get_name'.format(self.type, self.nbr ))
        return(self.__get_zone_data('name'))

    def get_status(self):
        logging.debug('{} {} get_status'.format(self.type, self.nbr))    
        return(self.__get_zone_data('status'))

    def set_status(self, state):
        logging.debug('{} {} - set_status {}'.format(self.type, self.nbr, state ))
        if self.__put_zone_data('status', state ):
            time.sleep(0.5)
        return(self.get_status())

    def get_air_temp(self):
        logging.debug('{} {} - get_air_temp'.format(self.type, self.nbr))
        return(self.__get_zone_data('airTemperature'))

    def get_setpoint(self):
        logging.debug('{} {} - get_setpoint'.format(self.type, self.nbr))
        return(self.__get_zone_data( 'setpoint'))


    def set_setpoint(self, setpoint):
        logging.debug('{} {} set_setpoint: {}'.format(self.type, self.nbr, setpoint ))
        if self.__put_zone_data('setpoint', setpoint):
            time.sleep(0.5)
        return(self.get_setpoint())


    def get_temp(self):
        logging.debug('{} {} - get_temp'.format(self.type, self.nbr))
        return(self.__get_zone_data('temperature'))


    def get_scheduleOn(self):
        logging.debug('{} {} - get_scheduleOn'.format(self.type, self.nbr))
        return(self.__get_zone_data('scheduleOn'))



    def set_scheduleOn(self, state):
        logging.debug('{} {} set_scheduleOn {}'.format(self.type, self.nbr, state ))
        if self.__put_zone_data('scheduleOn', state):
            time.sleep(0.5)
        return(self.get_scheduleOn())



    def get_thermal_status(self):
        logging.debug('{} {} - get_thermal_status'.format(self.type, self.nbr))
        return( self.__get_zone_data('thermalStatus'))



    def get_humidity(self):
        logging.debug('{} {} - get_humidity'.format(self.type, self.nbr))
        return(self.__get_zone_data('humidity'))


    def get_air_quality(self):
        logging.debug('{} {} - get_air_quality'.format(self.type, self.nbr))
        val = self.__get_zone_data('airQuality')
        logging.debug('Air quality;{}'.format(val))
        return( 0)
        #if val not in self.messana.NaNlist:
        #    return(val['category'])
        #else:
        #    return None

    def get_setpointCO2(self):
        logging.debug('{} {} - get_setpointCO2'.format(self.type, self.nbr))
        return( self.__get_zone_data('setpointCO2'))

    def set_setpointCO2(self, set_co2):
        logging.debug('{} {} set_setpointCO2: {}'.format(self.type, self.nbr, set_co2 ))
        if self.__put_zone_data('setpointCO2', set_co2):
            time.sleep(0.5)
        return(self.get_setpointCO2())


    def get_dewpoint(self):
        logging.debug('{} {} - get_dewpoint'.format(self.type, self.nbr))
        return( self.__get_zone_data( 'dewpoint'))
  

    def get_energy_saving(self):
        logging.debug('{} {} - get_energy_saving'.format(self.type, self.nbr))
        return(self.__get_zone_data('energySaving'))

       

    def set_energy_saving(self, energy_save):
        logging.debug('{} {} set_setpointCO2: {}'.format(self.type, self.nbr, energy_save ))
        if self.__put_zone_data('energySaving', energy_save ):
            time.sleep(0.5)
        return(self.get_energy_saving())

    def get_co2(self):
        logging.debug('{} {} - get_co2'.format(self.type, self.nbr))
        return(self.__get_zone_data('co2'))


    def get_alarmOn(self):
        logging.debug('{} {} -get_alarmOn'.format(self.type, self.nbr))
        return(self.__get_zone_data('alarmOn'))

    '''

    def get_active(self):
        logging.debug('get_active: zone:{}'.format(self.nbr ))
        self.get_temp()
        self.get_air_temp()
        self.get_humidity()
        self.get_air_quality()
        self.get_status()
        self.get_co2()
        self.get_thermal_status()


    def get_all(self):
        logging.debug('get_all: zone:{}'.format(self.nbr ))
        self.get_active()
        self.get_name()
        self.get_setpointCO2()
        self.get_setpoint()
        self.get_energy_saving()
        self.get_scheduleOn()
        self.get_status()

    
