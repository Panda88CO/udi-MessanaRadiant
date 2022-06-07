#!/usr/bin/env python3
import time

try:
    import udi_interface
    logging = udi_interface.logging
    Custom = udi_interface.Custom

except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    #logging = logging.getlogging('testLOG')

#from subprocess import call
from MessanaInfo import messanaInfo

#messana, controller, primary, address, name, nodeType, nodeNbr, messana
class messanaZone(messanaInfo):
    def __init__(self, messanaIP, messanaKey, zoneNbr):
        super().__init__(messanaIP, messanaKey)
        logging.info('init Zone:' )
        
        self.node_type = 'zone'
        #self.IPaddress = IPaddress
        #self.apiKey = messanaKey
        self.zone_nbr = zoneNbr
        self.stateList = [0,1]

        self.update_all()




    def update_active(self):
        self.temp = self.update_temp()
        self.air_temp = self.update_air_temp()
        self.humidity = self.update_humidity()
        self.air_quality = self.update_air_quality()
        self.status = self.update_status()
        self.co2 = self.update_co2()
        self.thermalStatus = self.update_thermal_status()


    def update_all(self):
        self.update_active()
        self.update_name()
        self.update_setpointCO2
        self.setpoint = self.update_setpoint
        self.energy_saving = self.update_energy_saving()
        self.scheduleOn = self.update_scheduleOn()
        self.status = self.update_status()



    def update_name(self):
         temp = self.GET_node_data(self.zone_nbr, 'name')
         if temp:
             self.name = temp

    def update_energy_saving(self):
        temp = self.GET_node_data(self.zone_nbr, 'energySaving')
        if temp:
            self.energy_saving = temp


    def update_scheduleOn(self):
        temp =  self.GET_node_data(self.zone_nbr, 'scheduleOn')
        if temp:
            self.scheduleOn = temp


    def update_scheduleOn(self):
        temp = self.GET_node_data(self.zone_nbr, 'scheduleOn'):
        if temp:
            self.scheduleOn = temp



    def set_scheduleOn(self, state):
        if self.PUT_node_data(self.zone_nbr, 'scheduleOn', state):
            time.sleep(0.5)
            self.scheduleOn = self.update_scheduleOn()
            return(True)
        else:
            return(False)



    def update_thermal_status(self):
        return( self.GET_node_data(self.zone_nbr, 'thermalStatus'))

    def update_temp(self):
        return(self.GET_node_data(self.zone_nbr, 'temperature'))
  

    def update_air_temp(self):
        return(self.GET_node_data(self.zone_nbr, 'airTemperature'))

    def update_setpoint(self):
        return(self.GET_node_data(self.zone_nbr, 'setpoint'))

    def set_setpoint(self, setpoint):
        if self.PUT_node_data(self.zone_nbr, 'setpoint'):
            time.sleep(0.5)
            self.setpoint = self.update_setpoint()
            return(self.setpoint)
        else:
            return




    def update_humidity(self):
        return( self.GET_node_data(self.zone_nbr, 'humidity'))


    def update_air_quality(self):
        val = self.GET_node_data(self.zone_nbr, 'airQuality')
        if val not in self.NaNlist:
            return(val['category'])
        else:
            return


    def update_setpointCO2(self):
        return( self.GET_node_data(self.zone_nbr, 'setpointCO2'))

    def set_setpointCO2(self):
        if self.PUT_node_data(self.zone_nbr, 'setpointCO2'):
            time.sleep(0.5)
            self.setpointCO2 = self.update_setpointCO2()
            return(self.setpointCO2)
        else:
            return

    def update_status(self):
        logging.debug('update_status {}'.format(zone_nbr))    
        return( self.GET_node_data(self.zone_nbr, 'status'))

    def set_status(self, state):
        if state in self.stateList:
            self.PUT_node_data(self.zone_nbr,'status', state )
            time.sleep(0.5)
            self.status = self.update_status()
            return(self.status)
        else:
            logging.error ('Wrong Status state passed ([0,1]: {}'.format(state))
            return(False)
          
    def update_dewpoint(self):
        return( self.GET_node_data(self.zone_nbr, 'dewpoint'))
  
    def update_energy_saving(self):
        return( self.GET_node_data(self.zone_nbr, 'energySaving'))

    def set_energy_save(self, state):
        if state in self.stateList:
            self.PUT_node_data(self.zone_nbr,'energySaving', state )
            self.energy_saving = self.update_energy_saving()
            return(self.energy_saving)
        else:
            logging.error ('Wrong enerySaving state passed ([0,1]: {}'.format(state))
            return(False)

    def update_co2(self):
        return(self.GET_node_data(self.zone_nbr, 'co2'))