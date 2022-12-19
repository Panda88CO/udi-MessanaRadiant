#!/usr/bin/env python3

try:
    import udi_interface
    
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom

except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)


from MessanaSystem import messanaSystem
from Temp.udiMessanaSystem import udi_messana_system
#from MessanaZone import messanaZone
from udiMessanaZone import udiMessanaZone
import time
import re

class messana (udi_interface.Node):
    def  __init__(self, polyglot, primary, address, name):
        super().__init__( polyglot, primary, address, name)  
        self.hb = 0
        self.poly=polyglot
        self.nodeDefineDone = False
        self.handleParamsDone = False
        self.address = address
        self.name = name
        self.primary = primary

        self.n_queue = []
        #logging.setLevel(30)

        

        self.Parameters = Custom(self.poly, 'customparams')
        self.Notices = Custom(self.poly, 'notices')
        logging.debug('YoLinkSetup init')
        logging.debug('self.address : ' + str(self.address))
        logging.debug('self.name :' + str(self.name))
        self.poly.updateProfile()
        self.poly.ready()
        self.poly.addNode(self)
        self.wait_for_node_done()

        self.node = self.poly.getNode(self.address)
        self.node.setDriver('ST', 1, True, True)
        logging.debug('Messana init DONE')
        self.nodeDefineDone = True


    def node_queue(self, data):
        self.n_queue.append(data['address'])

    def wait_for_node_done(self):
        while len(self.n_queue) == 0:
            time.sleep(0.1)
        self.n_queue.pop()

    def getValidName(self, name):
        name = bytes(name, 'utf-8').decode('utf-8','ignore')
        return re.sub(r"[^A-Za-z0-9_ ]", "", name)

    # remove all illegal characters from node address
    def getValidAddress(self, name):
        name = bytes(name, 'utf-8').decode('utf-8','ignore')
        return re.sub(r"[^A-Za-z0-9_]", "", name.lower()[:14])
    

    def start (self):
        logging.info('Executing start - Messana System')
        #logging.setLevel(30)
        while not self.nodeDefineDone:
            time.sleep(1)
            logging.debug ('waiting for inital node to get created')
        

        if self.ip_address == None or self.ip_address == '' or self.messana_key ==None or self.messana_key == '':
            logging.error('IP address and Messana Key must be provided to start node server')
            exit()

        self.messana  = messanaSystem()
        self.messana.init_system(self.ip_address,  self.messana_key)
        name = self.messana.name
        self.sys_addr = self.getValidAddress(self.messana.name)
        sys_name = self.getValidName(self.messana.name)
        self.m_sys = udi_messana_system(self.poly, self.sys_addr, self.sys_addr, name )

        if self.messana.nbr_zones > 0:
            self.zones = {}
            for zoneNbr in range(0, self.messana.nbr_zones):
                zone_name = self.messana.get_name('zone', zoneNbr)
                self.zones[zoneNbr] =  udiMessanaZone(self.poly, self.messana, zoneNbr)

        self.update_drivers()
        
        
        self.addNodes(self.deviceList)

        #self.poly.updateProfile()

    def update_drivers(self):
        self.node.setDriver('ST', 1, True, True)
        self.node.setDriver('GV0', self.system.nbr_zones, True, True)
        self.node.setDriver('GV1', self.system.nbr_atus, True, True)
        


    def add_nodes (self, deviceList):

        logging.debug('Parsing Parameters for old elements')
        delparams = []
        for param in self.Parameters:
            logging.debug( 'Parameters - checking {}'.format(param))
            if param not in self.supportParams:           
                if param.find(self.TTSstr) == -1:   
                    logging.debug( 'Parameters - deleting {}'.format(param))               
                    delparams.append(param)
        for param in delparams:
            self.Parameters.delete(param)
            logging.debug( 'Parameters - deleting {}'.format(param))


        for dev in range(0,len(self.deviceList)):
            if self.deviceList[dev]['type']  in self.supportedYoTypes:
                logging.info('adding/checking device : {} - {}'.format(self.deviceList[dev]['name'], self.deviceList[dev]['type']))
                if self.deviceList[dev]['type'] == 'Hub':    
                    logging.info('Hub not added - ISY cannot do anything useful with it')    
                    name = self.deviceList[dev]['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                    logging.info('Adding device {} ({}) as {}'.format( self.deviceList[dev]['name'], self.deviceList[dev]['type'], str(name) ))                                        
                    #udiYoHub(self.poly, name, name, self.deviceList[dev]['name'], self.yoAccess, self.deviceList[dev] )
                    #self.Parameters[name]  =  self.deviceList[dev]['name']
              
                elif self.deviceList[dev]['type'] == 'LeakSensor': 
                    name = self.deviceList[dev]['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                    logging.info('Adding device {} ({}) as {}'.format( self.deviceList[dev]['name'], self.deviceList[dev]['type'], str(name) ))                                        
                    udiYoLeakSensor(self.poly, name, name, self.deviceList[dev]['name'], self.yoAccess, self.deviceList[dev] )
                    self.Parameters[name]  =  self.deviceList[dev]['name']                  
            else:
                logging.debug('Currently unsupported device : {}'.format(self.deviceList[dev]['type'] ))
        #time.sleep(30)
        # checking params for erassed nodes 
        self.poly.updateProfile()
        ''''
        # check and remove for nodes that no longer exists
        logging.debug('Checking for old nodes ')
        nodes = self.poly.getNodes()
        logging.debug('nodelist {} : {}'.format(len(nodes), nodes))
        for nde in nodes:
            logging.debug('parsing node {}: {}'.format(nde, nodes[nde]))
            if nde != 'setup':
                nodeAddress = nodes[nde].address
                primAddress = nodes[nde].primary
                logging.debug('node{}:  {} {}'.format(nodes[nde].name, nodeAddress, primAddress ))
                if nodeAddress == primAddress: # it is not a sub node
                    found = False
                    for dev in range(0,len(self.deviceList)):
                        adr = self.deviceList[dev]['deviceId'][-14:]
                        if adr == nodeAddress:
                            found = True
                    if not found:
                        self.delNode(nde)
                        logging.debug('delete node {}'.format(nde))
        # checking params
        '''
    def stop(self):
        logging.info('Stop Called:')
        #self.yoAccess.writeTtsFile() #save current TTS messages
        if 'self.node' in locals():
            self.node.setDriver('ST', 0, True, True)
            #nodes = self.poly.getNodes()
            #for node in nodes:
            #    if node != 'setup':   # but not the controller node
            #        nodes[node].setDriver('ST', 0, True, True)
            time.sleep(2)
        if self.yoAccess:
            self.yoAccess.shut_down()
        self.poly.stop()
        exit()

    def heartbeat(self):
        logging.debug('heartbeat: ' + str(self.hb))
        
        if self.hb == 0:
            self.reportCmd('DON',2)
            self.hb = 1
        else:
            self.reportCmd('DOF',2)
            self.hb = 0

    def checkNodes(self):
        logging.info('Updating Nodes')
        self.deviceList = self.yoAccess.getDeviceList()
        nodes = self.poly.getNodes()
        for dev in range(0,len(self.deviceList)):
            devList = []
            name = self.deviceList[dev]['deviceId'][-14:]
            if name not in nodes:
                #device was likely off line during inital instellation or added afterwards
                devList.append(self.deviceList[dev])
                self.addNodes(devList)


    def systemPoll (self, polltype):
        if self.nodeDefineDone:
            logging.debug('System Poll executing: {}'.format(polltype))
            if 'longPoll' in polltype:
                #Keep token current
                try:
                    if not self.yoAccess.refresh_token(): #refresh failed
                        while not self.yoAccess.request_new_token():
                                time.sleep(60)
                    #logging.info('Updating device status')
                    nodes = self.poly.getNodes()
                    for nde in nodes:
                        if nde != 'setup':   # but not the controller node
                            nodes[nde].checkOnline()
                except Exception as e:
                    logging.debug('Exeption occcured during request_new_token : {}'.format(e))
                    self.yoAccess = YoLinkInitPAC (self.uaid, self.secretKey)
                    self.deviceList = self.yoAccess.getDeviceList()           
                
            if 'shortPoll' in polltype:
                self.heartbeat()
    


    def handleLevelChange(self, level):
        logging.info('New log level: {}'.format(level))
        logging.setLevel(level['level'])



    def handleParams (self, userParam ):
        logging.debug('handleParams')
        supportParams = ['YOLINKV2_URL', 'TOKEN_URL','MQTT_URL', 'MQTT_PORT', 'UAID', 'SECRET_KEY', 'NBR_TTS' ]
        self.Parameters.load(userParam)

       
        self.poly.Notices.clear()

        try:
            if 'IPADDRESS' in userParam:
                self.ip_address = userParam['IPADDRESS']
            #else:
            #    self.poly.Notices['yl2url'] = 'Missing YOLINKV2_URL parameter'
            #    self.yolinkV2URL = ''

            if 'MESSANA_KEY' in userParam:
                self.messana_key = userParam['MESSANA_KEY']
            #else:
            #    self.poly.Notices['turl'] = 'Missing TOKEN_URL parameter'
            #    self.tokenURL = ''

           
            self.handleParamsDone = True


        except:
            logging.debug('Error: {}'.format(userParam))

 
    commands = { 'UPDATE': ISYupdate
                ,'SET_STATUS': setStatus
                ,'SET_ENERGYSAVE': setEnergySave
                ,'SET_SETBACK' : setSetback 
                }
   
    id = 'setup'


    drivers = [
            {'driver': 'ST', 'value':1, 'uom':25},
            {'driver': 'GV0', 'value':0, 'uom':107},
            {'driver': 'GV1', 'value':0, 'uom':107},
           
           ]

if __name__ == "__main__":
    try:
        polyglot = udi_interface.Interface([])
        polyglot.start('0.1.0')
        messana(polyglot, 'setup', 'setup', 'Messana')

        # Just sit and wait for events
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)















'''


import sys
from MessanaSysV2 import messanaSys
#from MessanaZoneV2 import messanaZone
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
    logging = udi_interface.logging
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


    def defineInputParams(self):
        self.IPAddress = self.getCustomParam('IP_ADDRESS')
        if self.IPAddress is None:
            self.addNotice('Please Set IP address of Messana system (IP_ADDRESS)')
            self.addNotice('E.g. 192.168.1.2')
            logging.error('IP address not set')
            self.addCustomParam({'IP_ADDRESS': '192.168.1.2'})

        
        self.IPAddress = self.getCustomParam('MESSANA_KEY')
        if self.MessanaKey is None:
            self.addNotice('Please Set Messana API access Key (MESSANA_KEY)')
            self.addNotice('E.g. 12345678-90ab-cdef-1234-567890abcdef')
            logging.error('check_params: Messana Key not specified')
            self.addCustomParam({'MESSANA_KEY': '12345678-90ab-cdef-1234-567890abcdef'})


        self.addNotice('Please restart Node server after setting the parameters')



    def start(self):
        self.removeNoticesAll()

        self.messanaSys = messanaSys(self.IPAddress, self.MessanaKey)
        #self.nbrZones = self.messanaSys.messanaZones(self.IPAddress, self.MessanaKey)
        #self.messanaZones = messanaSys.createZones()
        #self.messanaMacroZones = messanaSys.createMacroZones()
        #self.messanaAtus = messanaSys.createAtus()
        #self.messanaEnergySources = messanaSys.createEnegrgySpurces()
        #self.messanaFanCoils = messanaSys.createFanCoils()
        #self.messanaHotWater = messanaSys.createHotWater()
        #self.messanaHotColdCtrl = messanaSys.createHotColdCtrl()


        #self.messanaSys.installMacroZones()
        #self.messanaSys.installAtus(  )




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
            self.defineInputParams()
            self.stop()

        else:
            logging.info('Retrieving info from Messana System')
            self.messana = messanaInfo( self.IPAddress, self.MessanaKey)
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
                    #logging.debug(  'driver:  ' +  temp['driver'])

            logging.info ('Install Profile')    
            self.poly.installprofile()
            #logging.debug('Install Profile done')
        self.updateISYdrivers('all')
        self.messanaImportOK = 1
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
        except Exception as e:
            logging.error('Exception updateISYdrivers: '+  str(e))       

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
 
    def setStatus(self, command):
        #logging.debug('set Status Called')
        value = int(command.get('value'))
        #logging.debug('set Status Recived:' + str(value))
        if self.messana.systemSetStatus(value):
            ISYdriver = self.messana.getSystemStatusISYdriver()
            self.setDriver(ISYdriver, value, report = True)

    def setEnergySave(self, command):
        #logging.debug('setEnergySave Called')
        value = int(command.get('value'))
        #logging.debug('SetEnergySave Recived:' + str(value))
        if self.messana.systemSetEnergySave(value):
            ISYdriver = self.messana.getSystemEnergySaveISYdriver()
            self.setDriver(ISYdriver, value, report = True)

    def setSetback(self, command):
        #logging.debug('setSetback Called')
        value = int(command.get('value'))
        #logging.debug('setSetback Reeived:' + str(value))
        if self.messana.systemSetback(value):
            ISYdriver = self.messana.getSystemSetbackISYdriver()
            self.setDriver(ISYdriver, value, report = True)

    def ISYupdate (self, command):
        #logging.info('ISY-update called')
        self.messana.updateSystemData('all')
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
        MessanaController(polyglot, 'system', 'system', 'MessanaRadiant')

        # Just sit and wait for events
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
        
        '''