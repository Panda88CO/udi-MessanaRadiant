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
    from  udiLib import node_queue, wait_for_node_done, getValidName, getValidAddress, send_temp_to_isy, isy_value, send_rel_temp_to_isy, get_command_value, convert_temp_to_messana

    id = 'DHW'

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
        {'driver': 'TIME', 'value': 0, 'uom': 151},
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
        self.node.setDriver('ST', 0, True, True)

    def updateISY_shortpoll(self):
        updated = False
        Val = self.dhw.get_status()
        logging.debug('dhw Status (GV0): {}'.format(Val))
        if Val is not None:
            self.node.setDriver('GV0', self.isy_value(Val))
            updated = True

        Val = self.dhw.get_temp()
        logging.debug('dhw get_temp(CLITEMP): {}'.format(Val))
        if Val is not None:
            if self.send_temp_to_isy(Val, 'CLITEMP'):
                updated = True

        Val = self.dhw.get_target_temp()
        logging.debug('dhw get_target_temp (GV1): {}'.format(Val))
        if Val is not None:
            self.node.setDriver('GV1', self.isy_value(Val))
            updated = True

        if updated:
            self.node.setDriver('ST', 1)
            self.node.setDriver('TIME', int(time.time()), True, True, 151)
        else:
            logging.warning('Hot Water {}: No valid data received from API'.format(self.dhw_nbr))
            self.node.setDriver('ST', 0)


    def updateISY_longpoll(self):
        logging.debug('update_system - dhw {} Status:'.format(self.dhw_nbr))
        updated = False

        Val = self.dhw.get_status()
        logging.debug('dhw Status (GV0): {}'.format(Val))
        if Val is not None:
            self.node.setDriver('GV0', self.isy_value(Val))
            updated = True

        Val = self.dhw.get_temp()
        logging.debug('dhw get_temp(CLITEMP): {}'.format(Val))
        if Val is not None:
            if self.send_temp_to_isy(Val, 'CLITEMP'):
                updated = True

        Val = self.dhw.get_target_temp()
        logging.debug('dhw get_target_temp (GV1): {}'.format(Val))
        if Val is not None:
            self.node.setDriver('GV1', self.isy_value(Val))
            updated = True

        if updated:
            self.node.setDriver('ST', 1)
            self.node.setDriver('TIME', int(time.time()), True, True, 151)
        else:
            logging.warning('Hot Water {}: No valid data received from API'.format(self.dhw_nbr))
            self.node.setDriver('ST', 0)



    def set_status(self, command):
        logging.info('DHW {}: set_status called with command: {}'.format(self.dhw_nbr, command))
        val = self.get_command_value(command)
        if val is None:
            logging.error('DHW {}: No value provided to set_status in command: {}'.format(self.dhw_nbr, command))
            return
        status = int(float(val))
        logging.debug('DHW {}: calling set_status({})'.format(self.dhw_nbr, status))
        temp = self.dhw.set_status(status)
        logging.info('DHW {}: set_status result: {}'.format(self.dhw_nbr, temp))
        if temp is not None:
            self.node.setDriver('GV0', temp)
        else:
            logging.error('DHW {}: Error calling setStatus'.format(self.dhw_nbr))

    def set_target_temp(self, command):
        logging.info('DHW {}: set_target_temp called with command: {}'.format(self.dhw_nbr, command))
        val = self.get_command_value(command)
        if val is None:
            logging.error('DHW {}: No value provided to set_target_temp in command: {}'.format(self.dhw_nbr, command))
            return
        try:
            isy_temp = float(val)
        except (ValueError, TypeError) as e:
            logging.error('DHW {}: Invalid target temp value {} in command {}: {}'.format(self.dhw_nbr, val, command, e))
            return

        messana_temp = self.convert_temp_to_messana(isy_temp)
        target = round(round(messana_temp * 2, 0) / 2, 1)
        logging.info('DHW {}: set_target_temp {} (ISY unit: {}, Messana target: {})'.format(
            self.dhw_nbr, isy_temp, getattr(self, 'ISY_temp_unit', None), target
        ))
        temp = self.dhw.set_target_temp(target)
        logging.info('DHW {}: set_target_temp Messana returned: {}'.format(self.dhw_nbr, temp))
        if temp is not None:
            self.send_temp_to_isy(temp, 'GV1')
        else:
            logging.error('DHW {}: Error calling set_target_temp'.format(self.dhw_nbr))        

    def update(self, command):
        logging.info('DHW {}: update called with command: {}'.format(self.dhw_nbr, command))
        self.updateISY_longpoll()


    commands = { 'UPDATE': update 
                ,'STATUS': set_status
                ,'TARGETTEMP' : set_target_temp
                ,'TEMPMODE' : set_target_temp
                }
        