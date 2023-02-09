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
        self.mTemp_unit = self.GET_system_data('tempUnit')

        self.temp_unit = self.GET_system_data('status')
        self.temp_unit = self.GET_system_data('tempUnit')
        self.nbr_zones = self.GET_system_data('zoneCount')
        self.nbr_atus = self.GET_system_data('atuCount')
        self.nbr_buffer_tank = self.GET_system_data('bufferTankCount')
        self.nbr_energy_source = self.GET_system_data('energySourceCount')
        self.nbr_fancoil = self.GET_system_data('fancoilCount')
        self.nbr_HCgroup = self.GET_system_data('HCgroupCount')
        self.nbr_macrozone = self.GET_system_data('macroZoneCount')
        self.name = self.GET_system_data('name')




    def GET_system_data(self, mKey):
        logging.debug('GET_system_data: {}'.format(mKey))
        GETstr = self.IPstr +self.systemAPI+'/'+ mKey + '?' + self.apiStr
        logging.debug('GET_system_data: {}'.format(GETstr))

        #logging.debug( GETStr)
        try:
            systemTemp = requests.get(GETstr)
            #logging.debug(str(systemTemp))
            if str(systemTemp) == self.RESPONSE_OK:
                systemTemp = systemTemp.json()
                data = systemTemp[str(list(systemTemp.keys())[0])]
                logging.debug('GET_system_data - data: {}'.format(data))
            else:
                logging.error('GET_system_data error {} {}'.format(mKey, str(systemTemp)))
            if data in self.NaNlist:
                return (None)
            else:
                return(data) #No data for given keyword - remove from list
        except Exception as e:
            logging.error('System GET_system_data operation failed for {}: {}'.format(mKey, e))
            return



    def PUT_system_data(self, mKey, value):
        mData = {}
        PUTstr = self.IPstr + self.systemAPI+'/'+ mKey
        mData = {'value':value, 'apikey': self.apiStr}
        logging.debug('PUT_system_data :{} {}'.format(PUTstr, value) )
        try:
            resp = requests.put(PUTstr, json=mData)
            return( str(resp) == self.RESPONSE_OK)

        except Exception as e:
            logging.error('Error PUT_system_data {}: {}'.format(PUTstr, e))
            return
  



    def GET_node_data(self, mKey, node_type, node_nbr):
        logging.debug('GETNodeData: ' + mKey + ' ' + str(node_nbr)+ ' ' + mKey)
        GETstr = self.IPstr +'/api/'+ node_type+'/'+mKey+'/'+str(node_nbr)+'?'+ self.apiStr
        logging.debug('GET_node_data: {} '.format(GETstr))
        try:
            nTemp = requests.get(GETstr)
            if str(nTemp) == self.RESPONSE_OK:
                nData = nTemp.json()
                data   = nData[str(list(nData.keys())[0])]
                logging.debug('GET_node_data node {} - data: {}'.format(node_type, data))
                if data in self.NaNlist or data == self.RESPONSE_NO_SUPPORT:
                    return(None)
                else:
                    return(data)
            else:
                logging.info('GET_node_data: {} {} {}'.format(node_nbr, mKey, str(nTemp)))
                return(None)
        except Exception as e:
            logging.error ('Error GET_node_data:{} : {}'.format(GETstr, e))
            return(None)


    def PUT_node_data(self, mKey, value, node_type, node_nbr):
        mData = {}
        PUTstr = self.IPstr +'/api/'+ node_type +'/'+mKey+'/'+str(node_nbr)
        mData = {'id':node_nbr, 'value': value, 'apikey' : self.apiKey }
        logging.debug('PUT_node_data :{} {}'.format(PUTstr, mData) )
        try:
            resp = requests.put(PUTstr, json=mData)
            logging.debug('PUT_node_data  respomse:{} {}'.format(PUTstr, resp) )
            return(str(resp) == self.RESPONSE_OK)

        except Exception as e:
            logging.error('Error PUT_node_data try/cartch {}:{}'.format(PUTstr, e))
            return(False)


    def get_temp_unit(self):
        return(self.GET_system_data('tempUnit'))

    ###############################
    #pretty bad solution - just checking if a value can be extracted
    def system_connected(self):
        #sysData = self.GET_system_data('apiVersion')
        GETstr = self.IPstr +self.systemAPI+'/'+ 'apiVersion' + '?' + self.apiStr
        systemTemp = requests.get(GETstr)
        logging.debug('sysdata: {}'.format(systemTemp))
        return ( str(systemTemp) == self.RESPONSE_OK)
    