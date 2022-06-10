#!/usr/bin/env python3

import polyinterface
from subprocess import call
#from MessanaInfo import MessanaInfo

LOGGER = polyinterface.LOGGER
#self, controller, primary, address, name, nodeType, nodeNbr, messana
class messanaBufTank(polyinterface.Node):
    def __init__(self, controller, primary, address, name,  bufferTankNbr):
        super().__init__(controller, primary, address, name)
        LOGGER.info('_init_ Messana BufferTanks ' + str(bufferTankNbr) )
        self.bufferTankNbr = bufferTankNbr
        self.name = name
        self.address = address 
        self.messana = self.parent.messana
        self.id = self.messana.getBufferTankAddress(bufferTankNbr)

        self.bufferTank_GETKeys = self.messana.bufferTankPullKeys(self.bufferTankNbr)
        self.bufferTank_PUTKeys = self.messana.bufferTankPushKeys(self.bufferTankNbr)
        self.bufferTank_ActiveKeys = self.messana.bufferTankActiveKeys(self.bufferTankNbr)
        self.ISYforced = False
        
        self.drivers = []
        for key in self.bufferTank_GETKeys:
            #LOGGER.debug('Buffer driver loop ' + key)
            self.temp = self.messana.getBufferTankISYdriverInfo(key, self.bufferTankNbr)
            #LOGGER.debug('Buffer Tank driver ' + str(self.temp))
            if  self.temp != {}:
                self.drivers.append(self.temp)
                #LOGGER.debug(  'driver:  ' +  self.temp['driver'])
        self.messana.updateBufferTankData('all', self.bufferTankNbr)
        self.updateISYdrivers('all')
        self.ISYforced = True
       
    def start(self):
        return True


    def updateISYdrivers(self, level):
        #LOGGER.debug('BufferTanks updateISYdrivers')
        for ISYdriver in self.drivers:
            ISYkey = ISYdriver['driver']
            if level == 'active':
                temp = self.messana.getBufferTankMessanaISYkey(ISYkey, self.bufferTankNbr)
                if temp in self.bufferTank_ActiveKeys:                    
                    #LOGGER.debug('Messana BufferTanks ISYdrivers ACTIVE ' + temp)
                    status, value = self.messana.getBufferTankISYValue(ISYkey, self.bufferTankNbr)
                    if status:
                        if self.ISYforced:
                            self.setDriver(ISYdriver, value, report = True, force = False)
                        else:
                            self.setDriver(ISYdriver, value, report = True, force = True)
                        #LOGGER.debug('driver updated :' + ISYdriver['driver'] + ' =  '+str(value))
                    else:
                        LOGGER.error('Error getting ' + ISYdriver['driver'])
            elif level == 'all':
                temp = self.messana.getBufferTankMessanaISYkey(ISYkey, self.bufferTankNbr)
                status, value = self.messana.getBufferTankISYValue(ISYkey, self.bufferTankNbr)
                #LOGGER.debug('Messana BufferTanks ISYdrivers ALL ' + temp)
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
        LOGGER.info('stop - Messana BufferTanks Cleaning up')

    def shortPoll(self):
        #LOGGER.debug('Messana BufferTanks shortPoll - buffer tanks '+ str(self.bufferTankNbr))
        self.messana.updateBufferTankData('active', self.bufferTankNbr)
        self.updateISYdrivers('active')
                   
    def longPoll(self):
        #LOGGER.debug('Messana BufferTanks longPoll - buffer tanks ' + str(self.bufferTankNbr))
        self.messana.updateBufferTankData('all', self.bufferTankNbr)
        self.updateISYdrivers('all')
        self.reportDrivers()

    def query(self, command=None):
        LOGGER.debug('TOP querry')

    def bufTankUpdate(self, command):
        #LOGGER.debug(' bufTankUpdate ')
        self.messana.updateBufferTankData('all', self.bufferTankNbr)
        self.updateISYdrivers('all')
        self.reportDrivers()

    def setStatus(self, command):
        #LOGGER.debug('setStatus Called')
        value = int(command.get('value'))
        #LOGGER.debug('BufferTanks'+str(self.bufferTankNbr)+' setStatus Received:' + str(value))
        if self.messana.bufferTankSetStatus(value, self.bufferTankNbr):
            ISYdriver = self.messana.getBufferTankStatusISYdriver(self.bufferTankNbr)
            self.setDriver(ISYdriver, value, report = True)


    def setMode(self, command):
        #LOGGER.debug('setMode Called')
        value = int(command.get('value'))
        #LOGGER.debug('BufferTanks'+str(self.bufferTankNbr)+' setMode Received:' + str(value))
        if self.messana.bufferTankSetSetMode(value, self.bufferTankNbr):
            ISYdriver = self.messana.getBufferTankSetModeISYdriver(self.bufferTankNbr)
            self.setDriver(ISYdriver, value, report = True)



    def bufTankTempStatus(self, command):
        #LOGGER.debug('bufTankTempStatus Called')
        value = int(command.get('value'))
        #LOGGER.debug('BufferTanks'+str(self.bufferTankNbr)+' Temp Status Reeived:' + str(value))      
        if self.messana.bufferTankTempStatus(value, self.bufferTankNbr):
            ISYdriver = self.messana.getBufferTankTempStatusISYdriver(self.bufferTankNbr)
            self.setDriver(ISYdriver, value, report = True)     

 

    commands = { 'UPDATE' : bufTankUpdate
                ,'SET_MODE': setMode
                ,'SET_STATUS': setStatus
                ,'SET_TEMPMODE' : bufTankTempStatus
                }

