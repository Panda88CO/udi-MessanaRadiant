#!/usr/bin/env python3

import time
import re
#from MessanaInfo import messana_info
from Messana_Zone import messana_zone

try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)



#messana, controller, primary, address, name, nodeType, nodeNbr, messana
class udi_messana_zone(udi_interface.Node):
    from  udiLib import node_queue, wait_for_node_done, getValidName, getValidAddress, send_temp_to_isy, isy_value, send_rel_temp_to_isy

    id = 'ZONE'

    '''
       drivers = [
            'ST' = Room Temperature
            'GV0' = Zone status
            'GV1' = Thermal Operation (0-3)
            'GV2' = System Running
            'GV3' = Setpoint
            'CLIHUM' = humidity
            'DEWPT' = dewpoint
            'GV6' = AirQuality
            'CO2LVL' = CO2
            'GV7' = VOC Level
            'GV8' = energy_saving
            'GV9' = AlarmOn
            'GV10' = system_temperature
            'TIME' = Last Update
            ]
    '''
    drivers = [
        {'driver': 'ST', 'value': 99, 'uom': 25},
        {'driver': 'GV0', 'value': 99, 'uom': 25},
        {'driver': 'GV1', 'value': 99, 'uom': 25},
        {'driver': 'GV2', 'value': 1, 'uom': 25},
        {'driver': 'GV3', 'value': 99, 'uom': 25},
        {'driver': 'CLIHUM', 'value': 99, 'uom': 25},
        {'driver': 'DEWPT', 'value': 99, 'uom': 25},
        {'driver': 'GV6', 'value': 99, 'uom': 25},
        {'driver': 'CO2LVL', 'value': 99, 'uom': 25},
        {'driver': 'GV7', 'value': 99, 'uom': 25},
        {'driver': 'GV8', 'value': 99, 'uom': 25},
        {'driver': 'GV9', 'value': 99, 'uom': 25},
        {'driver': 'GV10', 'value': 99, 'uom': 25},
        {'driver': 'TIME', 'value': 0, 'uom': 151},
        ]

    def __init__(self, polyglot, primary, address, name, zone_nbr, messana_info):
        super().__init__(polyglot, primary, address, name)
        logging.info('init Messana Zone {}:'.format(zone_nbr) )

        self.primary = primary
        self.zone_nbr = zone_nbr
        self.zone = messana_zone(self.zone_nbr, messana_info)

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
        self.messana_temp_unit = self.zone.messana_temp_unit

    def start(self):
        logging.info('udiMessanaZone Start ')
        self.updateISY_longpoll()

    def stop(self):
        logging.info('udiMessanaZone Stop ')
        self.node.setDriver('GV2', 0, True, True)

    def updateISY_shortpoll(self):
        updated = False
        Val = self.zone.get_status()
        logging.debug('Zone Status (GV0): {}'.format(Val))
        if Val is not None:
            self.node.setDriver('GV0', self.isy_value(Val))
            updated = True

        Val = self.zone.get_air_temp()
        logging.debug('get_air_temp(ST): {}'.format(Val))
        if Val is not None:
            if self.send_temp_to_isy(Val, 'ST'):
                updated = True

        Val = self.zone.get_humidity()
        logging.debug('Humidity(CLIHUM): {}'.format(Val))
        if Val is not None:
            self.node.setDriver('CLIHUM', self.isy_value(Val))
            updated = True

        Val = self.zone.get_dewpoint()
        logging.debug('get_dewpoint (DEWPT): {}'.format(Val))
        if Val is not None:
            if self.send_temp_to_isy(Val, 'DEWPT'):
                updated = True

        Val = self.zone.get_air_quality()
        logging.debug('get_air_quality (GV6): {}'.format(Val))
        if Val is not None:
            self.node.setDriver('GV6', self.isy_value(Val))
            updated = True

        Val = self.zone.get_alarmOn()
        logging.debug('get_get_alarmOn(GV9): {}'.format(Val))
        if Val is not None:
            self.node.setDriver('GV9', self.isy_value(Val), True, True)
            updated = True

        if updated:
            self.node.setDriver('GV2', 1)
            self.node.setDriver('TIME', int(time.time()), True, True, 151)
        else:
            logging.warning('Zone {}: No valid data received from API'.format(self.zone_nbr))
            self.node.setDriver('GV2', 0)

    def updateISY_longpoll(self):
        logging.debug('update_system - zone {} Status:'.format(self.zone_nbr))
        updated = False

        Val = self.zone.get_status()
        logging.debug('Zone Status (GV0): {}'.format(Val))
        if Val is not None:
            self.node.setDriver('GV0', self.isy_value(Val))
            updated = True

        Val = self.zone.get_thermal_status()
        logging.debug('Thermal Mode(GV1): {}'.format(Val))
        if Val is not None:
            self.node.setDriver('GV1', self.isy_value(Val))
            updated = True

        #Val = self.zone.get_scheduleOn()
        #logging.debug('Schedule Mode(GV2): {}'.format(Val))
        #self.node.setDriver('GV2', self.isy_value(Val))

        Val = self.zone.get_setpoint()
        logging.debug('Set point (GV3): {}'.format(Val))
        if Val is not None:
            if self.send_temp_to_isy(Val, 'GV3'):
                updated = True

        Val = self.zone.get_air_temp()
        logging.debug('get_air_temp(ST): {}'.format(Val))
        if Val is not None:
            if self.send_temp_to_isy(Val, 'ST'):
                updated = True

        Val = self.zone.get_humidity()
        logging.debug('get_humidity(CLIHUM)): {}'.format(Val))
        if Val is not None:
            self.node.setDriver('CLIHUM', self.isy_value(Val), True, True)
            updated = True

        Val = self.zone.get_dewpoint()
        logging.debug('get_dewpoint (DEWPT): {}'.format(Val))
        if Val is not None:
            if self.send_temp_to_isy(Val, 'DEWPT'):
                updated = True

        Val = self.zone.get_energy_saving()
        logging.debug('get_energy_saving On (GV8): {}'.format(Val))
        if Val is not None:
            self.node.setDriver('GV8', self.isy_value(Val))
            updated = True

        Val = self.zone.get_alarmOn()
        logging.debug('get_alarmOn(GV9): {}'.format(Val))
        if Val is not None:
            self.node.setDriver('GV9', self.isy_value(Val), True, True)
            updated = True

        Val = self.zone.get_temp()
        logging.debug('System Temp (GV10): {}'.format(Val))
        if Val is not None:
            if self.send_temp_to_isy(Val, 'GV10'):
                updated = True

        if updated:
            Val = self.zone.get_air_quality()
            logging.debug('get_air_quality (GV6): {}'.format(Val))
            if Val == -1 or Val is None:
                self.node.setDriver('GV6', 98, True, True, 25)
            else:
                self.node.setDriver('GV6', self.isy_value(Val), True, False, 56)

            Val = self.zone.get_co2()
            logging.debug('get_co2 (CO2LVL): {}'.format(Val))
            if Val == -1 or Val is None:
                self.node.setDriver('CO2LVL', 98, True, True, 25)
            else:
                self.node.setDriver('CO2LVL', self.isy_value(Val), True, False, 56)

            Val = self.zone.get_voc()
            logging.debug('get_voc (GV7): {}'.format(Val))
            if Val == -1 or Val is None:
                self.node.setDriver('GV7', 98, True, True, 25)
            else:
                self.node.setDriver('GV7', self.isy_value(Val), True, False, 96)

            self.node.setDriver('GV2', 1)
            self.node.setDriver('TIME', int(time.time()), True, True, 151)
        else:
            logging.warning('Zone {}: No valid data received from API'.format(self.zone_nbr))
            self.node.setDriver('GV2', 0)

    def set_status(self, command):
        status = int(command.get('value'))
        logging.debug('set Status Called {} for zone: {}'.format(status, self.zone_nbr))
        new_status = self.zone.set_status(status)
        logging.debug('new_status {}'.format(new_status))
        if new_status != None:
            self.node.setDriver('GV0', new_status)
        else:
            logging.error('Error calling setStatus')

    def set_on(self, command=None):
        logging.debug('set_on Called (DON) for zone: {}'.format(self.zone_nbr))
        new_status = self.zone.set_status(1)
        if new_status is not None:
            self.node.setDriver('GV0', new_status)
        else:
            logging.error('Error calling set_on')

    def set_off(self, command=None):
        logging.debug('set_off Called (DOF) for zone: {}'.format(self.zone_nbr))
        new_status = self.zone.set_status(0)
        if new_status is not None:
            self.node.setDriver('GV0', new_status)
        else:
            logging.error('Error calling set_off')

    def set_energy_save(self, command):
        energy_save = int(command.get('value'))
        logging.debug('setEnergySave Called {} for zone {}'.format(energy_save, self.zone_nbr))
        new_es = self.zone.set_energy_saving(energy_save)
        logging.debug('new_es {}'.format(new_es))
        if new_es != None:
            self.node.setDriver('GV8', new_es)
        else:
            logging.error('Error calling set_energy_save')
        
    def set_setpoint(self, command):
        set_point = round(round(int(command.get('value'))*2,0)/2,1)
        logging.debug('set_setpoint {} for zone {}'.format(set_point, self.zone_nbr))
        new_SP = self.zone.set_setpoint(set_point)
        logging.debug('new SP: {}'.format(new_SP))
        if new_SP != None:
            self.node.setDriver('GV3', new_SP)
        else:
            logging.error('Error calling set_setpoint')

    def update(self, command):
        logging.debug('update')
        self.updateISY_longpoll()

    
    commands = { 'UPDATE': update
                ,'STATUS': set_status
                ,'DON': set_on
                ,'DOF': set_off
                ,'ENERGYSAVE': set_energy_save
                ,'SETPOINT' : set_setpoint
     #           ,'SETPOINTCO2' : set_setpoint_co2        
     #           ,'SCHEDULEON' : set_schedule
                
                }

        #Val = self.zone.system_online
        #logging.debug('System Status: {}'.format(Val))
        #self.node.setDriver('ST', self.isy_value(Val), True, True)    
        