#!/usr/bin/env python3

import time
import re
#from MessanaInfo import messana_info
from MessanaZone import messana_zone

try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)



#messana, controller, primary, address, name, nodeType, nodeNbr, messana
class udi_messana_zone(udi_interface.Node):

    id = 'meszone'  
    '''
       drivers = [
            'GV0' = DoorState
            'GV1' = Batery
            'GV8' = Online
            ]
    ''' 

    drivers = [
            {'driver': 'GV0', 'value': 99, 'uom': 25},
            {'driver': 'GV1', 'value': 99, 'uom': 25},
            {'driver': 'GV8', 'value': 0, 'uom': 25},
            {'driver': 'ST', 'value': 0, 'uom': 25},
            ]

    def __init__(self, polyglot, primary, zone_nbr):
        super().__init__(polyglot)
        logging.info('init Messana Zone {}:'.format(zone_nbr) )
        #self.node_type = 'zone'
        self.parent = primary
        #self.messana = system
        #self.zone_nbr = zone_nbr

        self.zone = messana_zone(zone_nbr)
        tmp_name = self.zone.name
        self.address = self.getValidAddress(tmp_name)
        self.name = self.getValidName(tmp_name)
        self.poly = polyglot
 

        
        self.n_queue = []
        polyglot.subscribe(polyglot.START, self.start, self.address)
        polyglot.subscribe(polyglot.STOP, self.stop)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)
        

        polyglot.ready()
        self.poly.addNode(self)
        self.wait_for_node_done()
        self.node = self.poly.getNode(self.address)

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


    def start(self):
        logging.info('Start - adding zone {}'.format(self.zone_nbr))
        self.zone = messana_zone( self.zone_nbr)


