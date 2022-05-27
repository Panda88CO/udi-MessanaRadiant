#!/usr/bin/env python3

import polyinterface
from subprocess import call


LOGGER = polyinterface.LOGGER
#self, controller, primary, address, name, nodeType, nodeNbr, messana
class messanaHotWater(polyinterface.Node):
    def __init__(self, controller, primary, address, name,  hotWaterNbr):
        super().__init__(controller, primary, address, name)
        LOGGER.info('_init_ Messana Hot Water ' + str(hotWaterNbr) )
        self.hotWaterNbr = hotWaterNbr
        self.name = name
        self.address = address 
        self.ID = self.messana.getHotWaterAddress(hotWaterNbr)

        self.hotWater_GETKeys = self.messana.hotWaterPullKeys(self.hotWaterNbr)
        self.hotWater_PUTKeys = self.messana.hotWaterPushKeys(self.hotWaterNbr)
        self.hotWater_ActiveKeys = self.messana.hotWaterActiveKeys(self.hotWaterNbr)
        self.ISYforced = False
        
        self.drivers = []
        for key in self.hotWater_GETKeys:
            self.temp = self.messana.getHotWaterISYdriverInfo(key, self.hotWaterNbr)
            if  self.temp != {}:
                self.drivers.append(self.temp)
                #LOGGER.debug(  'driver:  ' +  self.temp['driver'])
        self.messana.updateHotWaterData('all', self.hotWaterNbr)
        self.updateISYdrivers('all')
        self.ISYforced = True
       
    def start(self):


        return True


    def updateISYdrivers(self, level):
        #LOGGER.debug('HotWater updateISYdrivers')
        for ISYdriver in self.drivers:
            ISYkey = ISYdriver['driver']
            if level == 'active':
                temp = self.messana.getHotWaterMessanaISYkey(ISYkey, self.hotWaterNbr)
                if temp in self.hotWater_ActiveKeys:                    
                    #LOGGER.debug('Messana HotWater ISYdrivers ACTIVE ' + temp)
                    status, value = self.messana.getHotWaterISYValue(ISYkey, self.hotWaterNbr)
                    if status:
                        if self.ISYforced:
                            self.setDriver(ISYdriver, value, report = True, force = False)
                        else:
                            self.setDriver(ISYdriver, value, report = True, force = True)
                        #LOGGER.debug('driver updated :' + ISYdriver['driver'] + ' =  '+str(value))
                    else:
                        LOGGER.error('Error getting ' + ISYdriver['driver'])
            elif level == 'all':
                temp = self.messana.getHotWaterMessanaISYkey(ISYkey, self.hotWaterNbr)
                status, value = self.messana.getHotWaterISYValue(ISYkey, self.hotWaterNbr)
                #LOGGER.debug('Messana HotWater ISYdrivers ALL ' + temp)
                if status:
                    if self.ISYforced:
                        self.setDriver(ISYdriver, value, report = True, force = False)
                    else:
                        self.setDriver(ISYdriver, value, report = True, force = True)
                    #LOGGER.debug('driver updated :' + ISYdriver['driver'] + ' =  '+str(value))
                else:
                    LOGGER.error('Error getting ' + ISYdriver['driver'])
            else:
                LOGGER.error('Error!  Unknow level: ' + level)
        
    def stop(self):
        LOGGER.info('stop - Messana HotWater Cleaning up')

    def shortPoll(self):
        #LOGGER.debug('Messana HotWater shortPoll - hotWater '+ str(self.hotWaterNbr))
        self.messana.updateHotWaterData('active', self.hotWaterNbr)
        self.updateISYdrivers('active')
                   
    def longPoll(self):
        #LOGGER.debug('Messana HotWater longPoll - hotWater ' + str(self.hotWaterNbr))
        self.messana.updateHotWaterData('all', self.hotWaterNbr)
        self.updateISYdrivers('all')
        self.reportDrivers()

    def query(self, command=None):
        LOGGER.info('TOP querry')

    def setStatus(self, command):
        #LOGGER.debug('setStatus Called')
        value = int(command.get('value'))
        #LOGGER.debug('HotWater'+str(self.hotWaterNbr)+' setStatus Received:' + str(value))
        if self.messana.hotWaterSetStatus(value, self.hotWaterNbr):
            ISYdriver = self.messana.getHotWaterStatusISYdriver(self.hotWaterNbr)
            self.setDriver(ISYdriver, value, report = True)

    def HotWaterUpdate(self, command):
        #LOGGER.debug('HWupdate called' + str(self.hotWaterNbr))
        self.messana.updateHotWaterData('all', self.hotWaterNbr)
        self.updateISYdrivers('all')
        self.reportDrivers()
    

    def setHWTargetTemp(self, command):
        #LOGGER.debug('setSetpoint Called')
        value = int(command.get('value'))
        #LOGGER.debug('HotWater'+str(self.hotWaterNbr)+' Target Temp Received:' + str(value))
        if self.messana.hotWaterSetTargetTempt(value, self.hotWaterNbr):
            ISYdriver = self.messana.getHotWaterSetTargetTempISYdriver(self.hotWaterNbr)
            self.setDriver(ISYdriver, value, report = True)


    commands = { 'SET_TARGETTEMP': setHWTargetTemp
                ,'SET_STATUS' : setStatus
                , 'UPDATE'    : HotWaterUpdate
                }



