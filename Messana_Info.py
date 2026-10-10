#!/usr/bin/env python3
import requests
#from subprocess import call
import json
import os
import time

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

#class MessanaInit(object):



class messana_control(object):
    def __init__(self, ip_address, api_key ):
        self.systemAPI = '/api/system'
        self.RESPONSE_OK = '<Response [200]>'
        self.RESPONSE_NO_SUPPORT = '<Response [400]>'
        self.RESPONSE_NO_RESPONSE = '<Response [404]>'
        self.RESPONSE_SERVER_ERROR = '<Response [500]>'
        self.NaNlist= [-32768 , -3276.8 ]
        self.IPaddress = ip_address
        self.apiKey = api_key
        self.apiStr = 'apikey=' + self.apiKey
        self.IPstr ='http://'+ self.IPaddress
        self.timeout = 10
        self.mTemp_unit = self.GET_system_data('tempUnit')

    def _extract_value(self, data_dict):
        if not isinstance(data_dict, dict) or not data_dict:
            return None
        # Prioritize standard property keys (especially 'value' for multi-key responses like airQuality)
        for key in ('value', 'status', 'count', 'name', 'content', 'apiVersion', 'mode'):
            if key in data_dict:
                return data_dict[key]
        return data_dict[str(list(data_dict.keys())[0])]

    def GET_system_data(self, mKey):
        logging.debug('GET_system_data: {}'.format(mKey))
        GETstr = self.IPstr + self.systemAPI + '/' + mKey + '?' + self.apiStr
        try:
            systemTemp = requests.get(GETstr, timeout=self.timeout)
            is_ok = (hasattr(systemTemp, 'status_code') and systemTemp.status_code == 200) or str(systemTemp) == self.RESPONSE_OK
            if is_ok:
                systemJson = systemTemp.json()
                data = self._extract_value(systemJson)
                logging.debug('GET_system_data - data: {}'.format(data))
                if data in self.NaNlist:
                    return None
                else:
                    return data
            else:
                logging.error('GET_system_data error {} {}'.format(mKey, str(systemTemp)))
                return None
        except Exception as e:
            logging.error('System GET_system_data operation failed for {}: {}'.format(mKey, e))
            return None

    def PUT_system_data(self, mKey, value):
        PUTstr = self.IPstr + self.systemAPI + '/' + mKey + '?' + self.apiStr
        mData = {'value': value}
        logging.debug('PUT_system_data : {} {} {}'.format(PUTstr, mData, value))
        try:
            resp = requests.put(PUTstr, json=mData, timeout=self.timeout)
            return (hasattr(resp, 'status_code') and resp.status_code == 200) or str(resp) == self.RESPONSE_OK
        except Exception as e:
            logging.error('Error PUT_system_data {} {}: {}'.format(PUTstr, mData, e))
            return False

    def GET_node_data(self, mKey, node_type, node_nbr):
        logging.debug('GETNodeData: {}, type {},node nbr {}'.format(mKey, node_type, node_nbr))
        GETstr = self.IPstr + '/api/' + node_type + '/' + mKey + '/' + str(node_nbr) + '?' + self.apiStr
        try:
            nTemp = requests.get(GETstr, timeout=self.timeout)
            logging.debug('nTemp = {}'.format(nTemp))
            is_ok = (hasattr(nTemp, 'status_code') and nTemp.status_code == 200) or str(nTemp) == self.RESPONSE_OK
            if is_ok:
                nJson = nTemp.json()
                logging.debug('nData : {}'.format(nJson))
                data = self._extract_value(nJson)
                logging.debug('GET_node_data node {} - data: {}'.format(node_type, data))
                if data in self.NaNlist or data == self.RESPONSE_NO_SUPPORT:
                    return None
                else:
                    return data
            else:
                logging.info('GET_node_data: {} {} {}'.format(node_nbr, mKey, str(nTemp)))
                return None
        except Exception as e:
            logging.error('Error GET_node_data:{} : {}'.format(GETstr, e))
            return None

    def PUT_node_data(self, mKey, value, node_type, node_nbr):
        PUTstr = self.IPstr + '/api/' + node_type + '/' + mKey + '?' + self.apiStr
        mData = {'id': node_nbr, 'value': value}
        logging.debug('PUT_node_data :{} {}'.format(PUTstr, mData))
        try:
            resp = requests.put(PUTstr, json=mData, timeout=self.timeout)
            logging.debug('PUT_node_data response:{} {}'.format(PUTstr, resp))
            return (hasattr(resp, 'status_code') and resp.status_code == 200) or str(resp) == self.RESPONSE_OK
        except Exception as e:
            logging.error('Error PUT_node_data exception {}: {}'.format(PUTstr, e))
            return False

    def get_temp_unit(self):
        return(self.GET_system_data('tempUnit'))

    def system_connected(self):
        GETstr = self.IPstr + self.systemAPI + '/' + 'apiVersion' + '?' + self.apiStr
        try:
            systemTemp = requests.get(GETstr, timeout=self.timeout)
            logging.debug('sysdata: {}'.format(systemTemp))
            return (hasattr(systemTemp, 'status_code') and systemTemp.status_code == 200) or str(systemTemp) == self.RESPONSE_OK
        except Exception as e:
            logging.error('Error system_connected: {}'.format(e))
            return False
    