#!/usr/bin/env python3

import polyinterface
from subprocess import call
#from MessanaInfo import MessanaInfo

LOGGER = polyinterface.LOGGER
#self, controller, primary, address, name, nodeType, nodeNbr, messana
class messanaEnergySource(polyinterface.Node):
    def __init__(self, controller, primary, address, name,  energySourceNbr):
        super().__init__(controller, primary, address, name)
        LOGGER.info('_init_ Messana EnergySource ' + str(energySourceNbr) )
        self.energySourceNbr = energySourceNbr
        self.name = name
        self.address = address 
        self.messana = self.parent.messana
        self.id = self.messana.getEnergySourceAddress(energySourceNbr)

        self.energySource_GETKeys = self.messana.energySourcePullKeys(self.energySourceNbr)
        self.energySource_PUTKeys = self.messana.energySourcePushKeys(self.energySourceNbr)
        self.energySource_ActiveKeys = self.messana.energySourceActiveKeys(self.energySourceNbr)
        self.ISYforced = False
        
        self.drivers = []
        for key in self.energySource_GETKeys:
            self.temp = self.messana.getEnergySourceISYdriverInfo(key, self.energySourceNbr)
            if  self.temp != {}:
                self.drivers.append(self.temp)
                #LOGGER.debug(  'driver:  ' +  self.temp['driver'])
        self.messana.updateEnergySourceData('all', self.energySourceNbr)
        self.updateISYdrivers('all')
        self.ISYforced = True
       
    def start(self):


        return True


    def updateISYdrivers(self, level):
        #LOGGER.debug('EnergySource updateISYdrivers')
        for ISYdriver in self.drivers:
            ISYkey = ISYdriver['driver']
            if level == 'active':
                temp = self.messana.getEnergySourceMessanaISYkey(ISYkey, self.energySourceNbr)
                if temp in self.energySource_ActiveKeys:                    
                    #LOGGER.debug('Messana EnergySource ISYdrivers ACTIVE ' + temp)
                    status, value = self.messana.getEnergySourceISYValue(ISYkey, self.energySourceNbr)
                    if status:
                        if self.ISYforced:
                            self.setDriver(ISYdriver, value, report = True, force = False)
                        else:
                            self.setDriver(ISYdriver, value, report = True, force = True)
                        #LOGGER.debug('driver updated :' + ISYdriver['driver'] + ' =  '+str(value))
                    else:
                        LOGGER.error('Error getting ' + ISYdriver['driver'])
            elif level == 'all':
                temp = self.messana.getEnergySourceMessanaISYkey(ISYkey, self.energySourceNbr)
                status, value = self.messana.getEnergySourceISYValue(ISYkey, self.energySourceNbr)
                #LOGGER.debug('Messana EnergySource ISYdrivers ALL ' + temp)
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
        LOGGER.info('stop - Messana EnergySource Cleaning up')

    def shortPoll(self):
        #LOGGER.debug('Messana EnergySource shortPoll - energySource '+ str(self.energySourceNbr))
        self.messana.updateEnergySourceData('active', self.energySourceNbr)
        self.updateISYdrivers('active')
                   
    def longPoll(self):
        #LOGGER.debug('Messana EnergySource longPoll - energySource ' + str(self.energySourceNbr))
        self.messana.updateEnergySourceData('all', self.energySourceNbr)
        self.updateISYdrivers('all')
        self.reportDrivers()

    def query(self, command=None):
        LOGGER.info('TOP querry')

    def energySourceUpdate(self, command):
        #LOGGER.debug('energySourceUpdate Called')
        self.messana.updateEnergySourceData('all', self.energySourceNbr)
        self.updateISYdrivers('all')
        self.reportDrivers()


    commands = { 'UPDATE' : energySourceUpdate
                }

    drivers = [  ]

