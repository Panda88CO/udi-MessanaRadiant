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

#messana, controller, primary, address, name, nodeType, nodeNbr, messana
class messanaZone(messanaInfo):
    def __init__(self, IPaddress, messanaKey):
        super().__init__(IPaddress, messanaKey)
        logging.info('init Zone:' )
        
        self.node_type = 'zone'
        self.IPaddress = IPaddress
        self.apiKey = messanaKey

        self.stateList = [0,1]

       
    def get_name(self, zone_nbr):
        return( self.GET_node_data(zone_nbr, 'name'))


    def get_temp(self, zone_nbr):
        return(self.GET_node_data(zone_nbr, 'temperature'))
  

    def get_air_temp(self, zone_nbr):
        return(self.GET_node_data(zone_nbr, 'airTemperature'))

    
    def get_setpoint(self, zone_nbr):
        return(self.GET_node_data(zone_nbr, 'setpoint'))


    def get_humidity(self, zone_nbr):
        logging.debug('get_humidity {}'.format(zone_nbr))    
        val = self.GET_node_data(zone_nbr, 'humidity')
        return(val)

    def get_air_quality(self, zone_nbr):
        val = self.GET_node_data(zone_nbr, 'airQuality')
        return(val)


    def get_set_pointCO2(self, zone_nbr):
        return( self.GET_node_data(zone_nbr, 'setpointCO2'))


    def get_status(self, zone_nbr):
        logging.debug('get_status {}'.format(zone_nbr))    
        return( self.GET_node_data(zone_nbr, 'status'))

    def set_status(self, zone_nbr, state):
        if state in self.stateList:
            return(self.PUT_node_data(zone_nbr,'status', state ))
        else:
            logging.error ('Wrong Status state passed ([0,1]: {}'.format(state))
            return(False)
          
    def get_dewpoint(self, zone_nbr):
        return( self.GET_node_data(zone_nbr, 'dewpoint'))
  
    def get_energy_saving(self, zone_nbr):
        return( self.GET_node_data(zone_nbr, 'energySaving'))

    def set_energy_save(self, zone_nbr, state):
        if state in self.stateList:
            return(self.PUT_node_data(zone_nbr,'energySaving', state ))
        else:
            logging.error ('Wrong enerySaving state passed ([0,1]: {}'.format(state))
            return(False)

    def get_co2(self, zone_nbr):
        logging.debug('get_co2 {}'.format(zone_nbr))    
        return(self.GET_node_data(zone_nbr, 'co2'))
    





          


        
    '''

   


    def setSetpoint(messana, command):
        #logging.debug('setSetpoint Called')
        value = int(command.get('value'))
        #logging.debug('Zone'+str(messana.zone_nbr)+' setSetpoint Received:' + str(value))
        if messana.messana.zoneSetSetpoint(value, messana.zone_nbr):
            ISYdriver = messana.messana.getSetPointISYdriver(messana.zone_nbr)
            messana.setDriver(ISYdriver, value, report = True)


    def enableSchedule(messana, command):
        #logging.debug('EnSchedule Called')
        value = int(command.get('value'))
        #logging.debug('Zone'+str(messana.zone_nbr)+' EnSchedule Reeived:' + str(value))      
        if messana.messana.zoneEnableSchedule(value, messana.zone_nbr):
            ISYdriver = messana.messana.getEnableScheduleISYdriver(messana.zone_nbr)
            messana.setDriver(ISYdriver, value, report = True)     
        
    def ISYupdate(messana, command):
        #logging.info('ISY-update called - zone' + str(messana.zone_nbr))
        messana.messana.updateZoneData('all', messana.zone_nbr)
        messana.updateISYdrivers('all')
        messana.reportDrivers()

    def setCurrentDewPt(messana, command):
        #logging.debug('setCurrentDP Not tested yet')
        value = int(command.get('value'))
        #logging.debug('Zone'+str(messana.zone_nbr)+' setCurrentDewPt Received:' + str(value))
        if messana.messana.zonesetCurrentDPt(value, messana.zone_nbr):
            ISYdriver = messana.messana.getsetCurrentDPtISYdriver(messana.zone_nbr)
            messana.setDriver(ISYdriver, value, report = True)

    def setCurRelHum(messana, command):
        #logging.debug('setCurRelHum Not tested yet')
        value = int(command.get('value'))
        #logging.debug('Zone'+str(messana.zone_nbr)+' setCurrentDewPt Received:' + str(value))
        if messana.messana.zonesetCurrentRH(value, messana.zone_nbr):
            ISYdriver = messana.messana.getsetCurrentRHISYdriver(messana.zone_nbr)
            messana.setDriver(ISYdriver, value, report = True)

    def setDewTempDehum(messana, command):
        #logging.debug('setDewTempDehum Not tested yet')
        value = int(command.get('value'))
        #logging.debug('Zone'+str(messana.zone_nbr)+' setCurrentDewPt Received:' + str(value))
        if messana.messana.zonesetDehumDpt(value, messana.zone_nbr):
            ISYdriver = messana.messana.getsetDehumDPtISYdriver(messana.zone_nbr)
            messana.setDriver(ISYdriver, value, report = True)

    def setRelDehum(messana, command):
        #logging.debug('setRelDehum Not tested yet')
        value = int(command.get('value'))
        #logging.debug('Zone'+str(messana.zone_nbr)+' setCurrentDewPt Received:' + str(value))
        if messana.messana.zonesetDehumRH(value, messana.zone_nbr):
            ISYdriver = messana.messana.getsetDehumRHISYdriver(messana.zone_nbr)
            messana.setDriver(ISYdriver, value, report = True)

    def setDewTempHum(messana, command):
        #logging.debug('setDewTempHum Not tested yet')
        value = int(command.get('value'))
        #logging.debug('Zone'+str(messana.zone_nbr)+' setCurrentDewPt Received:' + str(value))
        if messana.messana.zonesetHumDpt(value, messana.zone_nbr):
            ISYdriver = messana.messana.getsetHumDPtISYdriver(messana.zone_nbr)
            messana.setDriver(ISYdriver, value, report = True)


    def setRelHum(messana, command):
        #logging.debug('setRelHum Not tested yet')
        value = int(command.get('value'))
        #logging.debug('Zone'+str(messana.zone_nbr)+' setCurrentDewPt Received:' + str(value))
        if messana.messana.zonesetHumRH(value, messana.zone_nbr):
            ISYdriver = messana.messana.getsetHumRHISYdriver(messana.zone_nbr)
            messana.setDriver(ISYdriver, value, report = True)

    def setCO2(messana, command):
        #logging.debug('setCO2 Not tested yet')
        value = int(command.get('value'))
        #logging.debug('Zone'+str(messana.zone_nbr)+' setCurrentDewPt Received:' + str(value))
        if messana.messana.zonesetCO2(value, messana.zone_nbr):
            ISYdriver = messana.messana.getsetCO2ISYdriver(messana.zone_nbr)
            messana.setDriver(ISYdriver, value, report = True)
    '''
