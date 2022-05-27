#!/usr/bin/env python3

import polyinterface
from subprocess import call


LOGGER = polyinterface.LOGGER
#self, controller, primary, address, name, nodeType, nodeNbr, messana
class messanaHcCo(polyinterface.Node):
    def __init__(self, controller, primary, address, name,  HcCoNbr):
        super().__init__(controller, primary, address, name)
        LOGGER.info('_init_ Messana HcCo ' + str(HcCoNbr) )
        self.HcCoNbr = HcCoNbr
        self.name = name
        self.address = address 
        self.messana = self.parent.messana
        self.id = self.messana.getHcCoAddress(self.HcCoNbr) 

        self.HcCo_GETKeys = self.messana.HcCoPullKeys(self.HcCoNbr)
        self.HcCo_PUTKeys = self.messana.HcCoPushKeys(self.HcCoNbr)
        self.HcCo_ActiveKeys = self.messana.HcCoActiveKeys(self.HcCoNbr)
        self.ISYforced = False
        
        self.drivers = []
        for key in self.HcCo_GETKeys:
            self.temp = self.messana.getHcCoISYdriverInfo(key, self.HcCoNbr)
            if  self.temp != {}:
                self.drivers.append(self.temp)
                #LOGGER.debug(  'driver:  ' +  self.temp['driver'])
        self.messana.updateHcCoData('all', self.HcCoNbr)
        self.updateISYdrivers('all')
        self.ISYforced = True
       
    def start(self):


        return True


    def updateISYdrivers(self, level):
        #LOGGER.debug('HcCo updateISYdrivers')
        for ISYdriver in self.drivers:
            ISYkey = ISYdriver['driver']
            if level == 'active':
                temp = self.messana.getHcCoMessanaISYkey(ISYkey, self.HcCoNbr)
                if temp in self.HcCo_ActiveKeys:                    
                    #LOGGER.debug('Messana HcCo ISYdrivers ACTIVE ' + temp)
                    status, value = self.messana.getHcCoISYValue(ISYkey, self.HcCoNbr)
                    if status:
                        if self.ISYforced:
                            self.setDriver(ISYdriver, value, report = True, force = False)
                        else:
                            self.setDriver(ISYdriver, value, report = True, force = True)
                        #LOGGER.debug('driver updated :' + ISYdriver['driver'] + ' =  '+str(value))
                    else:
                        LOGGER.error('Error getting ' + ISYdriver['driver'])
            elif level == 'all':
                temp = self.messana.getHcCoMessanaISYkey(ISYkey, self.HcCoNbr)
                status, value = self.messana.getHcCoISYValue(ISYkey, self.HcCoNbr)
                #LOGGER.debug('Messana HcCo ISYdrivers ALL ' + temp)
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
        LOGGER.info('stop - Messana HcCo Cleaning up')

    def shortPoll(self):
        #LOGGER.debug('Messana HcCo shortPoll - HcCo '+ str(self.HcCoNbr))
        self.messana.updateHcCoData('active', self.HcCoNbr)
        self.updateISYdrivers('active')
                   
    def longPoll(self):
        #LOGGER.debug('Messana HcCo longPoll - HcCo ' + str(self.HcCoNbr))
        self.messana.updateHcCoData('all', self.HcCoNbr)
        self.updateISYdrivers('all')
        self.reportDrivers()

    def query(self, command=None):
        LOGGER.info('TOP querry')

    def setStatus(self, command):
        #LOGGER.debug('setStatus Called')
        value = int(command.get('value'))
        #LOGGER.debug('HcCo'+str(self.HcCoNbr)+' setStatus Received:' + str(value))
        if self.messana.HcCoSetStatus(value, self.HcCoNbr):
            ISYdriver = self.messana.getHcCoStatusISYdriver(self.HcCoNbr)
            self.setDriver(ISYdriver, value, report = True)



    def HcCoUpdate(self, command):
        #LOGGER.debug('HcCoUpdate Called')
        self.messana.updateHcCoData('all', self.HcCoNbr)
        self.updateISYdrivers('all')
        self.reportDrivers()     


    def setHcCoMode(self, command):
        #LOGGER.debug('setHcCoMode Called')
        value = int(command.get('value'))
        #LOGGER.debug('HcCo'+str(self.HcCoNbr)+' setSetpoint Received:' + str(value))
        if self.messana.HcCoSetMode(value, self.HcCoNbr):
            ISYdriver = self.messana.getHcCoSetModeISYdriver(self.HcCoNbr)
            self.setDriver(ISYdriver, value, report = True)


    def setAdaptiveComfort(self, command):
        #LOGGER.debug('setAdaptiveComfort Called')
        value = int(command.get('value'))
        #LOGGER.debug('HcCo'+str(self.HcCoNbr)+' EnSchedule Reeived:' + str(value))      
        if self.messana.HcCoAdaptiveComfort(value, self.HcCoNbr):
            ISYdriver = self.messana.getHcCoAdaptiveComfortISYdriver(self.HcCoNbr)
            self.setDriver(ISYdriver, value, report = True)     
        

 

    commands = { 'UPDATE': HcCoUpdate
                ,'SET_MODE': setHcCoMode
                ,'SET_ADAPTIVE_COMFORT': setAdaptiveComfort
                }
