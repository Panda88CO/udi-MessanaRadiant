#!/usr/bin/env python3

import time
import re
#from MessanaInfo import messana_info
from Messana_Fancoil import messana_fancoil

try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)



#messana, controller, primary, address, name, nodeType, nodeNbr, messana
class udi_messana_fancoil(udi_interface.Node):
    from  udiLib import node_queue, wait_for_node_done, getValidName, getValidAddress, send_temp_to_isy, isy_value, send_rel_temp_to_isy

    id = 'fancoil'

    '''
       drivers = [
            'GV0' = fancoil status
            'GV1' = Cooling Speed
            'GV2' = Heating Speed
            'GV3' = Fancoil Type
            'GV4' = Alarm
            'ST' = System Status
            ]
    '''
    
    
    drivers = [
        {'driver': 'GV0', 'value': 99, 'uom': 25},
        {'driver': 'GV1', 'value': 99, 'uom': 25},
        {'driver': 'GV2', 'value': 99, 'uom': 25},
        {'driver': 'GV3', 'value': 99, 'uom': 25},
        {'driver': 'GV4', 'value': 99, 'uom': 25},        
        {'driver': 'ST', 'value': 0, 'uom': 25},
        ]

    def __init__(self, polyglot, primary, address, name, fancoil_nbr, messana_info):
        super().__init__(polyglot, primary, address, name)
        logging.info('init Messana fancoil {}:'.format(fancoil_nbr) )

        self.primary = primary  
        self.fancoil_nbr = fancoil_nbr
        self.fancoil = messana_fancoil(self.fancoil_nbr, messana_info)
        self.address = address

        self.poly = polyglot
        #self.Parameters = Custom(self.poly, 'customparams')
        self.n_queue = []
        self.poly.subscribe(polyglot.START, self.start, self.address)
        self.poly.subscribe(polyglot.STOP, self.stop)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)

        
        logging.debug('setup node: {} {} {} {}'.format(self.address, name, self.id, self.primary))
        self.poly.ready()
        self.poly.addNode(self, conn_status='ST')
        self.wait_for_node_done()

        logging.debug('Drivers: {}'.format(self.drivers))
        logging.debug('address: {}'.format(self.address))
        self.node = self.poly.getNode(self.address)
        self.node.setDriver('ST', 1, True, True)
        self.ISY_temp_unit = messana_info['isy_temp_unit']
        self.messana_temp_unit = self.fancoil.messana_temp_unit

    def start(self):
        logging.info('udiMessanaFanCoil Start ')
        self.updateISY_longpoll()

    def stop(self):
        logging.info('udiMessanaFanCoil Stop ')

    def updateISY_shortpoll(self):
        Val = self.fancoil.get_status()
        logging.debug('fancoil Status (GV0): {}'.format(Val))
        self.node.setDriver('GV0', self.isy_value(Val))

        Val = self.fancoil.get_fancoil_heat_speed()
        logging.debug('Fancoil get_fancoil_heat_speed(GV2): {}'.format(Val))
        self.node.setDriver('GV2', self.isy_value(Val))

        Val = self.fancoil.get_fancoil_cool_speed()
        logging.debug('Fancoil get_fancoil_cool_speed(GV3): {}'.format(Val))
        self.node.setDriver('GV3', self.isy_value(Val))

        Val = self.fancoil.get_alarmOn()
        logging.debug('fancoil get_alarmOn(GV4): {}'.format(Val))
        #self.node.setDriver('GV4', self.isy_value(Val), True, True)
        self.send_temp_to_isy(Val, 'GV4')




    def updateISY_longpoll(self):
        logging.debug('update_system - Fancoil {} Status:'.format(self.fancoil_nbr))

        Val = self.fancoil.get_status()
        logging.debug('fancoil Status (GV0): {}'.format(Val))
        self.node.setDriver('GV0', self.isy_value(Val))

        Val = self.fancoil.get_fctype()
        logging.debug('get_fctype(GV3): {}'.format(Val))
        self.node.setDriver('GV3', self.isy_value(Val))

        Val = self.fancoil.get_fancoil_heat_speed()
        logging.debug('Fancoil get_fancoil_heat_speed(GV2): {}'.format(Val))
        self.node.setDriver('GV2', self.isy_value(Val))

        Val = self.fancoil.get_fancoil_cool_speed()
        logging.debug('Fancoil get_fancoil_cool_speed(GV3): {}'.format(Val))
        self.node.setDriver('GV3', self.isy_value(Val))

        Val = self.fancoil.get_alarmOn()
        logging.debug('fancoil get_alarmOn(GV4): {}'.format(Val))
        #self.node.setDriver('GV4', self.isy_value(Val), True, True)
        self.send_temp_to_isy(Val, 'GV4')



    def set_status(self, command):
        status = int(command.get('value'))
        logging.debug('set Status Called {} for FC: {}'.format(status, self.fancoil_nbr))
        temp = self.fancoil.set_status(status)
        if temp is not None:
            self.node.setDriver('GV0', temp)
        else:
            logging.error('Error calling setStatus')

    def set_heat_speed(self, command):
        speed = int(command.get('value'))
        logging.debug('set_heat_speed Called {} for FC {}'.format(speed, self.fancoil_nbr))
        temp = self.fancoil.set_fancoil_heat_speed(speed)
        if temp is not None:
            self.node.setDriver('GV1', temp)
        else:
            logging.error('Error calling set_energy_save')
        
    def set_cool_speed(self, command):
        speed = int(command.get('value'))
        logging.debug('set_cool_speed {} for FC {}'.format(speed, self.fancoil_nbr))   
        temp = self.fancoil.set_fancoil_cool_speed(speed)
        if temp is not None :
            self.node.setDriver('GV2', temp)
        else:
            logging.error('Error calling set_setpoint')

    def update(self, command):
        logging.debug('update')
        self.updateISY_longpoll()

    
    commands = { 'UPDATE': update 
                ,'STATUS': set_status
                ,'HEATSPEED' : set_heat_speed
                ,'COOLSPEED' : set_cool_speed     
                }
        