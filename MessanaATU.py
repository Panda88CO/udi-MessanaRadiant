#!/usr/bin/env python3
import time

try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom

except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    #logging = logging.getlogging('testLOG')

#from subprocess import call
from Temp.MessanaInfo import messana_control

#messana, controller, primary, address, name, nodeType, nodeNbr, messana
class messanaAtu(messana_control):
    def __init__(self, messanaIP, messanaKey, atuNbr):
        super().__init__(messanaIP, messanaKey)
        logging.info('init Zone:' )
        self.node_type = 'atu'
        #self.IPaddress = IPaddress
        #self.apiKey = messanaKey
        #self.node_nbr  = atuNbr
        self.node_nbr = atuNbr
        self.stateList = [0,1]

        #self.update_all()


def update_active(self):
    logging.debug('update_active: atu:{}'.format(self.node_nbr ))
    self.air_temp = self.update_air_temp()


def update_all(self):
    logging.debug('update_active: atu:{}'.format(self.node_nbr ))

def update_air_temp(self):
    logging.debug('update_air_temp: atu:{}'.format(self.node_nbr ))
    temp = self.GET_node_data(self.node_nbr , 'airTemperature')
    if temp:
        self.air_temp = temp

def update_alarmOn(self):
    logging.debug('update_alarmOn: atu:{}'.format(self.node_nbr ))
    temp = self.GET_node_data(self.node_nbr , 'alarmOn')
    if temp:
        self.alarmOn = temp


def update_humidificationStatus(self):
    logging.debug('update_humidificationStatus: atu:{}'.format(self.node_nbr ))
    temp = self.GET_node_data(self.node_nbr , 'humidificationStatus')
    if temp:
        self.humidification_status = temp

def update_humOn(self):
    logging.debug('update_humOn: atu:{}'.format(self.node_nbr ))
    temp = self.GET_node_data(self.node_nbr , 'humOn')
    if temp:
        self.humOn = temp

def update_intOn(self):
    logging.debug('update_intOn: atu:{}'.format(self.node_nbr ))
    temp = self.GET_node_data(self.node_nbr , 'intOn')
    if temp:
        self.intOn = temp

def update_hrvOn(self):
    logging.debug('update_hrvOn: atu:{}'.format(self.node_nbr ))
    temp = self.GET_node_data(self.node_nbr , 'hrvOn')
    if temp:
        self.hrvOn = temp

def update_hrvStatus(self):
    logging.debug('update_hrvStatus: atu:{}'.format(self.node_nbr ))
    temp = self.GET_node_data(self.node_nbr , 'hrvStatus')
    if temp:
        self.hrvStatus = temp


def update_ntdOn(self):
    logging.debug('update_ntdOn: atu:{}'.format(self.node_nbr ))
    temp = self.GET_node_data(self.node_nbr , 'ntdOn')
    if temp:
        self.hrvOn = temp



def update_status(self):
    logging.debug('update_status: atu:{}'.format(self.node_nbr ))
    temp = self.GET_node_data(self.node_nbr , 'status')
    if temp:
        self.status = temp

def set_status(self, state):
        if state in self.stateList:
            self.PUT_node_data(self.node_nbr ,'status', state )
            time.sleep(0.5)
            self.status = self.update_status()
            return(self.status)
        else:
            logging.error ('Wrong Status state passed ([0,1]: {}'.format(state))
            return(False)


def update_flowLEvel(self):
    logging.debug('update_flowLevel: atu:{}'.format(self.node_nbr ))
    temp = self.GET_node_data(self.node_nbr , 'flowLEvel')
    if temp:
        self.flow_level = temp        
                