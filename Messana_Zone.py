#!/usr/bin/env python3
import time
import os

try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    if (os.path.exists('./debug1.log')):
        os.remove('./debug1.log')
    import logging
    import sys
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] [%(threadName)s] %(message)s",
    handlers=[
        logging.FileHandler("debug1.log"),
        logging.StreamHandler(sys.stdout) ]
    )

#from MessanaInfo import messana_control

from Messana_Node import messana_node
#messana, controller, primary, address, name, nodeType, nodeNbr, messana
class messana_zone(messana_node):
    def __init__(self, zone_nbr, messana_info):
        super().__init__(messana_info, 'zone', zone_nbr)
        logging.info('init Zone:' )
        self.type = 'zone'
        self.nbr = zone_nbr
        self.name = self.get_name()
        self.messana_temp_unit = self.GET_system_data('tempUnit')
        #self.get_all()

    
