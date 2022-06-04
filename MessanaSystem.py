#!/usr/bin/env python3
import requests
#from subprocess import call
import json
import os
try:
    import udi_interface
    logging = udi_interface.logging
    Custom = udi_interface.Custom

except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    #logging = logging.getlogging('testLOG')


from MessanaInfo import messanaInfo

class messanaSystem(messanaInfo):
    def __init__ (messana, IPaddress, apiKey):
        super().__init__(IPaddress, apiKey)
        messana.IPaddress = IPaddress
        messana.apiKey = apiKey
        messana.nbrZones = messana.GETsystemData('zoneCount')
        
        #messana.nbrZones = messana.Zones.nbrZones
