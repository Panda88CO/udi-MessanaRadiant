#!/usr/bin/env python3

import polyinterface
from subprocess import call

LOGGER = polyinterface.LOGGER
#self, controller, primary, address, name, nodeType, nodeNbr, messana
class messanaMacrozone(polyinterface.Node):
    def __init__(self, controller, primary, address, name,  macrozoneNbr):
        super().__init__(controller, primary, address, name)
        LOGGER.info('_init_ Messana Macrozone ' + str(macrozoneNbr) )
        self.macrozoneNbr = macrozoneNbr
        self.name = name
        self.address = address 
        self.messana = self.parent.messana
        self.id =  self.messana.getMacrozoneAddress(self.macrozoneNbr)
        
        self.macrozone_GETKeys = self.messana.macrozonePullKeys(self.macrozoneNbr)
        self.macrozone_PUTKeys = self.messana.macrozonePushKeys(self.macrozoneNbr)
        self.macrozone_ActiveKeys = self.messana.macrozoneActiveKeys(self.macrozoneNbr)
        self.ISYforced = False
        
        self.drivers = []
        for key in self.macrozone_GETKeys:
            self.temp = self.messana.getMacrozoneISYdriverInfo(key, self.macrozoneNbr)
            if  self.temp != {}:
                self.drivers.append(self.temp)
                #LOGGER.debug(  'driver:  ' +  self.temp['driver'])
                
        self.updateISYdrivers('all')
        self.ISYforced = True
       
    def start(self):
        return True
    '''
    def checkMacrozoneCommands(self, zoneNbr):
        tempList = []
        for cmd in self.commands:
            if not(self.messana.checkMacrozoneCommand(cmd, self.macrozoneNbr)):
                tempList.append(cmd)
        for key in tempList:
            self.commands.pop(key)
    '''

    def updateISYdrivers(self, level):
        #LOGGER.debug('Macrozone updateISYdrivers')
        for ISYdriver in self.drivers:
            ISYkey = ISYdriver['driver']
            if level == 'active':
                temp = self.messana.getMacrozoneMessanaISYkey(ISYkey, self.macrozoneNbr)
                if temp in self.macrozone_ActiveKeys:                    
                    #LOGGER.debug('Messana Macrozone ISYdrivers ACTIVE ' + temp)
                    status, value = self.messana.getMacrozoneISYValue(ISYkey, self.macrozoneNbr)
                    if status:
                        if self.ISYforced:
                            self.setDriver(ISYdriver['driver'], value, report = True, force = False)
                        else:
                            self.setDriver(ISYdriver['driver'], value, report = True, force = True)
                        #LOGGER.debug('driver updated for macrozone'+str(self.macrozoneNbr)+': ' + ISYdriver['driver'] + ' =  '+str(value))
                    else:
                        LOGGER.error('Error getting ' + ISYdriver['driver'])
            elif level == 'all':
                temp = self.messana.getMacrozoneMessanaISYkey(ISYkey, self.macrozoneNbr)
                status, value = self.messana.getMacrozoneISYValue(ISYkey, self.macrozoneNbr)
                #LOGGER.debug('Messana Zone ISYdrivers ALL ' + temp)
                if status:
                    if self.ISYforced:
                        self.setDriver(ISYdriver['driver'], value, report = True, force = False)
                    else:
                        self.setDriver(ISYdriver['driver'], value, report = True, force = True)
                    #LOGGER.debug('driver updated for macrozone'+str(self.macrozoneNbr)+': ' + ISYdriver['driver'] + ' =  '+str(value))
                else:
                    LOGGER.error('Error getting ' + ISYdriver['driver'])
            else:
                LOGGER.error('Error!  Unknow level: ' + level)
        
    def stop(self):
        LOGGER.info('stop - Messana Zone Cleaning up')

    def shortPoll(self):
        #LOGGER.debug('Messana Macrozone shortPoll - zone '+ str(self.macrozoneNbr))
        #self.messana.updateMacrozoneData('active', self.macrozoneNbr)
        self.updateISYdrivers('active')
        self.reportDrivers()
                   
    def longPoll(self):
        LOGGER.debug('Messana Macrozone longPoll - zone ' + str(self.macrozoneNbr))
        #self.messana.updateMacrozoneData('all', self.macrozoneNbr)
        self.updateISYdrivers('all')
        self.reportDrivers()

    def query(self, command=None):
        LOGGER.info('TOP querry')

    def setStatus(self, command):
        #LOGGER.debug('setStatus Called')
        value = int(command.get('value'))
        #LOGGER.debug('Macrozone'+str(self.macrozoneNbr)+' setStatus Received:' + str(value))
        if self.messana.macrozoneSetStatus(value, self.macrozoneNbr):
            ISYdriver = self.messana.getMacrozoneStatusISYdriver(self.macrozoneNbr)
            self.setDriver(ISYdriver, value, report = True)

    def setSetpoint(self, command):
        #LOGGER.debug('setSetpoint Called')
        value = int(command.get('value'))
        #LOGGER.debug('Zone'+str(self.macrozoneNbr)+' setSetpoint Received:' + str(value))
        if self.messana.macrozoneSetSetpoint(value, self.macrozoneNbr):
            ISYdriver = self.messana.getMacrozoneSetPointISYdriver(self.macrozoneNbr)
            self.setDriver(ISYdriver, value, report = True)


    def enableSchedule(self, command):
        #LOGGER.debug('EnSchedule Called')
        value = int(command.get('value'))
        #LOGGER.debug('Zone'+str(self.macrozoneNbr)+' EnSchedule Reeived:' + str(value))      
        if self.messana.macrozoneEnableSchedule(value, self.macrozoneNbr):
            ISYdriver = self.messana.getMacrozoneEnableScheduleISYdriver(self.macrozoneNbr)
            self.setDriver(ISYdriver, value, report = True)     
        
    def ISYupdate(self, command):
        self.messana.updateMacrozoneData('all', self.macrozoneNbr)
        self.updateISYdrivers('all')
        self.reportDrivers()
 

    commands = { 'SET_SETPOINT': setSetpoint
                ,'SET_STATUS': setStatus
                ,'UPDATE': ISYupdate
                ,'SET_SCHEDULEON' : enableSchedule 
                }



