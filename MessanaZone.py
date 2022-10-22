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

from MessanaInfo import messana_info

#messana, controller, primary, address, name, nodeType, nodeNbr, messana
class messana_zone(messana_info):
    def __init__(self, zoneNbr):
        super().__init__()
        logging.info('init Zone:' )
        self.node_type = 'zone'
        self.node_nbr = zoneNbr
        self.stateList = [0,1]

        #self.get_all()


    def get_name(self):
        logging.debug('get_name {}: {}'.format(self.node_type, self.node_nbr ))
        return(self.GET_node_data('name'))

    def get_status(self):
        logging.debug('get_status {}:  {}'.format(self.node_type, self.node_nbr))    
        return(self.GET_node_data('status'))


    def set_status(self, state):
        if state in self.stateList:
            self.PUT_node_data('status', state )
            time.sleep(0.5)
   
            return(self.get_status())
        else:
            logging.error ('Wrong Status state passed ([0,1]: {}'.format(state))
            return(False)
          
    '''
    def get_air_temp(self):
        return(self.GET_node_data(self.node_nbr , 'airTemperature'))

    def get_setpoint(self):
        temp = self.GET_node_data(self.node_nbr , 'setpoint')
        if temp:
            self.setpint = temp



    def set_setpoint(self, setpoint):
        if self.PUT_node_data(self.node_nbr , 'setpoint'):
            time.sleep(0.5)
            self.get_setpoint()
            return(self.setpoint)
        else:
            return   

    def get_temp(self):
        return(self.GET_node_data(self.node_nbr , 'temperature'))




    def get_scheduleOn(self):
        temp =  self.GET_node_data(self.node_nbr , 'scheduleOn')
        if temp:
            self.schedule_on = temp


    def set_scheduleOn(self, state):
        if self.PUT_node_data(self.node_nbr , 'scheduleOn', state):
            time.sleep(0.5)
            self.get_scheduleOn()
            return(True)
        else:
            return(False)



    def get_thermal_status(self):
        return( self.GET_node_data(self.node_nbr , 'thermalStatus'))



    def get_humidity(self):
        return( self.GET_node_data(self.node_nbr , 'humidity'))


    def get_air_quality(self):
        val = self.GET_node_data(self.node_nbr , 'airQuality')
        if val not in self.NaNlist:
            return(val['category'])
        else:
            return


    def get_setpointCO2(self):
        return( self.GET_node_data(self.node_nbr , 'setpointCO2'))

    def set_setpointCO2(self):
        if self.PUT_node_data(self.node_nbr , 'setpointCO2'):
            time.sleep(0.5)
            self.get_setpointCO2()
            return(self.setpointCO2)
        else:
            return


    def get_dewpoint(self):
        return( self.GET_node_data(self.node_nbr , 'dewpoint'))
  

    def get_energy_saving(self):
        temp = self.GET_node_data(self.node_nbr , 'energySaving')
        if temp:
            self.energy_saving = temp
       

    def set_energy_saving(self, state):
        if state in self.stateList:
            self.PUT_node_data(self.node_nbr ,'energySaving', state )
            self.get_energy_saving()
            return(self.energy_saving)
        else:
            logging.error ('Wrong enerySaving state passed ([0,1]: {}'.format(state))
            return(False)

    def get_co2(self):
        return(self.GET_node_data(self.node_nbr , 'co2'))





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

    '''
