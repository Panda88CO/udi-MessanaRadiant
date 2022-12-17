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



class messana_system(object):
    def __init__(self, ip_address, api_key ) :
        self.systemAPI = '/api/system'
        self.RESPONSE_OK = '<Response [200]>'
        self.RESPONSE_NO_SUPPORT = '<Response [400]>'
        self.RESPONSE_NO_RESPONSE = '<Response [404]>'
        self.RESPONSE_SERVER_ERROR = '<Response [500]>'
        self.NaNlist= [-32768 , -3276.8 ]
        self.IPaddress = ''
        self.Key = ''
        self.apiStr = ''
        self.IPstr =''        
        self.IPaddress = ip_address
        self.Key = api_key
        self.apiStr = 'apikey=' + self.Key
        self.IPstr ='http://'+ self.IPaddress

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

    ###############################
    #pretty bad solution - just checking if a value can be extracted
    def connected(self):
        sysData = self.GET_system_data('mApiVer') 
        return (sysData['statusOK'])
    



    def get_data(self,apiKey):
        logging.debug('get_name {}}: {}'.format(self.node_type, self.node_nbr ))
        temp = self.GET_node_data(self.node_nbr , apiKey)
        if temp:
            return(temp)
        else:
            return(None)


    def GET_system_data(self, mKey):
        GETstr = self.IPstr +self.systemAPI+'/'+ mKey + '?' + self.apiStr
        logging.debug('GET_system_data: {}'.format(mKey))

        #logging.debug( GETStr)
        try:
            systemTemp = requests.get(GETstr)
            #logging.debug(str(systemTemp))
            if str(systemTemp) == self.RESPONSE_OK:
                systemTemp = systemTemp.json()
                data = systemTemp[str(list(systemTemp.keys())[0])]
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
  



    def GET_node_data(self, mKey):
        #logging.debug('GETNodeData: ' + mNodeKey + ' ' + str(nodeNbr)+ ' ' + mKey)
        GETstr =self.IPstr +'/api/'+ self.node_type+'/'+mKey+'/'+str(self.node_nbr)+'?'+ self.apiStr
        logging.debug('GET_node_data: {}-{}-{} '.format(node_type, node_nbr, mKey ))
        try:
            nTemp = requests.get(GETstr)
            if str(nTemp) == self.RESPONSE_OK:
                nData = nTemp.json()
                data   = nData[str(list(nData.keys())[0])]
                if data in self.NaNlist:
                    return(None)
                else:
                    return(data)

            else:
                logging.error('GET_node_data: {} {} {}'.format(node_nbr, mKey, str(nTemp)))
                return(None)
        except Exception as e:
            logging.error ('Error GET_node_data:{} : {}'.format(GETstr, e))
            return(None)


    def PUT_node_data(self, mKey, value):
        mData = {}
        PUTstr = self.IPstr + +'/api/'+ self.node_type +'/'+mKey+'/'+str(self.node_nbr)
        mData = {'id':self.node_nbr, 'value': value, 'apikey' : self.apiKey }
        logging.debug('PUT_node_data :{} {}'.format(PUTstr, mData) )
        try:
            resp = requests.put(PUTstr, json=mData)
            logging.debug('PUT_node_data  respomse:{} {}'.format(PUTstr, resp) )
            return(str(resp) == self.RESPONSE_OK)

        except Exception as e:
            logging.error('Error PUT_node_data try/cartch {}:{}'.format(PUTstr, e))
            return(False)


            

class zone(mess_node):
    def __init__(self, zone_nbr):
        super().__init__()
        logging.info('init Zone:' )
        self.node_type = 'zone'
        self.node_nbr = zone_nbr
        self.stateList = [0,1]

    def get_name(self):
        logging.debug('get_name {}: {}'.format(self.node_type, self.node_nbr ))
        return(self.GET_node_data('name'))

    def get_status(self):
        logging.debug('get_status {}:  {}'.format(self.node_type, self.node_nbr))    
        return(self.GET_node_data('status'))


    def set_status(self, state):
        if state in self.stateList:
            self.PUT_node_data('status', state )
            time.sleep(0.5)

            return(self.get_status())
        else:
            logging.error ('Wrong Status state passed ([0,1]: {}'.format(state))
            return(False)
          



 



#