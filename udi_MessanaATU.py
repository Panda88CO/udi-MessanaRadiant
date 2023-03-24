#!/usr/bin/env python3


#from MessanaInfo import messana_info
from Messana_ATU import messana_atu

try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)


import time
#messana, controller, primary, address, name, nodeType, nodeNbr, messana
class udi_messana_atu(udi_interface.Node):
    from  udiLib import node_queue, wait_for_node_done, getValidName, getValidAddress, send_temp_to_isy, isy_value, send_rel_temp_to_isy

    id = 'atu'

    '''
       drivers = [
            'GV0' = atu status #
            'CLITEMP' = air_temp #
            'GV1' = flowLevel #
            'GV2' = hrvStatus #
            'GV3' = hrvOn #
            'GV4' = HumStatus
            'GV5' = HumOn
            'GV6' = DehumStatus
            'GV7' = DehumOn
            'GV8' = ConvStatus
            'GV9' = ConvOn
   
            'GV11' = AlarmOn

            'ST' = System Status
            ]
    '''
 
    drivers = [
        {'driver': 'GV0', 'value': 99, 'uom': 25},
        {'driver': 'CLITEMP', 'value': 99, 'uom': 25},
        {'driver': 'GV1', 'value': 99, 'uom': 25},
        {'driver': 'GV2', 'value': 99, 'uom': 25},
        {'driver': 'GV3', 'value': 99, 'uom': 25},
        {'driver': 'GV4', 'value': 99, 'uom': 25},
        {'driver': 'GV5', 'value': 99, 'uom': 25},
        {'driver': 'GV6', 'value': 99, 'uom': 25},
        {'driver': 'GV7', 'value': 99, 'uom': 25},
        {'driver': 'GV8', 'value': 99, 'uom': 25},
        {'driver': 'GV9', 'value': 99, 'uom': 25},

        {'driver': 'GV11', 'value': 99, 'uom': 25},
        {'driver': 'ST', 'value': 0, 'uom': 25},
        ]

    def __init__(self, polyglot, primary, address, name, atu_nbr, messana_info):
        super().__init__(polyglot, primary, address, name)
        logging.info('init Messana ATU {}:'.format(atu_nbr) )

        self.poly = polyglot
        self.primary = primary
        self.atu_nbr = atu_nbr
        self.address = address

        self.atu = messana_atu(self.atu_nbr, messana_info)
        #self.name = name
        logging.debug('ATU {} name : {}'.format(atu_nbr, name ))
       

        
        #self.Parameters = Custom(self.poly, 'customparams')
        self.n_queue = []
        self.poly.subscribe(polyglot.START, self.start, address)
        self.poly.subscribe(polyglot.STOP, self.stop)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)

        
        logging.debug('setup node: {} {} {} {}'.format(address, name, self.id, primary))
        self.poly.ready()
        self.poly.addNode(self, conn_status='ST')
        self.wait_for_node_done()

        logging.debug('Drivers: {}'.format(self.drivers))
        logging.debug('address: {}'.format(self.address))
        self.node = self.poly.getNode(self.address)
        self.node.setDriver('ST', 1, True, True)
        self.ISY_temp_unit = messana_info['isy_temp_unit']
        self.messana_temp_unit = self.atu.messana_temp_unit

    def start(self):
        logging.info('udiMessanaATUStart ')
        self.updateISY_longpoll()

    def stop(self):
        logging.info('udiMessanaATU Stop ')

    def updateISY_shortpoll(self):
        Val = self.atu.get_status()
        logging.debug('atu Status (GV0): {}'.format(Val))
        self.node.setDriver('GV0', self.isy_value(Val))

        Val = self.atu.get_air_temp()
        logging.debug('et_air_temp(CLITEMP)): {}'.format(Val))
        #self.node.setDriver('GV4', self.isy_value(Val), True, True)
        self.send_temp_to_isy(Val, 'CLITEMP')

        Val = self.atu.get_flow_level()
        logging.debug('get_flow_level(GV1): {}'.format(Val))
        self.node.setDriver('GV1', self.isy_value(Val))

        Val = self.atu.get_HRV_status()
        logging.debug('get_HRV_status(GV2): {}'.format(Val))
        self.node.setDriver('GV2', self.isy_value(Val))

        Val = self.atu.get_humidification_status()
        logging.debug('get_humidification_status(GV4): {}'.format(Val))
        self.node.setDriver('GV4', self.isy_value(Val))

        Val = self.atu.get_dehumidification_status()
        logging.debug('get_humidification_status(GV4): {}'.format(Val))
        self.node.setDriver('GV6', self.isy_value(Val))

        Val = self.atu.get_convection_status()
        logging.debug('get_convection_status(GV8): {}'.format(Val))
        self.node.setDriver('GV8', self.isy_value(Val))

        Val = self.atu.get_alarmOn()
        logging.debug('get_alarmOn(GV11): {}'.format(Val))
        self.node.setDriver('GV11', self.isy_value(Val))


    def updateISY_longpoll(self):
        logging.debug('update_system - ATU {} Status:'.format(self.atu_nbr))

        Val = self.atu.get_status()
        logging.debug('atu Status (GV0): {}'.format(Val))
        self.node.setDriver('GV0', self.isy_value(Val))

        Val = self.atu.get_air_temp()
        logging.debug('get_air_temp(CLITEMP): {}'.format(Val))
        #self.node.setDriver('GV4', self.isy_value(Val), True, True)
        self.send_temp_to_isy(Val, 'CLITEMP')

        Val = self.atu.get_flow_level()
        logging.debug('get_flow_level(GV1): {}'.format(Val))
        self.node.setDriver('GV1', self.isy_value(Val))


        Val = self.atu.get_HRV_status()
        logging.debug('get_HRV_status(GV2): {}'.format(Val))
        self.node.setDriver('GV2', self.isy_value(Val))

        Val = self.atu.get_activate_HRV()
        logging.debug('get_activate_HRV(GV3): {}'.format(Val))
        self.node.setDriver('GV3', self.isy_value(Val))

        Val = self.atu.get_humidification_status()
        logging.debug('get_humidification_status(GV4): {}'.format(Val))
        self.node.setDriver('GV4', self.isy_value(Val))

        Val = self.atu.get_humidification_enable()
        logging.debug('get_humidification_enable(GV5): {}'.format(Val))
        self.node.setDriver('GV5', self.isy_value(Val))


        Val = self.atu.get_dehumidification_status()
        logging.debug('get_humidification_status(GV4): {}'.format(Val))
        self.node.setDriver('GV6', self.isy_value(Val))

        Val = self.atu.get_dehumidification_enable()
        logging.debug('get_humidification_enable(GV5): {}'.format(Val))
        self.node.setDriver('GV7', self.isy_value(Val))

        Val = self.atu.get_convection_status()
        logging.debug('get_convection_status(GV8): {}'.format(Val))
        self.node.setDriver('GV8', self.isy_value(Val))

        Val = self.atu.get_convection_enable()
        logging.debug('get_humidification_status(GV9): {}'.format(Val))
        self.node.setDriver('GV9', self.isy_value(Val))

        Val = self.atu.get_alarmOn()
        logging.debug('get_alarmOn(GV11): {}'.format(Val))
        self.node.setDriver('GV11', self.isy_value(Val))




    def set_status(self, command):
        status = int(command.get('value'))
        logging.debug('set Status Called {} for atu: {}'.format(status, self.atu_nbr))
        
        temp = self.atu.set_status(status)
        if temp is not None:
            self.node.setDriver('GV0', temp)
        else:
            logging.error('Error calling setStatus')

    def heat_recovery_en(self, command):
        val = int(command.get('value'))
        logging.debug('heat_recovery_en: {}'.format(val))
        temp = self.atu.set_activate_HRV(val)
        if temp is not None:
            time.sleep(0.2)
            self.node.setDriver('GV2', self.atu.get_HRV_status())
            self.node.setDriver('GV3', temp)

    def humidification_en(self, command):
        val = int(command.get('value'))
        logging.debug('humidification_en: {}'.format(val))
        temp = self.atu.set_humidification_enable(val)
        if temp is not None:
            time.sleep(0.2)
            self.node.setDriver('GV4', self.atu.get_humidification_status())
            self.node.setDriver('GV5', temp)



    def dehumidification_en(self, command):
        val = int(command.get('value'))
        logging.debug('dehumidification_en: {}'.format(val))
        temp = self.atu.set_dehumidification_enable(val)
        if temp is not None:
            time.sleep(0.2)
            self.node.setDriver('GV6', self.atu.get_dehumidification_status())
            self.node.setDriver('GV7', temp)


    def convection_en(self, command):
        val = int(command.get('value'))
        logging.debug('convection_en: {}'.format(val))
        temp = self.atu. set_convection_enable(val)
        if temp is not None:
            time.sleep(0.2)
            self.node.setDriver('GV2', self.atu.get_convection_status())
            self.node.setDriver('GV3', temp)


    def set_flow(self, command):
        val = int(command.get('value'))
        logging.debug('set_flow: {}'.format(val))
        temp = self.atu.set_flow_level(val) 
        if  temp is not None:
            time.sleep(0.2)
            self.node.setDriver('GV2', temp)

    def update(self, command):
        logging.debug('update')
        self.updateISY_longpoll()

    commands = { 'UPDATE': update
                ,'STATUS': set_status
                ,'HRVEN' : heat_recovery_en
                ,'HUMEN' : humidification_en
                ,'DEHUMEN' : dehumidification_en
                ,'CONVEN' : convection_en
                ,'SET_FLOW' : set_flow,
                
                }
        