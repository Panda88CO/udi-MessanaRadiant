#!/usr/bin/env python3

import polyinterface
from subprocess import call
#from MessanaInfo import MessanaInfo

LOGGER = polyinterface.LOGGER
#self, controller, primary, address, name, nodeType, nodeNbr, messana
class messanaAtu(polyinterface.Node):
    def __init__(self, controller, primary, address, name,  atuNbr):
        super().__init__(controller, primary, address, name)
        LOGGER.info('_init_ Messana atu ' + str(atuNbr) )
        self.atuNbr = atuNbr
        self.name = name
        self.address = address 
        self.messana = self.parent.messana
        self.id = self.messana.getAtuAddress(atuNbr)

        self.atu_GETKeys = self.messana.atuPullKeys(self.atuNbr)
        self.atu_PUTKeys = self.messana.atuPushKeys(self.atuNbr)
        self.atu_ActiveKeys = self.messana.atuActiveKeys(self.atuNbr)
        self.ISYforced = False
        
        self.drivers = []
        for key in self.atu_GETKeys:
            self.temp = self.messana.getAtuISYdriverInfo(key, self.atuNbr)
            if  self.temp != {}:
                self.drivers.append(self.temp)
                #LOGGER.debug(  'driver:  ' +  self.temp['driver'])

        self.updateISYdrivers('all')
        self.ISYforced = True
       
    def start(self):
        return True


    def updateISYdrivers(self, level):
        #LOGGER.debug('ATU updateISYdrivers')
        for ISYdriver in self.drivers:
            ISYkey = ISYdriver['driver']
            if level == 'active':
                temp = self.messana.getAtuMessanaISYkey(ISYkey, self.atuNbr)
                if temp in self.atu_ActiveKeys:                    
                    #LOGGER.debug('Messana ATU ISYdrivers ACTIVE ' + temp)
                    status, value = self.messana.getAtuISYValue(ISYkey, self.atuNbr)
                    if status:
                        if self.ISYforced:
                            self.setDriver(ISYdriver, value, report = True, force = False)
                        else:
                            self.setDriver(ISYdriver, value, report = True, force = True)
                        #LOGGER.debug('driver updated :' + ISYdriver['driver'] + ' =  '+str(value))
                    else:
                        LOGGER.error('Error getting ' + ISYdriver['driver'])
            elif level == 'all':
                temp = self.messana.getAtuMessanaISYkey(ISYkey, self.atuNbr)
                status, value = self.messana.getAtuISYValue(ISYkey, self.atuNbr)
                #LOGGER.debug('Messana ATU ISYdrivers ALL ' + temp)
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
        LOGGER.debug('stop - Messana ATU Cleaning up')

    def shortPoll(self):
        #LOGGER.debug('Messana ATU shortPoll - atu '+ str(self.atuNbr))
        self.messana.updateAtuData('active', self.atuNbr)
        self.updateISYdrivers('active')
                   
    def longPoll(self):
        #LOGGER.debug('Messana ATU longPoll - atu ' + str(self.atuNbr))
        self.messana.updateAtuData('all', self.atuNbr)
        self.updateISYdrivers('all')
        self.reportDrivers()

    def query(self, command=None):
        LOGGER.info('TOP querry')

    def atuSetStatus(self, command):
        #LOGGER.debug('atuSetStatus Called')
        value = int(command.get('value'))
        #LOGGER.debug('ATU'+str(self.atuNbr)+' setStatus Received:' + str(value))
        if self.messana.atuSetStatus(value, self.atuNbr):
            ISYdriver = self.messana.getAtuStatusISYdriver(self.atuNbr)
            self.setDriver(ISYdriver, value, report = True)

 
    def atuUpdate(self, command):
        #LOGGER.debug(' atuUpdate ')
        self.messana.updateAtuData('all', self.atuNbr)
        self.updateISYdrivers('all')
        self.reportDrivers()


    def atuHRV(self, command):
        #LOGGER.debug('atuHRV called')
        value = int(command.get('value'))
        LOGGER.debug('Atu'+str(self.atuNbr)+' atuHRV Received:' + str(value))      
        if self.messana.atuSetHrv(value, self.atuNbr):
            ISYdriver = self.messana.getAtuHrvISYdriver(self.atuNbr)
            self.setDriver(ISYdriver, value, report = True)   


    def atuFlowlevel(self, command):
        #LOGGER.debug('atu FlowLevel called')
        value = int(command.get('value'))
        #LOGGER.debug('Atu'+str(self.atuNbr)+' atuFlowlevel Received:' + str(value))      
        if self.messana.atuSetFlowlevel(value, self.atuNbr):
            ISYdriver = self.messana.getAtuSetFlowlevelISYdriver(self.atuNbr)
            self.setDriver(ISYdriver, value, report = True)   


    def atuHUM(self, command):
        #LOGGER.debug('atuHUM called')
        value = int(command.get('value'))
        #LOGGER.debug('Atu'+str(self.atuNbr)+' atuHUM Received:' + str(value))      
        if self.messana.atuSetHum(value, self.atuNbr):
            ISYdriver = self.messana.getAtuSetHumISYdriver(self.atuNbr)
            self.setDriver(ISYdriver, value, report = True)   


    def atuINT(self, command):
        #LOGGER.debug('atuINT called')
        value = int(command.get('value'))
        #LOGGER.debug('Atu'+str(self.atuNbr)+' atuINT Received:' + str(value))      
        if self.messana.atuSetInt(value, self.atuNbr):
            ISYdriver = self.messana.getAtuSetIntISYdriver(self.atuNbr)
            self.setDriver(ISYdriver, value, report = True)   

    
    def atuNTD(self, command):
        #LOGGER.debug('atuNTD called')
        value = int(command.get('value'))
        #LOGGER.debug('Atu'+str(self.atuNbr)+' atuNTD Received:' + str(value))      
        if self.messana.atuSetNtd(value, self.atuNbr):
            ISYdriver = self.messana.getAtuSetNtdISYdriver(self.atuNbr)
            self.setDriver(ISYdriver, value, report = True)   


    def atuHumSetpointRH(self, command):
        #LOGGER.debug('atuHumSetpointRH called')
        value = int(command.get('value'))
        #LOGGER.debug('Atu'+str(self.atuNbr)+' atuHumSetpointRH Received:' + str(value))      
        if self.messana.atuSetHumSetpointRH(value, self.atuNbr):
            ISYdriver = self.messana.getAtuSetHumSetpointRHISYdriver(self.atuNbr)
            self.setDriver(ISYdriver, value, report = True)   



    def atuHumSetpointDP(self, command):
        #LOGGER.debug('atuHumSetpointDP called')
        value = int(command.get('value'))
        #LOGGER.debug('Atu'+str(self.atuNbr)+' atuHumSetpointDP Received:' + str(value))      
        if self.messana.atuSetHumSetpointDP(value, self.atuNbr):
            ISYdriver = self.messana.getAtuSetHumSetpointDPISYdriver(self.atuNbr)
            self.setDriver(ISYdriver, value, report = True)   


    def atuDehumSetpointRH(self, command):
        #LOGGER.debug('called')
        value = int(command.get('value'))
        #LOGGER.debug('Atu'+str(self.atuNbr)+' atuDehumSetpointRH Received:' + str(value))      
        if self.messana.atuSetDehumSetpointRH(value, self.atuNbr):
            ISYdriver = self.messana.getAtuSetDehumSetpointRHISYdriver(self.atuNbr)
            self.setDriver(ISYdriver, value, report = True)   


    def atuDehumSetpointDP(self, command):
        #LOGGER.debug('atuDehumSetpointRH called')
        value = int(command.get('value'))
        #LOGGER.debug('Atu'+str(self.atuNbr)+' atuDehumSetpointDP Received:' + str(value))      
        if self.messana.atuSetDehumSetpointDP(value, self.atuNbr):
            ISYdriver = self.messana.getAtuSetDehumSetpointDPISYdriver(self.atuNbr)
            self.setDriver(ISYdriver, value, report = True)   


    def atuCurrentSetpointRH(self, command):
        #LOGGER.debug('atuCurrentSetpointRH called')
        value = int(command.get('value'))
        #LOGGER.debug('Atu'+str(self.atuNbr)+' atuCurrentSetpointRH Received:' + str(value))      
        if self.messana.atuSetCurrentSetpointRH(value, self.atuNbr):
            ISYdriver = self.messana.getAtuSetCurrentSetpointRHISYdriver(self.atuNbr)
            self.setDriver(ISYdriver, value, report = True)   


    def atuCurrentSetpointDP(self, command):
        #LOGGER.debug('atuCurrentSetpointDP called')
        value = int(command.get('value'))
        #LOGGER.debug('Atu'+str(self.atuNbr)+' atuCurrentSetpointDP Received:' + str(value))      
        if self.messana.atuSetCurrentSetpointDP(value, self.atuNbr):
            ISYdriver = self.messana.getAtuSetCurrentSetpointDPISYdriver(self.atuNbr)
            self.setDriver(ISYdriver, value, report = True)   

    commands = { 'SET_STATUS': atuSetStatus
                ,'UPDATE': atuUpdate
                ,'SET_HRVON': atuHRV
                ,'SET_FLOWLEVEL': atuFlowlevel
                ,'SET_HUMON' : atuHUM
                ,'SET_INTON' : atuINT
                ,'SET_NTDON' : atuNTD
                ,'SET_HUM_SP_RH' : atuHumSetpointRH
                ,'SET_HUM_SP_DP' : atuHumSetpointDP
                ,'SET_DEHUM_SP_RH' : atuDehumSetpointRH
                ,'SET_DEHUM_SP_DP' : atuDehumSetpointDP
                ,'SET_CURR_SP_RH' : atuCurrentSetpointRH
                ,'SET_CURR_SP_DP' : atuCurrentSetpointDP
                }



