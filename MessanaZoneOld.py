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

from MessanaControl import messanaInfo

#messana, controller, primary, address, name, nodeType, nodeNbr, messana
class messanaZone(messanaInfo):
    def __init__(messana, IPaddress, apiKey):
        super().__init__(IPaddress, apiKey)
        logging.info('init Messana Zones:' )
        messana.nodeType = 'zone'
        messana.IPaddress = IPaddress
        messana.apiKey = apiKey

        messana.nbrZones = messana.GETsystemData('zoneCount')

        
    def getZoneName(messana, zoneNbr):
        logging.debug('getZoneName {}'.format(zoneNbr))
        val = messana.GETNodeData(zoneNbr, 'name')
        return(val)


    def getZoneTemp(messana, zoneNbr):
        logging.debug('getZoneTemp {}'.format(zoneNbr))
        val = messana.GETNodeData(zoneNbr, 'temperature')
        return(val)

    def getZoneAirTemp(messana, zoneNbr):
        logging.debug('getZoneAirTemp {}'.format(zoneNbr))    
        val = messana.GETNodeData(zoneNbr, 'airTemperature')
        return(val)
    
    def getZoneHumidity(messana, zoneNbr):
        logging.debug('getZoneHumidity {}'.format(zoneNbr))    
        val = messana.GETNodeData(zoneNbr, 'humidity')
        return(val)

    def getZoneSetPoint(messana, zoneNbr):
        logging.debug('getZoneSetPoint {}'.format(zoneNbr))    
        val = messana.GETNodeData(zoneNbr, 'setPoint')
        return(val)

    def getZoneStatus(messana, zoneNbr):
        logging.debug('getZoneStatus {}'.format(zoneNbr))    
        val = messana.GETNodeData(zoneNbr, 'status')
        return(val)

    def getZoneDewpoint(messana, zoneNbr):
        logging.debug('getZoneDewpoint {}'.format(zoneNbr))    
        val = messana.GETNodeData(zoneNbr, 'dewpoint')
        return(val)

    def getZoneEnergySaving(messana, zoneNbr):
        logging.debug('getZoneEnergySaving {}'.format(zoneNbr))    
        val = messana.GETNodeData(zoneNbr, 'energySaving')
        return(val)

    def getZoneCo2(messana, zoneNbr):
        logging.debug('getZoneCo2 {}'.format(zoneNbr))    
        val = messana.GETNodeData(zoneNbr, 'co2')
        return(val)



        
    '''

    def setEnergySave(messana, command):
        #logging.debug('setEnergySave Called')
        value = int(command.get('value'))
        #logging.debug('Zone'+str(messana.zoneNbr)+' setEnergySave Received:' + str(value))
        if messana.messana.zoneSetEnergySave(value, messana.zoneNbr):
            ISYdriver = messana.messana.getZoneEnergySaveISYdriver(messana.zoneNbr)
            messana.setDriver(ISYdriver, value, report = True)


    def setSetpoint(messana, command):
        #logging.debug('setSetpoint Called')
        value = int(command.get('value'))
        #logging.debug('Zone'+str(messana.zoneNbr)+' setSetpoint Received:' + str(value))
        if messana.messana.zoneSetSetpoint(value, messana.zoneNbr):
            ISYdriver = messana.messana.getZoneSetPointISYdriver(messana.zoneNbr)
            messana.setDriver(ISYdriver, value, report = True)


    def enableSchedule(messana, command):
        #logging.debug('EnSchedule Called')
        value = int(command.get('value'))
        #logging.debug('Zone'+str(messana.zoneNbr)+' EnSchedule Reeived:' + str(value))      
        if messana.messana.zoneEnableSchedule(value, messana.zoneNbr):
            ISYdriver = messana.messana.getZoneEnableScheduleISYdriver(messana.zoneNbr)
            messana.setDriver(ISYdriver, value, report = True)     
        
    def ISYupdate(messana, command):
        #logging.info('ISY-update called - zone' + str(messana.zoneNbr))
        messana.messana.updateZoneData('all', messana.zoneNbr)
        messana.updateISYdrivers('all')
        messana.reportDrivers()

    def setCurrentDewPt(messana, command):
        #logging.debug('setCurrentDP Not tested yet')
        value = int(command.get('value'))
        #logging.debug('Zone'+str(messana.zoneNbr)+' setCurrentDewPt Received:' + str(value))
        if messana.messana.zonesetCurrentDPt(value, messana.zoneNbr):
            ISYdriver = messana.messana.getZonesetCurrentDPtISYdriver(messana.zoneNbr)
            messana.setDriver(ISYdriver, value, report = True)

    def setCurRelHum(messana, command):
        #logging.debug('setCurRelHum Not tested yet')
        value = int(command.get('value'))
        #logging.debug('Zone'+str(messana.zoneNbr)+' setCurrentDewPt Received:' + str(value))
        if messana.messana.zonesetCurrentRH(value, messana.zoneNbr):
            ISYdriver = messana.messana.getZonesetCurrentRHISYdriver(messana.zoneNbr)
            messana.setDriver(ISYdriver, value, report = True)

    def setDewTempDehum(messana, command):
        #logging.debug('setDewTempDehum Not tested yet')
        value = int(command.get('value'))
        #logging.debug('Zone'+str(messana.zoneNbr)+' setCurrentDewPt Received:' + str(value))
        if messana.messana.zonesetDehumDpt(value, messana.zoneNbr):
            ISYdriver = messana.messana.getZonesetDehumDPtISYdriver(messana.zoneNbr)
            messana.setDriver(ISYdriver, value, report = True)

    def setRelDehum(messana, command):
        #logging.debug('setRelDehum Not tested yet')
        value = int(command.get('value'))
        #logging.debug('Zone'+str(messana.zoneNbr)+' setCurrentDewPt Received:' + str(value))
        if messana.messana.zonesetDehumRH(value, messana.zoneNbr):
            ISYdriver = messana.messana.getZonesetDehumRHISYdriver(messana.zoneNbr)
            messana.setDriver(ISYdriver, value, report = True)

    def setDewTempHum(messana, command):
        #logging.debug('setDewTempHum Not tested yet')
        value = int(command.get('value'))
        #logging.debug('Zone'+str(messana.zoneNbr)+' setCurrentDewPt Received:' + str(value))
        if messana.messana.zonesetHumDpt(value, messana.zoneNbr):
            ISYdriver = messana.messana.getZonesetHumDPtISYdriver(messana.zoneNbr)
            messana.setDriver(ISYdriver, value, report = True)


    def setRelHum(messana, command):
        #logging.debug('setRelHum Not tested yet')
        value = int(command.get('value'))
        #logging.debug('Zone'+str(messana.zoneNbr)+' setCurrentDewPt Received:' + str(value))
        if messana.messana.zonesetHumRH(value, messana.zoneNbr):
            ISYdriver = messana.messana.getZonesetHumRHISYdriver(messana.zoneNbr)
            messana.setDriver(ISYdriver, value, report = True)

    def setCO2(messana, command):
        #logging.debug('setCO2 Not tested yet')
        value = int(command.get('value'))
        #logging.debug('Zone'+str(messana.zoneNbr)+' setCurrentDewPt Received:' + str(value))
        if messana.messana.zonesetCO2(value, messana.zoneNbr):
            ISYdriver = messana.messana.getZonesetCO2ISYdriver(messana.zoneNbr)
            messana.setDriver(ISYdriver, value, report = True)
    '''
