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

from Messana_Info import messana_control


class messana_node(messana_control):
    def __init__(self, messana_info, node_type, node_nbr):
        super().__init__(messana_info['ip_address'], messana_info['api_key'])
        #self.messana = messana_info
        self.type = node_type
        self.nbr = node_nbr
        logging.info('init Node {} {}:'.format(node_type, node_nbr ) )
        self.name = self.get_name()
        self.stateList = [0,1]
        self.messana_temp_unit = self.GET_system_data('tempUnit')
        #self.get_all()

    def __get_node_data(self, mKey):
        logging.debug('{} {} __get_node_data'.format(self.type, self.nbr ))
        return(self.GET_node_data(mKey, self.type, self.nbr))

    def __put_node_data(self, mKey, value):
        logging.debug('{} {} __put_node_data'.format(self.type, self.nbr ))
        return(self.PUT_node_data(mKey, value, self.type, self.nbr))

    def get_name(self):
        logging.debug('{} {} get_name'.format(self.type, self.nbr ))
        return(self.__get_node_data('name'))

    def get_status(self):
        logging.debug('{} {} get_status'.format(self.type, self.nbr))
        return(self.__get_node_data('status'))

    def set_status(self, state):
        logging.debug('{} {} - set_status {}'.format(self.type, self.nbr, state ))
        if self.__put_node_data('status', state ):
            time.sleep(0.5)
        return(self.get_status())

    def get_air_temp(self):
        logging.debug('{} {} - get_air_temp'.format(self.type, self.nbr))
        return(self.__get_node_data('airTemperature'))

    def get_setpoint(self):
        logging.debug('{} {} - get_setpoint'.format(self.type, self.nbr))
        return(self.__get_node_data('setpoint'))


    def set_setpoint(self, setpoint):
        logging.debug('{} {} set_setpoint: {}'.format(self.type, self.nbr, setpoint ))
        if self.__put_node_data('setpoint', setpoint):
            time.sleep(0.5)
        return(self.get_setpoint())


    def get_temp(self):
        logging.debug('{} {} - get_temp'.format(self.type, self.nbr))
        return(self.__get_node_data('temperature'))


    def get_scheduleOn(self):
        logging.debug('{} {} - get_scheduleOn'.format(self.type, self.nbr))
        return(self.__get_node_data('scheduleOn'))



    def set_scheduleOn(self, state):
        logging.debug('{} {} set_scheduleOn {}'.format(self.type, self.nbr, state ))
        if self.__put_node_data('scheduleOn', state):
            time.sleep(0.5)
        return(self.get_scheduleOn())



    def get_thermal_status(self):
        logging.debug('{} {} - get_thermal_status'.format(self.type, self.nbr))
        return( self.__get_node_data('thermalStatus'))



    def get_humidity(self):
        logging.debug('{} {} - get_humidity'.format(self.type, self.nbr))
        return(self.__get_node_data('humidity'))


    def get_air_quality(self):
        logging.debug('{} {} - get_air_quality'.format(self.type, self.nbr))
        val = self.__get_node_data('airQuality')
        logging.debug('Air quality;{}'.format(val))
        if val == self.RESPONSE_NO_SUPPORT or val == None:
            return(None)
        else:
            return(val)
        #if val not in self.messana.NaNlist:
        #    return(val['category'])
        #else:
        #    return None

    def get_setpointCO2(self):
        logging.debug('{} {} - get_setpointCO2'.format(self.type, self.nbr))
        return( self.__get_node_data('setpointCO2'))

    def set_setpointCO2(self, set_co2):
        logging.debug('{} {} set_setpointCO2: {}'.format(self.type, self.nbr, set_co2 ))
        if self.__put_node_data('setpointCO2', set_co2):
            time.sleep(0.5)
        return(self.get_setpointCO2())


    def get_dewpoint(self):
        logging.debug('{} {} - get_dewpoint'.format(self.type, self.nbr))
        return( self.__get_node_data( 'dewpoint'))


    def get_energy_saving(self):
        logging.debug('{} {} - get_energy_saving'.format(self.type, self.nbr))
        return(self.__get_node_data('energySaving'))

    

    def set_energy_saving(self, energy_save):
        logging.debug('{} {} set_setpointCO2: {}'.format(self.type, self.nbr, energy_save ))
        if self.__put_node_data('energySaving', energy_save ):
            time.sleep(0.5)
        return(self.get_energy_saving())

    def get_co2(self):
        logging.debug('{} {} - get_co2'.format(self.type, self.nbr))
        val = self.__get_node_data('co2')
        if val == self.RESPONSE_NO_SUPPORT or val == None:
            return(-1)
        else:
            return(val)
        #self.__get_node_data('co2')
        #return(self.__get_node_data('co2'))


    def get_alarmOn(self):
        logging.debug('{} {} -get_alarmOn'.format(self.type, self.nbr))
        alarm = self.__get_node_data('alarmOn')
        logging.debug('get_alarmOn: {}'.format(alarm))

        if alarm != 0:
            alarm_code = self.__get_node_data('alarms')
            logging.debug('alarmc codes: {}'.format(alarm_code))
            logging.info('Alarm set : {}'.format(alarm_code))
            if len(alarm_code) == 0:
                alarm = 0
        return(alarm)



    def get_antifreeze_setpoint(self):
        logging.debug('{} {} - get_antifreeze_setpoint'.format(self.type, self.nbr))
        return(self.__get_node_data('antifreezeSP'))

    def set_antifreeze_setpoint(self, af_sp):
        logging.debug('{} {} set_scheduleOn {}'.format(self.type, self.nbr, af_sp ))
        if self.__put_node_data('antifreezeSP', af_sp):
            time.sleep(0.5)
        return(self.get_antifreeze_setpoint())


    def get_flow_level(self):
        logging.debug('{} {} - get_flow_level'.format(self.type, self.nbr))
        return(self.__get_node_data('flowLevel'))
    
    def set_flow_level(self, flow_level):
        logging.debug('{} {} - set_flow_level {} '.format(self.type, self.nbr, flow_level))
        if self.__put_node_data('flowLevel', flow_level):
            time.sleep(0.5)
        return(self.get_flow_level())
    
    def get_HRV_status(self):
        logging.debug('{} {} - get_HRVstatus'.format(self.type, self.nbr))
        return(self.__get_node_data('hrvStatus'))
    
    def get_activate_HRV(self):
        logging.debug('{} {} - get_HRVstatus'.format(self.type, self.nbr))
        return(self.__get_node_data('hrvON'))

    def set_activate_HRV(self, hrv_en):
        logging.debug('{} {} - set_activate_HRV {} '.format(self.type, self.nbr, hrv_en))
        if self.__put_node_data('hrvON', hrv_en):
            time.sleep(0.5)
        return(self.get_activate_HRV())


    def get_humidification_status(self):
        logging.debug('{} {} - get_humidification_status'.format(self.type, self.nbr))
        return(self.__get_node_data('humidificationStatus'))
    
    def get_humidification_enable(self):
        logging.debug('{} {} - get_humidification_enable'.format(self.type, self.nbr))
        return(self.__get_node_data('humON'))

    def set_humidification_enable(self, hum_en):
        logging.debug('{} {} - set_humidification_enable {} '.format(self.type, self.nbr, hum_en))
        if self.__put_node_data('humON', hum_en):
            time.sleep(0.5)
        return(self.get_humidification_enable())

    def get_dehumidification_status(self):
        logging.debug('{} {} - get_dehumidification_status'.format(self.type, self.nbr))
        return(self.__get_node_data('dehumidificationStatus'))
    
    def get_dehumidification_enable(self):
        logging.debug('{} {} - get_dehumidification_enable'.format(self.type, self.nbr))
        return(self.__get_node_data('ntdON'))

    def set_dehumidification_enable(self, dehum_en):
        logging.debug('{} {} - set_dehumidification_enable {} '.format(self.type, self.nbr, dehum_en))
        if self.__put_node_data('ntdON', dehum_en):
            time.sleep(0.5)
        return(self.get_dehumidification_enable())
    

    def get_convection_status(self):
        logging.debug('{} {} - get_convection_status'.format(self.type, self.nbr))
        return(self.__get_node_data('integratioStatus'))
    

    def get_convection_enable(self):
        logging.debug('{} {} - get_convection_enable'.format(self.type, self.nbr))
        return(self.__get_node_data('intON'))

    def set_convection_enable(self, conv_en):
        logging.debug('{} {} - set_convection_enable {} '.format(self.type, self.nbr, conv_en))
        if self.__put_node_data('intON', conv_en):
            time.sleep(0.5)
        return(self.get_convection_enable())

    def get_buffertank_mode(self):
        logging.debug('{} {} - get_buffertank_mode'.format(self.type, self.nbr))
        return(self.__get_node_data('mode'))

    def set_buffertank_mode(self, mode):
        logging.debug('{} {} - set_buffertank_mode {} '.format(self.type, self.nbr, mode))
        if self.__put_node_data('mode', mode):
            time.sleep(0.5)
        return(self.get_buffertank_mode())

    def get_buffertank_temp_mode(self):
        logging.debug('{} {} - get_buffertank_temp_mode'.format(self.type, self.nbr))
        return(self.__get_node_data('tempMode'))

    def set_buffertank_temp_mode(self, temp_mode):
        logging.debug('{} {} - set_buffertank_temp_mode {} '.format(self.type, self.nbr, temp_mode))
        if self.__put_node_data('tempMode', temp_mode):
            time.sleep(0.5)
        return(self.get_buffertank_temp_mode())


    def get_adaptive_comf_status(self):
        logging.debug('{} {} - get_adaptive_comf_status'.format(self.type, self.nbr))
        return(self.__get_node_data('adaptiveComfort'))

    def set_adaptive_comf_status(self, temp_mode):
        logging.debug('{} {} - set_adaptive_comf_status {} '.format(self.type, self.nbr, temp_mode))
        if self.__put_node_data('adaptiveComfort', temp_mode):
            time.sleep(0.5)
        return(self.get_adaptive_comf_status())


    def get_hc_co_mode(self):
        logging.debug('{} {} - get_hc_co_mode'.format(self.type, self.nbr))
        return(self.__get_node_data('mode'))

    def set_hc_co_mode(self, temp_mode):
        logging.debug('{} {} - set_hc_co_mode {} '.format(self.type, self.nbr, temp_mode))
        if self.__put_node_data('mode', temp_mode):
            time.sleep(0.5)
        return(self.get_hc_co_mode())

    def get_hc_co_season_mode(self):
        logging.debug('{} {} - get_hc_co_season_mode'.format(self.type, self.nbr))
        return(self.__get_node_data('executiveSeason'))


    def get_fctype(self):
        logging.debug('{} {} - get_fc type'.format(self.type, self.nbr))
        return(self.__get_node_data('type'))


    def get_fancoil_heat_speed(self):
        logging.debug('{} {} - get_fancoil_heat_speed'.format(self.type, self.nbr))
        return(self.__get_node_data('heatingSpeed'))

    def set_fancoil_heat_speed(self, speed):
        logging.debug('{} {} -     def set_fancoil_heat_speed(self, temp_mode):{} '.format(self.type, self.nbr, speed))
        if self.__put_node_data('heatingSpeed', speed):
            time.sleep(0.5)
        return(self.get_fancoil_heat_speed())

    def get_fancoil_cool_speed(self):
        logging.debug('{} {} - get_fancoil_cool_speed'.format(self.type, self.nbr))
        return(self.__get_node_data('coolingSpeed'))

    def set_fancoil_cool_speed(self, speed):
        logging.debug('{} {} - set_fancoil_cool_speed {} '.format(self.type, self.nbr, speed))
        if self.__put_node_data('coolingSpeed', speed):
            time.sleep(0.5)
        return(self.get_fancoil_heat_speed())

    def get_energy_source_dhwStatus(self):
        logging.debug('{} {} - get_energy_source_dhwStatus'.format(self.type, self.nbr))
        return(self.__get_node_data('dhwStatus'))

    def get_energy_source_type(self):
        logging.debug('{} {} - get_energy_source_type'.format(self.type, self.nbr))
        return(self.__get_node_data('type'))

    def get_target_temp(self):
        logging.debug('{} {} - get_target_temp'.format(self.type, self.nbr))
        return(self.__get_node_data('targetTemperature'))
    
    def set_target_temp(self, speed):
        logging.debug('{} {} - set_target_temp {} '.format(self.type, self.nbr, speed))
        if self.__put_node_data('targetTemperature', speed):
            time.sleep(0.5)
        return(self.get_target_temp())