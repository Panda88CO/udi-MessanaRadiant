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
class messana_atu(messana_node):
    def __init__(self, atu_nbr, messana_info):
        super().__init__(messana_info, 'atu', atu_nbr)
        logging.info('init ATUs:' )
        self.type = 'atu'
        self.nbr = atu_nbr
        self.name = self.get_name()
        logging.debug('ATU node name {}'.format(self.name))
        self.stateList = [0,1]
        self.messana_temp_unit = self.GET_system_data('tempUnit')
