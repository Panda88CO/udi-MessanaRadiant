#!/usr/bin/env python3
import requests
#from subprocess import call
import json
import os

from MessanaZone import messanaZone
try:
    import udi_interface
    logging = udi_interface.logging
    Custom = udi_interface.Custom

except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    #logging = logging.getlogging('testLOG')


from MessanaInfo import messana_info


class messanaSystem(messana_info):
    def __init__(self):
        super().__init__()
        #self.Sys = messana_info(IPaddress, messanaKey)
        self.status = self.get_status()
        self.temp_unit = self.GET_system_data('tempUnit')
        self.nbr_zones = self.GET_system_data('zoneCount')
        self.nbr_atus = self.GET_system_data('atuCount')
        self.nbr_buffer_tank = self.GET_system_data('bufferTankCount')
        self.nbr_energy_source = self.GET_system_data('energySourceCount')
        self.nbr_fancoil = self.GET_system_data('fancoilCount')
        self.nbr_HCgroup = self.GET_system_data('HCgroupCount')
        self.nbr_macrozone = self.GET_system_data('macroZoneCount')
        self.name = self.GET_system_data('name')

    def get_status(self):
        return(self.GET_system_data('status'))

    def set_status(self, status):
        return(self.PUT_system_data('status', status))

    def get_energySaving(self):
        return(self.GET_system_data('status'))

    def set_energySaving(self, status):
        return(self.PUT_system_data('status', status))

    def get_setback(self):
        return(self.GET_system_data('setback'))

    def set_setback(self, status):
        return(self.PUT_system_data('setback', status))

    def get_setback_diff(self):
        return(self.GET_system_data("setbackDiff"))

    def set_setback_diff(self, diff):
        return(self.PUT_system_data("setbackDiff", diff))
