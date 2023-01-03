#!/usr/bin/env python3


import sys
from MessanaSystem import messana_system
from udiMessanaZone import udi_messana_zone
#from MessanaMacrozoneV2 import messanaMacrozone
#from MessanaATUV2 import messanaAtu
#from MessanaBufTankV2 import messanaBufTank
#from MessanaEnergySourceV2 import messanaEnergySource
#from MessanaFanCoilV2 import  messanaFanCoil
#from MessanaHotColdCOV2 import messanaHcCo
#from MessanaHotWaterV2 import messanaHotWater
import time 

try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom

except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    #logging = logging.getlogging('testLOG')


class MessanaController(udi_interface.Controller):

    def  __init__(self, polyglot, primary, address, name):
        super().__init__( polyglot, primary, address, name)
        logging.info('_init_ Messsana Controller')
        self.messanaImportOK = 0
        self.ISYforced = False
        self.name = 'Messana Main'
        #self.address ='msystem'
        self.id = 'msystem'
        #logging.debug('Name/address: '+ self.name + ' ' + self.address)
        self.primary = self.address
        self.hb = 0
        self.ISYdrivers=[]
        #self.ISYcommands = {}
        self.ISYTempUnit = 0
        self.drivers = []
        self.nodeDefineDone = False
        self.zones = {}


        self.poly.subscribe(self.poly.STOP, self.stop)
        self.poly.subscribe(self.poly.START, self.start, address)
        self.poly.subscribe(self.poly.LOGLEVEL, self.handleLevelChange)
        self.poly.subscribe(self.poly.CUSTOMPARAMS, self.handleParams)
        self.poly.subscribe(self.poly.POLL, self.systemPoll)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)
        self.n_queue = []


    def node_queue(self, data):
        self.n_queue.append(data['address'])

    def wait_for_node_done(self):
        while len(self.n_queue) == 0:
            time.sleep(0.1)
        self.n_queue.pop()



    def start(self):
        self.removeNoticesAll()
        #check params are ok 
        logging.info('Start Messana Main NEW')
        self.IPAddress = self.getCustomParam('IP_ADDRESS')
        if self.IPAddress == None:
            logging.error('No IPaddress retrieved:' )
        else:
            logging.debug('IPaddress retrieved: ' + self.IPAddress)
        self.MessanaKey = self.getCustomParam('MESSANA_KEY')
        if self.MessanaKey == None:
            logging.error('No MESSANA_KEY retrieved:')
        else:
            logging.debug('MESSANA_KEY retrieved: ')

        if (self.IPAddress is None) or (self.MessanaKey is None):
            #self.defineInputParams()
            self.stop()

        else:
            logging.info('Retrieving info from Messana System')
            self.messana = messana_system( self.IPAddress, self.MessanaKey)
            if not self.messana.connected():
                self.stop()
        
        for zone in range(0, self.messana):
            self.zones[zone] = udi_messana_zone(self.poly, 'system', zone)

            '''
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
                    #logging.debug(  'driver:  ' +  temp['driver'])

            logging.info ('Install Profile')
            self.poly.installprofile()
            #logging.debug('Install Profile done')
            '''
        self.updateISYdrivers('all')
        #self.messanaImportOK = 1
        self.discover()


              


    def stop(self):
        #self.removeNoticesAll()
        logging.info('stop - Cleaning up')

    def heartbeat(self):
        #logging.debug('heartbeat: hb={}'.format(self.hb))
        if self.hb == 0:
            self.reportCmd('DON',2)
            self.hb = 1
        else:
            self.reportCmd('DOF',2)
            self.hb = 0

    
    def shortPoll(self):
        #logging.debug('Messana Controller shortPoll')
        try:
            if self.messanaImportOK == 1:
                #logging.debug('Short Poll System Up')
                if self.ISYforced:
                    #self.messana.updateSystemData('active')
                    self.updateISYdrivers('active')
                else:
                    #self.messana.updateSystemData('all')
                    self.updateISYdrivers('all')
                self.ISYforced = True
                #logging.debug('Short POll controller: ' )
                if self.nodeDefineDone == True:
                    for node in self.nodes:
                        if node != self.address and node != 'controller':
                            #logging.debug('Calling SHORT POLL for node : ' + node )
                            self.nodes[node].shortPoll()     
        except Exception as e:
            logging.error('Exception shortPoll: '+  str(e))     


    def longPoll(self):
        #logging.debug('Messana Controller longPoll')
        try:
            if self.messanaImportOK == 1:
                self.heartbeat()
                self.messana.updateSystemData('all')
                #logging.debug( self.drivers)
                self.updateISYdrivers('all')
                self.reportDrivers()
                self.ISYforced = True   
                if self.nodeDefineDone == True:       
                    for node in self.nodes:
                        if node != self.address and node != 'controller':
                            #logging.debug('Calling LONG POLL for node : ' + node )
                            self.nodes[node].longPoll()
        except Exception as e:
            logging.error('Exception longPoll: '+  str(e))         


    def updateISYdrivers(self, level):
        #logging.debug('System updateISYdrivers')
        try:
            logging.debug('updateISYdrivers')
            '''
            for ISYdriver in self.drivers:
                ISYkey = ISYdriver['driver']
                if level == 'active':
                    temp = self.messana.getMessanaSystemKey(ISYkey)
                    if temp in self.systemActiveKeys:
                        #logging.debug('MessanaController ISYdrivers ACTIVE ' + temp)
                        status, value = self.messana.getSystemISYValue(ISYkey)
                        if status:
                            if self.ISYforced:
                                self.setDriver(ISYdriver['driver'], value, report = True, force = False)
                            else:
                                self.setDriver(ISYdriver['driver'], value, report = True, force = True)
                            #logging.debug('driver updated :' + ISYdriver['driver'] + ' =  '+str(value))
                        else:
                            logging.error('Error getting ' + ISYdriver['driver'])
                elif level == 'all':
                    temp = self.messana.getMessanaSystemKey(ISYkey)
                    #logging.debug('MessanaController ISYdrivers ACTIVE ' + temp)
                    status, value = self.messana.getSystemISYValue(ISYkey)
                    if status:
                        if self.ISYforced:
                            self.setDriver(ISYdriver['driver'], value, report = True, force = False)
                        else:
                            self.setDriver(ISYdriver['driver'], value, report = True, force = True)
                        #logging.debug('driver updated :' + ISYdriver['driver'] + ' =  '+str(value))
                    else:
                        logging.error('Error getting ' + ISYdriver['driver'])
                else:
                    logging.error('Error!  Unknown level passed: ' + level)
            '''
        except Exception as e:
            logging.error('Exception updateISYdrivers: '+  str(e))       
    '''
    def query(self, command=None):
        logging.debug('TOP querry')
        self.messana.updateSystemData('all')
        self.reportDrivers()

    def discover(self, command=None):

        logging.info('discover zones')
        nbrZones =  self.messana.getZoneCount()
        for zoneNbr in range(0,nbrZones):
            #logging.debug('Adding zone ' + str(zoneNbr))
            zonename = self.messana.getZoneName(zoneNbr)
            zoneaddress = self.messana.getZoneAddress(zoneNbr)
            #logging.debug('zone ' + str(zoneNbr) + ' : name, Address: ' + zonename +' ' + zoneaddress) 
            if not zoneaddress in self.nodes:
                self.addNode(messanaZone(self, self.address, zoneaddress, zonename, zoneNbr))
        
        logging.info('discover macrozones')
        nbrMacrozones =  self.messana.getMacrozoneCount()
        for macrozoneNbr in range(0,nbrMacrozones):
            #logging.debug('Adding macrozone ' + str(macrozoneNbr))
            macrozonename = self.messana.getMacrozoneName(macrozoneNbr)
            macrozoneaddress = self.messana.getMacrozoneAddress(macrozoneNbr)
            #logging.debug('macrozone ' + str(macrozoneNbr) + ' : name, Address: ' + macrozonename +' ' + macrozoneaddress) 
            if not macrozoneaddress in self.nodes:
                self.addNode(messanaMacrozone(self, self.address, macrozoneaddress, macrozonename, macrozoneNbr))
        
        logging.info('discover atus')
        nbrAtus =  self.messana.getAtuCount()
        for atuNbr in range(0,nbrAtus):
            #logging.debug('Adding atu ' + str(atuNbr))
            atuname = self.messana.getAtuName(atuNbr)
            atuaddress = self.messana.getAtuAddress(atuNbr)
            #logging.debug('ATU ' + str(atuNbr) + ' : name, Address: ' + atuname +' ' + atuaddress) 
            if not atuaddress in self.nodes:
                self.addNode(messanaAtu(self, self.address, atuaddress, atuname, atuNbr))
               
        logging.info('discover buffer tanks')
        nbrBufferTanks =  self.messana.getBufferTankCount()
        for bufferTankNbr in range(0,nbrBufferTanks):
            #logging.debug('Adding buffer tank ' + str(bufferTankNbr))
            bufferTankName = self.messana.getBufferTankName(bufferTankNbr)
            bufferTankAddress = self.messana.getBufferTankAddress(bufferTankNbr)
            #logging.debug('Buffer Tank' + str(bufferTankNbr) + ' : name, Address: ' + bufferTankName +' ' + bufferTankAddress) 
            if not bufferTankAddress in self.nodes:
                self.addNode(messanaBufTank(self, self.address, bufferTankAddress, bufferTankName, bufferTankNbr))
               
        logging.info('discover hot cold change overs')
        nbrHcCos =  self.messana.getHcCoCount()
        for HcCoNbr in range(0,nbrHcCos):
            #logging.debug('Adding hot cold cnage over ' + str(HcCoNbr))
            atuname = self.messana.getHcCoName(HcCoNbr)
            atuaddress = self.messana.getHcCoAddress(HcCoNbr)
            #logging.debug('ATU ' + str(HcCoNbr) + ' : name, Address: ' + atuname +' ' + atuaddress) 
            if not atuaddress in self.nodes:
                self.addNode(messanaHcCo(self, self.address, atuaddress, atuname, HcCoNbr))

        logging.info('discover fan coils')
        nbrFanCoils =  self.messana.getFanCoilCount()
        for fanCoilNbr in range(0,nbrFanCoils):
            #logging.debug('Adding fan coils ' + str(fanCoilNbr))
            atuname = self.messana.getFanCoilName(fanCoilNbr)
            atuaddress = self.messana.getFanCoilAddress(fanCoilNbr)
            #logging.debug('ATU ' + str(fanCoilNbr) + ' : name, Address: ' + atuname +' ' + atuaddress) 
            if not atuaddress in self.nodes:
                self.addNode(messanaFanCoil(self, self.address, atuaddress, atuname, fanCoilNbr))

        logging.info('discover energy sources' )
        nbrEnergySources =  self.messana.getEnergySourceCount()
        for energySourceNbr in range(0, nbrEnergySources):
            #logging.debug('Adding energy sources ' + str(energySourceNbr))
            atuname = self.messana.getEnergySourceName(energySourceNbr)
            atuaddress = self.messana.getEnergySourceAddress(energySourceNbr)
            #logging.debug('ATU ' + str(energySourceNbr) + ' : name, Address: ' + atuname +' ' + atuaddress) 
            if not atuaddress in self.nodes:
                self.addNode(messanaEnergySource(self, self.address, atuaddress, atuname, energySourceNbr))


        logging.info('discover domestic hot waters' )
        nbrDHWs =  self.messana.getDomesticHotWaterCount()
        for DHWNbr in range(0,nbrDHWs):
            #logging.debug('Adding domestic hot water ' + str(DHWNbr))
            atuname = self.messana.getDomesticHotWaterName(DHWNbr)
            atuaddress = self.messana.getDomesticHotWaterAddress(DHWNbr)
            #logging.debug('ATU ' + str(DHWNbr) + ' : name, Address: ' + atuname +' ' + atuaddress) 
            if not atuaddress in self.nodes:
                self.addNode(messanaHotWater(self, self.address, atuaddress, atuname, DHWNbr))

        self.nodeDefineDone = True
  
    

    def check_params(self, command=None):
        logging.debug('Check Params')
    '''
    def setStatus(self, command):
        #logging.debug('set Status Called')
        value = int(command.get('value'))
        #logging.debug('set Status Recived:' + str(value))
        #if self.messana.systemSetStatus(value):
        #    ISYdriver = self.messana.getSystemStatusISYdriver()
        #    self.setDriver(ISYdriver, value, report = True)
    
    def setEnergySave(self, command):
        #logging.debug('setEnergySave Called')
        value = int(command.get('value'))
        #logging.debug('SetEnergySave Recived:' + str(value))
        #if self.messana.systemSetEnergySave(value):
        #    ISYdriver = self.messana.getSystemEnergySaveISYdriver()
        #    self.setDriver(ISYdriver, value, report = True)

    def setSetback(self, command):
        #logging.debug('setSetback Called')
        value = int(command.get('value'))
        #logging.debug('setSetback Reeived:' + str(value))
        #if self.messana.systemSetback(value):
        #    ISYdriver = self.messana.getSystemSetbackISYdriver()
        #    self.setDriver(ISYdriver, value, report = True)

    def ISYupdate (self, command):
        #logging.info('ISY-update called')
        #self.messana.updateSystemData('all')
        self.updateISYdrivers('all')
        self.reportDrivers()
    

    commands = { 'UPDATE': ISYupdate
                ,'SET_STATUS': setStatus
                ,'SET_ENERGYSAVE': setEnergySave
                ,'SET_SETBACK' : setSetback
                }

    id = 'system'

if __name__ == "__main__":
    try:
        logging.info('Starting Messana Controller')
        polyglot = udi_interface.Interface([])
        polyglot.start('0.1.0')
        MessanaController(polyglot, 'system', 'system', 'Messana Radiant System')

        # Just sit and wait for events
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
        