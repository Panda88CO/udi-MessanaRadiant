#!/usr/bin/env python3
import requests
#from subprocess import call
import json
import os


try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom

except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    #logging = logging.getlogging('testLOG')


from MessanaInfo import messana_control


class messana_system(messana_control):
    def __init__(self):
        super().__init__()
        logging.debug('Getting System Data')
        self.status = self.get_status()
        logging.debug('Getting Status: {}'.format(self.status ))
        self.messana_temp_unit = self.get_temp_unit()
        logging.debug('Getting Temp Unit: {}'.format(self.messana_temp_unit))
        self.nbr_zones = self.GET_system_data('zoneCount')
        logging.debug('Getting nbr zones: {}'.format(self.nbr_zones   ))
        self.nbr_atus = self.GET_system_data('atuCount')
        logging.debug('Getting nbr atu Units: {}'.format( self.nbr_atus ))
        self.nbr_buffer_tank = self.GET_system_data('bufferTankCount')
        logging.debug('Getting nbr buffertanl Units: {}'.format(self.nbr_buffer_tank   ))
        self.nbr_energy_source = self.GET_system_data('energySourceCount')
        logging.debug('Getting nbr energy source Units: {}'.format( self.nbr_energy_source   ))
        self.nbr_fancoil = self.GET_system_data('fancoilCount')
        logging.debug('Getting nbr fancoil Units: {}'.format(self.nbr_fancoil  ))
        self.nbr_HCgroup = self.GET_system_data('HCgroupCount')
        logging.debug('Getting nbr hot cold Units: {}'.format( self.nbr_HCgroup ))
        self.nbr_macrozone = self.GET_system_data('macroZoneCount')
        logging.debug('Getting nbr macon zones: {}'.format( self.nbr_macrozone  ))
        self.nbr_dhwater = self.GET_system_data('dhwCount')
        logging.debug('Getting nbr domestic hot water: {}'.format( self.nbr_dhwater  ))

        self.name = self.GET_system_data('name')
        logging.debug('Getting  system name: {}'.format(self.name ))


    ###############################
    #pretty bad solution - just checking if a value can be extracted
    '''
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
                return(None)
            else:
                return(data) #No data for given keyword - remove from list
        except Exception as e:
            logging.error('System GET_system_data operation failed for {}: {}'.format(mKey, e))
            return(None)


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
            return(None)
    '''
    def get_status(self):
        return(self.GET_system_data('status'))

    def set_status(self, status):
        return(self.PUT_system_data('status', status))

    def get_energy_saving(self):
        return(self.GET_system_data('energySaving'))

    def set_energy_saving(self, status):
        return(self.PUT_system_data('status', status))

    def get_setback(self):
        return(self.GET_system_data('setback'))

    def set_setback(self, status):
        return(self.PUT_system_data('setback', status))

    def get_setback_diff(self):
        return(self.GET_system_data('setbackDiff'))

    def set_setback_diff(self, diff):
        return(self.PUT_system_data('setbackDiff', diff))

    def get_external_alarm(self):
        return(self.GET_system_data('externalAlarm'))

