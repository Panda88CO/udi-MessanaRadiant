#!/usr/bin/env python3

import polyinterface
from subprocess import call

LOGGER = polyinterface.LOGGER
#self, controller, primary, address, name, nodeType, nodeNbr, messana
class messanaZone(polyinterface.Node):
    def __init__(self, controller, primary, address, name,  zoneNbr):
        super().__init__(controller, primary, address, name)
        LOGGER.info('_init_ Messana Zone ' + str(zoneNbr) )
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
                #LOGGER.debug(  'driver:  ' +  self.temp['driver'])
                
        self.updateISYdrivers('all')
        self.ISYforced = True
       
    def start(self):
        return True

    def updateISYdrivers(self, level):
        #LOGGER.debug('Zone updateISYdrivers')
        for ISYdriver in self.drivers:
            ISYkey = ISYdriver['driver']
            if level == 'active':
                temp = self.messana.getZoneMessanaISYkey(ISYkey, self.zoneNbr)
                if temp in self.zone_ActiveKeys:                    
                    #LOGGER.debug('Messana Zone ISYdrivers ACTIVE ' + temp)
                    status, value = self.messana.getZoneISYValue(ISYkey, self.zoneNbr)
                    if status:
                        if self.ISYforced:
                            self.setDriver(ISYdriver['driver'], value, report = True, force = False)
                        else:
                            self.setDriver(ISYdriver['driver'], value, report = True, force = True)
                        #LOGGER.debug('driver updated for zone '+str(self.zoneNbr)+': ' + ISYdriver['driver'] + ' =  '+str(value))
                    else:
                        LOGGER.error('Error getting ' + ISYdriver['driver'])
            elif level == 'all':
                temp = self.messana.getZoneMessanaISYkey(ISYkey, self.zoneNbr)
                status, value = self.messana.getZoneISYValue(ISYkey, self.zoneNbr)
                #LOGGER.debug('Messana Zone ISYdrivers ALL ' + temp)
                if status:
                    if self.ISYforced:
                        self.setDriver(ISYdriver['driver'], value, report = True, force = False)
                    else:
                        self.setDriver(ISYdriver['driver'], value, report = True, force = True)
                    #LOGGER.debug('driver updated for zone '+str(self.zoneNbr)+': ' + ISYdriver['driver'] + ' =  '+str(value))
                else:
                    LOGGER.error('Error getting ' + ISYdriver['driver'])
            else:
                LOGGER.error('Error!  Unknow level: ' + level)
        
    def stop(self):
        LOGGER.info('stop - Messana Zone Cleaning up')

    def shortPoll(self):
        #LOGGER.debug('Messana Zone shortPoll - zone '+ str(self.zoneNbr))
        #self.messana.updateZoneData('active', self.zoneNbr)
        self.updateISYdrivers('active')
        self.reportDrivers()
                   
    def longPoll(self):
        #LOGGER.debug('Messana Zone longPoll - zone ' + str(self.zoneNbr))
        #self.messana.updateZoneData('all', self.zoneNbr)
        self.updateISYdrivers('all')
        self.reportDrivers()

    def query(self, command=None):
        LOGGER.debug('TOP querry')

    # ISY functions

    def setStatus(self, command):
        #LOGGER.debug('setStatus Called')
        value = int(command.get('value'))
        #LOGGER.debug('Zone'+str(self.zoneNbr)+' setStatus Received:' + str(value))
        if self.messana.zoneSetStatus(value, self.zoneNbr):
            ISYdriver = self.messana.getZoneStatusISYdriver(self.zoneNbr)
            self.setDriver(ISYdriver, value, report = True)

    def setEnergySave(self, command):
        #LOGGER.debug('setEnergySave Called')
        value = int(command.get('value'))
        #LOGGER.debug('Zone'+str(self.zoneNbr)+' setEnergySave Received:' + str(value))
        if self.messana.zoneSetEnergySave(value, self.zoneNbr):
            ISYdriver = self.messana.getZoneEnergySaveISYdriver(self.zoneNbr)
            self.setDriver(ISYdriver, value, report = True)


    def setSetpoint(self, command):
        #LOGGER.debug('setSetpoint Called')
        value = int(command.get('value'))
        #LOGGER.debug('Zone'+str(self.zoneNbr)+' setSetpoint Received:' + str(value))
        if self.messana.zoneSetSetpoint(value, self.zoneNbr):
            ISYdriver = self.messana.getZoneSetPointISYdriver(self.zoneNbr)
            self.setDriver(ISYdriver, value, report = True)


    def enableSchedule(self, command):
        #LOGGER.debug('EnSchedule Called')
        value = int(command.get('value'))
        #LOGGER.debug('Zone'+str(self.zoneNbr)+' EnSchedule Reeived:' + str(value))      
        if self.messana.zoneEnableSchedule(value, self.zoneNbr):
            ISYdriver = self.messana.getZoneEnableScheduleISYdriver(self.zoneNbr)
            self.setDriver(ISYdriver, value, report = True)     
        
    def ISYupdate(self, command):
        #LOGGER.info('ISY-update called - zone' + str(self.zoneNbr))
        self.messana.updateZoneData('all', self.zoneNbr)
        self.updateISYdrivers('all')
        self.reportDrivers()

    def setCurrentDewPt(self, command):
        #LOGGER.debug('setCurrentDP Not tested yet')
        value = int(command.get('value'))
        #LOGGER.debug('Zone'+str(self.zoneNbr)+' setCurrentDewPt Received:' + str(value))
        if self.messana.zonesetCurrentDPt(value, self.zoneNbr):
            ISYdriver = self.messana.getZonesetCurrentDPtISYdriver(self.zoneNbr)
            self.setDriver(ISYdriver, value, report = True)

    def setCurRelHum(self, command):
        #LOGGER.debug('setCurRelHum Not tested yet')
        value = int(command.get('value'))
        #LOGGER.debug('Zone'+str(self.zoneNbr)+' setCurrentDewPt Received:' + str(value))
        if self.messana.zonesetCurrentRH(value, self.zoneNbr):
            ISYdriver = self.messana.getZonesetCurrentRHISYdriver(self.zoneNbr)
            self.setDriver(ISYdriver, value, report = True)

    def setDewTempDehum(self, command):
        #LOGGER.debug('setDewTempDehum Not tested yet')
        value = int(command.get('value'))
        #LOGGER.debug('Zone'+str(self.zoneNbr)+' setCurrentDewPt Received:' + str(value))
        if self.messana.zonesetDehumDpt(value, self.zoneNbr):
            ISYdriver = self.messana.getZonesetDehumDPtISYdriver(self.zoneNbr)
            self.setDriver(ISYdriver, value, report = True)

    def setRelDehum(self, command):
        #LOGGER.debug('setRelDehum Not tested yet')
        value = int(command.get('value'))
        #LOGGER.debug('Zone'+str(self.zoneNbr)+' setCurrentDewPt Received:' + str(value))
        if self.messana.zonesetDehumRH(value, self.zoneNbr):
            ISYdriver = self.messana.getZonesetDehumRHISYdriver(self.zoneNbr)
            self.setDriver(ISYdriver, value, report = True)

    def setDewTempHum(self, command):
        #LOGGER.debug('setDewTempHum Not tested yet')
        value = int(command.get('value'))
        #LOGGER.debug('Zone'+str(self.zoneNbr)+' setCurrentDewPt Received:' + str(value))
        if self.messana.zonesetHumDpt(value, self.zoneNbr):
            ISYdriver = self.messana.getZonesetHumDPtISYdriver(self.zoneNbr)
            self.setDriver(ISYdriver, value, report = True)


    def setRelHum(self, command):
        #LOGGER.debug('setRelHum Not tested yet')
        value = int(command.get('value'))
        #LOGGER.debug('Zone'+str(self.zoneNbr)+' setCurrentDewPt Received:' + str(value))
        if self.messana.zonesetHumRH(value, self.zoneNbr):
            ISYdriver = self.messana.getZonesetHumRHISYdriver(self.zoneNbr)
            self.setDriver(ISYdriver, value, report = True)

    def setCO2(self, command):
        #LOGGER.debug('setCO2 Not tested yet')
        value = int(command.get('value'))
        #LOGGER.debug('Zone'+str(self.zoneNbr)+' setCurrentDewPt Received:' + str(value))
        if self.messana.zonesetCO2(value, self.zoneNbr):
            ISYdriver = self.messana.getZonesetCO2ISYdriver(self.zoneNbr)
            self.setDriver(ISYdriver, value, report = True)

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
    