#!/usr/bin/env python3

import time
import re
#from MessanaInfo import messana_info
from Messana_Macrozone import messana_macrozone

try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)



#messana, controller, primary, address, name, nodeType, nodeNbr, messana
class udi_messana_macrozone(udi_interface.Node):
    from  udiLib import node_queue, wait_for_node_done, getValidName, getValidAddress, send_temp_to_isy, isy_value, send_rel_temp_to_isy, get_command_value, convert_temp_to_messana, apply_profile_driver_names

    id = 'MACROZONE'

    '''
       drivers = [
            'GV0' = Macrozone status
            'GV3' = Setpoint
            'CLITEMP' = air_temp
            'CLIHUM' = humidity
            'DEWPT' = Dewpoint
            'ST' = System Status
            ]
    '''
    
    
    drivers = [
        {'driver': 'ST', 'value': 99, 'uom': 25, 'name': 'Macrozone Temperature'},
        {'driver': 'GV0', 'value': 99, 'uom': 25, 'name': 'Macrozone Status'},
        {'driver': 'GV2', 'value': 1, 'uom': 25, 'name': 'System Running'},
        {'driver': 'GV3', 'value': 99, 'uom': 25, 'name': 'Macrozone Setpoint'},
        {'driver': 'CLIHUM', 'value': 99, 'uom': 25, 'name': 'Macrozone Humidity'},
        {'driver': 'DEWPT', 'value': 99, 'uom': 25, 'name': 'Macrozone Dew Point'},
        {'driver': 'TIME', 'value': 0, 'uom': 151, 'name': 'Last Update'},
        ]

    def __init__(self, polyglot, primary, address, name, macrozone_nbr, messana_info):
        super().__init__(polyglot, primary, address, name)
        self.apply_profile_driver_names(self.id)
        logging.info('init Messana MacroZone {}:'.format(macrozone_nbr) )

        self.primary = primary  
        self.macrozone_nbr = macrozone_nbr
        self.macrozone = messana_macrozone(self.macrozone_nbr, messana_info)
        self.address = address
        self.poly = polyglot
        #self.Parameters = Custom(self.poly, 'customparams')
        self.n_queue = []
        self.poly.subscribe(polyglot.START, self.start, self.address)
        self.poly.subscribe(polyglot.STOP, self.stop)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)

        
        logging.debug('setup node: {} {} {} {}'.format(self.address, name, self.id, self.primary))
        self.poly.ready()
        self.poly.addNode(self, conn_status='GV2')
        self.wait_for_node_done()

        logging.debug('Drivers: {}'.format(self.drivers))
        logging.debug('address: {}'.format(self.address))
        self.node = self.poly.getNode(self.address)
        self.node.setDriver('GV2', 1, True, True)
        self.ISY_temp_unit = messana_info['isy_temp_unit']
        self.messana_temp_unit = self.macrozone.messana_temp_unit

    def start(self):
        logging.info('udiMessanaMacrozone Start ')
        self.updateISY_longpoll()

    def stop(self):
        logging.info('udiMessanaMacrozone Stop ')
        self.node.setDriver('GV2', 0, True, True)

    def updateISY_shortpoll(self):
        updated = False
        Val = self.macrozone.get_status()
        logging.debug('Macrozone Status (GV0): {}'.format(Val))
        if Val is not None:
            self.node.setDriver('GV0', self.isy_value(Val))
            updated = True

        Val = self.macrozone.get_temp()
        logging.debug('get_temp(ST): {}'.format(Val))
        if Val is not None:
            if self.send_temp_to_isy(Val, 'ST'):
                updated = True

        Val = self.macrozone.get_humidity()
        logging.debug('Humidity(CLIHUM): {}'.format(Val))
        if Val is not None:
            self.node.setDriver('CLIHUM', self.isy_value(Val))
            updated = True

        Val = self.macrozone.get_dewpoint()
        logging.debug('get_dewpoint (DEWPT): {}'.format(Val))
        if Val is not None:
            if self.send_temp_to_isy(Val, 'DEWPT'):
                updated = True

        if updated:
            self.node.setDriver('GV2', 1)
            self.node.setDriver('TIME', int(time.time()), True, True, 151)
        else:
            logging.warning('Macrozone {}: No valid data received from API'.format(self.macrozone_nbr))
            self.node.setDriver('GV2', 0)

    def updateISY_longpoll(self):
        logging.debug('update_system - macrozone {} Status:'.format(self.macrozone_nbr))
        updated = False

        Val = self.macrozone.get_status()
        logging.debug('Macrozone Status (GV0): {}'.format(Val))
        if Val is not None:
            self.node.setDriver('GV0', self.isy_value(Val))
            updated = True

        #Val = self.macrozone.get_scheduleOn()
        #logging.debug('Schedule Mode(GV2): {}'.format(Val))
        #self.node.setDriver('GV2', self.isy_value(Val))

        Val = self.macrozone.get_setpoint()
        logging.debug('Set point (GV3): {}'.format(Val))
        if Val is not None:
            if self.send_temp_to_isy(Val, 'GV3'):
                updated = True

        Val = self.macrozone.get_temp()
        logging.debug('get_temp(ST): {}'.format(Val))
        if Val is not None:
            if self.send_temp_to_isy(Val, 'ST'):
                updated = True

        Val = self.macrozone.get_humidity()
        logging.debug('Humidity(CLIHUM): {}'.format(Val))
        if Val is not None:
            self.node.setDriver('CLIHUM', self.isy_value(Val), True, True)
            updated = True

        Val = self.macrozone.get_dewpoint()
        logging.debug('get_dewpoint (DEWPT): {}'.format(Val))
        if Val is not None:
            if self.send_temp_to_isy(Val, 'DEWPT'):
                updated = True

        if updated:
            self.node.setDriver('GV2', 1)
            self.node.setDriver('TIME', int(time.time()), True, True, 151)
        else:
            logging.warning('Macrozone {}: No valid data received from API'.format(self.macrozone_nbr))
            self.node.setDriver('GV2', 0)



        
    def set_setpoint(self, command):
        logging.info('Macrozone {}: set_setpoint called with command: {}'.format(self.macrozone_nbr, command))
        val = self.get_command_value(command)
        if val is None:
            logging.error('Macrozone {}: No value provided to set_setpoint in command: {}'.format(self.macrozone_nbr, command))
            return
        try:
            isy_temp = float(val)
        except (ValueError, TypeError) as e:
            logging.error('Macrozone {}: Invalid setpoint value {} in command {}: {}'.format(self.macrozone_nbr, val, command, e))
            return

        messana_sp = self.convert_temp_to_messana(isy_temp)
        target_sp = round(round(messana_sp * 2, 0) / 2, 1)
        logging.info('Macrozone {}: set_setpoint {} (ISY unit: {}, Messana target: {})'.format(
            self.macrozone_nbr, isy_temp, getattr(self, 'ISY_temp_unit', None), target_sp
        ))
        temp = self.macrozone.set_setpoint(target_sp)
        logging.info('Macrozone {}: set_setpoint Messana returned: {}'.format(self.macrozone_nbr, temp))
        if temp is not None:
            self.send_temp_to_isy(temp, 'GV3')
        else:
            logging.error('Macrozone {}: Error calling set_setpoint'.format(self.macrozone_nbr))

    def set_schedule(self, command):
        logging.info('Macrozone {}: set_schedule called with command: {}'.format(self.macrozone_nbr, command))
        val = self.get_command_value(command)
        if val is None:
            return
        schedule = int(float(val))
        logging.debug('Macrozone {}: set_schedule: {}'.format(self.macrozone_nbr, schedule))

    def update(self, command):
        logging.info('Macrozone {}: update called with command: {}'.format(self.macrozone_nbr, command))
        self.updateISY_longpoll()

    def set_status(self, command):
        logging.info('Macrozone {}: set_status called with command: {}'.format(self.macrozone_nbr, command))
        val = self.get_command_value(command)
        if val is None:
            logging.error('Macrozone {}: No value provided to set_status in command: {}'.format(self.macrozone_nbr, command))
            return
        status = int(float(val))
        logging.debug('Macrozone {}: calling set_status({})'.format(self.macrozone_nbr, status))
        new_status = self.macrozone.set_status(status)
        logging.info('Macrozone {}: set_status result: {}'.format(self.macrozone_nbr, new_status))
        if new_status is not None:
            self.node.setDriver('GV0', new_status)
        else:
            logging.error('Macrozone {}: Error calling setStatus'.format(self.macrozone_nbr))

    def set_on(self, command=None):
        logging.debug('set_on Called (DON) for macrozone: {}'.format(self.macrozone_nbr))
        new_status = self.macrozone.set_status(1)
        if new_status is not None:
            self.node.setDriver('GV0', new_status)
        else:
            logging.error('Error calling set_on')

    def set_off(self, command=None):
        logging.debug('set_off Called (DOF) for macrozone: {}'.format(self.macrozone_nbr))
        new_status = self.macrozone.set_status(0)
        if new_status is not None:
            self.node.setDriver('GV0', new_status)
        else:
            logging.error('Error calling set_off')


    commands = { 'UPDATE': update
                ,'STATUS': set_status
                ,'DON': set_on
                ,'DOF': set_off
                ,'SETPOINT' : set_setpoint
     #           ,'SETPOINTCO2' : set_setpoint_co2
     #           ,'SCHEDULEON' : set_schedule
                
                }
        