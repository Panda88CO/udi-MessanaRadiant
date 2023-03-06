#!/usr/bin/env python3


import sys
from Messana_System import messana_system
from udi_MessanaZone import udi_messana_zone
from udi_MessanaMacrozone import udi_messana_macrozone
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
    from  udiLib import node_queue, wait_for_node_done, getValidName, getValidAddress, send_temp_to_isy, isy_value, convert_temp_unit, send_rel_temp_to_isy

    def __init__(self, polyglot, primary, address, name):
        super().__init__(polyglot, primary, address, name)

        logging.info('_init_ Messsana Controller')
        self.messanaImportOK = 0
        self.ISYforced = False
        self.name = 'Messana Main'

        #logging.debug('Name/address: '+ self.name + ' ' + self.address)
        self.poly = polyglot
        self.primary = primary
        self.address = address

        self.hb = 0
        self.ISYTempUnit = 0
        self.nodeDefineDone = False
        self.nodeConfigDone = False
        self.zones = {}
        self.macrozones = {}
        self.atus = {}
        self.buffertanks = {}
        self.fan_coils = {}
        self.hot_cold_change_overs = {}
        self.energy_sources = {}
        self.hotwaters = {}
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

        logging.debug('init node: {} {} {} {}'.format(self.address, self.name, self.id, self.primary))


        self.poly.ready()
        self.poly.updateProfile()
        self.poly.addNode(self, conn_status='ST')
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
            logging.debug( 'Temp Unit {} '.format(self.Parameters['TEMP_UNIT']) )
            self.ISY_temp_unit = self.convert_temp_unit(self.Parameters['TEMP_UNIT'])
        else:
            self.ISY_temp_unit = 0
            self.Parameters['TEMP_UNIT'] = 'C'
            logging.debug('TEMP_UNIT: {}'.format(self.ISY_temp_unit ))
       

        if (self.IPAddress is None) or (self.MessanaKey is None):
            #self.defineInputParams()
            self.stop()
        else:
            self.messana_info = {}
            self.messana_info['ip_address'] = self.IPAddress
            self.messana_info['api_key'] = self.MessanaKey
            self.messana_info['isy_temp_unit'] = self.ISY_temp_unit
            logging.info('Retrieving info from Messana System')
            #self.messana = messana_control(self.IPAddress, self.MessanaKey)
            #self.messana.initialize(self.IPAddress, self.MessanaKey)
            self.messana = messana_system(self.messana_info)
            if not self.messana.connected():
                self.stop()
            self.messana_temp_unit = self.convert_temp_unit(self.messana.temp_unit)
            logging.debug('Messana Temp unit; {}, ISY temp unit: {}'.format(self.messana_temp_unit, self.ISY_temp_unit ))
            
            
            self.updateISY_longpoll()
            time.sleep(1)

        for zone_nbr in range(0, self.messana.nbr_zones ):
            logging.debug('Creating zone {}'.format(zone_nbr))
            address = 'zone'+str(zone_nbr)
            name = 'dummy_name'
            self.zones[zone_nbr] = udi_messana_zone(self.poly, self.primary, address, name, zone_nbr, self.messana_info)
        
        for macrozone_nbr in range(0, self.messana.nbr_macrozones ):
            logging.debug('Creating macrozone {}'.format(macrozone_nbr))
            address = 'macrozone'+str(macrozone_nbr)
            name = 'dummy_name'
            self.macrozones[macrozone_nbr] = udi_messana_macrozone(self.poly, self.primary, address, name, macrozone_nbr, self.messana_info)

        for atu_nbr in range(0, self.messana.nbr_atus ):
            logging.debug('Creating atus {}'.format(atu_nbr))
            address = 'atu'+str(atu_nbr)
            name = 'dummy_name'
            self.macrozones[atu_nbr] = udi_messana_macrozone(self.poly, self.primary, address, name, atu_nbr, self.messana_info)
        '''
        for buffertank_nbr in range(0, self.messana.nbr_buffer_tank ):
            logging.debug('Creating buffer tanks {}'.format(buffertank_nbr))
            address = 'buffertank'+str(buffertank_nbr)
            name = 'dummy_name'
            self.macrozones[buffertank_nbr] = udi_messana_macrozone(self.poly, self.primary, address, name, buffertank_nbr, self.messana_info)

        for energy_source_nbr in range(0, self.messana.nbr_energy_source ):
            logging.debug('Creating energy_source {}'.format(energy_source_nbr))
            address = 'energysource'+str(energy_source_nbr)
            name = 'dummy_name'
            self.macrozones[energy_source_nbr] = udi_messana_macrozone(self.poly, self.primary, address, name, energy_source_nbr, self.messana_info)

        for fan_coil_nbr in range(0, self.messana.nbr_fancoil ):
            logging.debug('Creating fan coils {}'.format(fan_coil_nbr))
            address = 'fancoil'+str(fan_coil_nbr)
            name = 'dummy_name'
            self.macrozones[fan_coil_nbr] = udi_messana_macrozone(self.poly, self.primary, address, name, fan_coil_nbr, self.messana_info)

        for hotcold_nbr in range(0, self.messana.nbr_HCgroup ):
            logging.debug('Creating hot cold change overs {}'.format(hotcold_nbr))
            address = 'hotcold'+str(hotcold_nbr)
            name = 'dummy_name'
            self.macrozones[hotcold_nbr] = udi_messana_macrozone(self.poly, self.primary, address, name, hotcold_nbr, self.messana_info)

        for hotwater_nbr in range(0, self.messana.nbr_atus ):
            logging.debug('Creating domestic hot water {}'.format(hotwater_nbr))
            address = 'hotwater'+str(hotwater_nbr)
            name = 'dummy_name'
            self.macrozones[hotwater_nbr] = udi_messana_macrozone(self.poly, self.primary, address, name, hotwater_nbr, self.messana_info)
        '''                                                
        #self.updateISY_longpoll()
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

        tmp = self.messana.get_status()
        logging.debug('System State {}'.format(tmp))
        self.node.setDriver('GV0', tmp, True, True)

        tmp = self.messana.get_setback_diff()
        logging.debug('Setback Offset {}'.format(tmp))
        self.send_rel_temp_to_isy(tmp, 'GV1')
        #self.node.setDriver('GV1', tmp, True, True)

        tmp = self.messana.get_setback()
        logging.debug('Setback Enabled {}'.format(tmp))
        self.node.setDriver('GV2', tmp, True, True)

        tmp = self.messana.get_energy_saving()
        logging.debug('Setback Enabled {}'.format(tmp))
        self.node.setDriver('GV12', tmp, True, True)

        logging.debug('Nbr Zones{}'.format(self.messana.nbr_zones))
        self.node.setDriver('GV3', self.messana.nbr_zones)

        logging.debug('Nbr macrozones{}'.format(self.messana.nbr_macrozone))
        self.node.setDriver('GV4', self.messana.nbr_macrozone)

        logging.debug('Nbr atu{}'.format(self.messana.nbr_atus))
        self.node.setDriver('GV5', self.messana.nbr_atus)

        logging.debug('Nbr Hot Cold{}'.format(self.messana.nbr_HCgroup))
        self.node.setDriver('GV6', self.messana.nbr_HCgroup)

        logging.debug('Nbr fan coil{}'.format(self.messana.nbr_fancoil))
        self.node.setDriver('GV7', self.messana.nbr_fancoil)

        logging.debug('Nbr domestic Hot Water{}'.format(self.messana.nbr_dhwater))
        self.node.setDriver('GV8', self.messana.nbr_dhwater)

        logging.debug('Nbr buffer Tank {}'.format(self.messana.nbr_buffer_tank))
        self.node.setDriver('GV9', self.messana.nbr_buffer_tank)

        logging.debug('Nbr energy source{}'.format(self.messana.nbr_energy_source))
        self.node.setDriver('GV10', self.messana.nbr_energy_source)

        tmp = self.messana.get_external_alarm()
        logging.debug('Alarm Status{}'.format(tmp))
        self.node.setDriver('GV11', tmp, True, True)                

    def updateISY_shortpoll(self):
        logging.debug('updateISY_shortpoll')
        self.heartbeat()

        tmp = self.messana.get_status()
        logging.debug('System State {}'.format(tmp))
        self.node.setDriver('GV0', tmp)

        tmp = self.messana.get_external_alarm()
        logging.debug('Alarm Status{}'.format(tmp))
        self.node.setDriver('GV11', tmp)


    def setStatus(self, command):
        status = int(command.get('value'))
        logging.debug('set Status Called: {}'.format(status))
        if self.messana.set_status(status):
            self.node.setDriver('GV0', status)
        else:
            logging.error('Error calling setStatus')


    def setEnergySave(self, command): 
        energy_save = int(command.get('value'))
        logging.debug('setEnergySave Called: {}'.format(energy_save))
        if  self.messana.set_energy_saving(energy_save):
            self.node.setDriver('GV12', energy_save)
        else:
            logging.error('Error calling setEnergySave')


    def setSetback(self, command):
        setback = int(command.get('value'))
        logging.debug('setSetback Called: {}'.format(setback))
        if  self.messana.set_energy_saving(setback):
            self.node.setDriver('GV2', setback)
        else:
            logging.error('Error calling setSetback')

    def setSetbackOffset(self, command):
        setback_diff = int(command.get('value'))
        logging.debug('setSetbackOffset Called: {}'.format(setback_diff))
        if  self.messana.set_setback_diff(setback_diff):
            self.send_rel_temp_to_isy(setback_diff, 'GV1')
            #self.node.setDriver('GV1', setback_diff)
        else:
            logging.error('Error calling setSetbackOffset')

    def ISYupdate (self, command):
        #logging.info('ISY-update called')
        #self.messana.updateSystemData('all')
        self.updateISY_longpoll()
        #self.reportDrivers()

    drivers = [
            {'driver': 'GV0', 'value':99, 'uom':25 }, # system State
            {'driver': 'GV1', 'value':99, 'uom':25 }, # Setback diff Temp
            {'driver': 'GV2', 'value':99, 'uom':25 }, # Setback Enabled
            {'driver': 'GV12', 'value':99, 'uom':25 }, # Energy Saving
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
                ,'STATUS': setStatus
                ,'ENERGYSAVE': setEnergySave
                ,'SETBACK' : setSetback
                ,'SETBACK_OFFSET' : setSetbackOffset
                }

    id = 'system'

if __name__ == "__main__":
    try:
        logging.info('Starting Messana Controller')
        polyglot = udi_interface.Interface([])
        polyglot.start('0.0.88')
        MessanaController(polyglot, 'system', 'system', 'Messana Radiant System')

        # Just sit and wait for events
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
        