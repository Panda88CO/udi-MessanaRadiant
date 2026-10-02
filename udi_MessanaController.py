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
import json
from profile_def import build_profile_definition
from version import __version__

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
  
    id = 'SYSTEM'

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
            {'driver': 'TIME', 'value':0, 'uom':151 }, #last update
            ]
    

    def __init__(self, polyglot, primary, address, name):
        super().__init__(polyglot, primary, address, name)

        logging.info(f'_init_ Messana Controller v{__version__}')
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
        self.ISY_temp_unit = self.TEMP_C
        self.messana_temp_unit = self.TEMP_C
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
        self.poly.addNode(self, conn_status='ST')
        self.wait_for_node_done()

        self.node = self.poly.getNode(self.address)
        logging.debug('Node is {}'.format(self.node))
        logging.debug('drivers: {}'.format(self.drivers))

        logging.debug('MessanaRadiant init DONE')

        self.nodeDefineDone = True

    def _configdone_handler(self):
        logging.debug('config done')
        self.nodeConfigDone = True




    def start(self):
        logging.info(f'Start Messana Main v{__version__}')
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
            self.messana_info['messana_temp_unit'] = self.messana.temp_unit
            logging.debug('Messana Temp unit; {}, ISY temp unit: {}'.format(self.messana_temp_unit, self.ISY_temp_unit ))
            
            self.updateISY_longpoll()
            time.sleep(1)

        try:
            node_delay = float(self.Parameters['NODE_DELAY']) if 'NODE_DELAY' in self.Parameters else 1.0
        except (ValueError, TypeError):
            node_delay = 1.0
        logging.info('Serializing node creation with {}s delay between nodes'.format(node_delay))

        for zone_nbr in range(0, self.messana.nbr_zones ):
            logging.info('Creating zone {} of {}'.format(zone_nbr + 1, self.messana.nbr_zones))
            address = self.poly.getValidAddress('zone'+str(zone_nbr))
            tmp_name= self.messana.get_zone_name(zone_nbr)
            name = self.poly.getValidName('Zone '+ (tmp_name or str(zone_nbr)))
            self.zone[zone_nbr] = udi_messana_zone(self.poly, self.primary, address, name, zone_nbr, self.messana_info)
            time.sleep(node_delay)
        
        for macrozone_nbr in range(0, self.messana.nbr_macrozones ):
            logging.info('Creating macrozone {} of {}'.format(macrozone_nbr + 1, self.messana.nbr_macrozones))
            address = self.poly.getValidAddress('macrozone'+str(macrozone_nbr))
            tmp_name= self.messana.get_macrozone_name(macrozone_nbr)
            name = self.poly.getValidName('Macrozone '+ (tmp_name or str(macrozone_nbr)))
            self.macrozone[macrozone_nbr] = udi_messana_macrozone(self.poly, self.primary, address, name, macrozone_nbr, self.messana_info)
            time.sleep(node_delay)

        for atu_nbr in range(0, self.messana.nbr_atus ):
            logging.info('Creating ATU {} of {}'.format(atu_nbr + 1, self.messana.nbr_atus))
            address = self.poly.getValidAddress('atu'+str(atu_nbr))
            tmp_name= self.messana.get_atu_name(atu_nbr)
            name = self.poly.getValidName('Atu '+ (tmp_name or str(atu_nbr)))
            self.atu[atu_nbr] = udi_messana_atu(self.poly, self.primary, address, name, atu_nbr, self.messana_info)
            time.sleep(node_delay)

        for buffertank_nbr in range(0, self.messana.nbr_buffer_tank ):
            logging.info('Creating buffer tank {} of {}'.format(buffertank_nbr + 1, self.messana.nbr_buffer_tank))
            address = self.poly.getValidAddress('buffertank'+str(buffertank_nbr))
            tmp_name= self.messana.get_buffertank_name(buffertank_nbr)
            name = self.poly.getValidName('Buffertank '+ (tmp_name or str(buffertank_nbr)))
            self.buffertank[buffertank_nbr] = udi_messana_buffertank(self.poly, self.primary, address, name, buffertank_nbr, self.messana_info)
            time.sleep(node_delay)

        for hc_co_nbr in range(0, self.messana.nbr_HCgroup ):
            logging.info('Creating HCCO {} of {}'.format(hc_co_nbr + 1, self.messana.nbr_HCgroup))
            address = self.poly.getValidAddress('hcco'+str(hc_co_nbr))
            tmp_name= self.messana.get_hc_co_name(hc_co_nbr)
            name = self.poly.getValidName('Hot Cold CO '+ (tmp_name or str(hc_co_nbr)))
            self.hot_cold_change_over[hc_co_nbr] = udi_messana_hc_co(self.poly, self.primary, address, name, hc_co_nbr, self.messana_info)
            time.sleep(node_delay)

        for fancoil_nbr in range(0, self.messana.nbr_fancoil ):
            logging.info('Creating fan coil {} of {}'.format(fancoil_nbr + 1, self.messana.nbr_fancoil))
            address = self.poly.getValidAddress('fancoil'+str(fancoil_nbr))
            tmp_name= self.messana.get_fancoil_name(fancoil_nbr)
            name = self.poly.getValidName('Fancoil '+ (tmp_name or str(fancoil_nbr)))
            self.fancoil[fancoil_nbr] = udi_messana_fancoil(self.poly, self.primary, address, name, fancoil_nbr, self.messana_info)
            time.sleep(node_delay)

        for energy_source_nbr in range(0, self.messana.nbr_energy_source ):
            logging.info('Creating energy source {} of {}'.format(energy_source_nbr + 1, self.messana.nbr_energy_source))
            address = self.poly.getValidAddress('energy'+str(energy_source_nbr))
            tmp_name= self.messana.get_energy_source_name(energy_source_nbr)
            name = self.poly.getValidName('Energy Source '+ (tmp_name or str(energy_source_nbr)))
            self.energy_source[energy_source_nbr] = udi_messana_energy_source(self.poly, self.primary, address, name, energy_source_nbr, self.messana_info)
            time.sleep(node_delay)

        for hotwater_nbr in range(0, self.messana.nbr_dhwater ):
            logging.info('Creating domestic hot water {} of {}'.format(hotwater_nbr + 1, self.messana.nbr_dhwater))
            address = self.poly.getValidAddress('hotwater'+str(hotwater_nbr))
            tmp_name= self.messana.get_hotwater_name(hotwater_nbr)
            name = self.poly.getValidName('Hotwater '+ (tmp_name or str(hotwater_nbr)))
            self.hotwater[hotwater_nbr] = udi_messana_hot_water(self.poly, self.primary, address, name, hotwater_nbr, self.messana_info)
            time.sleep(node_delay)
                                             
        self.nodeConfigDone = True
        logging.info('Messana system configured - updating profile')
        self.update_profile()
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
        if 'TEMP_UNIT' in self.Parameters:
            new_unit = self.convert_temp_unit(self.Parameters['TEMP_UNIT'])
            if new_unit != getattr(self, 'ISY_temp_unit', None):
                self.ISY_temp_unit = new_unit
                if hasattr(self, 'messana_info') and isinstance(self.messana_info, dict):
                    self.messana_info['isy_temp_unit'] = new_unit
                for zone in self.zone.values():
                    zone.ISY_temp_unit = new_unit
                for mzone in self.macrozone.values():
                    mzone.ISY_temp_unit = new_unit
                for atu in self.atu.values():
                    atu.ISY_temp_unit = new_unit
                for bt in self.buffertank.values():
                    bt.ISY_temp_unit = new_unit
                for dhw in self.hotwater.values():
                    dhw.ISY_temp_unit = new_unit
                self.update_profile()

    def _profiles_match(self, current_profile, expected_profile) -> bool:
        if not isinstance(current_profile, dict) or not isinstance(expected_profile, dict):
            return False
        return all(
            current_profile.get(k, []) == expected_profile.get(k, [])
            for k in ("editors", "nodedefs", "linkdefs")
        )

    def _publish_profile(self, wait_response: bool = False) -> None:
        update_json_profile = getattr(self.poly, "updateJsonProfile", None)
        if not callable(update_json_profile):
            logging.info("[_publish_profile] updateJsonProfile is unavailable, falling back to updateProfile")
            if hasattr(self.poly, "updateProfile"):
                self.poly.updateProfile()
            return

        temp_unit = getattr(self, "ISY_temp_unit", self.TEMP_C)
        profile = build_profile_definition(temp_unit)

        current_profile_getter = getattr(self.poly, "getJsonProfile", None)
        if callable(current_profile_getter):
            try:
                current_profile = current_profile_getter({"waitResponse": False})
                if self._profiles_match(current_profile, profile):
                    logging.info("[_publish_profile] Profile already up to date, skipping publish")
                    return
            except TypeError:
                try:
                    current_profile = current_profile_getter()
                    if self._profiles_match(current_profile, profile):
                        logging.info("[_publish_profile] Profile already up to date, skipping publish")
                        return
                except Exception as err:
                    logging.warning(f"[_publish_profile] Unable to read existing profile: {err}")
            except Exception as err:
                logging.warning(f"[_publish_profile] Unable to read existing profile: {err}")

        try:
            logging.debug(f"[_publish_profile] Publishing profile: {json.dumps(profile, sort_keys=True, indent=2)}")
            update_json_profile(profile, {"waitResponse": wait_response})
            logging.info("[_publish_profile] Dynamic JSON profile published successfully")
            if hasattr(self.poly, "Notices") and hasattr(self.poly.Notices, "delete"):
                self.poly.Notices.delete("profile")
        except TypeError:
            update_json_profile(profile)
            logging.info("[_publish_profile] Dynamic JSON profile published successfully")
            if hasattr(self.poly, "Notices") and hasattr(self.poly.Notices, "delete"):
                self.poly.Notices.delete("profile")
        except Exception as err:
            logging.error(f"[_publish_profile] Profile publish failed: {err}")
            if hasattr(self.poly, "Notices") and hasattr(self.poly.Notices, "__setitem__"):
                self.poly.Notices["profile"] = f"Dynamic profile publish failed: {err}"

    def update_profile(self, command=None) -> None:
        """Update ISY profile dynamically or via static files."""
        self._publish_profile(wait_response=True)

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
                        time.sleep(0.2)
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
                    time.sleep(0.1)


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
        updated = False

        tmp = self.messana.get_status()
        logging.debug('System State {}'.format(tmp))
        if tmp is not None:
            self.node.setDriver('GV0', tmp, True, True)
            updated = True

        tmp = self.messana.get_setback_diff()
        logging.debug('Setback Offset {}'.format(tmp))
        if tmp is not None:
            if self.send_rel_temp_to_isy(tmp, 'GV1'):
                updated = True

        tmp = self.messana.get_setback()
        logging.debug('Setback Enabled {}'.format(tmp))
        if tmp is not None:
            self.node.setDriver('GV2', tmp, True, True)
            updated = True

        tmp = self.messana.get_energy_saving()
        logging.debug('Setback Enabled {}'.format(tmp))
        if tmp is not None:
            self.node.setDriver('GV12', tmp, True, True)
            updated = True

        if updated:
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
            if tmp is not None:
                self.node.setDriver('GV11', tmp, True, True)

            self.node.setDriver('ST', 1)
            self.node.setDriver('TIME', int(time.time()), True, True, 151)
        else:
            logging.warning('Messana System: No valid data received from API')
            self.node.setDriver('ST', 0)

    def updateISY_shortpoll(self):
        logging.debug('updateISY_shortpoll')
        self.heartbeat()
        updated = False

        tmp = self.messana.get_status()
        logging.debug('System State {}'.format(tmp))
        if tmp is not None:
            self.node.setDriver('GV0', tmp)
            updated = True

        tmp = self.messana.get_external_alarm()
        logging.debug('Alarm Status{}'.format(tmp))
        if tmp is not None:
            self.node.setDriver('GV11', tmp)
            updated = True

        if updated:
            self.node.setDriver('ST', 1)
            self.node.setDriver('TIME', int(time.time()), True, True, 151)
        else:
            logging.warning('Messana System: No valid data received from API')
            self.node.setDriver('ST', 0)


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
                ,'SETBACKOFFSET' : setSetbackOffset
                ,'PROFILE' : update_profile
                ,'UPDATEPROFILE' : update_profile
                }



if __name__ == "__main__":
    try:
        logging.info('Starting Messana Controller')
        polyglot = udi_interface.Interface([])
        polyglot.start(__version__)
        MessanaController(polyglot, 'system', 'system', 'Messana Radiant System')

        # Just sit and wait for events
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
        