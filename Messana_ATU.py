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

#from Messana_Info import messana_control
from Messana_Node import messana_node
#messana, controller, primary, address, name, nodeType, nodeNbr, messana
class messana_atu(messana_node):
    def __init__(self, atu_nbr, messana_info):
        super().__init__(messana_info, 'atu', atu_nbr)
        logging.info('init ATUs:' )
        self.type = 'atu'
        self.nbr = atu_nbr
        self.name = self.get_name()
        self.stateList = [0,1]
        self.messana_temp_unit = self.GET_system_data('tempUnit')
        
        #self.get_all()

    '''
    def __get_node_data(self, mKey):
        logging.debug('{} {} get_zone_data'.format(self.type, self.nbr ))
        return(self.messana.GET_node_data(mKey, self.type, self.nbr))

    def __put_node_data(self, mKey, value):
        logging.debug('{} {} get_name'.format(self.type, self.nbr ))
        return(self.messana.PUT_node_data(mKey, value, self.type, self.nbr))

    def get_name(self):
        logging.debug('{} {} get_name'.format(self.type, self.nbr ))
        return(self.__get_node_data('name'))

    def get_status(self):
        logging.debug('{} {} get_status'.format(self.type, self.nbr))    
        return(self.__get_node_data('status'))

    def set_status(self, state):
        logging.debug('{} {} - set_status {}'.format(self.type, self.nbr, state ))
        if self.__put_node_data('status', state ):
            time.sleep(0.5)
        return(self.get_status())


    def get_setpoint(self):
        logging.debug('{} {} - get_setpoint'.format(self.type, self.nbr))
        return(self.__get_node_data( 'setpoint'))


    def set_setpoint(self, setpoint):
        logging.debug('{} {} set_setpoint: {}'.format(self.type, self.nbr, setpoint ))
        if self.__put_node_data('setpoint', setpoint):
            time.sleep(0.5)
        return(self.get_setpoint())


    def get_temp(self):
        logging.debug('{} {} - get_temp'.format(self.type, self.nbr))
        return(self.__get_node_data('temperature'))


    def get_scheduleOn(self):
        logging.debug('{} {} - get_scheduleOn'.format(self.type, self.nbr))
        return(self.__get_node_data('scheduleOn'))



    def set_scheduleOn(self, state):
        logging.debug('{} {} set_scheduleOn {}'.format(self.type, self.nbr, state ))
        if self.__put_node_data('scheduleOn', state):
            time.sleep(0.5)
        return(self.get_scheduleOn())

    def get_antifreeze_setpoint(self):
        logging.debug('{} {} - get_antifreeze_setpoint'.format(self.type, self.nbr))
        return(self.__get_node_data('antifreezeSP'))



    def set_antifreeze_setpoint(self, af_sp):
        logging.debug('{} {} set_scheduleOn {}'.format(self.type, self.nbr, af_sp ))
        if self.__put_node_data('antifreezeSP', af_sp):
            time.sleep(0.5)
        return(self.get_scheduleOn())


    def get_humidity(self):
        logging.debug('{} {} - get_humidity'.format(self.type, self.nbr))
        return(self.__get_node_data('humidity'))

 


    def get_dewpoint(self):
        logging.debug('{} {} - get_dewpoint'.format(self.type, self.nbr))
        return( self.__get_node_data( 'dewpoint'))
  
   '''


    def get_active(self):
        logging.debug('get_active: zone:{}'.format(self.nbr ))
        self.get_temp()
        self.get_humidity()
        self.get_status()



    def get_all(self):
        logging.debug('get_all: zone:{}'.format(self.nbr ))
        self.get_active()
        self.get_name()
        self.get_setpoint()
        self.get_scheduleOn()
        self.get_status()

    
