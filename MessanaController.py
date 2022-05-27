#!/usr/bin/env python3


import sys
from MessanaInfo import messanaInfo
from MessanaZone import messanaZone
from MessanaMacrozone import messanaMacrozone
from MessanaATU import messanaAtu
from MessanaBufTank import messanaBufTank
from MessanaEnergySource import messanaEnergySource
from MessanaFanCoil import  messanaFanCoil
from MessanaHotColdCO import messanaHcCo
from MessanaHotWater import messanaHotWater
PC = False
if PC:
    import logging
    logging.basicConfig(level=logging.DEBUG)
    LOGGER = logging.getLogger('testLOG')
else:
    import polyinterface
    LOGGER = polyinterface.LOGGER
    Custom = polyinterface.Custom
    LOGGER = polyinterface.LOGGER
               
class MessanaController(polyinterface.Controller):

    def __init__(self):
        super(MessanaController, self).__init__(polyglot)
        LOGGER.info('_init_ Messsana Controller')
        self.messanaImportOK = 0
        self.ISYforced = False
        self.name = 'Messana Main'
        #self.address ='msystem'
        self.id = 'msystem'
        #LOGGER.debug('Name/address: '+ self.name + ' ' + self.address)
        self.primary = self.address
        self.hb = 0
        self.ISYdrivers=[]
        #self.ISYcommands = {}
        self.ISYTempUnit = 0
        self.drivers = []
        self.nodeDefineDone = False



    def defineInputParams(self):
        self.IPAddress = self.getCustomParam('IP_ADDRESS')
        if self.IPAddress is None:
            self.addNotice('Please Set IP address of Messana system (IP_ADDRESS)')
            self.addNotice('E.g. 192.168.1.2')
            LOGGER.error('IP address not set')
            self.addCustomParam({'IP_ADDRESS': '192.168.1.2'})

        
        self.IPAddress = self.getCustomParam('MESSANA_KEY')
        if self.MessanaKey is None:
            self.addNotice('Please Set Messana API access Key (MESSANA_KEY)')
            self.addNotice('E.g. 12345678-90ab-cdef-1234-567890abcdef')
            LOGGER.error('check_params: Messana Key not specified')
            self.addCustomParam({'MESSANA_KEY': '12345678-90ab-cdef-1234-567890abcdef'})


        self.addNotice('Please restart Node server after setting the parameters')



    def start(self):
        self.removeNoticesAll()
        LOGGER.info('Start Messana Main NEW')
        self.IPAddress = self.getCustomParam('IP_ADDRESS')
        if self.IPAddress == None:
            LOGGER.error('No IPaddress retrieved:' )
        else:
            LOGGER.debug('IPaddress retrieved: ' + self.IPAddress)
        self.MessanaKey = self.getCustomParam('MESSANA_KEY')
        if self.MessanaKey == None:
            LOGGER.error('No MESSANA_KEY retrieved:')
        else:
            LOGGER.debug('MESSANA_KEY retrieved: ')

        if (self.IPAddress is None) or (self.MessanaKey is None):
            self.defineInputParams()
            self.stop()

        else:
            LOGGER.info('Retrieving info from Messana System')
            self.messana = messanaInfo( self.IPAddress, self.MessanaKey, self.address )
            if self.messana == False:
                self.stop()
            self.id = self.messana.getSystemAddress()
            #self.address = self.messana.getSystemAddress()
            self.messana.updateSystemData('all')
            self.systemGETKeys = self.messana.systemPullKeys()
            self.systemPUTKeys = self.messana.systemPushKeys()
            self.systemActiveKeys = self.messana.systemActiveKeys()
            
            
            for key in self.systemGETKeys:
                temp = self.messana.getSystemISYdriverInfo(key)
                if  temp != {}:
                    self.drivers.append(temp)
                    #LOGGER.debug(  'driver:  ' +  temp['driver'])

            LOGGER.info ('Install Profile')    
            self.poly.installprofile()
            #LOGGER.debug('Install Profile done')
        self.updateISYdrivers('all')
        self.messanaImportOK = 1
        self.discover()


              


    def stop(self):
        #self.removeNoticesAll()
        LOGGER.info('stop - Cleaning up')

    def heartbeat(self):
        #LOGGER.debug('heartbeat: hb={}'.format(self.hb))
        if self.hb == 0:
            self.reportCmd('DON',2)
            self.hb = 1
        else:
            self.reportCmd('DOF',2)
            self.hb = 0

    
    def shortPoll(self):
        #LOGGER.debug('Messana Controller shortPoll')
        try:
            if self.messanaImportOK == 1:
                #LOGGER.debug('Short Poll System Up')
                if self.ISYforced:
                    #self.messana.updateSystemData('active')
                    self.updateISYdrivers('active')
                else:
                    #self.messana.updateSystemData('all')
                    self.updateISYdrivers('all')
                self.ISYforced = True
                #LOGGER.debug('Short POll controller: ' )
                if self.nodeDefineDone == True:
                    for node in self.nodes:
                        if node != self.address and node != 'controller':
                            #LOGGER.debug('Calling SHORT POLL for node : ' + node )
                            self.nodes[node].shortPoll()     
        except Exception as e:
            LOGGER.error('Exception shortPoll: '+  str(e))     


    def longPoll(self):
        #LOGGER.debug('Messana Controller longPoll')
        try:
            if self.messanaImportOK == 1:
                self.heartbeat()
                self.messana.updateSystemData('all')
                #LOGGER.debug( self.drivers)
                self.updateISYdrivers('all')
                self.reportDrivers()
                self.ISYforced = True   
                if self.nodeDefineDone == True:       
                    for node in self.nodes:
                        if node != self.address and node != 'controller':
                            #LOGGER.debug('Calling LONG POLL for node : ' + node )
                            self.nodes[node].longPoll()
        except Exception as e:
            LOGGER.error('Exception longPoll: '+  str(e))         


    def updateISYdrivers(self, level):
        #LOGGER.debug('System updateISYdrivers')
        try:
            for ISYdriver in self.drivers:
                ISYkey = ISYdriver['driver']
                if level == 'active':
                    temp = self.messana.getMessanaSystemKey(ISYkey)
                    if temp in self.systemActiveKeys:
                        #LOGGER.debug('MessanaController ISYdrivers ACTIVE ' + temp)
                        status, value = self.messana.getSystemISYValue(ISYkey)
                        if status:
                            if self.ISYforced:
                                self.setDriver(ISYdriver['driver'], value, report = True, force = False)
                            else:
                                self.setDriver(ISYdriver['driver'], value, report = True, force = True)
                            #LOGGER.debug('driver updated :' + ISYdriver['driver'] + ' =  '+str(value))
                        else:
                            LOGGER.error('Error getting ' + ISYdriver['driver'])
                elif level == 'all':
                    temp = self.messana.getMessanaSystemKey(ISYkey)
                    #LOGGER.debug('MessanaController ISYdrivers ACTIVE ' + temp)
                    status, value = self.messana.getSystemISYValue(ISYkey)
                    if status:
                        if self.ISYforced:
                            self.setDriver(ISYdriver['driver'], value, report = True, force = False)
                        else:
                            self.setDriver(ISYdriver['driver'], value, report = True, force = True)
                        #LOGGER.debug('driver updated :' + ISYdriver['driver'] + ' =  '+str(value))
                    else:
                        LOGGER.error('Error getting ' + ISYdriver['driver'])
                else:
                    LOGGER.error('Error!  Unknown level passed: ' + level)
        except Exception as e:
            LOGGER.error('Exception updateISYdrivers: '+  str(e))       

    def query(self, command=None):
        LOGGER.debug('TOP querry')
        self.messana.updateSystemData('all')
        self.reportDrivers()

    def discover(self, command=None):

        LOGGER.info('discover zones')
        nbrZones =  self.messana.getZoneCount()
        for zoneNbr in range(0,nbrZones):
            #LOGGER.debug('Adding zone ' + str(zoneNbr))
            zonename = self.messana.getZoneName(zoneNbr)
            zoneaddress = self.messana.getZoneAddress(zoneNbr)
            #LOGGER.debug('zone ' + str(zoneNbr) + ' : name, Address: ' + zonename +' ' + zoneaddress) 
            if not zoneaddress in self.nodes:
                self.addNode(messanaZone(self, self.address, zoneaddress, zonename, zoneNbr))
        
        LOGGER.info('discover macrozones')
        nbrMacrozones =  self.messana.getMacrozoneCount()
        for macrozoneNbr in range(0,nbrMacrozones):
            #LOGGER.debug('Adding macrozone ' + str(macrozoneNbr))
            macrozonename = self.messana.getMacrozoneName(macrozoneNbr)
            macrozoneaddress = self.messana.getMacrozoneAddress(macrozoneNbr)
            #LOGGER.debug('macrozone ' + str(macrozoneNbr) + ' : name, Address: ' + macrozonename +' ' + macrozoneaddress) 
            if not macrozoneaddress in self.nodes:
                self.addNode(messanaMacrozone(self, self.address, macrozoneaddress, macrozonename, macrozoneNbr))
        
        LOGGER.info('discover atus')
        nbrAtus =  self.messana.getAtuCount()
        for atuNbr in range(0,nbrAtus):
            #LOGGER.debug('Adding atu ' + str(atuNbr))
            atuname = self.messana.getAtuName(atuNbr)
            atuaddress = self.messana.getAtuAddress(atuNbr)
            #LOGGER.debug('ATU ' + str(atuNbr) + ' : name, Address: ' + atuname +' ' + atuaddress) 
            if not atuaddress in self.nodes:
                self.addNode(messanaAtu(self, self.address, atuaddress, atuname, atuNbr))
               
        LOGGER.info('discover buffer tanks')
        nbrBufferTanks =  self.messana.getBufferTankCount()
        for bufferTankNbr in range(0,nbrBufferTanks):
            #LOGGER.debug('Adding buffer tank ' + str(bufferTankNbr))
            bufferTankName = self.messana.getBufferTankName(bufferTankNbr)
            bufferTankAddress = self.messana.getBufferTankAddress(bufferTankNbr)
            #LOGGER.debug('Buffer Tank' + str(bufferTankNbr) + ' : name, Address: ' + bufferTankName +' ' + bufferTankAddress) 
            if not bufferTankAddress in self.nodes:
                self.addNode(messanaBufTank(self, self.address, bufferTankAddress, bufferTankName, bufferTankNbr))
               
        LOGGER.info('discover hot cold change overs')
        nbrHcCos =  self.messana.getHcCoCount()
        for HcCoNbr in range(0,nbrHcCos):
            #LOGGER.debug('Adding hot cold cnage over ' + str(HcCoNbr))
            atuname = self.messana.getHcCoName(HcCoNbr)
            atuaddress = self.messana.getHcCoAddress(HcCoNbr)
            #LOGGER.debug('ATU ' + str(HcCoNbr) + ' : name, Address: ' + atuname +' ' + atuaddress) 
            if not atuaddress in self.nodes:
                self.addNode(messanaHcCo(self, self.address, atuaddress, atuname, HcCoNbr))

        LOGGER.info('discover fan coils')
        nbrFanCoils =  self.messana.getFanCoilCount()
        for fanCoilNbr in range(0,nbrFanCoils):
            #LOGGER.debug('Adding fan coils ' + str(fanCoilNbr))
            atuname = self.messana.getFanCoilName(fanCoilNbr)
            atuaddress = self.messana.getFanCoilAddress(fanCoilNbr)
            #LOGGER.debug('ATU ' + str(fanCoilNbr) + ' : name, Address: ' + atuname +' ' + atuaddress) 
            if not atuaddress in self.nodes:
                self.addNode(messanaFanCoil(self, self.address, atuaddress, atuname, fanCoilNbr))

        LOGGER.info('discover energy sources' )
        nbrEnergySources =  self.messana.getEnergySourceCount()
        for energySourceNbr in range(0, nbrEnergySources):
            #LOGGER.debug('Adding energy sources ' + str(energySourceNbr))
            atuname = self.messana.getEnergySourceName(energySourceNbr)
            atuaddress = self.messana.getEnergySourceAddress(energySourceNbr)
            #LOGGER.debug('ATU ' + str(energySourceNbr) + ' : name, Address: ' + atuname +' ' + atuaddress) 
            if not atuaddress in self.nodes:
                self.addNode(messanaEnergySource(self, self.address, atuaddress, atuname, energySourceNbr))


        LOGGER.info('discover domestic hot waters' )
        nbrDHWs =  self.messana.getDomesticHotWaterCount()
        for DHWNbr in range(0,nbrDHWs):
            #LOGGER.debug('Adding domestic hot water ' + str(DHWNbr))
            atuname = self.messana.getDomesticHotWaterName(DHWNbr)
            atuaddress = self.messana.getDomesticHotWaterAddress(DHWNbr)
            #LOGGER.debug('ATU ' + str(DHWNbr) + ' : name, Address: ' + atuname +' ' + atuaddress) 
            if not atuaddress in self.nodes:
                self.addNode(messanaHotWater(self, self.address, atuaddress, atuname, DHWNbr))

        self.nodeDefineDone = True
  
    

    def check_params(self, command=None):
        LOGGER.debug('Check Params')
 
    def setStatus(self, command):
        #LOGGER.debug('set Status Called')
        value = int(command.get('value'))
        #LOGGER.debug('set Status Recived:' + str(value))
        if self.messana.systemSetStatus(value):
            ISYdriver = self.messana.getSystemStatusISYdriver()
            self.setDriver(ISYdriver, value, report = True)

    def setEnergySave(self, command):
        #LOGGER.debug('setEnergySave Called')
        value = int(command.get('value'))
        #LOGGER.debug('SetEnergySave Recived:' + str(value))
        if self.messana.systemSetEnergySave(value):
            ISYdriver = self.messana.getSystemEnergySaveISYdriver()
            self.setDriver(ISYdriver, value, report = True)

    def setSetback(self, command):
        #LOGGER.debug('setSetback Called')
        value = int(command.get('value'))
        #LOGGER.debug('setSetback Reeived:' + str(value))
        if self.messana.systemSetback(value):
            ISYdriver = self.messana.getSystemSetbackISYdriver()
            self.setDriver(ISYdriver, value, report = True)

    def ISYupdate (self, command):
        #LOGGER.info('ISY-update called')
        self.messana.updateSystemData('all')
        self.updateISYdrivers('all')
        self.reportDrivers()
 

    commands = { 'UPDATE': ISYupdate
                ,'SET_STATUS': setStatus
                ,'SET_ENERGYSAVE': setEnergySave
                ,'SET_SETBACK' : setSetback 
                }

  
if __name__ == "__main__":
    try:
        LOGGER.info('Starting Messana Controller')
        polyglot = polyinterface.Interface('Messana_Control')
        polyglot.start()
        control = MessanaController(polyglot)
        control.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
