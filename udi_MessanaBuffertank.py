#!/usr/bin/env python3

import time
import re
#from MessanaInfo import messana_info
from Messana_Buffertank import messana_buffertank

try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)



#messana, controller, primary, address, name, nodeType, nodeNbr, messana
class udi_messana_buffertank(udi_interface.Node):
    from  udiLib import node_queue, wait_for_node_done, getValidName, getValidAddress, send_temp_to_isy, isy_value, send_rel_temp_to_isy

    id = 'buffertank'

    '''
       drivers = [
            'GV0' = buffertank status
            'GV1' = mode
            'GV2' = Temp mpde
            'CLITEMP' = air_temp
            'ST' = System Status
            ]
    '''
    
    
    drivers = [
        {'driver': 'GV0', 'value': 99, 'uom': 25},
        {'driver': 'GV1', 'value': 99, 'uom': 25},
        {'driver': 'GV2', 'value': 99, 'uom': 25},
        {'driver': 'CLITEMP', 'value': 99, 'uom': 25},
        {'driver': 'ST', 'value': 0, 'uom': 25},
        ]

    def __init__(self, polyglot, primary, address, name, buffertank_nbr, messana_info):
        super().__init__(polyglot, primary, address, name)
        logging.info('init Messana buffertank {}:'.format(buffertank_nbr) )

        self.primary = primary  
        self.buffertank_nbr = buffertank_nbr
        self.buffertank = messana_buffertank(self.buffertank_nbr, messana_info)
        self.address =self.getValidAddress(address)
        tmp_name = self.buffertank.name
        self.name = self.getValidName(tmp_name)
        self.poly = polyglot
        #self.Parameters = Custom(self.poly, 'customparams')
        self.n_queue = []
        self.poly.subscribe(polyglot.START, self.start, self.address)
        self.poly.subscribe(polyglot.STOP, self.stop)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)

        
        logging.debug('setup node: {} {} {} {}'.format(self.address, self.name, self.id, self.primary))
        self.poly.ready()
        self.poly.addNode(self, conn_status='ST')
        self.wait_for_node_done()

        logging.debug('Drivers: {}'.format(self.drivers))
        logging.debug('address: {}'.format(self.address))
        self.node = self.poly.getNode(self.address)
        self.node.setDriver('ST', 1, True, True)
        self.ISY_temp_unit = messana_info['isy_temp_unit']
        self.messana_temp_unit = self.buffertank.messana_temp_unit

    def start(self):
        logging.info('udiMessanaZone Start ')
        self.updateISY_longpoll()

    def stop(self):
        logging.info('udiMessanaZone Stop ')

    def updateISY_shortpoll(self):
        Val = self.buffertank.get_status()
        logging.debug('buffertank Status (GV0): {}'.format(Val))
        self.node.setDriver('GV0', self.isy_value(Val))

        Val = self.buffertank.get_temp()
        logging.debug('get_temp(CLITEMP): {}'.format(Val))
        #self.node.setDriver('GV4', self.isy_value(Val), True, True)
        self.send_temp_to_isy(Val, 'CLITEMP')




    def updateISY_longpoll(self):
        logging.debug('update_system - zone {} Status:'.format(self.buffertank_nbr))

        Val = self.buffertank.get_status()
        logging.debug('buffertank Status (GV0): {}'.format(Val))
        self.node.setDriver('GV0', self.isy_value(Val))

        Val = self.buffertank.get_buffertank_mode()
        logging.debug('buffertank temp(GV1): {}'.format(Val))
        self.node.setDriver('GV1', self.isy_value(Val))

        Val = self.buffertank.get_buffertank_temp_mode()
        logging.debug('Schedule Mode(GV2): {}'.format(Val))
        self.node.setDriver('GV2', self.isy_value(Val))

        Val = self.buffertank.get_temp()
        logging.debug('get_temp(CLITEMP): {}'.format(Val))
        #self.node.setDriver('GV4', self.isy_value(Val), True, True)
        self.send_temp_to_isy(Val, 'CLITEMP')



    def set_status(self, command):
        status = int(command.get('value'))
        logging.debug('set Status Called {} for zone: {}'.format(status, self.buffertank_nbr))
        if self.buffertank.set_status(status):
            self.node.setDriver('GV0', status)
        else:
            logging.error('Error calling setStatus')

    def set_buffertank_mode(self, command):
        mode = int(command.get('value'))
        logging.debug('set_buffertank_mode Called {} for BT {}'.format(mode, self.buffertank_nbr))
        if self.buffertank.set_buffertank_mode(mode):
            self.node.setDriver('GV1', mode)
        else:
            logging.error('Error calling set_energy_save')
        
    def set_buffertank_temp_mode(self, command):
        mode = int(command.get('value'))
        logging.debug('set_buffertank_temp_mode {} for BT {}'.format(mode, self.buffertank_nbr))   
        if self.buffertank.set_buffertank_temp_mode(mode):
            self.node.setDriver('GV2', mode)
        else:
            logging.error('Error calling set_setpoint')


    
    commands = { 'UPDATE': updateISY_longpoll
                ,'STATUS': set_status
                #,'ENERGYSAVE': set_energy_save
                ,'MODE' : set_buffertank_mode
                ,'TEMPMODE' : set_buffertank_temp_mode        
     #           ,'SCHEDULEON' : set_schedule
                
                }
        