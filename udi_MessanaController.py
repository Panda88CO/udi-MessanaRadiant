#!/usr/bin/env python3


import sys
from Messana_System import messana_system
from udi_MessanaZone import udi_messana_zone
from udi_MessanaMacrozone import udi_messana_macrozone
from udi_MessanaATU import udi_messana_atu
from udi_MessanaBuffertank import udi_messana_buffertank
from udi_MessanaHCCO import udi_messana_hc_co
from udi_MessanaFancoil import  udi_messana_fancoil
from udi_MessanaEnergySource import  udi_messana_energy_source
from udi_MessanaHotWater import  udi_messana_hot_water

#from udi_MessanaEnergySource import udi_messanaEnergySource
#

#from udi_MessanaHotWater import udi_messanaHotWater

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
  
    id = 'system'

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
        self.TEMP_C = self.convert_temp_unit('C')
        self.TEMP_F = self.convert_temp_unit('F')
    
        self.ISYTempUnit = self.TEMP_C
        self.nodeDefineDone = False
        self.nodeConfigDone = False
        self.zone = {}
        self.macrozone = {}
        self.atu = {}
        self.buffertank = {}
        self.fancoil = {}
        self.hot_cold_change_over = {}
        self.energy_source = {}
        self.hotwater = {}
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
            self.ISY_temp_unit = self.TEMP_C
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
            address = self.poly.getValidAddress('zone'+str(zone_nbr))
            tmp_name= self.messana.get_zone_name(zone_nbr)
            name = self.poly.getValidName('Zone '+ tmp_name)
            self.zone[zone_nbr] = udi_messana_zone(self.poly, self.primary, address, name, zone_nbr, self.messana_info)
        
        for macrozone_nbr in range(0, self.messana.nbr_macrozones ):
            logging.debug('Creating macrozone {}'.format(macrozone_nbr))
            address = self.poly.getValidAddress('macrozone'+str(macrozone_nbr))
            tmp_name= self.messana.get_macrozone_name(macrozone_nbr)
            name = self.poly.getValidName('Macrozone '+tmp_name)
            self.macrozone[macrozone_nbr] = udi_messana_macrozone(self.poly, self.primary, address, name, macrozone_nbr, self.messana_info)

        for atu_nbr in range(0, self.messana.nbr_atus ):
            logging.debug('Creating atus {}'.format(atu_nbr))
            address = self.poly.getValidAddress('atu'+str(atu_nbr))
            tmp_name= self.messana.get_atu_name(atu_nbr)
            name = self.poly.getValidName('Atu '+tmp_name)
            self.atu[atu_nbr] = udi_messana_atu(self.poly, self.primary, address, name, atu_nbr, self.messana_info)

        for buffertank_nbr in range(0, self.messana.nbr_buffer_tank ):
            logging.debug('Creating buffer tanks {}'.format(buffertank_nbr))
            address = self.poly.getValidAddress('buffertank'+str(buffertank_nbr))
            tmp_name= self.messana.get_buffertank_name(buffertank_nbr)
            name = self.poly.getValidName('Buffertank '+tmp_name)
            self.buffertank[buffertank_nbr] = udi_messana_buffertank(self.poly, self.primary, address, name, buffertank_nbr, self.messana_info)

        for hc_co_nbr in range(0, self.messana.nbr_energy_source ):
            logging.debug('Creating hot cold change over {}'.format(hc_co_nbr))
            address = self.poly.getValidAddress('hcco'+str(hc_co_nbr))
            tmp_name= self.messana.get_hc_co_name(hc_co_nbr)
            name = self.poly.getValidName('Hot Cold CO '+tmp_name)
            self.hot_cold_change_over[hc_co_nbr] = udi_messana_hc_co(self.poly, self.primary, address, name, hc_co_nbr, self.messana_info)

        for fancoil_nbr in range(0, self.messana.nbr_fancoil ):
            logging.debug('Creating fan coils {}'.format(fancoil_nbr))
            address = self.poly.getValidAddress('fancoil'+str(fancoil_nbr))
            tmp_name= self.messana.get_fancoil_name(fancoil_nbr)
            name = self.poly.getValidName('Fancoil '+tmp_name)
            self.fancoil[fancoil_nbr] = udi_messana_fancoil(self.poly, self.primary, address, name, fancoil_nbr, self.messana_info)

        for energy_source_nbr in range(0, self.messana.nbr_energy_source ):
            logging.debug('Creating energy_source {}'.format(energy_source_nbr))
            address = self.poly.getValidAddress('energy'+str(energy_source_nbr))
            tmp_name= self.messana.get_energy_source_name(energy_source_nbr)
            name = self.poly.getValidName('Energy Source '+tmp_name)
            self.energy_source[energy_source_nbr] = udi_messana_energy_source(self.poly, self.primary, address, name, energy_source_nbr, self.messana_info)

        for hotwater_nbr in range(0, self.messana.nbr_dhwater ):
            logging.debug('Creating domestic hot water {}'.format(hotwater_nbr))
            address = self.poly.getValidAddress('hotwater'+str(hotwater_nbr))
            tmp_name= self.messana.get_hotwater_name(hotwater_nbr)
            name = self.poly.getValidName('Hotwater '+tmp_name)
            self.hotwater[hotwater_nbr] = udi_messana_hot_water(self.poly, self.primary, address, name, hotwater_nbr, self.messana_info)
                                             
        #self.updateISY_longpoll()
        #self.updateISYdrivers('all')
        #self.messanaImportOK = 1
        self.poll_start = True
        #self.discover()


    def stop(self):
        #self.removeNoticesAll()
        logging.info('stop - Cleaning up')
        nodes = self.poly.getNodes()
        for nde in nodes:
            logging.debug('Stop node {}'.format(nde))
            if nde != 'system':
                nodes[nde].stop()
        self.node.setDriver('ST', 0, True, True)
        self.poly.stop()


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
        if 0 == self.messana.nbr_zones:
            self.node.setDriver('GV3', 98, True, False, 25)
        else:
            self.node.setDriver('GV3', self.messana.nbr_zones, True, False, 107)

        logging.debug('Nbr macrozones{}'.format(self.messana.nbr_macrozones))
        if 0 == self.messana.nbr_macrozones:
            self.node.setDriver('GV4', 98, True, False, 25)
        else:
            self.node.setDriver('GV4', self.messana.nbr_macrozones, True, False, 107)

        logging.debug('Nbr atu{}'.format(self.messana.nbr_atus))
        if 0 == self.messana.nbr_atus:
            self.node.setDriver('GV5', 98, True, False, 25)
        else:
            self.node.setDriver('GV5', self.messana.nbr_atus, True, False, 107)

        logging.debug('Nbr Hot Cold{}'.format(self.messana.nbr_HCgroup))
        if 0 == self.messana.nbr_HCgroup:
            self.node.setDriver('GV6', 98, True, False, 25)
        else:
            self.node.setDriver('GV6', self.messana.nbr_HCgroup, True, False, 107)

        logging.debug('Nbr fan coil{}'.format(self.messana.nbr_fancoil))
        if 0 == self.messana.nbr_fancoil:
            self.node.setDriver('GV7', 98, True, False, 25)
        else:
            self.node.setDriver('GV7', self.messana.nbr_fancoil, True, False, 107)

        logging.debug('Nbr domestic Hot Water{}'.format(self.messana.nbr_dhwater))
        if 0 == self.messana.nbr_dhwater:
            self.node.setDriver('GV8', 98, True, False, 25)
        else:
            self.node.setDriver('GV8', self.messana.nbr_dhwater, True, False, 107)

        logging.debug('Nbr buffer Tank {}'.format(self.messana.nbr_buffer_tank))
        if 0 == self.messana.nbr_buffer_tank:
            self.node.setDriver('GV9', 98, True, False, 25)
        else:
            self.node.setDriver('GV9', self.messana.nbr_buffer_tank, True, False, 107)

        logging.debug('Nbr energy source{}'.format(self.messana.nbr_energy_source))
        if 0 == self.messana.nbr_energy_source:
            self.node.setDriver('GV10', 98, True, False, 25)
        else:
            self.node.setDriver('GV10', self.messana.nbr_energy_source, True, False, 107)

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
        temp = self.messana.set_status(status) 
        if temp is not None:
            self.node.setDriver('GV0', temp)
        else:
            logging.error('Error calling setStatus')


    def setEnergySave(self, command): 
        energy_save = int(command.get('value'))
        logging.debug('setEnergySave Called: {}'.format(energy_save))
        temp = self.messana.set_energy_saving(energy_save)
        if   temp is not None:
            self.node.setDriver('GV12', temp)
        else:
            logging.error('Error calling setEnergySave')


    def setSetback(self, command):
        setback = int(command.get('value'))
        logging.debug('setSetback Called: {}'.format(setback))
        temp = self.messana.set_energy_saving(setback)
        if temp is not None:
            self.node.setDriver('GV2', temp)
        else:
            logging.error('Error calling setSetback')

    def setSetbackOffset(self, command):
        setback_diff = int(command.get('value'))
        #setback_unit = int(temp_uom.get('value'))
        logging.debug('setSetbackOffset Called: {}'.format(setback_diff))
        messana_diff = setback_diff
        if self.messana_temp_unit == self.TEMP_C :
            if self.ISY_temp_unit == self.TEMP_F:
                messana_diff = (setback_diff - 32)*5/9
        elif  self.messana_temp_unit == self.TEMP_F:
            if self.ISY_temp_unit == self.TEMP_C :
                messana_diff = setback_diff*9/5 + 32
        temp = self.messana.set_setback_diff(messana_diff)
        if temp is not None:
            self.send_rel_temp_to_isy(temp, 'GV1')

            #self.node.setDriver('GV1', setback_diff)
        else:
            logging.error('Error calling setSetbackOffset')

    def ISYupdate (self, command):
        #logging.info('ISY-update called')
        #self.messana.updateSystemData('all')
        self.updateISY_longpoll()
        #self.reportDrivers()



    commands = { 'UPDATE': ISYupdate
                ,'STATUS': setStatus
                ,'ENERGYSAVE': setEnergySave
                ,'SETBACK' : setSetback
                ,'SETBACK_OFFSET' : setSetbackOffset
                }



if __name__ == "__main__":
    try:
        logging.info('Starting Messana Controller')
        polyglot = udi_interface.Interface([])
        polyglot.start('0.0.128')
        MessanaController(polyglot, 'system', 'system', 'Messana Radiant System')

        # Just sit and wait for events
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
        