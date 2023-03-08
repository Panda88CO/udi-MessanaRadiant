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

#from Messana_Info import messana_control
from Messana_Node import messana_node
#messana, controller, primary, address, name, nodeType, nodeNbr, messana
class messana_hot_water(messana_node):
    def __init__(self, dhw_nbr, messana_info):
        super().__init__(messana_info, 'dhw', dhw_nbr)
        logging.info('init dwh:' )
        self.type = 'dhw'
        self.nbr = dhw_nbr
        self.name = self.get_name()
        self.stateList = [0,1]
        self.messana_temp_unit = self.GET_system_data('tempUnit')
        
        #self.get_all()

    
