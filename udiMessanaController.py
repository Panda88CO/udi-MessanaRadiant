#!/usr/bin/env python3


import sys
from MessanaSystem import messana_system
from MessanaInfo import messana_control
from MessanaZone import messana_zone
from udiMessanaZone import udi_messana_zone
#from MessanaMacrozoneV2 import messanaMacrozone
#from MessanaATUV2 import messanaAtu
#from MessanaBufTankV2 import messanaBufTank
#from MessanaEnergySourceV2 import messanaEnergySource
#from MessanaFanCoilV2 import  messanaFanCoil
#from MessanaHotColdCOV2 import messanaHcCo
#from MessanaHotWaterV2 import messanaHotWater
import time
import re

try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom

except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    #logging = logging.getlogging('testLOG')


class MessanaController(udi_interface.Node):

    def __init__(self, polyglot, primary, address, name):
        super().__init__( polyglot, primary, address, name)

        logging.info('_init_ Messsana Controller')
        self.messanaImportOK = 0
        self.ISYforced = False
        self.name = 'Messana Main'

        #logging.debug('Name/address: '+ self.name + ' ' + self.address)
        self.primary = primary
        self.address = address
        self.poly = polyglot
        self.hb = 0
        self.ISYdrivers=[]
        self.ISYTempUnit = 0
        self.nodeDefineDone = False
        self.nodeConfigDone = False
        self.zones = {}
        self.poll_start = False
        
        self.Parameters = Custom(self.poly, 'customparams')
        self.Notices = Custom(self.poly, 'notices')
        self.n_queue = []

        self.poly.subscribe(self.poly.STOP, self.stop)
        self.poly.subscribe(self.poly.START, self.start, address)
        self.poly.subscribe(self.poly.LOGLEVEL, self.handleLevelChange)
        self.poly.subscribe(self.poly.CUSTOMPARAMS, self.handleParams)
        self.poly.subscribe(self.poly.POLL, self.systemPoll)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)
        self.poly.subscribe(self.poly.CONFIGDONE, self._configdone_handler)
        
        self.poly.ready()
        self.poly.addNode(self)
        self.wait_for_node_done()

        self.poly.updateProfile()
        self.node = self.poly.getNode(self.address)
        logging.debug('Node is {}'.format(self.node))
        logging.debug('drivers: {}'.format(self.drivers))

        logging.debug('MessanaRadiant init DONE')
        self.nodeDefineDone = True

    def _configdone_handler(self):
        logging.debug('config done')
        self.nodeConfigDone = True


    def node_queue(self, data):
        self.n_queue.append(data['address'])

    def wait_for_node_done(self):
        while len(self.n_queue) == 0:
            time.sleep(0.1)
        self.n_queue.pop()

    def convert_temp_unit(self, tempStr):
        if tempStr.capitalize()[:1] == 'F':
            return(1)
        elif tempStr.capitalize()[:1] == 'K':
            return(2)
        else:
            return(0)


    def getValidName(self, name):
        name = bytes(name, 'utf-8').decode('utf-8','ignore')
        return re.sub(r"[^A-Za-z0-9_ ]", "", name)

    # remove all illegal characters from node address
    def getValidAddress(self, name):
        name = bytes(name, 'utf-8').decode('utf-8','ignore')
        return re.sub(r"[^A-Za-z0-9_]", "", name.lower()[:14])
    

    def start(self):
        logging.info('Start Messana Main NEW')
        self.poly.Notices.clear()
        while not self.nodeDefineDone:
            time.sleep(2)
            logging.debug('Waiting for stuff to initialize')


        self.node.setDriver('ST', 1, True, True)
        #check params are ok 

        if 'IP_ADDRESS' in self.Parameters:
            self.IPAddress = self.Parameters['IP_ADDRESS']
            if self.IPAddress is None:
                logging.error('IP_ADDRESS must be specified in configuration:' )
            else:
                logging.debug('IPaddress retrieved: {}'.format(self.IPAddress))
        else:
            logging.error('IP_ADDRESS must be specified in configuration:' )

        if 'MESSANA_KEY' in self.Parameters:
            self.MessanaKey = self.Parameters['MESSANA_KEY']
            if self.MessanaKey is None:
                logging.error('MESSANA_KEY must be provided in configuration:' )
            else:
                logging.debug('MESSANA_KEY retrieved: {}'.format(self.MessanaKey))
        else:
            logging.error('MESSANA_KEY must be provided in configuration:' )

        if 'TEMP_UNIT' in self.Parameters:
            self.ISY_temp_unit = self.convert_temp_unit(self.Parameters['TEMP_UNIT'])
        else:
            self.ISY_temp_unit = 0  
            self.Parameters['TEMP_UNIT'] = 'C'
            logging.debug('TEMP_UNIT: {}'.format(self.ISY_temp_unit ))
       

        if (self.IPAddress is None) or (self.MessanaKey is None):
            #self.defineInputParams()
            self.stop()
        else:
            logging.info('Retrieving info from Messana System')
            self.messana = messana_control(self.IPAddress, self.MessanaKey)
            self.messana_system = messana_system(self.messana)
            if not self.messana.connected():
                self.stop()
        
        for zone_nbr in range(0, self.messana_system.nbr_zones ):
            logging.debug('Creating zone {}'.format(zone_nbr))
            address = 'zone'+str(zone_nbr)
            name = 'dummy_name'
            self.zones[zone_nbr] = udi_messana_zone(self.poly, self.primary, address, name, zone_nbr, self.messana)
        


        self.updateISY_longpoll()
        #self.updateISYdrivers('all')
        #self.messanaImportOK = 1
        self.poll_start = True
        #self.discover()


    def stop(self):
        #self.removeNoticesAll()
        logging.info('stop - Cleaning up')
        self.node.setDriver('ST', 0, True, True)


    def handleLevelChange(self, level):
        logging.info('New log level: {}'.format(level))
        logging.setLevel(level['level'])



    def handleParams (self, userParam ):
        logging.debug('handleParams')
        self.Parameters.load(userParam)
        self.poly.Notices.clear()



    def systemPoll (self, polltype):
        if self.poll_start:
            logging.debug('System Poll executing: {}'.format(polltype))

            if 'longPoll' in polltype:
                #Keep token current
                #self.node.setDriver('GV0', self.ISY_temp_unit, True, True)
                try:
                    nodes = self.poly.getNodes()
                    for nde in nodes:
                        logging.debug('Longpoll update nodes {}'.format(nde))
                        if nde != 'controller':   # but not the controller node
                            nodes[nde].updateISY_longpoll()
                except Exception as e:
                    logging.debug('Exeption occcured during systemPoll : {}'.format(e))
                    #self.yoAccess = YoLinkInitPAC (self.uaid, self.secretKey)
                    #self.deviceList = self.yoAccess.getDeviceList()           
                
            if 'shortPoll' in polltype:
                self.heartbeat()
                nodes = self.poly.getNodes()
                for nde in nodes:
                    logging.debug('short poll update nodes {}'.format(nde))
                    if nde != 'controller':   # but not the controller node
                        nodes[nde].updateISY_shortpoll()


    def heartbeat(self):
        #logging.debug('heartbeat: hb={}'.format(self.hb))
        if self.hb == 0:
            self.reportCmd('DON',2)
            self.hb = 1
        else:
            self.reportCmd('DOF',2)
            self.hb = 0

   
    def set_temp_Driver(self, Key, temperature):
        logging.debug('set_temp_Driver')
        

    def updateISY_longpoll(self):
        logging.debug('updateISY_longpoll')
        tmp = self.messana_system.get_status()
        logging.debug('System State {}'.format(tmp))
        self.node.setDriver('GV0', tmp, True, True)

        tmp = self.messana_system.get_setback_diff()
        logging.debug('Setback Offset {}'.format(tmp))
        self.node.setDriver('GV1', tmp, True, True)        

        tmp = self.messana_system.get_setback()
        logging.debug('Setback Enabled {}'.format(tmp))

        self.node.setDriver('GV2', tmp, True, True)

        logging.debug('Nbr Zones{}'.format(self.messana_system.nbr_zones))
        self.node.setDriver('GV3', self.messana_system.nbr_zones)

        logging.debug('Nbr macrozones{}'.format(self.messana_system.nbr_macrozone))
        self.node.setDriver('GV4', self.messana_system.nbr_macrozone)

        logging.debug('Nbr atu{}'.format(self.messana_system.nbr_atus))
        self.node.setDriver('GV5', self.messana_system.nbr_atus)

        logging.debug('Nbr Hot Cold{}'.format(self.messana_system.nbr_HCgroup))
        self.node.setDriver('GV6', self.messana_system.nbr_HCgroup)

        logging.debug('Nbr fan coil{}'.format(self.messana_system.nbr_fancoil))
        self.node.setDriver('GV7', self.messana_system.nbr_fancoil)

        logging.debug('Nbr domestic Hot Water{}'.format(self.messana_system.nbr_dhwater))
        self.node.setDriver('GV8', self.messana_system.nbr_dhwater)


        logging.debug('Nbr buffer Tank {}'.format(self.messana_system.nbr_buffer_tank))
        self.node.setDriver('GV9', self.messana_system.nbr_buffer_tank)

        logging.debug('Nbr energy source{}'.format(self.messana_system.nbr_energy_source))
        self.node.setDriver('GV10', self.messana_system.nbr_energy_source)

        tmp = self.messana_system.get_external_alarm()
        logging.debug('Alarm Status{}'.format(tmp))
        self.node.setDriver('GV11', tmp, True, True)                

    def updateISY_shortpoll(self):
        logging.debug('updateISY_shortpoll')
        self.heartbeat()

        tmp = self.messana_system.get_status()
        logging.debug('System State {}'.format(tmp))
        self.node.setDriver('GV0', tmp)

        tmp = self.messana_system.get_external_alarm()
        logging.debug('Alarm Status{}'.format(tmp))
        self.node.setDriver('GV11', tmp)

    '''
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
        self.updateISY_longpoll()
        #self.reportDrivers()

    drivers = [
            {'driver': 'GV0', 'value':99, 'uom':25 }, # system State
            {'driver': 'GV1', 'value':0, 'uom':4 }, # Setback Temp
            {'driver': 'GV2', 'value':99, 'uom':25 }, # Energy Saving
            {'driver': 'GV3', 'value':99, 'uom':25 }, # Zone Count    
            {'driver': 'GV4', 'value':99, 'uom':25 }, # Macrozone stamp
            {'driver': 'GV5', 'value':99, 'uom':25 }, # ATU count
            {'driver': 'GV6', 'value':99, 'uom':25 }, # HotCold count
            {'driver': 'GV7', 'value':99, 'uom':25 }, # Fancoil count
            {'driver': 'GV8', 'value':99, 'uom':25 }, # Hot Water count
            {'driver': 'GV9', 'value':99, 'uom':25 }, # Buffer Tank Count
            {'driver': 'GV10', 'value':99, 'uom':25 }, # Energy Source Count      
            {'driver': 'GV11', 'value':99, 'uom':25 }, #alarm
            {'driver': 'ST', 'value':0, 'uom':25 }, #state
            ]

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
        polyglot.start('0.0.48')
        MessanaController(polyglot, 'system', 'system', 'Messana Radiant System')

        # Just sit and wait for events
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
        