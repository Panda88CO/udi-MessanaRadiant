#!/usr/bin/env python3

import time
import re
#from MessanaInfo import messana_info
from Messana_EnergySource import messana_energy_source

try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)



#messana, controller, primary, address, name, nodeType, nodeNbr, messana
class udi_messana_energy_source(udi_interface.Node):
    from  udiLib import node_queue, wait_for_node_done, getValidName, getValidAddress, send_temp_to_isy, isy_value, send_rel_temp_to_isy

    id = 'energy_source'

    '''
       drivers = [
            'GV0' = energy_source status
            'GV1' = hotWater status
            'GV2' = energy_source Type
            'GV3' = Alarm
            'ST' = System Status
            ]
    '''
    
    
    drivers = [
        {'driver': 'GV0', 'value': 99, 'uom': 25},
        {'driver': 'GV1', 'value': 99, 'uom': 25},
        {'driver': 'GV2', 'value': 99, 'uom': 25},
        {'driver': 'GV3', 'value': 99, 'uom': 25},        
        {'driver': 'ST', 'value': 0, 'uom': 25},
        ]

    def __init__(self, polyglot, primary, address, name, energy_source_nbr, messana_info):
        super().__init__(polyglot, primary, address, name)
        logging.info('init Messana energy_source {}:'.format(energy_source_nbr) )

        self.primary = primary  
        self.energy_source_nbr = energy_source_nbr
        self.energy_source = messana_energy_source(self.energy_source_nbr, messana_info)
        self.address =self.getValidAddress(address)
        tmp_name = self.energy_source.name
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
        self.messana_temp_unit = self.energy_source.messana_temp_unit

    def start(self):
        logging.info('udiMessana Energy Source Start ')
        self.updateISY_longpoll()

    def stop(self):
        logging.info('udiMessana Energy Source  Stop ')

    def updateISY_shortpoll(self):
        Val = self.energy_source.get_status()
        logging.debug('energy_source Status (GV0): {}'.format(Val))
        self.node.setDriver('GV0', self.isy_value(Val))

        Val = self.energy_source.get_energy_source_dhwStatus()
        logging.debug('get_energy_source_dhwStatus(GV1): {}'.format(Val))
        self.node.setDriver('GV1', self.isy_value(Val))

        Val = self.energy_source.get_alarmOn()
        logging.debug('energy_source get_alarmOn(GV3): {}'.format(Val))
        self.node.setDriver('GV3', self.isy_value(Val))




    def updateISY_longpoll(self):
        logging.debug('update_system - Energy Source {} Status:'.format(self.energy_source_nbr))

        Val = self.energy_source.get_status()
        logging.debug('energy_source Status (GV0): {}'.format(Val))
        self.node.setDriver('GV0', self.isy_value(Val))

        Val = self.energy_source.get_energy_source_dhwStatus()
        logging.debug('get_energy_source_dhwStatus(GV2): {}'.format(Val))
        self.node.setDriver('GV1', self.isy_value(Val))

        Val = self.energy_source.get_energy_source_type()
        logging.debug('get_energy_source_type(GV2): {}'.format(Val))
        self.node.setDriver('GV2', self.isy_value(Val))

        Val = self.energy_source.get_alarmOn()
        logging.debug('energy_source get_alarmOn(GV3): {}'.format(Val))
        self.node.setDriver('GV3', self.isy_value(Val))







    
    commands = { 'UPDATE': updateISY_longpoll

                }
        