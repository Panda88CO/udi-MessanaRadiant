#!/usr/bin/env python3

import time
import re
#from MessanaInfo import messana_info
from MessanaZone import messana_zone

try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)



#messana, controller, primary, address, name, nodeType, nodeNbr, messana
class udi_messana_zone(udi_interface.Node):

    id = 'messana_zone'

    '''
       drivers = [
            'GV0' = Zone status
            'GV1' = Thermal Operation (0-3)
            'GV2' = Schedule State
            'GV3' = Setpoint
            'GV4' = air_temp
            'GV5' = humidity
            'GV6' = AirQuality
            'GV7' = CO2
            'GV8' = get_energy_saving()
            'GV9' = AlarmOn
            'GV10' = system_temperature
            'ST' = System Status

               
            ]
    ''' 
    drivers = [
        {'driver': 'GV0', 'value': 99, 'uom': 25},
        {'driver': 'GV1', 'value': 99, 'uom': 25},
        {'driver': 'GV2', 'value': 99, 'uom': 25},
        {'driver': 'GV3', 'value': 99, 'uom': 4},
        {'driver': 'GV4', 'value': 99, 'uom': 4},
        {'driver': 'GV5', 'value': 99, 'uom': 21},
        {'driver': 'GV6', 'value': 99, 'uom': 0},
        {'driver': 'GV7', 'value': 99, 'uom': 0},                                                         
        {'driver': 'GV8', 'value': 99, 'uom': 25},
        {'driver': 'GV9', 'value': 99, 'uom': 25},        
        {'driver': 'GV10', 'value': 99, 'uom': 4},
        {'driver': 'ST', 'value': 0, 'uom': 25},
        ]
        

    def __init__(self, polyglot, primary, address, name, zone_nbr, messana_info):
        super().__init__(polyglot, primary, address, name)
        logging.info('init Messana Zone {}:'.format(zone_nbr) )
        #self.node_type = 'zone'
        self.parent = primary
        self.zone_nbr = zone_nbr
        self.zone = messana_zone(self.zone_nbr, messana_info)
        
        self.address = self.address
        tmp_name = self.zone.name
        self.name = self.getValidName(tmp_name)
        self.poly = polyglot

        self.n_queue = []
        polyglot.subscribe(polyglot.START, self.start, self.address)
        polyglot.subscribe(polyglot.STOP, self.stop)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)
        polyglot.ready()
        self.poly.addNode(self)
        self.wait_for_node_done()
        self.node = self.poly.getNode(self.address)
        self.node.setDriver('ST', 1, True, True)

    def node_queue(self, data):
        self.n_queue.append(data['address'])

    def wait_for_node_done(self):
        while len(self.n_queue) == 0:
            time.sleep(0.1)
        self.n_queue.pop()


    def getValidName(self, name):
        name = bytes(name, 'utf-8').decode('utf-8','ignore')
        return re.sub(r"[^A-Za-z0-9_ ]", "", name)

    # remove all illegal characters from node address
    def getValidAddress(self, name):
        name = bytes(name, 'utf-8').decode('utf-8','ignore')
        return re.sub(r"[^A-Za-z0-9_]", "", name.lower()[:14])

    def isy_value(self, value):
        if value == None:
            return (99)
        else:
            return(value)


    def start(self):
        logging.info('udiMessanaZone Start ')
        self.updateISY_longpoll()
        

    def stop(self):
        logging.info('udiMessanaZone Stop ')

    def updateISY_shortpoll(self):
        Val = self.zone.get_status()
        logging.debug('Zone Status (GV0): {}'.format(Val))
        self.node.setDriver('GV0', self.isy_value(Val), True, True)

        Val = self.zone.get_air_temp()
        logging.debug('get_air_temp(GV4): {}'.format(Val))
        self.node.setDriver('GV4', self.isy_value(Val), True, True)

        Val = self.zone.get_humidity()
        logging.debug('Humidity(GV5): {}'.format(Val))
        self.node.setDriver('GV5', self.isy_value(Val), True, True)

        Val = self.zone.get_air_quality()
        logging.debug('get_air_quality (GV6): {}'.format(Val))
        self.node.setDriver('GV6', self.isy_value(Val), True, True)

        Val = self.zone.get_alarmOn()
        logging.debug('get_get_alarmOn(GV9): {}'.format(Val))
        self.node.setDriver('GV9', self.isy_value(Val), True, True)

    def updateISY_longpoll(self):
        logging.debug('update_system - zone {} Status:'.format(self.zone_nbr))

        Val = self.zone.get_status()
        logging.debug('Zone Status (GV0): {}'.format(Val))
        self.node.setDriver('GV0', self.isy_value(Val), True, True)

        Val = self.zone.get_thermal_status()
        logging.debug('Thermal Mode(GV1): {}'.format(Val))
        self.node.setDriver('GV1', self.isy_value(Val), True, True)

        Val = self.zone.get_scheduleOn()
        logging.debug('Schedule Mode(GV2): {}'.format(Val))
        self.node.setDriver('GV2', self.isy_value(Val), True, True)

        Val = self.zone.get_setpoint()
        logging.debug('Set point (GV3): {}'.format(Val))
        self.node.setDriver('GV3', self.isy_value(Val), True, True)

        Val = self.zone.get_air_temp()
        logging.debug('get_air_temp(GV4): {}'.format(Val))
        self.node.setDriver('GV4', self.isy_value(Val), True, True)

        Val = self.zone.get_humidity()
        logging.debug('Humidity(GV5): {}'.format(Val))
        self.node.setDriver('GV5', self.isy_value(Val), True, True)

        Val = self.zone.get_air_quality()
        logging.debug('get_air_quality (GV6): {}'.format(Val))
        self.node.setDriver('GV6', self.isy_value(Val), True, True)

        Val = self.zone.get_co2()
        logging.debug('Alarm On (GV7): {}'.format(Val))
        self.node.setDriver('GV7', self.isy_value(Val), True, True)

        Val = self.zone.get_energy_saving()
        logging.debug('get_energy_saving On (GV8): {}'.format(Val))
        self.node.setDriver('GV8', self.isy_value(Val), True, True)

        Val = self.zone.get_alarmOn()
        logging.debug('get_get_alarmOn(GV9): {}'.format(Val))
        self.node.setDriver('GV9', self.isy_value(Val), True, True)

        Val = self.zone.get_temp()
        logging.debug('System Temp (GV10): {}'.format(Val))
        self.node.setDriver('GV10', self.isy_value(Val), True, True)


        #Val = self.zone.system_online
        #logging.debug('System Status: {}'.format(Val))
        #self.node.setDriver('ST', self.isy_value(Val), True, True)    
        