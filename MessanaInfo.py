#!/usr/bin/env python3
import requests
#from subprocess import call
import json
import os
import time

try:
    import udi_interface
    logging = udi_interface.logging
    Custom = udi_interface.Custom

except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    #logging = logging.getlogging('testLOG')

#class MessanaInit(object):



class messanaInfo(object):
    def __init__(messana, IPaddress, messanaKey):
        messana.systemAPI = '/api/system'
        messana.RESPONSE_OK = '<Response [200]>'
        messana.RESPONSE_NO_SUPPORT = '<Response [400]>'
        messana.RESPONSE_NO_RESPONSE = '<Response [404]>'
        messana.RESPONSE_SERVER_ERROR = '<Response [500]>'
        messana.NaNlist= [-32768 , -3276.8 ]
        messana.IPaddress = IPaddress
        messana.apiKey = messanaKey
        messana.apiStr = 'apikey=' + messana.apiKey
        messana.IPstr ='http://'+ messana.IPaddress
 
    def GET_system_data(messana, mKey):
        GETstr = messana.IPstr +messana.systemAPI+'/'+ mKey + '?' + messana.apiStr
        logging.debug('GET_system_data: {} '.format(GETstr) )

        #logging.debug( GETStr)
        try:
            systemTemp = requests.get(GETstr)
            #logging.debug(str(systemTemp))
            if str(systemTemp) == messana.RESPONSE_OK:
                systemTemp = systemTemp.json()
                data = systemTemp[str(list(systemTemp.keys())[0])]
            else:
                logging.error('GETsystemData error {} {}'.format(mKey,str(systemTemp) ))
            if data in messana.NaNlist:
                return
            else:
                return(data) #No data for given keyword - remove from list

        except Exception as e:
            logging.error('System GET_system_data operation failed for {}: {}'.format(mKey, e))
            return



    def PUT_system_data(messana, mKey, value):
        mData = {}
        PUTstr = messana.IPstr + messana.systemAPI+'/'+ mKey
        mData = {'value':value, 'apikey': messana.apiKey}
        logging.debug('PUT_system_data :{} {}'.format(PUTstr, mData) )
        try:
            resp = requests.put(PUTstr, json=mData)
            return( str(resp) == messana.RESPONSE_OK)

        except Exception as e:
            logging.error('Error PUT_system_data {}: {}'.format(PUTstr, e))
            return
  
    def GET_node_data(messana, nodeNbr, mKey):
        #logging.debug('GETNodeData: ' + mNodeKey + ' ' + str(nodeNbr)+ ' ' + mKey)
        GETstr =messana.IPstr +'/api/'+messana.node_type+'/'+mKey+'/'+str(nodeNbr)+'?'+ messana.apiStr 
        logging.debug('GET_node_data: {} '.format(GETstr) )
        try:
            nTemp = requests.get(GETstr)
            if str(nTemp) == messana.RESPONSE_OK:
                nData = nTemp.json()
                data   = nData[str(list(nData.keys())[0])]
                if data in messana.NaNlist:
                    return
                else:
                    return(data)

            else:
                logging.error('GETNodeData: {} {} {}'.format(nodeNbr, mKey, str(nTemp)))
                return
        except Exception as e:
            logging.error ('Error GETNodeData:{} : {}'.format(GETstr, e))
            return

    def PUT_node_data(messana, nodeNbr, mKey, value):
        mData = {}
        PUTstr = messana.IPstr + +'/api/'+messana.nodeType+'/'+mKey+'/'+str(nodeNbr)
        mData = {'id':nodeNbr, 'value': value, 'apikey' : messana.apiKey }
        logging.debug('PUT_node_data :{} {}'.format(PUTstr, mData) )
        try:
            resp = requests.put(PUTstr, json=mData)
            if str(resp) == messana.RESPONSE_OK:
                return(True)
            else:
                return(False)
        except Exception as e:
            logging.error('Error PUT_node_data try/cartch {}:{}'.format(PUTstr, e))
            return(False)


###############################


    def update_name(self):
        logging.debug('update_name: atu:{}'.format(self.node_nbr ))
        temp = self.GET_node_data(self.node_nbr , 'name')
        if temp:
            self.name = temp

    def update_status(self):
        logging.debug('update_status {}'.format(self.node_nbr))    
        temp = self.GET_node_data(self.node_nbr , 'status')
        if temp:
            self.status = temp

    def set_status(self, state):
        if state in self.stateList:
            self.PUT_node_data(self.node_nbr ,'status', state )
            time.sleep(0.5)
            self.status = self.update_status()
            return(self.status)
        else:
            logging.error ('Wrong Status state passed ([0,1]: {}'.format(state))
            return(False)
          

    def update_air_temp(self):
        return(self.GET_node_data(self.node_nbr , 'airTemperature'))

    def update_setpoint(self):
        temp = self.GET_node_data(self.node_nbr , 'setpoint')
        if temp:
            self.setpint = temp



    def set_setpoint(self, setpoint):
        if self.PUT_node_data(self.node_nbr , 'setpoint'):
            time.sleep(0.5)
            self.update_setpoint()
            return(self.setpoint)
        else:
            return   

    def update_temp(self):
        return(self.GET_node_data(self.node_nbr , 'temperature'))




    def update_scheduleOn(self):
        temp =  self.GET_node_data(self.node_nbr , 'scheduleOn')
        if temp:
            self.schedule_on = temp


    def set_scheduleOn(self, state):
        if self.PUT_node_data(self.node_nbr , 'scheduleOn', state):
            time.sleep(0.5)
            self.update_scheduleOn()
            return(True)
        else:
            return(False)



    def update_thermal_status(self):
        return( self.GET_node_data(self.node_nbr , 'thermalStatus'))



    def update_humidity(self):
        return( self.GET_node_data(self.node_nbr , 'humidity'))


    def update_air_quality(self):
        val = self.GET_node_data(self.node_nbr , 'airQuality')
        if val not in self.NaNlist:
            return(val['category'])
        else:
            return


    def update_setpointCO2(self):
        return( self.GET_node_data(self.node_nbr , 'setpointCO2'))

    def set_setpointCO2(self):
        if self.PUT_node_data(self.node_nbr , 'setpointCO2'):
            time.sleep(0.5)
            self.update_setpointCO2()
            return(self.setpointCO2)
        else:
            return


    def update_dewpoint(self):
        return( self.GET_node_data(self.node_nbr , 'dewpoint'))
  

    def update_energy_saving(self):
        temp = self.GET_node_data(self.node_nbr , 'energySaving')
        if temp:
            self.energy_saving = temp
       



    def set_energy_saving(self, state):
        if state in self.stateList:
            self.PUT_node_data(self.node_nbr ,'energySaving', state )
            self.update_energy_saving()
            return(self.energy_saving)
        else:
            logging.error ('Wrong enerySaving state passed ([0,1]: {}'.format(state))
            return(False)

    def update_co2(self):
        return(self.GET_node_data(self.node_nbr , 'co2'))








 
    #pretty bad solution - just checking if a value can be extracted
    def checkMessanaConnection(messana):
        sysData = messana.GETSystemData('mApiVer') 
        return (sysData['statusOK'])
    


#