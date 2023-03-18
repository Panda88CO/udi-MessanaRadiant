#!/usr/bin/env python3

import time
import re
#from MessanaInfo import messana_info
from Messana_HotWater import messana_hot_water

try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)



#messana, controller, primary, address, name, nodeType, nodeNbr, messana
class udi_messana_hot_water(udi_interface.Node):
    from  udiLib import node_queue, wait_for_node_done, getValidName, getValidAddress, send_temp_to_isy, isy_value, send_rel_temp_to_isy

    id = 'dhw'

    '''
       drivers = [
            'GV0' = dhw status
            'CLITEMP' = Temperature
            'GV1' = Target Temperature
            'ST' = System Status
            ]
    '''
    
    
    drivers = [
        {'driver': 'GV0', 'value': 99, 'uom': 25},
        {'driver': 'CLITEMP', 'value': 99, 'uom': 25},
        {'driver': 'GV1', 'value': 99, 'uom': 25},
        {'driver': 'ST', 'value': 0, 'uom': 25},
        ]

    def __init__(self, polyglot, primary, address, name, dhw_nbr, messana_info):
        super().__init__(polyglot, primary, address, name)
        logging.info('init Messana dhw {}:'.format(dhw_nbr) )

        self.primary = primary  
        self.dhw_nbr = dhw_nbr
        self.dhw = messana_hot_water(self.dhw_nbr, messana_info)
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
        self.messana_temp_unit = self.dhw.messana_temp_unit

    def start(self):
        logging.info('udiMessanaHotWater Start ')
        self.updateISY_longpoll()

    def stop(self):
        logging.info('udiMessanaHotWater Stop ')

    def updateISY_shortpoll(self):
        Val = self.dhw.get_status()
        logging.debug('dhw Status (GV0): {}'.format(Val))
        self.node.setDriver('GV0', self.isy_value(Val))

        Val = self.dhw.get_temp()
        logging.debug('dhw get_temp(CLITEMP): {}'.format(Val))
        #self.node.setDriver('GV4', self.isy_value(Val), True, True)
        self.send_temp_to_isy(Val, 'CLITEMP')

        Val = self.dhw.get_target_temp()
        logging.debug('dhw get_target_temp (GV1): {}'.format(Val))
        self.node.setDriver('GV1', self.isy_value(Val))


    def updateISY_longpoll(self):
        logging.debug('update_system - dhw {} Status:'.format(self.dhw_nbr))

        Val = self.dhw.get_status()
        logging.debug('dhw Status (GV0): {}'.format(Val))
        self.node.setDriver('GV0', self.isy_value(Val))

        Val = self.dhw.get_temp()
        logging.debug('dhw get_temp(CLITEMP): {}'.format(Val))
        #self.node.setDriver('GV4', self.isy_value(Val), True, True)
        self.send_temp_to_isy(Val, 'CLITEMP')

        Val = self.dhw.get_target_temp()
        logging.debug('dhw get_target_temp (GV1): {}'.format(Val))
        self.node.setDriver('GV1', self.isy_value(Val))



    def set_status(self, command):
        status = int(command.get('value'))
        logging.debug('set Status Called {} for zone: {}'.format(status, self.dhw_nbr))
        if self.dhw.set_status(status):
            self.node.setDriver('GV0', status)
        else:
            logging.error('Error calling setStatus')

    def set_target_temp(self, command):
        mode = int(command.get('value'))
        logging.debug('set_dhw_target_temp Called {} for DHW {}'.format(mode, self.dhw_nbr))
        if self.dhw.set_target_temp(mode):
            self.node.setDriver('GV1', mode)
        else:
            logging.error('Error calling set_energy_save')        

    def update(self, command):
        logging.debug('update')
        self.updateISY_longpoll()


    commands = { 'UPDATE': update 
                ,'STATUS': set_status
                ,'TEMPMODE' : set_target_temp
                
                }
        