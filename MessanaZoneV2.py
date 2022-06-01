#!/usr/bin/env python3


try:
    import udi_interface
    logging = udi_interface.logging
    Custom = udi_interface.Custom

except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    #logging = logging.getlogging('testLOG')

from subprocess import call
from MessanaNode import messanaNode

#self, controller, primary, address, name, nodeType, nodeNbr, messana
class messanaZones(messanaNode):
    def __init__(self):
        logging.info('init Messana Zones:' )
        self.nodeType = 'zone'
        
        '''
        self.nbrZones = self.getNbrZones()
        self.zoneNbr = zoneNbr
        self.name = name
        self.address = address 
        self.messana = self.parent.messana
        self.id = self.messana.getZoneAddress(self.zoneNbr)

        self.zone_GETKeys = self.messana.zonePullKeys(self.zoneNbr)
        self.zone_PUTKeys = self.messana.zonePushKeys(self.zoneNbr)
        self.zone_ActiveKeys = self.messana.zoneActiveKeys(self.zoneNbr)
        self.ISYforced = False
        
        self.drivers = []
        for key in self.zone_GETKeys:
            self.temp = self.messana.getZoneISYdriverInfo(key, self.zoneNbr)
            if  self.temp != {}:
                self.drivers.append(self.temp)
                #logging.debug(  'driver:  ' +  self.temp['driver'])
                
        self.updateISYdrivers('all')
        self.ISYforced = True
        '''
    def start(self):
        return True

    def updateISYdrivers(self, level):
        #logging.debug('Zone updateISYdrivers')
        for ISYdriver in self.drivers:
            ISYkey = ISYdriver['driver']
            if level == 'active':
                temp = self.messana.getZoneMessanaISYkey(ISYkey, self.zoneNbr)
                if temp in self.zone_ActiveKeys:                    
                    #logging.debug('Messana Zone ISYdrivers ACTIVE ' + temp)
                    status, value = self.messana.getZoneISYValue(ISYkey, self.zoneNbr)
                    if status:
                        if self.ISYforced:
                            self.setDriver(ISYdriver['driver'], value, report = True, force = False)
                        else:
                            self.setDriver(ISYdriver['driver'], value, report = True, force = True)
                        #logging.debug('driver updated for zone '+str(self.zoneNbr)+': ' + ISYdriver['driver'] + ' =  '+str(value))
                    else:
                        logging.error('Error getting ' + ISYdriver['driver'])
            elif level == 'all':
                temp = self.messana.getZoneMessanaISYkey(ISYkey, self.zoneNbr)
                status, value = self.messana.getZoneISYValue(ISYkey, self.zoneNbr)
                #logging.debug('Messana Zone ISYdrivers ALL ' + temp)
                if status:
                    if self.ISYforced:
                        self.setDriver(ISYdriver['driver'], value, report = True, force = False)
                    else:
                        self.setDriver(ISYdriver['driver'], value, report = True, force = True)
                    #logging.debug('driver updated for zone '+str(self.zoneNbr)+': ' + ISYdriver['driver'] + ' =  '+str(value))
                else:
                    logging.error('Error getting ' + ISYdriver['driver'])
            else:
                logging.error('Error!  Unknow level: ' + level)
        
    def stop(self):
        logging.info('stop - Messana Zone Cleaning up')

    def shortPoll(self):
        #logging.debug('Messana Zone shortPoll - zone '+ str(self.zoneNbr))
        #self.messana.updateZoneData('active', self.zoneNbr)
        self.updateISYdrivers('active')
        self.reportDrivers()
                   
    def longPoll(self):
        #logging.debug('Messana Zone longPoll - zone ' + str(self.zoneNbr))
        #self.messana.updateZoneData('all', self.zoneNbr)
        self.updateISYdrivers('all')
        self.reportDrivers()

    def query(self, command=None):
        logging.debug('TOP querry')

    # ISY functions

    def setStatus(self, command):
        #logging.debug('setStatus Called')
        value = int(command.get('value'))
        #logging.debug('Zone'+str(self.zoneNbr)+' setStatus Received:' + str(value))
        if self.messana.zoneSetStatus(value, self.zoneNbr):
            ISYdriver = self.messana.getZoneStatusISYdriver(self.zoneNbr)
            self.setDriver(ISYdriver, value, report = True)

    def setEnergySave(self, command):
        #logging.debug('setEnergySave Called')
        value = int(command.get('value'))
        #logging.debug('Zone'+str(self.zoneNbr)+' setEnergySave Received:' + str(value))
        if self.messana.zoneSetEnergySave(value, self.zoneNbr):
            ISYdriver = self.messana.getZoneEnergySaveISYdriver(self.zoneNbr)
            self.setDriver(ISYdriver, value, report = True)


    def setSetpoint(self, command):
        #logging.debug('setSetpoint Called')
        value = int(command.get('value'))
        #logging.debug('Zone'+str(self.zoneNbr)+' setSetpoint Received:' + str(value))
        if self.messana.zoneSetSetpoint(value, self.zoneNbr):
            ISYdriver = self.messana.getZoneSetPointISYdriver(self.zoneNbr)
            self.setDriver(ISYdriver, value, report = True)


    def enableSchedule(self, command):
        #logging.debug('EnSchedule Called')
        value = int(command.get('value'))
        #logging.debug('Zone'+str(self.zoneNbr)+' EnSchedule Reeived:' + str(value))      
        if self.messana.zoneEnableSchedule(value, self.zoneNbr):
            ISYdriver = self.messana.getZoneEnableScheduleISYdriver(self.zoneNbr)
            self.setDriver(ISYdriver, value, report = True)     
        
    def ISYupdate(self, command):
        #logging.info('ISY-update called - zone' + str(self.zoneNbr))
        self.messana.updateZoneData('all', self.zoneNbr)
        self.updateISYdrivers('all')
        self.reportDrivers()

    def setCurrentDewPt(self, command):
        #logging.debug('setCurrentDP Not tested yet')
        value = int(command.get('value'))
        #logging.debug('Zone'+str(self.zoneNbr)+' setCurrentDewPt Received:' + str(value))
        if self.messana.zonesetCurrentDPt(value, self.zoneNbr):
            ISYdriver = self.messana.getZonesetCurrentDPtISYdriver(self.zoneNbr)
            self.setDriver(ISYdriver, value, report = True)

    def setCurRelHum(self, command):
        #logging.debug('setCurRelHum Not tested yet')
        value = int(command.get('value'))
        #logging.debug('Zone'+str(self.zoneNbr)+' setCurrentDewPt Received:' + str(value))
        if self.messana.zonesetCurrentRH(value, self.zoneNbr):
            ISYdriver = self.messana.getZonesetCurrentRHISYdriver(self.zoneNbr)
            self.setDriver(ISYdriver, value, report = True)

    def setDewTempDehum(self, command):
        #logging.debug('setDewTempDehum Not tested yet')
        value = int(command.get('value'))
        #logging.debug('Zone'+str(self.zoneNbr)+' setCurrentDewPt Received:' + str(value))
        if self.messana.zonesetDehumDpt(value, self.zoneNbr):
            ISYdriver = self.messana.getZonesetDehumDPtISYdriver(self.zoneNbr)
            self.setDriver(ISYdriver, value, report = True)

    def setRelDehum(self, command):
        #logging.debug('setRelDehum Not tested yet')
        value = int(command.get('value'))
        #logging.debug('Zone'+str(self.zoneNbr)+' setCurrentDewPt Received:' + str(value))
        if self.messana.zonesetDehumRH(value, self.zoneNbr):
            ISYdriver = self.messana.getZonesetDehumRHISYdriver(self.zoneNbr)
            self.setDriver(ISYdriver, value, report = True)

    def setDewTempHum(self, command):
        #logging.debug('setDewTempHum Not tested yet')
        value = int(command.get('value'))
        #logging.debug('Zone'+str(self.zoneNbr)+' setCurrentDewPt Received:' + str(value))
        if self.messana.zonesetHumDpt(value, self.zoneNbr):
            ISYdriver = self.messana.getZonesetHumDPtISYdriver(self.zoneNbr)
            self.setDriver(ISYdriver, value, report = True)


    def setRelHum(self, command):
        #logging.debug('setRelHum Not tested yet')
        value = int(command.get('value'))
        #logging.debug('Zone'+str(self.zoneNbr)+' setCurrentDewPt Received:' + str(value))
        if self.messana.zonesetHumRH(value, self.zoneNbr):
            ISYdriver = self.messana.getZonesetHumRHISYdriver(self.zoneNbr)
            self.setDriver(ISYdriver, value, report = True)

    def setCO2(self, command):
        #logging.debug('setCO2 Not tested yet')
        value = int(command.get('value'))
        #logging.debug('Zone'+str(self.zoneNbr)+' setCurrentDewPt Received:' + str(value))
        if self.messana.zonesetCO2(value, self.zoneNbr):
            ISYdriver = self.messana.getZonesetCO2ISYdriver(self.zoneNbr)
            self.setDriver(ISYdriver, value, report = True)
    '''
    commands = { 'SET_SETPOINT' : setSetpoint
                ,'SET_STATUS' : setStatus
                ,'SET_ENERGYSAVE' : setEnergySave
                ,'SET_SCHEDULEON' : enableSchedule 
                ,'UPDATE' : ISYupdate
                ,'CurrentSetpointDP' : setCurrentDewPt
                ,'CurrentSetpointRH' : setCurRelHum
                ,'DehumSetpointDP' : setDewTempDehum
                ,'DehumSetpointRH' : setRelDehum
                ,'HumSetpointDP' : setDewTempHum
                ,'HumSetpointRH' : setRelHum                                                                    
                ,'SET_CO2' : setCO2
                }
    '''