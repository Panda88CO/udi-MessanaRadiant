#!/usr/bin/env python3

import time

from MessanaInfo import messanaInfo
from MessanaZone import messanaZone

try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)



#messana, controller, primary, address, name, nodeType, nodeNbr, messana
class udiMessanaZone(udi_interface.Node):
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

    def __init__(self, polyglot, primary, address, name, IPaddress, apiKey, zone_nbr):
        super().__init__(polyglot, primary, address, name)
        logging.info('init Messana Zones:' )
        #self.node_type = 'zone'
        self.parent = primary
		self.name = name
		self.address = address
		self.poly = polyglot
        self.IPaddress = IPaddress
        self.apiKey = apiKey
        self.zone_nbr = zone_nbr

        polyglot.subscribe(polyglot.START, self.start, self.address)
        polyglot.subscribe(polyglot.STOP, self.stop)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)
        self.n_queue = []

        polyglot.ready()
        self.poly.addNode(self)
        self.wait_for_node_done()
        self.node = self.poly.getNode(address)

    def node_queue(self, data):
        self.n_queue.append(data['address'])

    def wait_for_node_done(self):
        while len(self.n_queue) == 0:
            time.sleep(0.1)
        self.n_queue.pop()
     
    def start(self):
        logging.info('Start - adding zone {}'.format(self.zone_nbr))
        self.zone = messanaZone(self.IPaddress, self.apiKey, self.zone_nbr)


