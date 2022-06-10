#!/usr/bin/env python3

import polyinterface
from subprocess import call


LOGGER = polyinterface.LOGGER
#self, controller, primary, address, name, nodeType, nodeNbr, messana
class messanaFanCoil(polyinterface.Node):
    def __init__(self, controller, primary, address, name,  fanCoilNbr):
        super().__init__(controller, primary, address, name)
        LOGGER.info('_init_ Messana FanCoil ' + str(fanCoilNbr) )
        self.fanCoilNbr = fanCoilNbr
        self.name = name
        self.address = address 
        self.messana = self.parent.messana
        self.id = self.messana.getFanCoilAddredd(fanCoilNbr)

        self.fanCoil_GETKeys = self.messana.fanCoilPullKeys(self.fanCoilNbr)
        self.fanCoil_PUTKeys = self.messana.fanCoilPushKeys(self.fanCoilNbr)
        self.fanCoil_ActiveKeys = self.messana.fanCoilActiveKeys(self.fanCoilNbr)
        self.ISYforced = False
        
        self.drivers = []
        for key in self.fanCoil_GETKeys:
            self.temp = self.messana.getFanCoilISYdriverInfo(key, self.fanCoilNbr)
            if  self.temp != {}:
                self.drivers.append(self.temp)
                #LOGGER.debug(  'driver:  ' +  self.temp['driver'])
        self.messana.updateFanCoilData('all', self.fanCoilNbr)
        self.updateISYdrivers('all')
        self.ISYforced = True
       
    def start(self):
        return True


    def updateISYdrivers(self, level):
        #LOGGER.debug('FanCoil updateISYdrivers')
        for ISYdriver in self.drivers:
            ISYkey = ISYdriver['driver']
            if level == 'active':
                temp = self.messana.getFanCoilMessanaISYkey(ISYkey, self.fanCoilNbr)
                if temp in self.fanCoil_ActiveKeys:                    
                    #LOGGER.debug('Messana FanCoil ISYdrivers ACTIVE ' + temp)
                    status, value = self.messana.getFanCoilISYValue(ISYkey, self.fanCoilNbr)
                    if status:
                        if self.ISYforced:
                            self.setDriver(ISYdriver, value, report = True, force = False)
                        else:
                            self.setDriver(ISYdriver, value, report = True, force = True)
                        #LOGGER.debug('driver updated :' + ISYdriver['driver'] + ' =  '+str(value))
                    else:
                        LOGGER.error('Error getting ' + ISYdriver['driver'])
            elif level == 'all':
                temp = self.messana.getFanCoilMessanaISYkey(ISYkey, self.fanCoilNbr)
                status, value = self.messana.getFanCoilISYValue(ISYkey, self.fanCoilNbr)
                #LOGGER.debug('Messana FanCoil ISYdrivers ALL ' + temp)
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
        LOGGER.info('stop - Messana FanCoil Cleaning up')

    def shortPoll(self):
        #LOGGER.debug('Messana FanCoil shortPoll - fanCoil '+ str(self.fanCoilNbr))
        self.messana.updateFanCoilData('active', self.fanCoilNbr)
        self.updateISYdrivers('active')
                   
    def longPoll(self):
        #LOGGER.debug('Messana FanCoil longPoll - fanCoil ' + str(self.fanCoilNbr))
        self.messana.updateFanCoilData('all', self.fanCoilNbr)
        self.updateISYdrivers('all')
        self.reportDrivers()

    def query(self, command=None):
        LOGGER.info('TOP querry')

    def setStatus(self, command):
        #LOGGER.debug('setStatus Called')
        value = int(command.get('value'))
        #LOGGER.debug('FanCoil'+str(self.fanCoilNbr)+' setStatus Received:' + str(value))
        if self.messana.fanCoilSetStatus(value, self.fanCoilNbr):
            ISYdriver = self.messana.getFanCoilStatusISYdriver(self.fanCoilNbr)
            self.setDriver(ISYdriver, value, report = True)

    def fanCoilUpdate(self, command):
        #LOGGER.debug('fanCoilUpdate called')
        self.messana.updateFanCoilData('all', self.fanCoilNbr)
        self.updateISYdrivers('all')
        self.reportDrivers()


    def setCoolingSpeed(self, command):
        #LOGGER.debug('setHeatingSpeed Called')
        value = int(command.get('value'))
        #LOGGER.debug('FanCoil'+str(self.fanCoilNbr)+' setHeatingSpeed Received:' + str(value))
        if self.messana.fanCoilSetCoolingSpeed(value, self.fanCoilNbr):
            ISYdriver = self.messana.getFanCoilCoolingSpeedISYdriver(self.fanCoilNbr)
            self.setDriver(ISYdriver, value, report = True)


    def setHeatingSpeed(self, command):
        #LOGGER.debug('setHeatingSpeed Called')
        value = int(command.get('value'))
        #LOGGER.debug('FanCoil'+str(self.fanCoilNbr)+' setHeatingSpeed Received:' + str(value))
        if self.messana.fanCoilSetHeatingSpeed(value, self.fanCoilNbr):
            ISYdriver = self.messana.getFanCoilHeatingSpeedISYdriver(self.fanCoilNbr)
            self.setDriver(ISYdriver, value, report = True)


 

 

    commands = { 'UPDATE': fanCoilUpdate
                ,'SET_STATUS': setStatus
                ,'SET_COOLING_SPEED': setHeatingSpeed
                ,'SET_HEATING_SPEED' : setHeatingSpeed 
                }


