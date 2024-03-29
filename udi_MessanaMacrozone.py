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
    from  udiLib import node_queue, wait_for_node_done, getValidName, getValidAddress, send_temp_to_isy, isy_value, send_rel_temp_to_isy

    id = 'macrozone'

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
        {'driver': 'GV0', 'value': 99, 'uom': 25},
        #{'driver': 'GV2', 'value': 99, 'uom': 25},
        {'driver': 'GV3', 'value': 99, 'uom': 25},
        {'driver': 'CLITEMP', 'value': 99, 'uom': 25},
        {'driver': 'CLIHUM', 'value': 99, 'uom': 25},
        {'driver': 'DEWPT', 'value': 99, 'uom': 25},
        {'driver': 'ST', 'value': 0, 'uom': 25},
        ]

    def __init__(self, polyglot, primary, address, name, macrozone_nbr, messana_info):
        super().__init__(polyglot, primary, address, name)
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
        self.poly.addNode(self, conn_status='ST')
        self.wait_for_node_done()

        logging.debug('Drivers: {}'.format(self.drivers))
        logging.debug('address: {}'.format(self.address))
        self.node = self.poly.getNode(self.address)
        self.node.setDriver('ST', 1, True, True)
        self.ISY_temp_unit = messana_info['isy_temp_unit']
        self.messana_temp_unit = self.macrozone.messana_temp_unit

    def start(self):
        logging.info('udiMessanaMacrozone Start ')
        self.updateISY_longpoll()

    def stop(self):
        logging.info('udiMessanaMacrozone Stop ')

    def updateISY_shortpoll(self):
        Val = self.macrozone.get_status()
        logging.debug('Macrozone Status (GV0): {}'.format(Val))
        self.node.setDriver('GV0', self.isy_value(Val))

        Val = self.macrozone.get_temp()
        logging.debug('get_temp(CLITEMP): {}'.format(Val))
        #self.node.setDriver('GV4', self.isy_value(Val), True, True)
        self.send_temp_to_isy(Val, 'CLITEMP')

        Val = self.macrozone.get_humidity()
        logging.debug('Humidity(CLIHUM): {}'.format(Val))
        self.node.setDriver('CLIHUM', self.isy_value(Val))

        Val = self.macrozone.get_dewpoint()
        logging.debug('get_dewpoint (DEWPT): {}'.format(Val))
        self.send_temp_to_isy(Val, 'DEWPT')



    def updateISY_longpoll(self):
        logging.debug('update_system - macrozone {} Status:'.format(self.macrozone_nbr))

        Val = self.macrozone.get_status()
        logging.debug('Macrozone Status (GV0): {}'.format(Val))
        self.node.setDriver('GV0', self.isy_value(Val))

        #Val = self.macrozone.get_scheduleOn()
        #logging.debug('Schedule Mode(GV2): {}'.format(Val))
        #self.node.setDriver('GV2', self.isy_value(Val))

        Val = self.macrozone.get_setpoint()
        logging.debug('Set point (GV3): {}'.format(Val))
        self.send_temp_to_isy(Val, 'GV3')
        #self.node.setDriver('GV3', self.isy_value(Val))

        Val = self.macrozone.get_temp()
        logging.debug('get_temp(CLITEMP): {}'.format(Val))
        #self.node.setDriver('GV4', self.isy_value(Val), True, True)
        self.send_temp_to_isy(Val, 'CLITEMP')

        Val = self.macrozone.get_humidity()
        logging.debug('Humidity(CLIHUM): {}'.format(Val))
        self.node.setDriver('CLIHUM', self.isy_value(Val), True, True)

        Val = self.macrozone.get_dewpoint()
        logging.debug('get_dewpoint (DEWPT): {}'.format(Val))
        self.send_temp_to_isy(Val, 'DEWPT')



        
    def set_setpoint(self, command):
        temp_1 = float(command.get('value'))
        set_point = round(round(temp_1*2,0)/2,1)
        logging.debug('set_setpoint {} = {} for macrozone {}'.format(temp_1, set_point, self.macrozone_nbr))   
        temp = self.macrozone.set_setpoint(set_point)
        if temp is not None:
            self.node.setDriver('GV3', temp)
        else:
            logging.error('Error calling set_setpoint')

    def set_schedule(self, command):
        schedule = int(command.get('value'))
        logging.debug('set_schedule: {}'.format(schedule))

    def update(self, command):
        logging.debug('update')
        self.updateISY_longpoll()

    def set_status(self, command):
        status = int(command.get('value'))
        logging.debug('set Status Called {} for macrozone: {}'.format(status, self.macrozone_nbr))
        new_status = self.macrozone.set_status(status)
        logging.debug('new_status {}'.format(new_status))
        if new_status != None:
            self.node.setDriver('GV0', new_status)
        else:
            logging.error('Error calling setStatus')


    commands = { 'UPDATE': update
                ,'STATUS': set_status
                ,'SETPOINT' : set_setpoint
     #           ,'SETPOINTCO2' : set_setpoint_co2
     #           ,'SCHEDULEON' : set_schedule
                
                }
        