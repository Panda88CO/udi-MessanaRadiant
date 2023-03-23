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

    id = 'zone'

    '''
       drivers = [
            'GV0' = Zone status
            'GV1' = Thermal Operation (0-3)
            'GV2' = Schedule State
            'GV3' = Setpoint
            'CLITEMP' = air_temp
            'CLIHUM' = humidity
            'DEWPT' = dewpoint
            'GV6' = AirQuality
            'CO2LVL' = CO2
            'GV8' = energy_saving
            'GV9' = AlarmOn
            'CLITEMP' = system_temperature
            'ST' = System Status
            ]
    '''
    drivers = [
        {'driver': 'GV0', 'value': 99, 'uom': 25},
        {'driver': 'GV1', 'value': 99, 'uom': 25},
        {'driver': 'GV2', 'value': 99, 'uom': 25},
        {'driver': 'GV3', 'value': 99, 'uom': 25},
        {'driver': 'CLITEMP', 'value': 99, 'uom': 25},
        {'driver': 'CLIHUM', 'value': 99, 'uom': 25},
        {'driver': 'DEWPT', 'value': 99, 'uom': 25},
        {'driver': 'GV6', 'value': 99, 'uom': 25},
        {'driver': 'CO2LVL', 'value': 99, 'uom': 25},
        {'driver': 'GV8', 'value': 99, 'uom': 25},
        {'driver': 'GV9', 'value': 99, 'uom': 25},
        {'driver': 'GV10', 'value': 99, 'uom': 25},
        {'driver': 'ST', 'value': 0, 'uom': 25},
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
        self.poly.addNode(self, conn_status='ST')
        self.wait_for_node_done()

        logging.debug('Drivers: {}'.format(self.drivers))
        logging.debug('address: {}'.format(self.address))
        self.node = self.poly.getNode(self.address)
        self.node.setDriver('ST', 1, True, True)
        self.ISY_temp_unit = messana_info['isy_temp_unit']
        self.messana_temp_unit = self.zone.messana_temp_unit

    def start(self):
        logging.info('udiMessanaZone Start ')
        self.updateISY_longpoll()

    def stop(self):
        logging.info('udiMessanaZone Stop ')

    def updateISY_shortpoll(self):
        Val = self.zone.get_status()
        logging.debug('Zone Status (GV0): {}'.format(Val))
        self.node.setDriver('GV0', self.isy_value(Val))

        Val = self.zone.get_air_temp()
        logging.debug('get_air_temp(CLITEMP): {}'.format(Val))
        #self.node.setDriver('GV4', self.isy_value(Val), True, True)
        self.send_temp_to_isy(Val, 'CLITEMP')

        Val = self.zone.get_humidity()
        logging.debug('Humidity(CLIHUM): {}'.format(Val))
        self.node.setDriver('CLIHUM', self.isy_value(Val))

        Val = self.zone.get_dewpoint()
        logging.debug('get_dewpoint (DEWPT): {}'.format(Val))
        self.send_temp_to_isy(Val, 'DEWPT')


        Val = self.zone.get_air_quality()
        logging.debug('get_air_quality (GV6): {}'.format(Val))
        if Val == None:
             self.node.setDriver('GV6', 98, True, True, 25)
        else:
            self.node.setDriver('GV6', self.isy_value(Val))

        Val = self.zone.get_alarmOn()
        logging.debug('get_get_alarmOn(GV9): {}'.format(Val))
        self.node.setDriver('GV9', self.isy_value(Val), True, True)



    def updateISY_longpoll(self):
        logging.debug('update_system - zone {} Status:'.format(self.zone_nbr))

        Val = self.zone.get_status()
        logging.debug('Zone Status (GV0): {}'.format(Val))
        self.node.setDriver('GV0', self.isy_value(Val))

        Val = self.zone.get_thermal_status()
        logging.debug('Thermal Mode(GV1): {}'.format(Val))
        self.node.setDriver('GV1', self.isy_value(Val))

        Val = self.zone.get_scheduleOn()
        logging.debug('Schedule Mode(GV2): {}'.format(Val))
        self.node.setDriver('GV2', self.isy_value(Val))

        Val = self.zone.get_setpoint()
        logging.debug('Set point (GV3): {}'.format(Val))
        self.send_temp_to_isy(Val, 'GV3')
        #self.node.setDriver('GV3', self.isy_value(Val))

        Val = self.zone.get_air_temp()
        logging.debug('get_air_temp(CLITEMP): {}'.format(Val))
        #self.node.setDriver('GV4', self.isy_value(Val), True, True)
        self.send_temp_to_isy(Val, 'CLITEMP')

        Val = self.zone.get_humidity()
        logging.debug('get_humidity(CLIHUM)): {}'.format(Val))
        self.node.setDriver('CLIHUM', self.isy_value(Val), True, True)
        
        Val = self.zone.get_dewpoint()
        logging.debug('get_dewpoint (DEWPT): {}'.format(Val))
        self.send_temp_to_isy(Val, 'DEWPT')


        Val = self.zone.get_air_quality()
        logging.debug('get_air_quality (GV6): {}'.format(Val))
        if Val == -1 or Val == None:
             self.node.setDriver('GV6', 98, True, True, 25)
        else:
            self.node.setDriver('GV6', self.isy_value(Val), True, False, 56)

        Val = self.zone.get_co2()
        logging.debug('get_co2 (CO2LVL): {}'.format(Val))
        if Val == -1 or Val == None:
             self.node.setDriver('CO2LVL', 98, True, True, 25)
        else:
            self.node.setDriver('CO2LVL', self.isy_value(Val), True, False, 56)

        Val = self.zone.get_energy_saving()
        logging.debug('get_energy_saving On (GV8): {}'.format(Val))
        self.node.setDriver('GV8', self.isy_value(Val))

        Val = self.zone.get_alarmOn()
        logging.debug('get_alarmOn(GV9): {}'.format(Val))
        self.node.setDriver('GV9', self.isy_value(Val), True, True)

        Val = self.zone.get_temp()
        logging.debug('System Temp (GV10): {}'.format(Val))
        #self.node.setDriver('GV10', self.isy_value(Val), True, True)
        self.send_temp_to_isy(Val, 'GV10')

    def set_status(self, command):
        status = int(command.get('value'))
        logging.debug('set Status Called {} for zone: {}'.format(status, self.zone_nbr))
        new_status = int(self.zone.set_status(status))
        logging.debug('new_status {}'.format(new_status))
        if new_status:
            self.node.setDriver('GV0', new_status)
        else:
            logging.error('Error calling setStatus')

    def set_energy_save(self, command):
        energy_save = int(command.get('value'))
        logging.debug('setEnergySave Called {} for zone {}'.format(energy_save, self.zone_nbr))
        new_es = int(self.zone.set_energy_saving(energy_save))
        logging.debug('new_es {}'.format(new_es))
        if new_es:
            self.node.setDriver('GV8', new_es)
        else:
            logging.error('Error calling set_energy_save')
        
    def set_setpoint(self, command):
        set_point = round(round(int(command.get('value'))*2,0)/2,1)
        logging.debug('set_setpoint {} for zone {}'.format(set_point, self.zone_nbr))
        new_SP = round(float(self.zone.set_setpoint(set_point)),1)
        logging.debug('new SP: {}'.format(new_SP))
        if new_SP:
            self.node.setDriver('GV3', new_SP)
        else:
            logging.error('Error calling set_setpoint')

    def update(self, command):
        logging.debug('update')
        self.updateISY_longpoll()

    
    commands = { 'UPDATE': update
                ,'STATUS': set_status
                ,'ENERGYSAVE': set_energy_save
                ,'SETPOINT' : set_setpoint
     #           ,'SETPOINTCO2' : set_setpoint_co2        
     #           ,'SCHEDULEON' : set_schedule
                
                }

        #Val = self.zone.system_online
        #logging.debug('System Status: {}'.format(Val))
        #self.node.setDriver('ST', self.isy_value(Val), True, True)    
        