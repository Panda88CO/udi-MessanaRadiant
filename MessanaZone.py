#!/usr/bin/env python3

try:
    import udi_interface
    logging = udi_interface.logging
    Custom = udi_interface.Custom

except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    #logging = logging.getlogging('testLOG')

#from subprocess import call
from MessanaInfo import messanaInfo

#self, controller, primary, address, name, nodeType, nodeNbr, self
class messanaZone(messanaInfo):
    def __init__(self, IPaddress, apiKey):
        super().__init__(IPaddress, apiKey)
        logging.info('init Zone:' )
        self.node_type = 'zone'
        self.IPaddress = IPaddress
        self.apiKey = apiKey
        self.nbr_zones = self.GET_system_data('zoneCount')

        
    def get_name(self, zone_nbr):
        logging.debug('get_name {}'.format(zone_nbr))
        val = self.GET_node_data(zone_nbr, 'name')
        return(val)


    def get_temp(self, zone_nbr):
        logging.debug('get_temp {}'.format(zone_nbr))
        val = self.GET_node_data(zone_nbr, 'temperature')
        return(val)

    def get_air_temp(self, zone_nbr):
        logging.debug('get_air_temp {}'.format(zone_nbr))    
        val = self.GET_node_data(zone_nbr, 'airTemperature')
        return(val)
    
    def get_humidity(self, zone_nbr):
        logging.debug('get_humidity {}'.format(zone_nbr))    
        val = self.GET_node_data(zone_nbr, 'humidity')
        return(val)

    def get_set_point(self, zone_nbr):
        logging.debug('get_set_point {}'.format(zone_nbr))    
        val = self.GET_node_data(zone_nbr, 'setPoint')
        return(val)

    def get_status(self, zone_nbr):
        logging.debug('get_status {}'.format(zone_nbr))    
        val = self.GET_node_data(zone_nbr, 'status')
        return(val)

    def get_dewpoint(self, zone_nbr):
        logging.debug('get_dewpoint {}'.format(zone_nbr))    
        val = self.GET_node_data(zone_nbr, 'dewpoint')
        return(val)

    def get_energy_saving(self, zone_nbr):
        logging.debug('get_energy_saving {}'.format(zone_nbr))    
        val = self.GET_node_data(zone_nbr, 'energySaving')
        return(val)

    def get_co2(self, zone_nbr):
        logging.debug('get_co2 {}'.format(zone_nbr))    
        val = self.GET_node_data(zone_nbr, 'co2')
        return(val)



        
    '''

    def setEnergySave(self, command):
        #logging.debug('setEnergySave Called')
        value = int(command.get('value'))
        #logging.debug('Zone'+str(self.zone_nbr)+' setEnergySave Received:' + str(value))
        if self.self.zoneSetEnergySave(value, self.zone_nbr):
            ISYdriver = self.self.getEnergySaveISYdriver(self.zone_nbr)
            self.setDriver(ISYdriver, value, report = True)


    def setSetpoint(self, command):
        #logging.debug('setSetpoint Called')
        value = int(command.get('value'))
        #logging.debug('Zone'+str(self.zone_nbr)+' setSetpoint Received:' + str(value))
        if self.self.zoneSetSetpoint(value, self.zone_nbr):
            ISYdriver = self.self.getSetPointISYdriver(self.zone_nbr)
            self.setDriver(ISYdriver, value, report = True)


    def enableSchedule(self, command):
        #logging.debug('EnSchedule Called')
        value = int(command.get('value'))
        #logging.debug('Zone'+str(self.zone_nbr)+' EnSchedule Reeived:' + str(value))      
        if self.self.zoneEnableSchedule(value, self.zone_nbr):
            ISYdriver = self.self.getEnableScheduleISYdriver(self.zone_nbr)
            self.setDriver(ISYdriver, value, report = True)     
        
    def ISYupdate(self, command):
        #logging.info('ISY-update called - zone' + str(self.zone_nbr))
        self.self.updateZoneData('all', self.zone_nbr)
        self.updateISYdrivers('all')
        self.reportDrivers()

    def setCurrentDewPt(self, command):
        #logging.debug('setCurrentDP Not tested yet')
        value = int(command.get('value'))
        #logging.debug('Zone'+str(self.zone_nbr)+' setCurrentDewPt Received:' + str(value))
        if self.self.zonesetCurrentDPt(value, self.zone_nbr):
            ISYdriver = self.self.getsetCurrentDPtISYdriver(self.zone_nbr)
            self.setDriver(ISYdriver, value, report = True)

    def setCurRelHum(self, command):
        #logging.debug('setCurRelHum Not tested yet')
        value = int(command.get('value'))
        #logging.debug('Zone'+str(self.zone_nbr)+' setCurrentDewPt Received:' + str(value))
        if self.self.zonesetCurrentRH(value, self.zone_nbr):
            ISYdriver = self.self.getsetCurrentRHISYdriver(self.zone_nbr)
            self.setDriver(ISYdriver, value, report = True)

    def setDewTempDehum(self, command):
        #logging.debug('setDewTempDehum Not tested yet')
        value = int(command.get('value'))
        #logging.debug('Zone'+str(self.zone_nbr)+' setCurrentDewPt Received:' + str(value))
        if self.self.zonesetDehumDpt(value, self.zone_nbr):
            ISYdriver = self.self.getsetDehumDPtISYdriver(self.zone_nbr)
            self.setDriver(ISYdriver, value, report = True)

    def setRelDehum(self, command):
        #logging.debug('setRelDehum Not tested yet')
        value = int(command.get('value'))
        #logging.debug('Zone'+str(self.zone_nbr)+' setCurrentDewPt Received:' + str(value))
        if self.self.zonesetDehumRH(value, self.zone_nbr):
            ISYdriver = self.self.getsetDehumRHISYdriver(self.zone_nbr)
            self.setDriver(ISYdriver, value, report = True)

    def setDewTempHum(self, command):
        #logging.debug('setDewTempHum Not tested yet')
        value = int(command.get('value'))
        #logging.debug('Zone'+str(self.zone_nbr)+' setCurrentDewPt Received:' + str(value))
        if self.self.zonesetHumDpt(value, self.zone_nbr):
            ISYdriver = self.self.getsetHumDPtISYdriver(self.zone_nbr)
            self.setDriver(ISYdriver, value, report = True)


    def setRelHum(self, command):
        #logging.debug('setRelHum Not tested yet')
        value = int(command.get('value'))
        #logging.debug('Zone'+str(self.zone_nbr)+' setCurrentDewPt Received:' + str(value))
        if self.self.zonesetHumRH(value, self.zone_nbr):
            ISYdriver = self.self.getsetHumRHISYdriver(self.zone_nbr)
            self.setDriver(ISYdriver, value, report = True)

    def setCO2(self, command):
        #logging.debug('setCO2 Not tested yet')
        value = int(command.get('value'))
        #logging.debug('Zone'+str(self.zone_nbr)+' setCurrentDewPt Received:' + str(value))
        if self.self.zonesetCO2(value, self.zone_nbr):
            ISYdriver = self.self.getsetCO2ISYdriver(self.zone_nbr)
            self.setDriver(ISYdriver, value, report = True)
    '''
