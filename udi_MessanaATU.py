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
            'GV10' = ntdOn
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
        {'driver': 'GV10', 'value': 99, 'uom': 25},
        {'driver': 'GV11', 'value': 99, 'uom': 25},
        {'driver': 'ST', 'value': 0, 'uom': 25},
        ]

    def __init__(self, polyglot, primary, address, name, atu_nbr, messana_info):
        super().__init__(polyglot, primary, address, name)
        logging.info('init Messana ATU {}:'.format(atu_nbr) )
        #self.node_type = 'atu'
        #self.parent = primary
        self.primary = primary
        #self.id = 'atu'
        self.atu_nbr = atu_nbr
        self.atu = messana_atu(self.atu_nbr, messana_info)

        self.address = address
        tmp_name = self.atu.name
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
        logging.debug('atu get_temp(CLITEMP)): {}'.format(Val))
        #self.node.setDriver('GV4', self.isy_value(Val), True, True)
        self.send_temp_to_isy(Val, 'CLITEMP')

        Val = self.atu.get_flow_level()
        logging.debug('Humidity(CLIHUM): {}'.format(Val))
        self.node.setDriver('CLIHUM', self.isy_value(Val))

        Val = self.atu.get_dewpoint()
        logging.debug('get_dewpoint (DEWPT): {}'.format(Val))
        self.send_temp_to_isy(Val, 'DEWPT')



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
        logging.debug('Schedule Mode(GV2): {}'.format(Val))
        self.node.setDriver('GV1', self.isy_value(Val))

        Val = self.atu.get_setpoint()
        logging.debug('Set point (GV3): {}'.format(Val))
        self.send_temp_to_isy(Val, 'GV3')
        #self.node.setDriver('GV3', self.isy_value(Val))



        Val = self.atu.get_humidity()
        logging.debug('Humidity(CLIHUM): {}'.format(Val))
        self.node.setDriver('CLIHUM', self.isy_value(Val), True, True)

        Val = self.atu.get_dewpoint()
        logging.debug('get_dewpoint (DEWPT): {}'.format(Val))
        self.send_temp_to_isy(Val, 'DEWPT')



    def set_status(self, command):
        status = int(command.get('value'))
        logging.debug('set Status Called {} for atu: {}'.format(status, self.atu_nbr))
        if self.atu.set_status(status):
            self.node.setDriver('GV0', status)
        else:
            logging.error('Error calling setStatus')

    def heat_recovery_en(self, command):
        val = int(command.get('value'))
        logging.debug('heat_recovery_en: {}'.format(val))

    def humidification_en(self, command):
        val = int(command.get('value'))
        logging.debug('humidification_en: {}'.format(val))

    def dehumidification_en(self, command):
        val = int(command.get('value'))
        logging.debug('dehumidification_en: {}'.format(val))

    def convection_en(self, command):
        val = int(command.get('value'))
        logging.debug('convection_en: {}'.format(val))

    def set_flow(self, command):
        val = int(command.get('value'))
        logging.debug('set_flow: {}'.format(val))


    commands = { 'UPDATE': updateISY_longpoll
                ,'STATUS': set_status
                ,'HRVEN' : heat_recovery_en
                ,'HUMEN' : humidification_en
                ,'DEHUMEN' : dehumidification_en
                ,'CONVEN' : convection_en
                ,'SET_FLOW' : set_flow,
     #           ,'SETPOINTCO2' : set_setpoint_co2        
     #           ,'SCHEDULEON' : set_schedule
                
                }
        