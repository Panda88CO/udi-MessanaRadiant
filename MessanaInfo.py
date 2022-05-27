#!/usr/bin/env python3
import requests
#from subprocess import call
import json
import os 
import polyinterface
LOGGER = polyinterface.LOGGER


class messanaInfo:
    def __init__ (self, mIPaddress, mAPIkey, mISYcontrollerName):
        # Note all xxIDs must be lower case without special characters (ISY requirement)
        self.systemID = mISYcontrollerName
        self.zoneID = 'zones'
        self.macrozoneID = 'macrozones'
        self.atuID = 'atus'
        self.dhwID = 'domhws'
        self.fcID = 'fancoils'
        self.energySourceID =  'energysys'
        self.HotColdcoID = 'hcco'
        self.bufferTankID = 'buftanks'
        self.supportedNodeList = [
                             self.zoneID
                            ,self.macrozoneID
                            ,self.atuID
                            ,self.dhwID
                            ,self.fcID
                            ,self.energySourceID
                            ,self.HotColdcoID 
                            ,self.bufferTankID
                            ] 
        self.mSystem = { self.systemID: {  'ISYnode':{ 'nlsICON' :'Thermostat'
                                                ,'sends'   : ['DON', 'DOF']
                                                ,'accepts' : {'UPDATE'         : {   'ISYtext' :'Update System Data'
                                                                                    ,'ISYeditor' : None} 
                                                             ,'SET_STATUS'     : {   'ISYtext' :'System Status'
                                                                                    ,'ISYeditor' : 'mStatus'}
                                                             ,'SET_ENERGYSAVE' : {   'ISYtext' :'Energy Save'
                                                                                    ,'ISYeditor' : 'mEnergySaving'}
                                                             ,'SET_SETBACK'    : {   'ISYtext' :'Setback'
                                                                                    ,'ISYeditor' : 'mSetback' }
                                                            }
                                                }
                                    ,'KeyInfo' : {
                                         'mName':{
                                             'GETstr': '/api/system/name/'
                                            ,'PUTstr': '/api/system/name/'
                                            ,'Active': None 
                                            ,'ISYeditor':{   
                                                     'ISYuom':None
                                                    ,'ISYmin':None
                                                    ,'ISYmax':None
                                                    ,'ISYsubset':None
                                                    ,'ISYstep':None
                                                    ,'ISYprec':None }
                                            , 'ISYnls': None  
                                            }   
                                        ,'mApiVer':{
                                             'GETstr' :'/api/system/apiVersion/'
                                            ,'PUTstr': None 
                                            ,'Active': None 
                                            ,'ISYeditor':{   
                                                     'ISYuom':None
                                                    ,'ISYmin':None
                                                    ,'ISYmax':None
                                                    ,'ISYsubset':None
                                                    ,'ISYstep':None
                                                    ,'ISYprec':None }
                                            , 'ISYnls': None               
                                            }                                           
                                        ,'mStatus': {
                                             'GETstr' : '/api/system/status/'
                                            ,'PUTstr' : '/api/system/status/'
                                            ,'Active' : None
                                            ,'ISYeditor':{   
                                                     'ISYuom': 25
                                                    ,'ISYmin':None
                                                    ,'ISYmax':None
                                                    ,'ISYsubset': '0-1'
                                                    ,'ISYstep':None
                                                    ,'ISYprec':None }
                                            ,'ISYnls': {    
                                                     'nlsTEXT' : 'System state'
                                                    ,'nlsValues' : { 0:'Off', 1:'On' }
                                                   }
                                                 }
                                        ,'mZoneCount':{
                                             'GETstr':'/api/system/zoneCount/'
                                            ,'PUTstr': None 
                                            ,'Active': None                                      
                                            ,'ISYeditor':{   
                                                     'ISYuom': 112
                                                    ,'ISYmin': 0 
                                                    ,'ISYmax': 32
                                                    ,'ISYsubset':None
                                                    ,'ISYstep': 1
                                                    ,'ISYprec': 0}
                                            ,'ISYnls': {    
                                                     'nlsTEXT' : '# of Zones' 
                                                    ,'nlsValues' : None
                                                    }
                                                }                                         
                                        ,'mATUcount':{
                                             'GETstr':'/api/system/atuCount/'
                                            ,'PUTstr': None 
                                            ,'Active': None                               
                                            ,'ISYeditor':{
                                                     'ISYuom': 112
                                                    ,'ISYmin': 0 
                                                    ,'ISYmax': 8
                                                    ,'ISYsubset':None
                                                    ,'ISYstep': 1
                                                    ,'ISYprec': 0}
                                            ,'ISYnls': {    
                                                     'nlsTEXT' : '# of ATU' 
                                                    ,'nlsValues' : None
                                                    }
                                                }
                                        ,'mDHWcount': {
                                             'GETstr':'/api/system/dhwCount/'
                                            ,'PUTstr': None 
                                            ,'Active': None                                     
                                            ,'ISYeditor':{   
                                                     'ISYuom': 112
                                                    ,'ISYmin': 0 
                                                    ,'ISYmax': 8
                                                    ,'ISYsubset':None
                                                    ,'ISYstep': 1
                                                    ,'ISYprec': 0}
                                            ,'ISYnls': {    
                                                     'nlsTEXT' : '# of Hot Water' 
                                                    ,'nlsValues' :None
                                                    }
                                                }
                                        ,'mMacrozoneCount': {
                                             'GETstr':'/api/system/macrozoneCount/'
                                            ,'PUTstr': None 
                                            ,'Active': None                                        
                                            ,'ISYeditor':{   
                                                     'ISYuom': 112
                                                    ,'ISYmin': 0 
                                                    ,'ISYmax': 16
                                                    ,'ISYsubset':None
                                                    ,'ISYstep': 1
                                                    ,'ISYprec': 0}
                                            ,'ISYnls': {    
                                                     'nlsTEXT' : '# of MacroZones (all=1)' 
                                                    ,'nlsValues' : None 
                                                    }
                                                }                                        
                                        ,'mFanCoilCount': {
                                            'GETstr':'/api/system/fancoilCount/'
                                            ,'PUTstr': None 
                                            ,'Active': None                                      
                                            ,'ISYeditor':{   
                                                     'ISYuom': 112
                                                    ,'ISYmin': 0 
                                                    ,'ISYmax': 16
                                                    ,'ISYsubset':None
                                                    ,'ISYstep': 1
                                                    ,'ISYprec': 0}
                                            ,'ISYnls': {    
                                                     'nlsTEXT' : '# of Fan Coils' 
                                                    ,'nlsValues' : None
                                                    }
                                                }                                          
                                        ,'mEnergySourceCount':{
                                             'GETstr':'/api/system/energySourceCount/'
                                            ,'PUTstr': None 
                                            ,'Active': None                                       
                                            ,'ISYeditor':{   
                                                     'ISYuom': 112
                                                    ,'ISYmin': 0 
                                                    ,'ISYmax': 16
                                                    ,'ISYsubset':None
                                                    ,'ISYstep': 1
                                                    ,'ISYprec': 0}
                                            ,'ISYnls': {    
                                                     'nlsTEXT' : '# of Energy Sources' 
                                                    ,'nlsValues' :  None 
                                                    }
                                                }                                          
                                        ,'mhc_coCount':{
                                             'GETstr':'/api/system/HCgroupCount/'
                                            ,'PUTstr': None 
                                            ,'Active': None                                       
                                            ,'ISYeditor':{   
                                                     'ISYuom': 112
                                                    ,'ISYmin': 0 
                                                    ,'ISYmax': 16
                                                    ,'ISYsubset':None
                                                    ,'ISYstep': 1
                                                    ,'ISYprec': 0}
                                            ,'ISYnls': {    
                                                     'nlsTEXT' : '# of Hot Cold ' 
                                                    ,'nlsValues' :  None 
                                                     }
                                                }                                          
                                        ,'mBufTankCount':{
                                             'GETstr':'/api/system/bufferTankCount/'
                                            ,'PUTstr': None 
                                            ,'Active': None                                  
                                            ,'ISYeditor':{   
                                                     'ISYuom': 112
                                                    ,'ISYmin': 0 
                                                    ,'ISYmax': 16
                                                    ,'ISYsubset':None
                                                    ,'ISYstep': 1
                                                    ,'ISYprec': 0}
                                            ,'ISYnls': {    
                                                     'nlsTEXT' : '# of Buffer Tanks' 
                                                    ,'nlsValues' : None
                                                        }
                                                }                                                                                                                           
                                        ,'mUnitTemp':{
                                             'GETstr' : '/api/system/tempUnit/'
                                            ,'PUTstr' : None
                                            ,'Active' : None
                                            ,'ISYeditor':{   
                                                     'ISYuom': 25
                                                    ,'ISYmin':None
                                                    ,'ISYmax':None
                                                    ,'ISYsubset':'0-1'
                                                    ,'ISYstep':None
                                                    ,'ISYprec':None }
                                            ,'ISYnls': {    
                                                    'nlsTEXT' : 'Temp Unit' 
                                                    ,'nlsValues' : {0:'Celcius', 1:'Farenheit'}
                                                        }
                                                }                                        
                                        ,'mEnergySaving':{
                                             'GETstr' : '/api/system/energySaving/'
                                            ,'PUTstr' : '/api/system/energySaving/'
                                            ,'Active' : None
                                            ,'ISYeditor':{   
                                                     'ISYuom': 25
                                                    ,'ISYmin':None
                                                    ,'ISYmax':None
                                                    ,'ISYsubset': '0-1'
                                                    ,'ISYstep':None
                                                    ,'ISYprec':None }
                                            ,'ISYnls': {    
                                                     'nlsTEXT' : 'Energy Savings' 
                                                    ,'nlsValues' : { 0:'Disabled', 1:'Enabled' }
                                                        }
                                                }                                        
                                        ,'mSetback':{
                                             'GETstr' : '/api/system/setback/'
                                            ,'PUTstr' : '/api/system/setback/'
                                            ,'Active' : None
                                            ,'ISYeditor':{   
                                                     'ISYuom': 25
                                                    ,'ISYmin':None
                                                    ,'ISYmax':None
                                                    ,'ISYsubset': '0-1'
                                                    ,'ISYstep':None
                                                    ,'ISYprec':None }
                                            ,'ISYnls': {    
                                                     'nlsTEXT' : 'Setback Status' 
                                                    ,'nlsValues' : { 0:'Disabled',  1:'Enabled' }
                                                        }
                                                }                                          
                                        ,'mExternalAlarm':{
                                             'GETstr' : '/api/system/externalAlarm/'
                                            ,'PUTstr' : None
                                            ,'Active' : '/api/system/externalAlarm/'
                                            ,'ISYeditor':{    
                                                     'ISYuom': 25
                                                    ,'ISYmin':None
                                                    ,'ISYmax':None
                                                    ,'ISYsubset': '0-1'
                                                    ,'ISYstep':None
                                                    ,'ISYprec':None }
                                            ,'ISYnls': {    
                                                     'nlsTEXT' : 'External Alarm' 
                                                    ,'nlsValues' : { 0:'Off', 1:'On' }
                                                        }
                                                }   
                                         }                                         
                                     ,'data':{}
                                     ,'SensorCapability' : {}
                                     ,'GETkeysList' :{}
                                     ,'PUTkeysList' :{}
                        },
                        self.zoneID: {   'ISYnode':{'nlsICON':'TempSensor'
                                                ,'sends'   : []
                                                ,'accepts' : {'UPDATE'          : {   'ISYtext' :'Update System Data'
                                                                                    ,'ISYeditor' : None} 
                                                             ,'SET_SETPOINT'    : {   'ISYtext' :'Set Temperature'
                                                                                    ,'ISYeditor' : 'mSetpoint' }
                                                             ,'SET_STATUS'      : {   'ISYtext' :'Zone State'
                                                                                    ,'ISYeditor' : 'mStatus' }                                                         
                                                             ,'SET_ENERGYSAVE'  : {   'ISYtext' :'Energy Saving'
                                                                                    ,'ISYeditor' : 'mEnergySaving' }
                                                             ,'SET_SCHEDULEON'  : {   'ISYtext' :'Schedule Status'
                                                                                    ,'ISYeditor' : 'mScheduleOn' }
                                                             ,'CurrentSetpointDP': { 'ISYtext' :'Current Setpoint Dewpoint'
                                                                                    ,'ISYeditor' : 'mCurrentSetpointDP'}
                                                             ,'CurrentSetpointRH' : { 'ISYtext' :'Current Setpoint Rel. Humidity'
                                                                                    ,'ISYeditor' : 'mCurrentSetpointRH'}
                                                             ,'DehumSetpointDP' : { 'ISYtext' :'Dehumdification Setpoint Dewpoint'
                                                                                    ,'ISYeditor' : 'mDehumSetpointDP'}
                                                             ,'DehumSetpointRH' : { 'ISYtext' :'Dehumdification Setpoint Rel. Humidity'
                                                                                    ,'ISYeditor' : 'mDehumSetpointRH'}
                                                             ,'HumSetpointDP'   : { 'ISYtext' :'Humdification Setpoint Dewpoint'
                                                                                    ,'ISYeditor' : 'mHumSetpointDP'}
                                                             ,'HumSetpointRH'   : { 'ISYtext' :'Humdification Setpoint Rel. Humidity'
                                                                                    ,'ISYeditor' : 'mHumSetpointRH'}
                                                             ,'SET_CO2'         :{ 'ISYtext' :'CO2 Setpoint'
                                                                                    ,'ISYeditor' : 'mCO2'}

                                                            } 
                                                }
                                    ,'KeyInfo' : {
                                         'mName':{
                                             'GETstr': '/api/zone/name/'
                                            ,'PUTstr': '/api/zone/name/'
                                            ,'Active': None 
                                            ,'ISYeditor':{   
                                                     'ISYuom':None
                                                    ,'ISYmin':None
                                                    ,'ISYmax':None
                                                    ,'ISYsubset':None
                                                    ,'ISYstep':None
                                                    ,'ISYprec':None }
                                            , 'ISYnls': {    
                                                     'nlsTEXT' : 'Zone Name' 
                                                    ,'nlsValues' : None 
                                                        }  
                                                }  
                                        ,'mSetpoint' :{
                                             'GETstr': '/api/zone/setpoint/'
                                            ,'PUTstr': '/api/zone/setpoint/'
                                            ,'Active': None 
                                            ,'ISYeditor':{   
                                                     'ISYuom':17
                                                    ,'ISYmin':60
                                                    ,'ISYmax':90
                                                    ,'ISYsubset':None
                                                    ,'ISYstep':0.5
                                                    ,'ISYprec':1 }
                                            , 'ISYnls': {    
                                                     'nlsTEXT' : 'Set Temp' 
                                                    ,'nlsValues' : None
                                                        }
                                                    }
                                        ,'mStatus':{ 
                                             'GETstr': '/api/zone/status/'
                                            ,'PUTstr': '/api/zone/status/'
                                            ,'Active': None 
                                            ,'ISYeditor':{   
                                                     'ISYuom': 25
                                                    ,'ISYmin':None
                                                    ,'ISYmax':None
                                                    ,'ISYsubset': '0-1'
                                                    ,'ISYstep':None
                                                    ,'ISYprec':None }
                                            ,'ISYnls': {    
                                                     'nlsTEXT' : 'Zone state'
                                                    ,'nlsValues' : {0:'Off', 1:'On' }
                                                        }
                                                    }
                                        ,'mHumSetpointRH': { 
                                             'GETstr': '/api/zone/humidSetpointRH/'
                                            ,'PUTstr': '/api/zone/humidSetpointRH/'
                                            ,'Active': None 
                                            ,'ISYeditor':{   
                                                     'ISYuom':112
                                                    ,'ISYmin':0
                                                    ,'ISYmax':100
                                                    ,'ISYsubset':None
                                                    ,'ISYstep':1
                                                    ,'ISYprec':0 }
                                            , 'ISYnls': {    
                                                     'nlsTEXT' : 'Hum Set Point RH'  
                                                    ,'nlsValues' : None 
                                                        }
                                                    }
                                        ,'mHumSetpointDP': { 
                                             'GETstr': '/api/zone/humidSetpointDP/'
                                            ,'PUTstr': '/api/zone/humidSetpointDP/'
                                            ,'Active': None 
                                            ,'ISYeditor':{   
                                                     'ISYuom':112
                                                    ,'ISYmin':0
                                                    ,'ISYmax':100
                                                    ,'ISYsubset':None
                                                    ,'ISYstep':1
                                                    ,'ISYprec':0 }
                                            , 'ISYnls': {    
                                                     'nlsTEXT' : 'Hum Set Point DP'  
                                                    ,'nlsValues' : None 
                                                        }
                                                    }
                                        ,'mDehumSetpointRH':{ 
                                             'GETstr': '/api/zone/dehumSetpointRH/'
                                            ,'PUTstr': '/api/zone/dehumSetpointRH/'
                                            ,'Active': None 
                                            ,'ISYeditor':{   
                                                     'ISYuom':112
                                                    ,'ISYmin':0
                                                    ,'ISYmax':100
                                                    ,'ISYsubset':None
                                                    ,'ISYstep':1
                                                    ,'ISYprec':0 }
                                            , 'ISYnls': {    
                                                     'nlsTEXT' : 'DeHum Set Point RH'  
                                                    ,'nlsValues' : None 
                                                        }
                                                    }
                                        ,'mDehumSetpointDP': { 
                                             'GETstr': '/api/zone/dehumSetpointDP/'
                                            ,'PUTstr': '/api/zone/dehumSetpointDP/'
                                            ,'Active': None 
                                            ,'ISYeditor':{   
                                                     'ISYuom':112
                                                    ,'ISYmin':0
                                                    ,'ISYmax':100
                                                    ,'ISYsubset':None
                                                    ,'ISYstep':1
                                                    ,'ISYprec':0 }
                                            , 'ISYnls': {    
                                                     'nlsTEXT' : 'DeHum Set Point DP'  
                                                    ,'nlsValues' : None 
                                                        }
                                                    }
                                        ,'mCurrentSetpointRH': { 
                                             'GETstr': '/api/zone/currentSetpointRH/'
                                            ,'PUTstr': '/api/zone/currentSetpointRH/'
                                            ,'Active': None
                                            ,'ISYeditor':{   
                                                     'ISYuom':112
                                                    ,'ISYmin':0
                                                    ,'ISYmax':100
                                                    ,'ISYsubset':None
                                                    ,'ISYstep':1
                                                    ,'ISYprec':0 }
                                            , 'ISYnls': {    
                                                     'nlsTEXT' : 'Current Set Point RH'  
                                                    ,'nlsValues' : None 
                                                        }
                                                    }
                                        ,'mCurrentSetpointDP': { 
                                             'GETstr': '/api/zone/currentSetpointDP/'
                                            ,'PUTstr': '/api/zone/currentSetpointDP/' 
                                            ,'Active': None
                                            ,'ISYeditor':{   
                                                     'ISYuom':112
                                                    ,'ISYmin':0
                                                    ,'ISYmax':100
                                                    ,'ISYsubset':None
                                                    ,'ISYstep':1
                                                    ,'ISYprec':0 }
                                            , 'ISYnls': {    
                                                     'nlsTEXT' : 'Current Set Point DP'  
                                                    ,'nlsValues' : None 
                                                        }
                                                    }
                                        ,'mHumidity': { 
                                             'GETstr': '/api/zone/humidity/'
                                            ,'PUTstr': None
                                            ,'Active': None
                                            ,'ISYeditor':{   
                                                     'ISYuom':51
                                                    ,'ISYmin':0
                                                    ,'ISYmax':100
                                                    ,'ISYsubset':None
                                                    ,'ISYstep':1
                                                    ,'ISYprec':1 }
                                            , 'ISYnls': {    
                                                     'nlsTEXT' : 'Humidity' 
                                                    ,'nlsValues' : None
                                                        }
                                                    }
                                        ,'mDewPoint' : { 
                                             'GETstr': '/api/zone/dewpoint/'
                                            ,'PUTstr': None
                                            ,'Active': None
                                            ,'ISYeditor':{   
                                                     'ISYuom':51
                                                    ,'ISYmin':0
                                                    ,'ISYmax':100
                                                    ,'ISYsubset':None
                                                    ,'ISYstep':1
                                                    ,'ISYprec':1 }
                                            , 'ISYnls': {    
                                                     'nlsTEXT' : 'Dew Point' 
                                                    ,'nlsValues' : None
                                                        } 
                                                    }
                                        ,'mTemp' : { 
                                             'GETstr': '/api/zone/temperature/'
                                            ,'PUTstr': None
                                            ,'Active': '/api/zone/temperature/'
                                            ,'ISYeditor':{   
                                                     'ISYuom':17
                                                    ,'ISYmin':-40
                                                    ,'ISYmax':120
                                                    ,'ISYsubset':None
                                                    ,'ISYstep':0.5
                                                    ,'ISYprec':1 }
                                            , 'ISYnls': {    
                                                     'nlsTEXT' : 'Perceived Temp' 
                                                    ,'nlsValues' : None
                                                        } 
                                                    }
                                        ,'mAirQuality' : { 
                                             'GETstr': '/api/zone/airQuality/'
                                            ,'PUTstr': None
                                            ,'Active': '/api/zone/airQuality/'
                                            ,'ISYeditor':{   
                                                     'ISYuom':108
                                                    ,'ISYmin':0
                                                    ,'ISYmax':1000
                                                    ,'ISYsubset':None
                                                    ,'ISYstep':1
                                                    ,'ISYprec':0 }
                                            , 'ISYnls': {    
                                                     'nlsTEXT' : 'Air Quality'  
                                                    ,'nlsValues' : None 
                                                        }
                                                    }                                     
                                        ,'mScheduleOn' : {
                                            'GETstr': '/api/zone/scheduleOn/'
                                            ,'PUTstr': '/api/zone/scheduleOn/'
                                            ,'Active': None 
                                            ,'ISYeditor':{   
                                                     'ISYuom':25
                                                    ,'ISYmin':None
                                                    ,'ISYmax':None
                                                    ,'ISYsubset':'0-1'
                                                    ,'ISYstep':None
                                                    ,'ISYprec':None }
                                            , 'ISYnls': {    
                                                     'nlsTEXT' : 'Schedule Status' 
                                                    ,'nlsValues' : { 0:'Off', 1:'On' }
                                                        }  
                                                    } 
                                        ,'mCO2' : { 
                                             'GETstr': '/api/zone/co2/'
                                            ,'PUTstr': None
                                            ,'Active': '/api/zone/co2/'
                                            ,'ISYeditor':{   
                                                     'ISYuom':108
                                                    ,'ISYmin':0
                                                    ,'ISYmax':1000
                                                    ,'ISYsubset':None
                                                    ,'ISYstep':1
                                                    ,'ISYprec':0 }
                                            , 'ISYnls': {    
                                                     'nlsTEXT' : 'CO2'  
                                                    ,'nlsValues' : None 
                                                        }
                                                    }                                     
                                        ,'mVoc' : { 
                                             'GETstr': '/api/zone/voc/'
                                            ,'PUTstr': None
                                            ,'Active': '/api/zone/voc/'
                                            ,'ISYeditor':{   
                                                     'ISYuom':108
                                                    ,'ISYmin':0
                                                    ,'ISYmax':1000
                                                    ,'ISYsubset':None
                                                    ,'ISYstep':1
                                                    ,'ISYprec':0 }
                                            , 'ISYnls': {    
                                                     'nlsTEXT' : 'Volatile Organic Compound'  
                                                    ,'nlsValues' : None 
                                                        }
                                                    }                                                  
                                        ,'mAirTemp' : { 
                                             'GETstr': '/api/zone/airTemperature/'
                                            ,'PUTstr': None
                                            ,'Active': '/api/zone/airTemperature/' 
                                            ,'ISYeditor':{   
                                                     'ISYuom':17
                                                    ,'ISYmin':-40
                                                    ,'ISYmax':120
                                                    ,'ISYsubset':None
                                                    ,'ISYstep':1
                                                    ,'ISYprec':1 }
                                            , 'ISYnls': {    
                                                     'nlsTEXT' : 'Roon air Temp' 
                                                    ,'nlsValues' : None
                                                        } 
                                                    }
                                        ,'mMacrozoneId' : { 
                                             'GETstr': '/api/zone/macrozoneId/'
                                            ,'PUTstr': None
                                            ,'Active': None 
                                            ,'ISYeditor':{   
                                                     'ISYuom':112
                                                    ,'ISYmin':0
                                                    ,'ISYmax':40
                                                    ,'ISYsubset':None
                                                    ,'ISYstep':1
                                                    ,'ISYprec':0 }
                                            , 'ISYnls': {    
                                                     'nlsTEXT' : 'Macro Zone member'  
                                                    ,'nlsValues' : None 
                                                        }
                                                    }  
                                        ,'mEnergySaving' : { 
                                             'GETstr': '/api/zone/energySaving/'
                                            ,'PUTstr': '/api/zone/energySaving/'
                                            ,'Active': None 
                                            ,'ISYeditor':{   
                                                     'ISYuom':25
                                                    ,'ISYmin':None
                                                    ,'ISYmax':None
                                                    ,'ISYsubset':'0-1'
                                                    ,'ISYstep':None
                                                    ,'ISYprec':None }
                                            , 'ISYnls': {    
                                                     'nlsTEXT' : 'Energy Save Status' 
                                                    ,'nlsValues' : { 0:'Off', 1:'On' }
                                                        }  
                                                    } 
                                        ,'mAlarmOn':{ 
                                             'GETstr': '/api/zone/alarmOn/'
                                            ,'PUTstr': None
                                            ,'Active': '/api/zone/alarmOn/'
                                            ,'ISYeditor':{   
                                                     'ISYuom':25
                                                    ,'ISYmin':None
                                                    ,'ISYmax':None
                                                    ,'ISYsubset':'0-1'
                                                    ,'ISYstep':None
                                                    ,'ISYprec':None }
                                            , 'ISYnls': {    
                                                     'nlsTEXT' : 'Alarm Status' 
                                                    ,'nlsValues' : { 0:'Off', 1:'On' }
                                                        }  
                                                    } 
                                        ,'mThermalStatus': { 
                                             'GETstr': '/api/zone/thermalStatus/'
                                            ,'PUTstr': None
                                            ,'Active': '/api/zone/thermalStatus/'
                                            ,'ISYeditor':{   
                                                     'ISYuom':25
                                                    ,'ISYmin':None
                                                    ,'ISYmax':None
                                                    ,'ISYsubset':'0-4'
                                                    ,'ISYstep':None
                                                    ,'ISYprec':None }
                                            , 'ISYnls': {    
                                                     'nlsTEXT' : 'Thermal Status'  
                                                    ,'nlsValues' : { 0:'No Thermal'
                                                                    ,1:'Heating Request'
                                                                    ,2:'Cooling Request'
                                                                    ,3:'H & C request' }
                                                        }
                                                    }    
                                        ,'mCapability': {
                                             'GETstr': '/api/zone/capability/'
                                            ,'PUTstr': None
                                            ,'Active': None 
                                            ,'ISYeditor':{   
                                                     'ISYuom':None
                                                    ,'ISYmin':None
                                                    ,'ISYmax':None
                                                    ,'ISYsubset':None
                                                    ,'ISYstep':None
                                                    ,'ISYprec':None }
                                            , 'ISYnls': {    
                                                     'nlsTEXT' : None
                                                    }
                                        }
                                    }
                                    ,'data' :{}
                                    ,'SensorCapability' : {}
                                    ,'GETkeysList' :{}
                                    ,'PUTkeysList' :{}
                        },
                        self.macrozoneID : {   'ISYnode':{   'nlsICON' :'TempSensor'
                                                        ,'sends'   : []
                                                        ,'accepts' : {'UPDATE'        : { 'ISYtext'   :'Update System'
                                                                                         ,'ISYeditor' : None }
                                                                    ,'SET_SETPOINT'   : {   'ISYtext' :'Set Temperature'
                                                                                         ,'ISYeditor' : 'mSetpoint' }
                                                                    ,'SET_STATUS'     : { 'ISYtext'   :'Macro Zone State'
                                                                                         ,'ISYeditor' : 'mStatus' } 
                                                                    ,'SET_SCHEDULEON' : {   'ISYtext' :'Schedule Status'
                                                                                         ,'ISYeditor' : 'mScheduleOn' }
   
                                                                    }
                                                        }

                                        ,'KeyInfo' : {
                                        'mName':{
                                             'GETstr': '/api/macrozone/name/'
                                            ,'PUTstr': '/api/macrozone/name/'
                                            ,'Active': None 
                                            ,'ISYeditor':{
                                                     'ISYuom':None
                                                    ,'ISYmin':None
                                                    ,'ISYmax':None
                                                    ,'ISYsubset':None
                                                    ,'ISYstep':None
                                                    ,'ISYprec':None }
                                            , 'ISYnls': {    
                                                     'nlsTEXT' : 'Zone Name' 
                                                    ,'nlsValues' : None 
                                                        }
                                                } 
                                        ,'mSetpoint': {
                                              'GETstr':'/api/macrozone/setpoint/'
                                             ,'PUTstr':'/api/macrozone/setpoint/'
                                             ,'Active': None 
                                             ,'ISYeditor':{   
                                                     'ISYuom':17
                                                    ,'ISYmin':60
                                                    ,'ISYmax':90
                                                    ,'ISYsubset':None
                                                    ,'ISYstep':0.5
                                                    ,'ISYprec':1 }
                                            , 'ISYnls': {    
                                                     'nlsTEXT' : 'Set Macro Zone Temp' 
                                                    ,'nlsValues' : None 
                                                    }  
                                                 }
                                        ,'mStatus':{
                                             'GETstr':'/api/macrozone/status/'
                                            ,'PUTstr':'/api/macrozone/status/'
                                            ,'Active': None 
                                            ,'ISYeditor':{   
                                                     'ISYuom': 25
                                                    ,'ISYmin':None
                                                    ,'ISYmax':None
                                                    ,'ISYsubset': '0-1'
                                                    ,'ISYstep':None
                                                    ,'ISYprec':None }
                                            ,'ISYnls': {    
                                                     'nlsTEXT' : 'Macro Zone status'
                                                    ,'nlsValues' : {0:'Off', 1:'On' }
                                                        }
                                                    }
                                        ,'mScheduleOn' :{
                                            'GETstr':'/api/macrozone/scheduleOn/'
                                            ,'PUTstr':'/api/macrozone/scheduleOn/'
                                            ,'Active': None 
                                            ,'ISYeditor':{   
                                                     'ISYuom':25
                                                    ,'ISYmin':None
                                                    ,'ISYmax':None
                                                    ,'ISYsubset':'0-1'
                                                    ,'ISYstep':None
                                                    ,'ISYprec':None }
                                            , 'ISYnls': {    
                                                     'nlsTEXT' : 'Schedule Status' 
                                                    ,'nlsValues' : { 0:'disabled', 1:'Enabled' }
                                                        }  
                                                    } 
                                        ,'mHumidity':{
                                            'GETstr':'/api/macrozone/humidity/'
                                            ,'PUTstr': None
                                            ,'Active': '/api/macrozone/humidity/' 
                                            ,'ISYeditor':{   
                                                     'ISYuom':51
                                                    ,'ISYmin':0
                                                    ,'ISYmax':100
                                                    ,'ISYsubset':None
                                                    ,'ISYstep':1
                                                    ,'ISYprec':1 }
                                            , 'ISYnls': {    
                                                     'nlsTEXT' : 'Humidity' 
                                                    ,'nlsValues' : None
                                                        }
                                                    }                                            }
                                        ,'mDewPoint' : {
                                            'GETstr':'/api/macrozone/dewpoint/'
                                            ,'PUTstr': None
                                            ,'Active': '/api/macrozone/dewpoint/'
                                            ,'ISYeditor':{   
                                                     'ISYuom':51
                                                    ,'ISYmin':0
                                                    ,'ISYmax':100
                                                    ,'ISYsubset':None
                                                    ,'ISYstep':1
                                                    ,'ISYprec':1 }
                                            , 'ISYnls': {    
                                                     'nlsTEXT' : 'Dew Point' 
                                                    ,'nlsValues' : None
                                                        } 
                                                    }                                            
                                        ,'mTemp' : {
                                            'GETstr':'/api/macrozone/temperature/'
                                            ,'PUTstr': None
                                            ,'Active': '/api/macrozone/temperature/'
                                            ,'ISYeditor':{   
                                                     'ISYuom':17
                                                    ,'ISYmin':-40
                                                    ,'ISYmax':120
                                                    ,'ISYsubset':None
                                                    ,'ISYstep':1
                                                    ,'ISYprec':1 }
                                            , 'ISYnls': {    
                                                     'nlsTEXT' : 'Perceived Temp' 
                                                    ,'nlsValues' : None
                                                        } 
                                                    }                                     
                                    ,'data' :{}
                                    ,'SensorCapability' : {}
                                    ,'GETkeysList' :{}
                                    ,'PUTkeysList' :{}                                    
                        }, 
                        self.HotColdcoID  :{ 'ISYnode':{   'nlsICON' :'GenericCtl'
                                                        ,'sends'   : []
                                                        ,'accepts' : {  'UPDATE':  { 'ISYtext'   :'Update System'
                                                                                    ,'ISYeditor' : None } 
                                                                       ,'SET_MODE': { 'ISYtext' :'Set Mode'
                                                                                    ,'ISYeditor' : 'mMode' }
                                                                       ,'SET_ADAPTIVE_COMFORT' :{ 'ISYtext' :'Adaptive System'
                                                                                    ,'ISYeditor' : 'mAdaptiveComfort' } }
                                                        }
                                    ,'KeyInfo' : {
                                         'mName':{
                                             'GETstr': '/api/hc/name/'
                                            ,'PUTstr': '/api/hc/name/'
                                            ,'Active': None 
                                            ,'ISYeditor':{
                                                     'ISYuom':None
                                                    ,'ISYmin':None
                                                    ,'ISYmax':None
                                                    ,'ISYsubset':None
                                                    ,'ISYstep':None
                                                    ,'ISYprec':None }
                                            , 'ISYnls': {    
                                                     'nlsTEXT' : 'Hot Cold CO Name' 
                                                    ,'nlsValues' : None }
                                                }
                                        ,'mMode':{
                                             'GETstr': '/api/hc/mode/'
                                            ,'PUTstr': '/api/hc/mode/'
                                            ,'Active': None 
                                            ,'ISYeditor':{
                                                     'ISYuom':25
                                                    ,'ISYmin':None
                                                    ,'ISYmax':None
                                                    ,'ISYsubset':'0-2'
                                                    ,'ISYstep':None
                                                    ,'ISYprec':None }
                                            , 'ISYnls': {    
                                                     'nlsTEXT' : 'Hot Cold Mode' 
                                                    ,'nlsValues' : {0:'Heat', 1:'Cool' , 2:'Auto' }
                                                    }
                                                }
                                        ,'mExcutiveSeason':{
                                             'GETstr': '/api/hc/executiveSeason/'
                                            ,'PUTstr': None
                                            ,'Active': None 
                                            ,'ISYeditor':{
                                                     'ISYuom':25
                                                    ,'ISYmin':None
                                                    ,'ISYmax':None
                                                    ,'ISYsubset':'0-2'
                                                    ,'ISYstep':None
                                                    ,'ISYprec':None }
                                            , 'ISYnls': {    
                                                     'nlsTEXT' : 'Executive Season' 
                                                    ,'nlsValues' : {0:'Heating', 1:'Cooling' }
                                                    }          
                                                }
                                        ,'mAdaptiveComfort' :{
                                             'GETstr': '/api/hc/adaptiveComfort/'
                                            ,'PUTstr': '/api/hc/adaptiveComfort/'
                                            ,'Active': None 
                                            ,'ISYeditor':{
                                                     'ISYuom':25
                                                    ,'ISYmin':None
                                                    ,'ISYmax':None
                                                    ,'ISYsubset':'0-1'
                                                    ,'ISYstep':None
                                                    ,'ISYprec':None }
                                            , 'ISYnls': {    
                                                     'nlsTEXT' : 'Adaptive Comfort' 
                                                    ,'nlsValues' : {0:'Off', 1:'On' }
                                                    }
                                                }
                                        }   
                                        ,'data' : {}
                                        ,'SensorCapability' : {}
                                        ,'GETkeysList' : {}
                                        ,'PUTkeysList' : {}
                                    },
                        self.fcID :{'ISYnode':{   'nlsICON' :'GenericCtl'
                                                        ,'sends'   : []
                                                        ,'accepts' : {  'SET_STATUS': { 'ISYtext' :'Set System Status'
                                                                                       ,'ISYeditor' :'mStatus' }
                                                                        ,'UPDATE' : { 'ISYtext'   :'Update System'
                                                                                     ,'ISYeditor' : None }
                                                                        ,'SET_COOLING_SPEED' : { 'ISYtext' :'Colling Speed'
                                                                                                ,'ISYeditor' : 'mCoolingSpeed' } 
                                                                        ,'SET_HEATING_SPEED' : { 'ISYtext' :'Heating Speed'
                                                                                                ,'ISYeditor' : 'mHeatingSpeed'} }
                                                }
                                    ,'KeyInfo' : {
                                         'mName':{
                                             'GETstr': '/api/fcu/name/'
                                            ,'PUTstr': '/api/fcu/name/'
                                            ,'Active': None 
                                            ,'ISYeditor':{
                                                     'ISYuom':None
                                                    ,'ISYmin':None
                                                    ,'ISYmax':None
                                                    ,'ISYsubset':None
                                                    ,'ISYstep':None
                                                    ,'ISYprec':None }
                                            , 'ISYnls': {    
                                                     'nlsTEXT' : 'Fan Coil Name' 
                                                    ,'nlsValues' : None }
                                                }
                                        ,'mStatus':{
                                             'GETstr':'/api/fcu/status/'
                                            ,'PUTstr':'/api/fcu/status/'                    
                                            ,'Active': None 
                                            ,'ISYeditor':{   
                                                     'ISYuom': 25
                                                    ,'ISYmin':None
                                                    ,'ISYmax':None
                                                    ,'ISYsubset': '0-1'
                                                    ,'ISYstep':None
                                                    ,'ISYprec':None }
                                            ,'ISYnls': {    
                                                     'nlsTEXT' : 'Fan Coil Status'
                                                    ,'nlsValues' : {0:'Off', 1:'On' }
                                                        }
                                                    }                            
                                        ,'mCoolingSpeed' :{
                                             'GETstr':'/api/fcu/coolingSpeed/'
                                            ,'PUTstr':'/api/fcu/coolingSpeed/'                   
                                            ,'Active':'/api/fcu/coolingSpeed/'  
                                            ,'ISYeditor':{   
                                                     'ISYuom': 25
                                                    ,'ISYmin':0
                                                    ,'ISYmax':100
                                                    ,'ISYsubset': None
                                                    ,'ISYstep':1
                                                    ,'ISYprec':0}
                                            ,'ISYnls': {    
                                                     'nlsTEXT' : 'Fan Coil Cooling Speed'
                                                    ,'nlsValues' : None
                                                        }
                                                    }  
                                        ,'mHeatingSpeed' :{
                                             'GETstr':'/api/fcu/heatingSpeed/'
                                            ,'PUTstr':'/api/fcu/heatingSpeed/'                   
                                            ,'Active':'/api/fcu/heatingSpeed/'
                                            ,'ISYeditor':{   
                                                     'ISYuom': 25
                                                    ,'ISYmin':0
                                                    ,'ISYmax':100
                                                    ,'ISYsubset': None
                                                    ,'ISYstep':1
                                                    ,'ISYprec':0}
                                            ,'ISYnls': {    
                                                     'nlsTEXT' : 'Fan Coil Heating Speed'
                                                    ,'nlsValues' : None
                                                        }
                                                    }      
                                        ,'mType':{
                                             'GETstr':'/api/fcu/type/'
                                            ,'PUTstr': None            
                                            ,'Active': None 
                                            ,'ISYeditor':{   
                                                     'ISYuom': 25
                                                    ,'ISYmin':None
                                                    ,'ISYmax':None
                                                    ,'ISYsubset': '0-3'
                                                    ,'ISYstep':None
                                                    ,'ISYprec':None }
                                            ,'ISYnls': {    
                                                     'nlsTEXT' : 'Fan Coil Type'
                                                    ,'nlsValues' : {0:'Radiator', 1:'Digital On/Off', 
                                                                    2:'Digital variable', 3:'Analog'}       
                                                    }
                                                }                                                                                             
                                        ,'mAlarmOn':{ 
                                             'GETstr': '/api/fcu/alarmOn/'
                                            ,'PUTstr': None
                                            ,'Active': '/api/fcu/alarmOn/'
                                            ,'ISYeditor':{   
                                                     'ISYuom':25
                                                    ,'ISYmin':None
                                                    ,'ISYmax':None
                                                    ,'ISYsubset':'0-1'
                                                    ,'ISYstep':None
                                                    ,'ISYprec':None }
                                            , 'ISYnls': {    
                                                     'nlsTEXT' : 'Alarm Status' 
                                                    ,'nlsValues' : { 0:'Off', 1:'On' }
                                                        }  
                                                    }
                                            }                                       
                                        ,'data' : {}
                                        ,'SensorCapability' : {}
                                        ,'GETkeysList' : {}
                                        ,'PUTkeysList' : {}  
                        },
                        self.atuID: {'ISYnode':{   'nlsICON' :'GenericCtl'
                                                        ,'sends'   : []
                                                        ,'accepts' : {  'SET_STATUS': { 'ISYtext' :'System Status'
                                                                                         ,'ISYeditor' : 'mStatus' }
                                                                        ,'UPDATE': { 'ISYtext'   :'Update System'
                                                                                         ,'ISYeditor'    : None }
                                                                        ,'SET_HRVON' : { 'ISYtext' :'Heat Revopvery'
                                                                                         ,'ISYeditor'    : 'mHRVOn' }
                                                                        ,'SET_FLOWLEVEL' :{ 'ISYtext' :'Set Flow Level'
                                                                                         ,'ISYeditor'    : 'mFlowLevel' }
                                                                        ,'SET_HUMON' : { 'ISYtext' :'Humidity Integration'
                                                                                         ,'ISYeditor'    : 'mHUMOn' }
                                                                        ,'SET_NTDON' : { 'ISYtext' :'NTD Integration'
                                                                                         ,'ISYeditor'    : 'mNTDOn' }
                                                                        ,'SET_INTON' : { 'ISYtext' :'Convective Integration'
                                                                                         ,'ISYeditor' : 'mINTOn' }     
                                                                        ,'SET_HUM_SP_RH' : { 'ISYtext'   :'Hum Setpoint RH'
                                                                                         ,'ISYeditor' : 'mHumSetpointRH'}     
                                                                        ,'SET_HUM_SP_DP' : { 'ISYtext'   :'Hum Setpoint DP'
                                                                                         ,'ISYeditor' : 'mHumSetpointDP' } 
                                                                        ,'SET_DEHUM_SP_RH' : { 'ISYtext' :'DehumSetpointRH'
                                                                                         ,'ISYeditor' : 'mDehumSetpointRH'}
                                                                        ,'SET_DEHUM_SP_DP' : { 'ISYtext' :'Dehum Setpoint DP'
                                                                                         ,'ISYeditor' : 'mDehumSetpointDP' }    
                                                                        ,'SET_CURR_SP_RH' : { 'ISYtext'  :'Current Setpoint RH'
                                                                                         ,'ISYeditor' : 'mCurrentSetpointRH' }     
                                                                        ,'SET_CURR_SP_DP' :{ 'ISYtext'   :'Current Setpoint DP'
                                                                                         ,'ISYeditor' : 'mCurrentSetpointDP' }
                                                                        }}
                                    ,'KeyInfo' : {  
                                        'mName':{
                                             'GETstr': '/api/atu/name/'
                                            ,'PUTstr': '/api/atu/name/'
                                            ,'Active': None 
                                            ,'ISYeditor':{
                                                     'ISYuom':None
                                                    ,'ISYmin':None
                                                    ,'ISYmax':None
                                                    ,'ISYsubset':None
                                                    ,'ISYstep':None
                                                    ,'ISYprec':None }
                                            , 'ISYnls': {    
                                                     'nlsTEXT' : 'ATU Name' 
                                                    ,'nlsValues' : None }
                                                }
                                        ,'mFlowLevel':{                                            
                                             'GETstr': '/api/atu/flowLevel/'
                                            ,'PUTstr': '/api/atu/flowLevel/'
                                            ,'Active': '/api/atu/flowLevel/' 
                                            ,'ISYeditor':{
                                                     'ISYuom':25
                                                    ,'ISYmin':0
                                                    ,'ISYmax':100
                                                    ,'ISYsubset':None
                                                    ,'ISYstep':None
                                                    ,'ISYprec':None }
                                            , 'ISYnls': {    
                                                     'nlsTEXT' : 'ATU Flow Level' 
                                                    ,'nlsValues' : None }
                                                   }
                                        ,'mStatus' : {                                             
                                             'GETstr':'/api/atu/status/'
                                            ,'PUTstr':'/api/atu/status/'                
                                            ,'Active': None 
                                            ,'ISYeditor':{   
                                                     'ISYuom': 25
                                                    ,'ISYmin':None
                                                    ,'ISYmax':None
                                                    ,'ISYsubset': '0-1'
                                                    ,'ISYstep':None
                                                    ,'ISYprec':None }
                                            ,'ISYnls': {    
                                                     'nlsTEXT' : 'ATU Status'
                                                    ,'nlsValues' : {0:'Off', 1:'On' }
                                                       }
                                                    }
                                        ,'mHRVOn' :{                                             
                                             'GETstr': '/api/atu/hrvOn/'
                                            ,'PUTstr': '/api/atu/hrvOn/'
                                            ,'Active': None 
                                            ,'ISYeditor':{ 
                                                     'ISYuom': 25
                                                    ,'ISYmin':None
                                                    ,'ISYmax':None
                                                    ,'ISYsubset': '0-1'
                                                    ,'ISYstep':None
                                                    ,'ISYprec':None }
                                            ,'ISYnls': {   
                                                     'nlsTEXT' : 'Heat Recovery Status'
                                                    ,'nlsValues' : {0:'Off', 1:'On' }
                                                        }
                                                   }
                                        ,'mHUMOn':{                                             
                                             'GETstr': '/api/atu/humOn/'
                                            ,'PUTstr': '/api/atu/humOn/'
                                            ,'Active': None 
                                            ,'ISYeditor':{
                                                     'ISYuom': 25
                                                    ,'ISYmin':None
                                                    ,'ISYmax':None
                                                    ,'ISYsubset': '0-1'
                                                    ,'ISYstep':None
                                                    ,'ISYprec':None }
                                            , 'ISYnls': {    
                                                     'nlsTEXT' : 'Humidufucation' 
                                                     ,'nlsValues' : {0:'Off', 1:'On' }
                                                        }
                                                   }
                                        ,'mNTDOn':{                                             
                                             'GETstr': '/api/atu/ntdOn/'
                                            ,'PUTstr': '/api/atu/ntdOn/'
                                            ,'Active': None 
                                            ,'ISYeditor':{
                                                     'ISYuom': 25
                                                    ,'ISYmin':None
                                                    ,'ISYmax':None
                                                    ,'ISYsubset':'0-1'
                                                    ,'ISYstep':None
                                                    ,'ISYprec':None }
                                            , 'ISYnls': {    
                                                      'nlsTEXT' : 'NTD Dehumidification??' 
                                                     ,'nlsValues' : {0:'Off', 1:'On' }
                                                        }
                                                   }
                                        ,'mINTOn':{                                             
                                             'GETstr': '/api/atu/intOn/'
                                            ,'PUTstr': '/api/atu/intOn/'
                                            ,'Active': None 
                                            ,'ISYeditor':{
                                                     'ISYuom': 25 
                                                    ,'ISYmin':None
                                                    ,'ISYmax':None
                                                    ,'ISYsubset':'0-1'
                                                    ,'ISYstep':None
                                                    ,'ISYprec':None }
                                            , 'ISYnls': {    
                                                     'nlsTEXT' : 'Convective Integration' 
                                                     ,'nlsValues' : {0:'Off', 1:'On' }
                                                        }
                                                   }
                                        ,'mDehumudityStatus':{                                             
                                             'GETstr': '/api/atu/dehumidificationStatus/'
                                            ,'PUTstr': None
                                            ,'Active': '/api/atu/dehumidificationStatus/' 
                                            ,'ISYeditor':{
                                                     'ISYuom':25
                                                    ,'ISYmin':None
                                                    ,'ISYmax':None
                                                    ,'ISYsubset':'0-1'
                                                    ,'ISYstep':None
                                                    ,'ISYprec':None }
                                            , 'ISYnls': {    
                                                      'nlsTEXT' : 'Dehumidification Status' 
                                                     ,'nlsValues' : {0:'Off', 1:'On' }
                                                        }
                                                   }
                                        ,'mHumidityStatus':{                                             
                                             'GETstr': '/api/atu/humidificationStatus/'
                                            ,'PUTstr': None
                                            ,'Active': '/api/atu/humidificationStatus/' 
                                            ,'ISYeditor':{
                                                     'ISYuom':25
                                                    ,'ISYmin':None
                                                    ,'ISYmax':None
                                                    ,'ISYsubset':'0-1'
                                                    ,'ISYstep':None
                                                    ,'ISYprec':None }
                                            , 'ISYnls': {    
                                                      'nlsTEXT' : 'Humidification Status' 
                                                     ,'nlsValues' : {0:'Off', 1:'On' }
                                                        }
                                                   }
                                        ,'mHRVstatus':{                                             
                                             'GETstr': '/api/atu/hrvStatus/'
                                            ,'PUTstr': None
                                            ,'Active': '/api/atu/hrvStatus/'
                                            ,'ISYeditor':{
                                                     'ISYuom':25
                                                    ,'ISYmin':None
                                                    ,'ISYmax':None
                                                    ,'ISYsubset':'0-1'
                                                    ,'ISYstep':None
                                                    ,'ISYprec':None }
                                            , 'ISYnls': {    
                                                      'nlsTEXT' : 'HRV Status' 
                                                     ,'nlsValues' : {0:'Off', 1:'On' }
                                                        }
                                                   }
                                        ,'mIntegrationStatus':{                                             
                                             'GETstr': '/api/atu/integrationStatus/'
                                            ,'PUTstr': None
                                            ,'Active': '/api/atu/integrationStatus/'
                                            ,'ISYeditor':{
                                                     'ISYuom':25
                                                    ,'ISYmin':None
                                                    ,'ISYmax':None
                                                    ,'ISYsubset':'0-1'
                                                    ,'ISYstep':None
                                                    ,'ISYprec':None }
                                            , 'ISYnls': {    
                                                     'nlsTEXT' : 'Integration Status'
                                                    ,'nlsValues' : {0:'Off', 1:'On' }  
                                                        }
                                                   }
                                        ,'mAlarmOn':{                                             
                                             'GETstr': '/api/atu/alarmOn/'
                                            ,'PUTstr': None
                                            ,'Active': '/api/atu/alarmOn/' 
                                            ,'ISYeditor':{
                                                     'ISYuom':25
                                                    ,'ISYmin':None
                                                    ,'ISYmax':None
                                                    ,'ISYsubset':'0-1'
                                                    ,'ISYstep':None
                                                    ,'ISYprec':None }
                                            , 'ISYnls': {    
                                                     'nlsTEXT' : 'Alarm Status' 
                                                    ,'nlsValues' : {0:'Off', 1:'On' }  
                                                        }
                                                   }
                                        ,'mAirTemp':{                                            
                                             'GETstr': '/api/atu/airTemperature/'
                                            ,'PUTstr': None
                                            ,'Active': '/api/atu/airTemperature/'
                                            ,'ISYeditor':{
                                                     'ISYuom':17
                                                    ,'ISYmin':40
                                                    ,'ISYmax':120
                                                    ,'ISYsubset':None
                                                    ,'ISYstep':1
                                                    ,'ISYprec':0}
                                            , 'ISYnls': {    
                                                     'nlsTEXT' : 'Air Temperature (flow)' 
                                                     ,'nlsValues' : None 
                                                        }
                                                   }
                                        ,'mHumSetpointRH':{                                             
                                             'GETstr': '/api/atu/humidSetpointRH/'
                                            ,'PUTstr': '/api/atu/humidSetpointRH/'
                                            ,'Active': None 
                                            ,'ISYeditor':{
                                                     'ISYuom':51
                                                    ,'ISYmin':0
                                                    ,'ISYmax':100
                                                    ,'ISYsubset':None
                                                    ,'ISYstep':1
                                                    ,'ISYprec':1 }
                                            , 'ISYnls': {    
                                                     'nlsTEXT' : 'Humidity Setpoint RH' 
                                                     ,'nlsValues' : None 
                                                        }
                                                   }
                                        ,'mHumSetpointDP':{                                             
                                             'GETstr': '/api/atu/humidSetpointDP/'
                                            ,'PUTstr': '/api/atu/humidSetpointDP/'
                                            ,'Active': None 
                                            ,'ISYeditor':{
                                                     'ISYuom':51
                                                    ,'ISYmin':0
                                                    ,'ISYmax':100
                                                    ,'ISYsubset':None
                                                    ,'ISYstep':1
                                                    ,'ISYprec':1  }
                                            , 'ISYnls': {    
                                                     'nlsTEXT' : 'Humidity Setpoint RH' 
                                                     ,'nlsValues' : None 
                                                        }
                                                   }
                                        ,'mDehumSetpointRH':{                                             
                                             'GETstr': '/api/atu/dehumSetpointRH/'
                                            ,'PUTstr': '/api/atu/dehumSetpointRH/'
                                            ,'Active': None 
                                            ,'ISYeditor':{
                                                     'ISYuom':51
                                                    ,'ISYmin':0
                                                    ,'ISYmax':100
                                                    ,'ISYsubset':None
                                                    ,'ISYstep':1
                                                    ,'ISYprec':1  }
                                            , 'ISYnls': {    
                                                     'nlsTEXT' : 'Deumidity Setpoint RH' 
                                                     ,'nlsValues' : None 
                                                        }
                                                   }
                                        ,'mDehumSetpointDP':{    
                                             'GETstr': '/api/atu/dehumidSetpointDP/'
                                            ,'PUTstr': '/api/atu/dehumidSetpointDP/'
                                            ,'Active': None 
                                            ,'ISYeditor':{
                                                     'ISYuom':51
                                                    ,'ISYmin':0
                                                    ,'ISYmax':100
                                                    ,'ISYsubset':None
                                                    ,'ISYstep':1
                                                    ,'ISYprec':1  }
                                            , 'ISYnls': {    
                                                     'nlsTEXT' : 'Dehumidity Setpoint DP' 
                                                     ,'nlsValues' : None 
                                                        }
                                                   }
                                        ,'mCurrentSetpointRH':{                                             
                                             'GETstr': '/api/atu/currentSetpointRH/'
                                            ,'PUTstr': '/api/atu/currentSetpointRH/'
                                            ,'Active': None 
                                            ,'ISYeditor':{
                                                     'ISYuom':51
                                                    ,'ISYmin':0
                                                    ,'ISYmax':100
                                                    ,'ISYsubset':None
                                                    ,'ISYstep':1
                                                    ,'ISYprec':1  }
                                            , 'ISYnls': {    
                                                     'nlsTEXT' : 'Current Setpoint RH' 
                                                     ,'nlsValues' : None 
                                                        }
                                                   }
                                        ,'mCurrentSetpointDP':{                                             
                                             'GETstr': '/api/atu/currentSetpointDP/'
                                            ,'PUTstr': '/api/atu/currentSetpointDP/'
                                            ,'Active': None 
                                            ,'ISYeditor':{
                                                     'ISYuom':51
                                                    ,'ISYmin':0
                                                    ,'ISYmax':100
                                                    ,'ISYsubset':None
                                                    ,'ISYstep':1
                                                    ,'ISYprec':1  }
                                            , 'ISYnls': {    
                                                     'nlsTEXT' : 'Current Setpoint RH' 
                                                    ,'nlsValues' : None 
                                                        }
                                                   }
                                        ,'mCapability': {
                                             'GETstr': '/api/atu/capability/'
                                            ,'PUTstr': None
                                            ,'Active': None 
                                            ,'ISYeditor':{   
                                                     'ISYuom':None
                                                    ,'ISYmin':None
                                                    ,'ISYmax':None
                                                    ,'ISYsubset':None
                                                    ,'ISYstep':None
                                                    ,'ISYprec':None }
                                            , 'ISYnls': {    
                                                     'nlsTEXT' : None
                                                    ,'nlsValues' : None 
                                                        }
                                                    }
                                    }
                                        ,'data' : {}
                                        ,'SensorCapability' : {}
                                        ,'GETkeysList' : {}
                                        ,'PUTkeysList' : {}     
                        },
                         self.energySourceID:{'ISYnode':{   'nlsICON' :'GenericCtl'
                                                        ,'sends'   : []
                                                        ,'accepts' : {  'UPDATE'        : { 'ISYtext'   :'Update System'
                                                                                         ,'ISYeditor' : None }}
                                                                        }
                                    ,'KeyInfo' : {  
                                        'mName':{
                                             'GETstr': '/api/energySource/name/'
                                            ,'PUTstr': '/api/energySource/name/'
                                            ,'Active': None 
                                            ,'ISYeditor':{
                                                     'ISYuom':None
                                                    ,'ISYmin':None
                                                    ,'ISYmax':None
                                                    ,'ISYsubset':None
                                                    ,'ISYstep':None
                                                    ,'ISYprec':None }
                                            , 'ISYnls': {    
                                                     'nlsTEXT' : 'Energy Source Name' 
                                                    ,'nlsValues' : None }
                                                }
                                        ,'mStatus' : {                                             
                                             'GETstr':'/api/energySource/status/'
                                            ,'PUTstr': None                  
                                            ,'Active': None 
                                            ,'ISYeditor':{   
                                                     'ISYuom': 25
                                                    ,'ISYmin':None
                                                    ,'ISYmax':None
                                                    ,'ISYsubset': '0-1'
                                                    ,'ISYstep':None
                                                    ,'ISYprec':None }
                                            ,'ISYnls': {    
                                                     'nlsTEXT' : 'Energy Source Status'
                                                    ,'nlsValues' : {0:'Off', 1:'On' }
                                                       }
                                                    }
                                        ,'mDHWstatus' : {                                             
                                             'GETstr':'/api/energySource/dhwStatus/'
                                            ,'PUTstr': None                  
                                            ,'Active': None 
                                            ,'ISYeditor':{   
                                                     'ISYuom': 25
                                                    ,'ISYmin':None
                                                    ,'ISYmax':None
                                                    ,'ISYsubset': '0-1'
                                                    ,'ISYstep':None
                                                    ,'ISYprec':None }
                                            ,'ISYnls': {    
                                                     'nlsTEXT' : 'Domestic Hot Water Status'
                                                    ,'nlsValues' : {0:'Off', 1:'On' }
                                                       }
                                                    }
                                        ,'mType' : {                                             
                                             'GETstr':'/api/energySource/type/'
                                            ,'PUTstr': None                  
                                            ,'Active': None 
                                            ,'ISYeditor':{   
                                                     'ISYuom': 25
                                                    ,'ISYmin':None
                                                    ,'ISYmax':None
                                                    ,'ISYsubset': '0-3'
                                                    ,'ISYstep':None
                                                    ,'ISYprec':None }
                                            ,'ISYnls': {    
                                                     'nlsTEXT' : 'Energy Source Type'
                                                    ,'nlsValues' : {0:'Broiler', 1:' H.P. Cooling Only'
                                                                    , 2: 'H.P. Heating Only', 3:'H.P. Heating and Cooling' }
                                                       }
                                                    }
                                        ,'mAlarmOn' : {                                             
                                             'GETstr':'/api/energySource/alarmOn/'
                                            ,'PUTstr': None                  
                                            ,'Active': None 
                                            ,'ISYeditor':{   
                                                     'ISYuom': 25
                                                    ,'ISYmin':None
                                                    ,'ISYmax':None
                                                    ,'ISYsubset': '0-1'
                                                    ,'ISYstep':None
                                                    ,'ISYprec':None }
                                            ,'ISYnls': {    
                                                     'nlsTEXT' : 'ATU Status'
                                                    ,'nlsValues' : {0:'Off', 1:'On' }
                                                       }
                                                    }  
                                        }                                                                                                      
                                        ,'data' : {}
                                        ,'SensorCapability' : {}
                                        ,'GETkeysList' : {}
                                        ,'PUTkeysList' : {}
                        }, 
                        self.bufferTankID: {'ISYnode':{  'nlsICON' :'GenericCtl'
                                                        ,'sends'   : []
                                                        ,'accepts' : {  'SET_STATUS'    : { 'ISYtext' :'Set Status'
                                                                                         ,'ISYeditor' : 'mStatus' }
                                                                       ,'UPDATE'        : { 'ISYtext'   :'Update System'
                                                                                         ,'ISYeditor' : None }
                                                                       ,'SET_MODE'      : { 'ISYtext' :'Set Mode'
                                                                                         ,'ISYeditor' : 'mMode' }
                                                                       ,'SET_TEMPMODE'  :{ 'ISYtext' :'Set Temperature Mode'
                                                                                         ,'ISYeditor' : 'mTempMode' }}
                                                                        }
                                    ,'KeyInfo' : {  
                                        'mName':{
                                             'GETstr': '/api/bufferTank/name/'
                                            ,'PUTstr': '/api/bufferTank/name/'
                                            ,'Active': None 
                                            ,'ISYeditor':{
                                                     'ISYuom':None
                                                    ,'ISYmin':None
                                                    ,'ISYmax':None
                                                    ,'ISYsubset':None
                                                    ,'ISYstep':None
                                                    ,'ISYprec':None }
                                            , 'ISYnls': {    
                                                     'nlsTEXT' : 'Buffer Tank Name' 
                                                    ,'nlsValues' : None }
                                                }
                                        ,'mStatus' : {                                             
                                             'GETstr':'/api/bufferTank/status/'
                                            ,'PUTstr':'/api/bufferTank/status/'                
                                            ,'Active': None 
                                            ,'ISYeditor':{   
                                                     'ISYuom': 25
                                                    ,'ISYmin':None
                                                    ,'ISYmax':None
                                                    ,'ISYsubset': '0-1'
                                                    ,'ISYstep':None
                                                    ,'ISYprec':None }
                                            ,'ISYnls': {    
                                                     'nlsTEXT' : 'Buffer Tank Status'
                                                    ,'nlsValues' : {0:'Off', 1:'On' }
                                                       }
                                                    }
                                        ,'mMode' : {                                             
                                             'GETstr':'/api/bufferTank/mode/'
                                            ,'PUTstr':'/api/bufferTank/mode/'                
                                            ,'Active': None 
                                            ,'ISYeditor':{   
                                                     'ISYuom': 25
                                                    ,'ISYmin':None
                                                    ,'ISYmax':None
                                                    ,'ISYsubset': '0-1'
                                                    ,'ISYstep':None
                                                    ,'ISYprec':None }
                                            ,'ISYnls': {    
                                                     'nlsTEXT' : 'Buffer Tank Mode'
                                                    ,'nlsValues' : {0:'Manual', 1:'Automatic' }
                                                       }
                                                    }                           
                                        ,'mTempMode' : {                                             
                                             'GETstr':'/api/bufferTank/tempMode/'
                                            ,'PUTstr':'/api/bufferTank/tempMode/'                
                                            ,'Active': None 
                                            ,'ISYeditor':{   
                                                     'ISYuom': 25
                                                    ,'ISYmin':None
                                                    ,'ISYmax':None
                                                    ,'ISYsubset': '0-2'
                                                    ,'ISYstep':None
                                                    ,'ISYprec':None }
                                            ,'ISYnls': {    
                                                     'nlsTEXT' : 'Buffer Tank Tempperature Mode'
                                                    ,'nlsValues' : {0:'Fixed Temp', 1:'Follow Loads', 2:'Outdoor Temp Compensation' }
                                                       }
                                                    }   
                                        ,'mTemp':{                                            
                                             'GETstr': '/api/atu/airTemperature/'
                                            ,'PUTstr': None
                                            ,'Active': '/api/atu/airTemperature/'
                                            ,'ISYeditor':{
                                                     'ISYuom':17
                                                    ,'ISYmin':40
                                                    ,'ISYmax':120
                                                    ,'ISYsubset':None
                                                    ,'ISYstep':1
                                                    ,'ISYprec':0}
                                            , 'ISYnls': {    
                                                     'nlsTEXT' : 'Buffer Tank Temperature' 
                                                     ,'nlsValues' : None 
                                                        }
                                                   }                                            
                                         ,'mAlarmOn' : {                                             
                                             'GETstr':'/api/bufferTank/alarmOn/'
                                            ,'PUTstr':None              
                                            ,'Active':None
                                            ,'ISYeditor':{   
                                                     'ISYuom': 25
                                                    ,'ISYmin':None
                                                    ,'ISYmax':None
                                                    ,'ISYsubset': '0-1'
                                                    ,'ISYstep':None
                                                    ,'ISYprec':None }
                                            ,'ISYnls': {    
                                                     'nlsTEXT' : 'Buffer Tank Alarm'
                                                    ,'nlsValues' : {0:'Off', 1:'On' }
                                                       }
                                                    }   
                                        }                        
                                        ,'data' : {}
                                        ,'SensorCapability' : {}
                                        ,'GETkeysList' : {}
                                        ,'PUTkeysList' : {}
                        },
                        self.dhwID: { 'ISYnode':{   'nlsICON' :'GenericCtl'
                                                        ,'sends'   : []
                                                        ,'accepts' : {  'SET_STATUS'     : { 'ISYtext' :'Hot Water Status'
                                                                                         ,'ISYeditor' : 'mStatus' }                                                      
                                                                        ,'UPDATE'        : { 'ISYtext'   :'Update Hot Water System'
                                                                                         ,'ISYeditor' : None }
                                                                        ,'SET_TARGETTEMP': { 'ISYtext' :'Target Temperature'
                                                                                         ,'ISYeditor' : 'mTargetTemp' }}
                                                            }
                                    ,'KeyInfo' : {  
                                        'mName':{
                                             'GETstr': '/api/dhw/name/'
                                            ,'PUTstr': '/api/dhw/name/'
                                            ,'Active': None 
                                            ,'ISYeditor':{
                                                     'ISYuom':None
                                                    ,'ISYmin':None
                                                    ,'ISYmax':None
                                                    ,'ISYsubset':None
                                                    ,'ISYstep':None
                                                    ,'ISYprec':None }
                                            , 'ISYnls': {    
                                                     'nlsTEXT' : 'Domestic Hot Water Name' 
                                                    ,'nlsValues' : None }
                                                }
                                        ,'mStatus' : {                                             
                                             'GETstr':'/api/dhw/status/'
                                            ,'PUTstr':'/api/dhw/status/'              
                                            ,'Active': None 
                                            ,'ISYeditor':{   
                                                     'ISYuom': 25
                                                    ,'ISYmin':None
                                                    ,'ISYmax':None
                                                    ,'ISYsubset': '0-1'
                                                    ,'ISYstep':None
                                                    ,'ISYprec':None }
                                            ,'ISYnls': {    
                                                     'nlsTEXT' : 'Domestic Hot Water Status'
                                                    ,'nlsValues' : {0:'Off', 1:'On' }
                                                       }
                                                    }
                                        ,'mTemp' : {                                             
                                             'GETstr':'/api/dhw/temperature/'
                                            ,'PUTstr':None             
                                            ,'Active': None 
                                            ,'ISYeditor':{   
                                                     'ISYuom':17
                                                    ,'ISYmin':-40
                                                    ,'ISYmax':150
                                                    ,'ISYsubset':None
                                                    ,'ISYstep':1
                                                    ,'ISYprec':1 }
                                            ,'ISYnls': {    
                                                     'nlsTEXT' : 'Domestic Hot Water Temp'
                                                    ,'nlsValues' : None
                                                       }
                                                    }                            
                                        ,'mTargetTemp' : {                                             
                                             'GETstr':'/api/dhw/targetTemperature/'
                                            ,'PUTstr':'/api/dhw/targetTemperature/'              
                                            ,'Active': None 
                                            ,'ISYeditor':{   
                                                     'ISYuom':17
                                                    ,'ISYmin':-40
                                                    ,'ISYmax':150
                                                    ,'ISYsubset':None
                                                    ,'ISYstep':1
                                                    ,'ISYprec':1 }
                                            ,'ISYnls': {    
                                                     'nlsTEXT' : 'Domestic Hot Water Target Temp'
                                                    ,'nlsValues' : None
                                                       }
                                                    } 
                                        }                              
                                        ,'data' : {}
                                        ,'SensorCapability' : {}
                                        ,'GETkeysList' : {}
                                        ,'PUTkeysList' : {}
                        }
                }
        
        
        #self.setupStruct = {'nodeDef': nodeNbr: { 'nodeDef':{}
        ##                                    ,'sts':{}
        #                                  ,'cmds':{
        #                                            'sends':{}
        #                                            ,'accepts':{}
        #                                            } 
        #                                    }
        #                        }
        #            ,'editors':{id:Name, range:{}}
        #            ,'nls':{}
        #                }
        
        self.nodeCount = 0
        self.setupFile = { 'nodeDef':{}
                            ,'editors':{}
                            ,'nls':{}}

        
        self.APIKey = 'apikey'
        self.APIStr = self.APIKey + '=' + mAPIkey

        self.IP ='http://'+ mIPaddress

        self.RESPONSE_OK = '<Response [200]>'
        self.RESPONSE_NO_SUPPORT = '<Response [400]>'
        self.RESPONSE_NO_RESPONSE = '<Response [404]>'
        self.NaNlist= [-32768 , -3276.8 ]
        


        #Dummy check to see if there is connection to Messana system)
        if not(self.checkMessanaConnection()):
            LOGGER.error('Error Connecting to MessanaSystem')
        else:  
            #LOGGER.info('Extracting Information about Messana System')
            self. setMessanaCredentials (mIPaddress, mAPIkey) 
            # Need SystemCapability function               
            self.getSystemCapability()
            self.updateSystemData('all')
            #LOGGER.debug(self.systemID + ' added')
 
            self.addSystemDefStruct(self.systemID)

            for zoneNbr in range(0,self.mSystem[ self.systemID]['data']['mZoneCount']):
                self.getZoneCapability(zoneNbr)
                self.updateZoneData('all', zoneNbr)
                zoneName = self.zoneID+str(zoneNbr)
                self.addNodeDefStruct(zoneNbr, self.zoneID, zoneName )
        
            for macrozoneNbr in range(0,self.mSystem[ self.systemID]['data']['mMacrozoneCount']):
                self.getMacrozoneCapability(macrozoneNbr)
                self.updateMacrozoneData('all', macrozoneNbr)
                macrozoneName = self.macrozoneID+str(macrozoneNbr)
                self.addNodeDefStruct(macrozoneNbr, self.macrozoneID, macrozoneName )
            
            for atuNbr in range(0,self.mSystem[ self.systemID]['data']['mATUcount']):
                self.getAtuCapability(atuNbr)
                self.updateAtuData('all', atuNbr)
                atuName = self.atuID+str(atuNbr)
                self.addNodeDefStruct(atuNbr, self.atuID, atuName )
    
            for dhwNbr in range(0,self.mSystem[ self.systemID]['data']['mDHWcount']):
                self.getDHWCapability(dhwNbr)
                self.updateDHWData('all', dhwNbr)
                dhwName = self.dhwID+str(dhwNbr)
                self.addNodeDefStruct(dhwNbr, self.dhwID, dhwName )

            for fcNbr in range(0,self.mSystem[ self.systemID]['data']['mFanCoilCount']):
                self.getFanCoilCapability(fcNbr)
                self.updateFanCoilData('all', fcNbr)
                fcName = self.fcID+str(fcNbr)
                self.addNodeDefStruct(fcNbr, self.fcID, fcName )
        
            for esNbr in range(0,self.mSystem[ self.systemID]['data']['mEnergySourceCount']):
                self.getEnergySourceCapability(esNbr)
                self.updateEnergySourceData('all', esNbr)
                esName =  self.energySourceID+str(esNbr)
                self.addNodeDefStruct(esNbr,  self.energySourceID, esName )   

            for HcCoNbr in range(0,self.mSystem[ self.systemID]['data']['mhc_coCount']):
                self.getHcCoCapability(HcCoNbr)
                self.updateHcCoData('all', HcCoNbr)
                hccoName = self.HotColdcoID +str(HcCoNbr)
                self.addNodeDefStruct(HcCoNbr, self.HotColdcoID , hccoName )          
            
            for btNbr in range(0,self.mSystem[ self.systemID]['data']['mBufTankCount']):
                self.getBufferTankCapability(btNbr)
                self.updateBufferTankData('all', btNbr)
                btName = self.bufferTankID+str(btNbr)
                self.addNodeDefStruct(btNbr, self.bufferTankID, btName )     

            LOGGER.info ('Creating Setup file')
            self.createSetupFiles('./profile/nodedef/nodedefs.xml','./profile/editor/editors.xml', './profile/nls/en_us.txt')
            self.ISYmap = self.createISYmapping()


    def createISYmapping(self):
        temp = {}
        for nodes in self.setupFile['nodeDef']:
            temp[nodes]= {}
            for mKeys in self.setupFile['nodeDef'][nodes]['sts']:
                for ISYkey in self.setupFile['nodeDef'][nodes]['sts'][mKeys]:
                    if ISYkey != 'ISYInfo':
                        temp[nodes][ISYkey] = {}
                        temp[nodes][ISYkey].update({'messana': mKeys})
                        temp[nodes][ISYkey].update({'editor': self.setupFile['nodeDef'][nodes]['sts'][mKeys][ISYkey]})
        #LOGGER.debug(temp) 
        return (temp)

    def setMessanaCredentials (self, mIPaddress, APIkey):
        self.mIPaddress = mIPaddress
        self.APIKeyVal = APIkey



    def getnodeISYdriverInfo(self, node, nodeNbr, mKey):
        info = {}
        if mKey in self.setupFile['nodeDef'][ self.systemID]['sts']:
            keys = list(self.setupFile['nodeDef'][ self.systemID]['sts'][mKey].keys())
            info['driver'] = keys[0]
            tempData =  self.GETSystemData(mKey)
            if tempData['statusOK']:
                val = tempData['data']        
                if val in  ['Celcius', 'Fahrenheit']:
                    if val == 'Celcius':
                        val = 0
                    else:  
                        val = 1 
                info['value'] = val
            else:
                info['value'] = ''
            editor = self.setupFile['nodeDef'][ self.systemID]['sts'][mKey][keys[0]]

            info['uom'] = self.setupFile['editors'][editor]['ISYuom']
        return(info)

    def checkValidNodeCommand(self, key, node, nodeNbr):
        exists = True
        mCmd = self.mSystem[node]['ISYnode']['accepts'][key]['ISYeditor']
        if mCmd != None:
            if not(mCmd in self.mSystem[node]['PUTkeysList'][nodeNbr]):
                exists = False
        return(exists)



    def addNodeDefStruct(self, nodeNbr, nodeName, nodeId):
        self.keyCount = 0
        nodeId.lower()
        #LOGGER.debug('addNodeDefStruct: ' + nodeName+ ' ' + str(nodeNbr) + ' '+nodeId)
        self.name = nodeName+str(nodeNbr)
        self.nlsKey = 'nls' + self.name
        self.nlsKey.lower()
        #editorName = nodeName+'_'+str(keyCount)
        self.setupFile['nodeDef'][self.name]={}
        self.setupFile['nodeDef'][self.name]['CodeId'] = nodeId
        self.setupFile['nodeDef'][self.name]['nlsId'] = self.nlsKey
        self.setupFile['nodeDef'][self.name]['nlsNAME']=self.mSystem[nodeName]['data'][nodeNbr]['mName']
        self.setupFile['nodeDef'][self.name]['nlsICON']=self.mSystem[nodeName]['ISYnode']['nlsICON']
        self.setupFile['nodeDef'][self.name]['sts']={}

        #for mKey in self.mSystem[nodeName]['data'][nodeNbr]: 
        for mKey in self.mSystem[nodeName]['GETkeysList'][nodeNbr]:             
            #make check if system has unit installed
            if self.mSystem[nodeName]['KeyInfo'][mKey]['ISYeditor']['ISYuom']:
                self.keyCount = self.keyCount + 1
                editorName = nodeName.upper()+str(nodeNbr)+'_'+str(self.keyCount)
                nlsName = editorName
                ISYvar = 'GV'+str(self.keyCount)
                self.setupFile['nodeDef'][self.name]['sts'][mKey]={ISYvar:editorName}
                self.setupFile['editors'][editorName]={}
                #self.setupFile['nls'][editorName][ISYparam]
                for ISYparam in self.mSystem[nodeName]['KeyInfo'][mKey]['ISYeditor']:
                    if self.mSystem[nodeName]['KeyInfo'][mKey]['ISYeditor'][ISYparam]!= None:
                        self.setupFile['editors'][editorName][ISYparam]=self.mSystem[nodeName]['KeyInfo'][mKey]['ISYeditor'][ISYparam]

                if self.mSystem[nodeName]['KeyInfo'][mKey]['ISYnls']:
                    self.setupFile['nls'][nlsName]={}
                for ISYnls in self.mSystem[nodeName]['KeyInfo'][mKey]['ISYnls']:
                    #LOGGER.debug( mKey + ' ' + ISYnls)
                    if  self.mSystem[nodeName]['KeyInfo'][mKey]['ISYnls'][ISYnls]:      
                        self.setupFile['nls'][nlsName][ISYnls] = self.mSystem[nodeName]['KeyInfo'][mKey]['ISYnls'][ISYnls]
                        if ISYnls == 'nlsValues':
                            self.setupFile['editors'][editorName]['nlsKey'] = nlsName 

        self.setupFile['nodeDef'][self.name]['cmds']= {}
        if 'accepts' in self.mSystem[nodeName]['ISYnode']:
            self.setupFile['nodeDef'][self.name]['cmds']['accepts']={}
            for key in  self.mSystem[nodeName]['ISYnode']['accepts']:
                if self.checkValidNodeCommand(key, nodeName, nodeNbr ):
                    if self.mSystem[nodeName]['ISYnode']['accepts'][key]['ISYeditor'] in self.setupFile['nodeDef'][self.name]['sts']:
                        self.setupFile['nodeDef'][self.name]['cmds']['accepts'][key]= self.setupFile['nodeDef'][self.name]['sts'][self.mSystem[nodeName]['ISYnode']['accepts'][key]['ISYeditor']]
                        self.setupFile['nodeDef'][self.name]['cmds']['accepts'][key]['ISYInfo']=self.mSystem[nodeName]['ISYnode']['accepts'][key]
                    else:
                        self.setupFile['nodeDef'][self.name]['cmds']['accepts'][key]={}
                        self.setupFile['nodeDef'][self.name]['cmds']['accepts'][key]['ISYInfo']= self.mSystem[nodeName]['ISYnode']['accepts'][key]
                else:
                    LOGGER.debug('Removed "accepts" for : ' + key + ' not supported')
                    
        if 'sends' in self.mSystem[nodeName]['ISYnode']:         
            self.setupFile['nodeDef'][self.name]['cmds']['sends'] = self.mSystem[nodeName]['ISYnode']['sends']                                 
        return()

    def addSystemDefStruct(self, nodeId):
        self.keyCount = 0
        nodeId.lower()
        self.nlsKey= 'nls' + nodeId
        self.nlsKey.lower()
        #LOGGER.debug('addSystemDefStruct: ' + nodeId)
        self.setupFile['nodeDef'][ self.systemID]={}
        self.setupFile['nodeDef'][ self.systemID]['CodeId'] = nodeId
        self.setupFile['nodeDef'][ self.systemID]['nlsId'] = self.nlsKey
        self.setupFile['nodeDef'][ self.systemID]['nlsNAME']=self.mSystem[ self.systemID]['data']['mName']
        self.setupFile['nodeDef'][ self.systemID]['nlsICON']=self.mSystem[ self.systemID]['ISYnode']['nlsICON']
        self.setupFile['nodeDef'][ self.systemID]['sts']={}

        #for mKey in self.mSystem[ self.systemID]['data']: 
        for mKey in self.mSystem[ self.systemID]['GETkeysList']:    
            #make check if system has unit installed
            if self.mSystem[ self.systemID]['KeyInfo'][mKey]['ISYeditor']['ISYuom']:
                if ((self.mSystem[ self.systemID]['KeyInfo'][mKey]['ISYeditor']['ISYuom'] == 112
                   and self.mSystem[ self.systemID]['data'][mKey] != 0)
                   or self.mSystem[ self.systemID]['KeyInfo'][mKey]['ISYeditor']['ISYuom'] != 112):
                    self.keyCount = self.keyCount + 1
                    editorName = 'SYSTEM_'+str(self.keyCount)
                    nlsName = editorName
                    ISYvar = 'GV'+str(self.keyCount)
                    self.setupFile['nodeDef'][ self.systemID]['sts'][mKey]={ISYvar:editorName}
                    self.setupFile['editors'][editorName]={}
                    #self.setupFile['nls'][editorName][ISYparam]
                    for ISYparam in self.mSystem[ self.systemID]['KeyInfo'][mKey]['ISYeditor']:
                        if self.mSystem[ self.systemID]['KeyInfo'][mKey]['ISYeditor'][ISYparam]!= None:
                            self.setupFile['editors'][editorName][ISYparam]=self.mSystem[ self.systemID]['KeyInfo'][mKey]['ISYeditor'][ISYparam]

                    if self.mSystem[ self.systemID]['KeyInfo'][mKey]['ISYnls']:
                        self.setupFile['nls'][nlsName]={}
                    for ISYnls in self.mSystem[ self.systemID]['KeyInfo'][mKey]['ISYnls']:
                        #LOGGER.debug( mKey + ' ' + ISYnls)
                        if  self.mSystem[ self.systemID]['KeyInfo'][mKey]['ISYnls'][ISYnls]:      
                            self.setupFile['nls'][nlsName][ISYnls] = self.mSystem[ self.systemID]['KeyInfo'][mKey]['ISYnls'][ISYnls]
                            if ISYnls == 'nlsValues':
                                self.setupFile['editors'][editorName]['nlsKey'] = nlsName
        
        self.setupFile['nodeDef'][ self.systemID]['cmds']={}
        if 'accepts' in self.mSystem[ self.systemID]['ISYnode']:
            self.setupFile['nodeDef'][ self.systemID]['cmds']['accepts'] = {}
            for key in  self.mSystem[ self.systemID]['ISYnode']['accepts']:     
                if self.mSystem[ self.systemID]['ISYnode']['accepts'][key]['ISYeditor'] in self.setupFile['nodeDef'][ self.systemID]['sts']:
                    mVal = self.mSystem[ self.systemID]['ISYnode']['accepts'][key]['ISYeditor']
                    self.setupFile['nodeDef'][ self.systemID]['cmds']['accepts'][key]= self.setupFile['nodeDef'][ self.systemID]['sts'][mVal]
                    self.setupFile['nodeDef'][ self.systemID]['cmds']['accepts'][key]['ISYInfo']=self.mSystem[ self.systemID]['ISYnode']['accepts'][key]
                else:
                    self.setupFile['nodeDef'][ self.systemID]['cmds']['accepts'][key]= {}
                    self.setupFile['nodeDef'][ self.systemID]['cmds']['accepts'][key]['ISYInfo']= self.mSystem[ self.systemID]['ISYnode']['accepts'][key]   
        if 'sends' in self.mSystem[ self.systemID]['ISYnode']:
            self.setupFile['nodeDef'][ self.systemID]['cmds']['sends']=self.mSystem[ self.systemID]['ISYnode']['sends']                              
        return()



    def getNodeCapability (self, nodeKey, nodeNbr):    
        #LOGGER.debug ('getNodeCapability') 
        self.keyDict = {}
        self.GETkeysList = []
        self.PUTkeysList = []
        for mKey in self.mSystem[nodeKey]['KeyInfo']:
            if mKey == 'mCapability':
                if 'GETstr' in self.mSystem[nodeKey]['KeyInfo']['mCapability']:
                    GETStr =self.IP+self.mSystem[nodeKey]['KeyInfo']['mCapability']['GETstr']+str(nodeNbr)+'?'+ self.APIStr 
                    try:
                        Nodep = requests.get(GETStr)
                        if str(Nodep) == self.RESPONSE_OK:
                            #self.GETkeysList.append(mKey)
                            tempKeys= Nodep.json()
                            for key in tempKeys:
                                #zones      
                                if key == 'operative_temperature':
                                    status = self.checkGETNode( nodeKey, nodeNbr, 'mTemp')   
                                    if status['statusOK'] == True:
                                        self.keyDict['mTemp'] = tempKeys['operative_temperature']
                                    else:
                                        self.keyDict['mTemp'] = 0
                                    status = self.checkGETNode( nodeKey, nodeNbr, 'mSetpoint')   
                                    if status['statusOK'] == True:
                                        self.keyDict['mSetpoint'] = tempKeys['operative_temperature']
                                    else:
                                        self.keyDict['mSetpoint'] = 0                                    
                                elif key == 'air_temperature':                            
                                    status = self.checkGETNode( nodeKey, nodeNbr, 'mAirTemp')   
                                    if status['statusOK'] == True:
                                        self.keyDict['mAirTemp'] = tempKeys["air_temperature"]
                                    else:
                                        self.keyDict[''] = 0   
                                elif key == 'relative_humidity':                            
                                    status = self.checkGETNode( nodeKey, nodeNbr, 'mHumSetpointRH')   
                                    if status['statusOK'] == True:
                                        self.keyDict['mHumSetpointRH'] = tempKeys['relative_humidity']
                                    else:
                                        self.keyDict['mHumSetpointRH'] = 0                                       
                                    status = self.checkGETNode( nodeKey, nodeNbr, 'mHumSetpointDP')   
                                    if status['statusOK'] == True:
                                        self.keyDict['mHumSetpointDP'] = tempKeys['relative_humidity']
                                    else:
                                        self.keyDict['mHumSetpointDP'] = 0                                       
                                    status = self.checkGETNode(nodeKey, nodeNbr, 'mDehumSetpointRH')   
                                    if status['statusOK'] == True:
                                        self.keyDict['mDehumSetpointRH'] = tempKeys['relative_humidity']
                                    else:
                                        self.keyDict['mDehumSetpointRH'] = 0                                       
                                    status = self.checkGETNode(nodeKey,  nodeNbr, 'mDehumSetpointDP')   
                                    if status['statusOK'] == True:
                                        self.keyDict['mDehumSetpointDP'] = tempKeys['relative_humidity']
                                    else:
                                        self.keyDict['mDehumSetpointDP'] = 0                                       
                                    status = self.checkGETNode( nodeKey, nodeNbr, 'mCurrentSetpointRH')   
                                    if status['statusOK'] == True:
                                        self.keyDict['mCurrentSetpointRH'] = tempKeys['relative_humidity']
                                    else:
                                        self.keyDict['mCurrentSetpointRH'] = 0  
                                    status = self.checkGETNode( nodeKey, nodeNbr, 'mCurrentSetpointDP')   
                                    if status['statusOK'] == True:
                                        self.keyDict['mCurrentSetpointDP'] = tempKeys['relative_humidity']    
                                    else:
                                        self.keyDict['mCurrentSetpointDP'] = 0                                                                          
                                    status = self.checkGETNode( nodeKey, nodeNbr, 'mHumidity')   
                                    if status['statusOK'] == True:
                                        self.keyDict['mHumidity'] = tempKeys['relative_humidity']      
                                    else:
                                        self.keyDict['mHumidity'] = 0                                      
                                elif key == 'dewpoint':
                                    status = self.checkGETNode( nodeKey, nodeNbr, 'mDewPoint')   
                                    if status['statusOK'] == True:
                                        self.keyDict['mDewPoint'] = tempKeys['dewpoint'] 
                                    else:
                                        self.keyDict['mDewPoint'] = 0                                        
                                elif key == 'co2':
                                    status = self.checkGETNode( nodeKey, nodeNbr, 'mCO2')   
                                    if status['statusOK'] == True:
                                        self.keyDict['mCO2'] = tempKeys['co2']   
                                    else:
                                        self.keyDict['mCO2'] = 0                                      
                                    status = self.checkGETNode( nodeKey, nodeNbr, 'mAirQuality')   
                                    if status['statusOK'] == True:
                                        self.keyDict['mAirQuality'] = tempKeys['co2']          
                                    else:
                                        self.keyDict['mAirQuality'] = 0                                                                          
                                elif key == 'voc':
                                    status = self.checkGETNode( nodeKey, nodeNbr, 'mVoc')   
                                    if status['statusOK'] == True:
                                        self.keyDict['mVoc'] = tempKeys['voc']   
                                    else:
                                        self.keyDict['mVoc'] = 0              
                                #ATUs
                                elif key == 'exhaust air extraction':
                                    # Not currently supported   - no correspinding
                                    None
        
                                elif key == 'freecooling':
                                    # Not currently supported  - no correspinding value
                                    None
                                
                                elif key == 'convective integration':
                                    status = self.checkGETNode( nodeKey, nodeNbr,  'mINTOn')   
                                    if status['statusOK'] == True:
                                        if isinstance(tempKeys['convective integration'], int):
                                            self.keyDict['mINTOn'] = tempKeys['convective integration']
                                    else:
                                        self.keyDict['mINTOn'] = 0
                                elif key == 'HRV':
                                    status = self.checkGETNode( nodeKey, nodeNbr,  'mHRVOn')   
                                    if status['statusOK'] == True:
                                        if isinstance(tempKeys['HRV'], int):
                                            self.keyDict['mHRVOn'] = tempKeys['HRV']
                                    else:
                                        self.keyDict['mHRVOn'] = 0                            

                                elif key == 'humidification':  
                                    status = self.checkGETNode( nodeKey, nodeNbr,  'mHUMOn')   
                                    if status['statusOK'] == True:
                                        if isinstance(tempKeys['humidification'], int):
                                            self.keyDict['mHUMOn'] = tempKeys['humidification']
                                    else:
                                        self.keyDict['mHUMOn'] = 0   
                                    status = self.checkGETNode( nodeKey, nodeNbr,  'mHumidityStatus')   
                                    #need to be verified
                                    if status['statusOK'] == True:
                                        if isinstance(tempKeys['humidification'], int):
                                            self.keyDict['mHumidityStatus'] = tempKeys['humidification']
                                    else:
                                        self.keyDict['mHumidityStatus'] = 0   
                                    status = self.checkGETNode( nodeKey, nodeNbr,  'mHumSetpointRH')   
                                    #need to be verified
                                    if status['statusOK'] == True:
                                        if isinstance(tempKeys['humidification'], int):
                                            self.keyDict['mHumSetpointRH'] = tempKeys['humidification']
                                    else:
                                        self.keyDict['mHumSetpointRH'] = 0   
                                    status = self.checkGETNode( nodeKey, nodeNbr,  'mHumSetpointDP')   
                                    #need to be verified
                                    if status['statusOK'] == True:
                                        if isinstance(tempKeys['humidification'], int):
                                            self.keyDict['mHumSetpointDP'] = tempKeys['humidification']
                                    else:
                                        self.keyDict['mHumSetpointDP'] = 0   
                                elif key == 'dehumidification':
                                    status = self.checkGETNode( nodeKey, nodeNbr,  'mNTDOn')  
                                    if status['statusOK'] == True:
                                        if isinstance(tempKeys['dehumidification'], int):
                                            self.keyDict['mNTDOn'] = tempKeys['dehumidification']
                                    else:
                                        self.keyDict['mNTDOn'] = 0 
                                    status = self.checkGETNode( nodeKey, nodeNbr,  'mDehumudityStatus')  
                                    if status['statusOK'] == True:
                                        if isinstance(tempKeys['dehumidification'], int):
                                            self.keyDict['mDehumudityStatus'] = tempKeys['dehumidification']
                                    else:
                                        self.keyDict['mDehumudityStatus'] = 0 
                                    status = self.checkGETNode( nodeKey, nodeNbr,  'mDehumSetpointRH')  
                                    if status['statusOK'] == True:
                                        if isinstance(tempKeys['dehumidification'], int):
                                            self.keyDict['mDehumSetpointRH'] = tempKeys['dehumidification']
                                    else:
                                        self.keyDict['mDehumSetpointRH'] = 0 
                                    status = self.checkGETNode( nodeKey, nodeNbr,  'mDehumSetpointDP')  
                                    if status['statusOK'] == True:
                                        if isinstance(tempKeys['dehumidification'], int):
                                            self.keyDict['mDehumSetpointDP'] = tempKeys['dehumidification']
                                    else:
                                        self.keyDict['mDehumSetpointDP'] = 0 

                    except:
                        LOGGER.error(key + ' unknown keyword')

            elif ((self.mSystem[nodeKey]['KeyInfo'][mKey]['GETstr'] != None) ):
                data = self.pullNodeDataIndividual(nodeNbr, nodeKey,  mKey)
                if data['statusOK'] and not(data['data'] in self.NaNlist) and (isinstance(data['data'], float) or isinstance(data['data'], int)):
                    # mKey used by ISY
                    if self.mSystem[nodeKey]['KeyInfo'][mKey]['ISYeditor']['ISYuom'] != None:
                        self.GETkeysList.append(mKey)
                        temp=data['data']
                        if self.mSystem[nodeKey]['KeyInfo'][mKey]['PUTstr']!=None:
                            data =  self.PUTNodeData( nodeKey, nodeNbr, mKey, temp)
                            if data['statusOK']:
                                self.PUTkeysList.append(mKey)
                            else:
                                LOGGER.error( 'Removed ' + mKey + 'from PUT commands')
        #remove capability for GET list
        for mKey in self.keyDict:
            if self.keyDict[mKey] == 0 and mKey in self.GETkeysList:
                self.GETkeysList.remove(mKey)
            if self.keyDict[mKey] == 0 and mKey in self.PUTkeysList:
                self.PUTkeysList.remove(mKey)

        self.mSystem[nodeKey]['SensorCapability'][nodeNbr] = self.keyDict
        self.mSystem[nodeKey]['GETkeysList'][nodeNbr] = []
        self.mSystem[nodeKey]['GETkeysList'][nodeNbr].extend(self.GETkeysList)
        self.mSystem[nodeKey]['PUTkeysList'][nodeNbr] = []
        self.mSystem[nodeKey]['PUTkeysList'][nodeNbr].extend(self.PUTkeysList)
    
    def GETSystemData(self, mKey):
        sysData= {}
        #LOGGER.debug('GETSystem: ' + mKey )
        GETStr = self.IP+self.mSystem[ self.systemID]['KeyInfo'][mKey]['GETstr'] + '?' + self.APIStr 
        #LOGGER.debug( GETStr)
        try:
            systemTemp = requests.get(GETStr)
            #LOGGER.debug(str(systemTemp))
            if str(systemTemp) == self.RESPONSE_OK:
                systemTemp = systemTemp.json()
                #LOGGER.debug(systemTemp)
                self.mSystem[ self.systemID]['data'][mKey] = systemTemp[str(list(systemTemp.keys())[0])]

                sysData['data'] = self.mSystem[ self.systemID]['data'][mKey]
                if sysData['data'] in self.NaNlist:
                    sysData['statusOK'] = False
                    sysData['error'] = 'NaN received'
                else:
                    sysData['statusOK'] = True 

            else:
                LOGGER.debug(str(mKey) + ' error')
                sysData['statusOK'] = False
                sysData['error'] = str(systemTemp)
                #self.systemDict[mKey] = -1
            return(sysData) #No data for given keyword - remove from list 
        except:
            LOGGER.error('System GET operation failed for :' + mKey)
            sysData['statusOK'] = False
            sysData['error'] = 'EXCEPT: System GET operation failed for :' + mKey  
            return(sysData)

    def PUTSystemData(self, mKey, value):
            sysData= {}
            #LOGGER.debug('PUT System: {' + mKey +':'+str(value)+'}' )
            #mData = defaultdict(list)
            if mKey in self.mSystem[ self.systemID]['KeyInfo']:
                if self.mSystem[ self.systemID]['KeyInfo'][mKey]['PUTstr'] == None:
                    sysData['statusOK'] = False
                    sysData['error'] = 'Not able to PUT Key: '+ mKey + ' value:' + str( value )
                    LOGGER.error('Error '+ sysData)    
                    return(sysData)                     
                else:
                    PUTStr = self.IP+self.mSystem[ self.systemID]['KeyInfo'][mKey]['PUTstr']
                    mData = {'value':value, self.APIKey : self.APIKeyVal}
                    try:
                        resp = requests.put(PUTStr, json=mData)
                        #LOGGER.debug(resp)
                        if str(resp) != self.RESPONSE_OK:
                            sysData['statusOK'] = False
                            sysData['error'] = str(resp)+ ': Not able to PUT Key: '+ mKey + ' value:' + str( value )
                        else:
                            sysData['statusOK'] = True
                            sysData['data'] = value
                        #LOGGER.debug(sysData)    
                        return(sysData)          
                    except:
                        sysData['statusOK'] = False
                        sysData['error'] = 'System PUT operation failed for :' + mKey + ' '+ str(value)
                        return(sysData)
  
    def GETNodeData(self, mNodeKey, nodeNbr, mKey):
        #LOGGER.debug('GETNodeData: ' + mNodeKey + ' ' + str(nodeNbr)+ ' ' + mKey)
        nodeData = {}

        if 'GETstr' in self.mSystem[mNodeKey]['KeyInfo'][mKey]:
            GETStr =self.IP+self.mSystem[mNodeKey]['KeyInfo'][mKey]['GETstr']+str(nodeNbr)+'?'+ self.APIStr 
            try:
                Nodep = requests.get(GETStr)
                if str(Nodep) == self.RESPONSE_OK:
                    Nodep = Nodep.json()
                    nodeData['data']  = Nodep[str(list(Nodep.keys())[0])]
                    if nodeData in self.NaNlist:
                        nodeData['statusOK'] = False
                        nodeData['error'] = 'NaN received'
                    else:
                        nodeData['dataAll'] = Nodep
                        nodeData['statusOK'] =True
                    if nodeNbr in self.mSystem[mNodeKey]['data']:
                        if mKey in self.mSystem[mNodeKey]['data'][nodeNbr]:
                            self.mSystem[mNodeKey]['data'][nodeNbr][mKey] = nodeData['data']
                        else:
                            self.mSystem[mNodeKey]['data'][nodeNbr].update({mKey : nodeData['data']})
                    else:
                        temp = {}
                        temp[nodeNbr] = {mKey : nodeData['data']}
                        self.mSystem[mNodeKey]['data'].update(temp)

                elif str(Nodep) == self.RESPONSE_NO_SUPPORT:
                    temp1 =  Nodep.content
                    res_dict = json.loads(temp1.decode('utf-8')) 
                    nodeData['error'] = str(Nodep) + ': Error: '+ str(res_dict.values()) + ' Node ' + str(nodeNbr) + ' for id: ' + str(mKey)
                    nodeData['statusOK'] =False
                elif str(Nodep) == self.RESPONSE_NO_RESPONSE:
                    nodeData['error'] = str(Nodep) + ': Error: No response from API:  Node ' + str(nodeNbr) + ' for id: ' + str(mKey)
                    nodeData['statusOK'] =False
                else:
                    nodeData['error'] = str(Nodep) + ': Error: Unknown: Node ' + str(nodeNbr) + ' for id: ' + str(mKey)
                    nodeData['statusOK'] =False
            except:
                LOGGER.error ('Error GETNodeData - try/except')
        else: 
                nodeData['error'] = 'Does not support keyword: ' + mKey
                nodeData['statusOK'] =False
        return(nodeData)   

    def PUTNodeData(self, mNodeKey, nodeNbr, mKey, value):
        nodeData = {}
        if 'PUTstr' in self.mSystem[mNodeKey]['KeyInfo'][mKey]:
            PUTStr = self.IP + self.mSystem[mNodeKey]['KeyInfo'][mKey]['PUTstr']
            #LOGGER.debug('PUT str: ' + PUTStr + str(value))
            mData = {'id':nodeNbr, 'value': value, self.APIKey : self.APIKeyVal}
            try:
                resp = requests.put(PUTStr, json=mData)
                if str(resp) == self.RESPONSE_OK:
                    self.mSystem[mNodeKey]['data'][nodeNbr][mKey] = value
                    nodeData['statusOK'] = True
                elif str(resp) == self.RESPONSE_NO_SUPPORT:
                    temp1 =  resp.content
                    res_dict = json.loads(temp1.decode('utf-8')) 
                    nodeData['error'] = str(resp) + ': Not able to PUT key: '+ str(res_dict.values()) + ' Node ' + str(id) + ' for key: ' + str(mKey) + ' value:', str(value)
                    LOGGER.debug(nodeData['error'])
                    nodeData['statusOK'] =False
                elif str(resp) == self.RESPONSE_NO_RESPONSE:
                    nodeData['error'] = str(resp) + ': Error: No response from API for key: ' + str(mKey)+ ' value:', str(value)
                    LOGGER.debug(nodeData['error'])
                    nodeData['statusOK'] =False
                else:
                    nodeData['error'] = str(resp) + ': Error: Unknown:for key: ' + str(mKey)+ ' value:', str(value)
                    LOGGER.debug(nodeData['error'])
                    nodeData['statusOK'] =False
            except:
                LOGGER.error('Error PUTNodeData try/cartch')
        else:
            nodeData['error'] = 'Node ' + mNodeKey + ' does not accept keyword: ' + mKey
            LOGGER.error(nodeData['error'])
            nodeData['nodeDataOK'] =False
        return(nodeData)

 
    # New Functions Need to be tested
    def getNodeKeys (self, nodeNbr, nodeKey, cmdKey):
        keys = []
        if len(self.mSystem[nodeKey]['GETkeysList'][nodeNbr]) == 0:
            LOGGER.error('NodeCapability must be run first')
        else:
            if cmdKey == 'PUTstr':
                for mKey in self.mSystem[nodeKey]['PUTkeysList'][nodeNbr]:
                    if self.mSystem[nodeKey]['KeyInfo'][mKey][cmdKey] != None:
                        keys.append(mKey)
            else:
                for mKey in self.mSystem[nodeKey]['GETkeysList'][nodeNbr]:
                    if self.mSystem[nodeKey]['KeyInfo'][mKey][cmdKey] != None:
                        keys.append(mKey)             
        return(keys)

    def updateNodeData(self, nodeNbr, nodeKey):
        #LOGGER.info('updatNodeData: ' + str(nodeNbr) + ' ' + nodeKey)
        Data = {}
        dataOK = True
        supportedPullKeys = self.mSystem[nodeKey]['GETkeysList'][nodeNbr]
        for mKey in supportedPullKeys:
            #LOGGER.debug('GET ' + mKey + ' in zone ' + str(nodeNbr))
            Data = self.pullNodeDataIndividual(nodeNbr, nodeKey,  mKey)
            if not(Data['statusOK']):
                dataOK = False
                #LOGGER.debug('Error GET' + Data['error'])
        return(dataOK)
    
    def pullNodeDataIndividual(self, nodeNbr, nodeKey, mKey): 
        Data = self.GETNodeData(nodeKey, nodeNbr, mKey)
        return(Data)
    
    def checkGETNode(self,  nodeKey, nodeNbr, mKey): 
        nodeData = {}
        if 'GETstr' in self.mSystem[nodeKey]['KeyInfo'][mKey]:
            GETStr =self.IP+self.mSystem[nodeKey]['KeyInfo'][mKey]['GETstr']+str(nodeNbr)+'?'+ self.APIStr 
            try:
                Nodep = requests.get(GETStr)
                if str(Nodep) == self.RESPONSE_OK:
                    Nodep = Nodep.json()
                    nodeData['data']  = Nodep[str(list(Nodep.keys())[0])] 
                    if nodeData['data'] in self.NaNlist:
                        nodeData['statusOK'] =False
                        nodeData['error'] = 'NaN received'
                    else:
                        nodeData['statusOK'] =True
                elif str(Nodep) == self.RESPONSE_NO_SUPPORT:
                    temp1 =  Nodep.content
                    res_dict = json.loads(temp1.decode('utf-8')) 
                    nodeData['error'] = str(Nodep) + ': Error: '+ str(res_dict.values()) + ' Node ' + str(nodeNbr) + ' for id: ' + str(mKey)
                    nodeData['statusOK'] =False
                elif str(Nodep) == self.RESPONSE_NO_RESPONSE:
                    nodeData['error'] = str(Nodep) + ': Error: No response from API:  Node ' + str(nodeNbr) + ' for id: ' + str(mKey)
                    nodeData['statusOK'] =False
                else:
                    nodeData['error'] = str(Nodep) + ': Error: Unknown: Node ' + str(nodeNbr) + ' for id: ' + str(mKey)
                    nodeData['statusOK'] =False
            except:
                LOGGER.error('error checkGETNode try/except')
        else: 
                nodeData['error'] = 'Does not support keyword: ' + mKey
                nodeData['statusOK'] =False
        return(nodeData)   

    def pushNodeDataIndividual(self, NodeNbr, NodeKey, mKey, value):
       # LOGGER.debug('pushZoneDataIndividual: ' +str(NodeNbr)  + ' ' + mKey + ' ' + str(value))  
        nodeData = {}
        nodeData= self.PUTNodeData(NodeKey, NodeNbr, mKey, value)
        if nodeData['statusOK']:
            return(True)
        else:
            LOGGER.error(nodeData['error'])
            return(False)

    #Setup file generation 
    def createSetupFiles(self, nodeDefFileName, editorFileName, nlsFileName):
        #LOGGER.debug ('Create Setup Files')
        status = True
        try:
            #LOGGER.debug('opening files')
            if not(os.path.exists('./profile')):
                os.mkdir('./profile')       
            if not(os.path.exists('./profile/editor')):
                os.mkdir('./profile/editor')
            if not(os.path.exists('./profile/nls')):
                os.mkdir('./profile/nls')           
            if not(os.path.exists('./profile/nodedef')):
                os.mkdir('./profile/nodedef')
            nodeFile = open(nodeDefFileName, 'w+')
            editorFile = open(editorFileName, 'w+')
            nlsFile = open(nlsFileName, 'w+')
            #LOGGER.debug('Opening Files OK')

            editorFile.write('<editors> \n')
            nodeFile.write('<nodeDefs> \n')
            for node in self.setupFile['nodeDef']:
                nodeDefStr ='   <nodeDef id="' + self.setupFile['nodeDef'][node]['CodeId']+'" '+ 'nls="'+self.setupFile['nodeDef'][node]['nlsId']+'">\n'
                #LOGGER.debug(nodeDefStr)
                nodeFile.write(nodeDefStr)
                nodeFile.write('      <editors />\n')
                nodeFile.write('      <sts>\n')
                #nlsStr = 'ND-'+self.setupFile['nodeDef'][node]['nlsId']+'-NAME = '+self.setupFile['nodeDef'][node]['nlsNAME']+ '\n'
                nlsStr = 'ND-'+self.setupFile['nodeDef'][node]['CodeId']+'-NAME = '+self.setupFile['nodeDef'][node]['nlsNAME']+ '\n'
                nlsFile.write(nlsStr)
                #nlsStr = 'ND-'+self.setupFile['nodeDef'][node]['nlsId']+'-ICON = '+self.setupFile['nodeDef'][node]['nlsICON']+ '\n'
                nlsStr = 'ND-'+self.setupFile['nodeDef'][node]['CodeId']+'-ICON = '+self.setupFile['nodeDef'][node]['nlsICON']+ '\n'
                nlsFile.write(nlsStr)
                for acceptCmd in self.setupFile['nodeDef'][node]['cmds']['accepts']:
                    cmdName =  self.setupFile['nodeDef'][node]['cmds']['accepts'][acceptCmd]['ISYInfo']['ISYtext']
                    nlsStr = 'CMD-' + self.setupFile['nodeDef'][node]['nlsId']+'-'+acceptCmd+'-NAME = ' + cmdName +'\n'
                    nlsFile.write(nlsStr)
                    #LOGGER.debug(nlsStr)

                for status in self.setupFile['nodeDef'][node]['sts']:
                    for statusId in self.setupFile['nodeDef'][node]['sts'][status]:
                        if statusId != 'ISYInfo':
                            nodeName = self.setupFile['nodeDef'][node]['sts'][status][statusId]
                            nodeDefStr =  '         <st id="' + statusId+'" editor="'+nodeName+'" />\n'
                            #LOGGER.debug(nodeDefStr)
                            nodeFile.write(nodeDefStr)
                            editorFile.write( '  <editor id = '+'"'+nodeName+'" > \n')
                            editorStr = '     <range '
                            for key in self.setupFile['editors'][nodeName]:
                                if key == 'ISYsubset':
                                    editorStr = editorStr + ' subset="'+ str(self.setupFile['editors'][nodeName][key])+'"'
                                elif key == 'ISYuom':
                                    editorStr = editorStr + ' uom="'+ str(self.setupFile['editors'][nodeName][key])+'"'
                                elif key == 'ISYmax':
                                    editorStr = editorStr + ' max="'+ str(self.setupFile['editors'][nodeName][key])+'"'
                                elif key == 'ISYmin': 
                                    editorStr = editorStr + ' min="'+ str(self.setupFile['editors'][nodeName][key])+'"'
                                elif key == 'ISYstep':
                                    editorStr = editorStr + ' step="'+ str(self.setupFile['editors'][nodeName][key])+'"'                  
                                elif key == 'ISYprec': 
                                    editorStr = editorStr + ' prec="'+ str(self.setupFile['editors'][nodeName][key])+'"'
                                elif key == 'ISYsubset': 
                                    editorStr = editorStr + ' subset="'+ str(self.setupFile['editors'][nodeName][key])+'"'
                                elif key == 'nlsKey': 
                                    nlsEditorKey = str(self.setupFile['editors'][nodeName][key])
                                    editorStr = editorStr + ' nls="'+ nlsEditorKey+'"'
                                else:
                                    LOGGER.error('unknown editor keyword: ' + str(key))
                            editorStr = editorStr + ' />\n'
                            #LOGGER.debug(editorStr)
                            editorFile.write(editorStr)
                            editorFile.write('</editor>\n')

                        for nlsInfo in self.setupFile['nls'][nodeName]:
                            if statusId != 'ISYInfo':
                                if nlsInfo == 'nlsTEXT':
                                    nlsStr = 'ST-' + self.setupFile['nodeDef'][node]['nlsId']+'-'+statusId+'-NAME = '
                                    nlsStr = nlsStr + self.setupFile['nls'][nodeName][nlsInfo] + '\n'
                                    nlsFile.write(nlsStr)
                                elif nlsInfo == 'nlsValues':
                                    nlsValues = 0
                                    for key in self.setupFile['nls'][nodeName][nlsInfo]:
                                        nlsStr = nlsEditorKey+'-'+str(nlsValues)+' = '+self.setupFile['nls'][nodeName][nlsInfo][key]+'\n'
                                        nlsFile.write(nlsStr)
                                        nlsValues = nlsValues + 1
                                #LOGGER.debug(nlsStr)

                nodeFile.write('      </sts>\n')
                nodeFile.write('      <cmds>\n')                
                nodeFile.write('         <sends>\n')            
                if self.setupFile['nodeDef'][node]['cmds']:
                    if len(self.setupFile['nodeDef'][node]['cmds']['sends']) != 0:
                        for sendCmd in self.setupFile['nodeDef'][node]['cmds']['sends']:
                            cmdStr = '            <cmd id="' +sendCmd +'" /> \n'
                            #LOGGER.debug(cmdStr)
                            nodeFile.write(cmdStr)
                nodeFile.write('         </sends>\n')               
                nodeFile.write('         <accepts>\n')      
                if self.setupFile['nodeDef'][node]['cmds']:
                    if 'accepts' in self.setupFile['nodeDef'][node]['cmds']:
                        for acceptCmd in self.setupFile['nodeDef'][node]['cmds']['accepts']:
                            
                            if len(self.setupFile['nodeDef'][node]['cmds']['accepts'][acceptCmd]) != 1:
                                for key in self.setupFile['nodeDef'][node]['cmds']['accepts'][acceptCmd]:
                                    if key != 'ISYInfo':
                                        cmdStr = '            <cmd id="' +acceptCmd+'" > \n'     
                                        nodeFile.write(cmdStr)  
                                        cmdStr = '               <p id="" editor="'
                                        cmdStr = cmdStr + self.setupFile['nodeDef'][node]['cmds']['accepts'][acceptCmd][key]+ '" init="' + key +'" /> \n' 
                                        #LOGGER.debug(cmdStr)                              
                                        nodeFile.write(cmdStr)
                                        nodeFile.write('            </cmd> \n')
                            else:
                                cmdStr = '            <cmd id="' +acceptCmd+'" /> \n' 
                                #LOGGER.debug(cmdStr)
                                nodeFile.write(cmdStr)  
                nodeFile.write('         </accepts>\n')                   

                nodeFile.write('      </cmds>\n')                
                                    
                nodeFile.write('   </nodeDef> \n')

            nodeFile.write('</nodeDefs> \n' )
            nodeFile.close()
            editorFile.write('</editors> \n')
            editorFile.close()
            nlsFile.close()
        
        except:
            LOGGER.error('something went wrong in creating setup files try/except')
            status = False
            nodeFile.close()
            editorFile.close()
            nlsFile.close()
        return(status)



    #System
    def updateSystemData(self, level):
        LOGGER.debug('Update Messana Sytem Data')
        sysData = {}
        DataOK = True
       
        if level == 'active':
            for mKey in self.systemActiveKeys():
                sysData= self.pullSystemDataIndividual(mKey)
                if not(sysData['statusOK']):
                    LOGGER.error('Error System Active GET: ' + mKey)
                    DataOK = False  
        elif level == 'all':
            for mKey in self.systemPullKeys():
                sysData= self.pullSystemDataIndividual(mKey)
                if not(sysData['statusOK']):
                    LOGGER.error('Error System Active GET: ' + mKey)
                    DataOK = False 
        else:
            LOGGER.error('Unknown level: ' + level)
            DataOK = False               
        return(DataOK)

    #pretty bad solution - just checking if a value can be extracted
    def checkMessanaConnection(self):
        sysData = self.GETSystemData('mApiVer') 
        return (sysData['statusOK'])
    


    def pullSystemDataIndividual(self, mKey):
        #LOGGER.debug('MessanaInfo pull System Data: ' + mKey)
        return(self.GETSystemData(mKey) )
                 

    def pushSystemDataIndividual(self, mKey, value):
        sysData={}
        #LOGGER.debug('MessanaInfo push System Data: ' + mKey)       
        sysData = self.PUTSystemData(mKey, value)
        if sysData['statusOK']:
            return(True)
        else:
            LOGGER.error(sysData['error'])
            return(False) 

     
    def getSystemCapability(self):
        GETkeysList=[]
        PUTkeysList=[]
        for mKey in self.mSystem[ self.systemID]['KeyInfo']:
            data = self.pullSystemDataIndividual(mKey)
            if data['statusOK']:
                # Parameter is used by ISY
                if self.mSystem[ self.systemID]['KeyInfo'][mKey]['ISYeditor']['ISYuom'] != None:
                    temp = data['data']
                    GETkeysList.append(mKey)
                    if self.mSystem[self.systemID]['KeyInfo'][mKey]['PUTstr'] != None:
                        if self.pushSystemDataIndividual(mKey, temp):
                            PUTkeysList.append(mKey)
        self.mSystem[self.systemID]['GETkeysList'] = []
        self.mSystem[self.systemID]['GETkeysList'].extend(GETkeysList)
        self.mSystem[self.systemID]['PUTkeysList'] = []
        self.mSystem[self.systemID]['PUTkeysList'].extend(PUTkeysList)
        

    def systemPullKeys(self):
        #LOGGER.debug('systemPullKeys')
        return(self.mSystem[self.systemID]['GETkeysList'])

    def systemPushKeys(self):
        #LOGGER.debug('systemPushKeys')
        return(self.mSystem[self.systemID]['PUTkeysList'])  
            
    def systemActiveKeys(self):
        #LOGGER.debug('systemActiveKeys')
        keys=[]
        for mKey in self.mSystem[self.systemID]['GETkeysList']:
            if self.mSystem[self.systemID]['KeyInfo'][mKey]['Active'] != None:
                keys.append(mKey)
        return(keys)  
            
    def getSystemISYValue(self, ISYkey):
        messanaKey = self.ISYmap[ self.systemID][ISYkey]['messana']
        systemPullKeys = self.systemPullKeys()
        if messanaKey in systemPullKeys:
            data = self.pullSystemDataIndividual(messanaKey)
            if data['statusOK']:
                val = data['data']        
                if val in  ['Celcius', 'Fahrenheit']:
                    if val == 'Celcius':
                        val = 0
                    else:  
                        val = 1 
                systemValue = val
                status = True
            else:
                systemValue = None
                status = False
        else:
            status = False
            systemValue = None
        return (status, systemValue)

    def PUTSystemISYValue(self, ISYkey, systemValue):
        messanaKey = self.ISYmap[ self.systemID][ISYkey]['messana']
        systemPushKeys = self.systemPushKeys()
        status = False
        if messanaKey in systemPushKeys:
            status = self.pushSystemDataIndividual(messanaKey, systemValue)
        return(status)
    
    def getMessanaSystemKey(self, ISYkey):
        return(self.ISYmap[ self.systemID][ISYkey]['messana'])

    def getSystemISYdriverInfo(self, mKey):
        info = {}
        if mKey in self.setupFile['nodeDef'][ self.systemID]['sts']:
            keys = list(self.setupFile['nodeDef'][ self.systemID]['sts'][mKey].keys())
            info['driver'] = keys[0]
            tempData =  self.GETSystemData(mKey)
            if tempData['statusOK']:
                val = tempData['data']        
                if val in  ['Celcius', 'Fahrenheit']:
                    if val == 'Celcius':
                        val = 0
                    else:  
                        val = 1 
                info['value'] = val
            else:
                info['value'] = ''
            editor = self.setupFile['nodeDef'][ self.systemID]['sts'][mKey][keys[0]]

            info['uom'] = self.setupFile['editors'][editor]['ISYuom']
        return(info)

    def getSystemSetbackISYdriver(self):
        Key = ''
        for ISYkey in self.ISYmap[ self.systemID]:
            if self.ISYmap[ self.systemID][ISYkey]['messana'] == 'mSetback':
                Key = ISYkey
        return(Key)

    def getSystemStatusISYdriver(self):
        Key = ''
        for ISYkey in self.ISYmap[ self.systemID]:
            if self.ISYmap[ self.systemID][ISYkey]['messana'] == 'mStatus':
                Key = ISYkey
        return(Key)

    def getSystemEnergySaveISYdriver(self):
        Key = ''
        for ISYkey in self.ISYmap[ self.systemID]:
            if self.ISYmap[ self.systemID][ISYkey]['messana'] == 'mEnergySaving':
                Key = ISYkey
        return(Key)       

    def systemSetStatus (self, value):
        #LOGGER.debug('systemSetstatus called')
        status = self.pushSystemDataIndividual('mStatus', value)
        return(status)

    def systemSetEnergySave (self, value):
        #LOGGER.debug('systemSetEnergySave called')
        status = self.pushSystemDataIndividual('mEnergySaving', value)
        return(status)
        
    def systemSetback (self, value):
        #LOGGER.debug('setSetback called')
        status = self.pushSystemDataIndividual('mSetback', value)
        return(status)

    def getSystemAddress(self):
        return(self.systemID)


    # Zones
    def getZoneCapability(self, zoneNbr):
        #LOGGER.debug('getZoneCapability for ' + str(zoneNbr)) 
        self.getNodeCapability(self.zoneID, zoneNbr)

    def addZoneDefStruct(self, zoneNbr, nodeId):
        self.addNodeDefStruct(zoneNbr, self.zoneID, nodeId)

    def updateZoneData(self, level, zoneNbr):
        #LOGGER.debug('updatZoneData: ' + str(zoneNbr))

        keys =[]
        if level == 'all':
            #LOGGER.debug('ALL update zone ' + str(zoneNbr))
            keys =  self.zonePullKeys(zoneNbr)
        elif level == 'active':
            #LOGGER.debug('ACTIVE update zone ' + str(zoneNbr))
            keys =  self.zoneActiveKeys(zoneNbr)
        
        self.dataOK = True
        for mKey in keys:
            self.data = self.pullZoneDataIndividual(zoneNbr, mKey)
            self.dataOK = self.dataOK and self.data['statusOK']
        return(self.dataOK)

    def pullZoneDataIndividual(self, zoneNbr, mKey): 
        #LOGGER.debug('pullZoneDataIndividual: ' +str(zoneNbr)  + ' ' + mKey)    
        return(self.pullNodeDataIndividual(zoneNbr, self.zoneID, mKey))


    def pushZoneDataIndividual(self, zoneNbr, mKey, value):
        #LOGGER.debug('pushZoneDataIndividual: ' +str(zoneNbr)  + ' ' + mKey + ' ' + str(value))  
        return(self.pushNodeDataIndividual(zoneNbr, self.zoneID, mKey, value))

    def zonePullKeys(self, zoneNbr):
        #LOGGER.debug('zonePullKeys')
        self.tempZoneKeys =  self.getNodeKeys (zoneNbr, self.zoneID, 'GETstr')
        return( self.tempZoneKeys)

    def zonePushKeys(self, zoneNbr):
        #LOGGER.debug('zonePushKeys')
        return( self.getNodeKeys (zoneNbr, self.zoneID, 'PUTstr'))
  
    def zoneActiveKeys(self, zoneNbr):
        #LOGGER.debug('zoneActiveKeys')
        return( self.getNodeKeys (zoneNbr, self.zoneID, 'Active'))

    def getZoneCount(self):
        return(self.mSystem[ self.systemID]['data']['mZoneCount'])

    def getZoneName(self, zoneNbr):
        tempName = self.pullNodeDataIndividual(zoneNbr, self.zoneID, 'mName')
        if tempName['statusOK']:
            return(tempName['data'])
        else:
            return('NA')

    def getZoneAddress(self, zoneNbr):
        return(self.zoneID + str(zoneNbr))


    def getZoneMessanaISYkey(self, ISYkey, zoneNbr):
        zoneName = self.zoneID+str(zoneNbr)
        return(self.ISYmap[zoneName][ISYkey]['messana'])

    def getZoneISYValue(self, ISYkey, zoneNbr):
        zoneName = self.zoneID+str(zoneNbr)
        messanaKey = self.ISYmap[zoneName][ISYkey]['messana']
        #systemPullKeys = self.zonePullKeys(zoneNbr)
        try:
            data = self.pullZoneDataIndividual(zoneNbr, messanaKey)
            if data['statusOK']:
                val = data['data']        
                if val in  ['Celcius', 'Fahrenheit']:
                    if val == 'Celcius':
                        val = 0
                    else:  
                        val = 1 
                systemValue = val
                status = True
            else:
                systemValue = None
                status = False
        except:
            status = False
            systemValue = None
        return (status, systemValue)


    def checkZoneCommand(self, cmd, zoneNbr):
        exists = True
        mCmd = self.mSystem[self.zoneID]['ISYnode']['accepts'][cmd]['ISYeditor']
        
        if mCmd != None:
            if mCmd in self.mSystem[self.zoneID]['SensorCapability'][zoneNbr]:
                if self.mSystem[self.zoneID]['SensorCapability'][zoneNbr][mCmd] == 0:
                    exists = False
        return(exists)



    def zoneSetStatus(self, value, zoneNbr):
        #LOGGER.debug(' zoneSetstatus called for zone: ' + str(zoneNbr))
        
        status = self.pushZoneDataIndividual(zoneNbr, 'mStatus', value)
        return(status)
 

    def getZoneStatusISYdriver(self, zoneNbr):
        #LOGGER.debug('getZoneStatusISYdriver called for zone: '+str(zoneNbr))
        
        Key = ''
        zoneName = self.zoneID+str(zoneNbr)
        for ISYkey in self.ISYmap[zoneName]:
            if self.ISYmap[zoneName][ISYkey]['messana'] == 'mStatus':
                Key = ISYkey
        return(Key)  
        

    def zoneSetEnergySave(self, value, zoneNbr):
        #LOGGER.debug(' zoneSetEnergySave called for zone: ' + str(zoneNbr))
        
        status = self.pushZoneDataIndividual(zoneNbr, 'mEnergySaving', value)
        return(status)
    
    def getZoneEnergySaveISYdriver(self, zoneNbr):
        #LOGGER.debug('getZoneEnergySaveISYdriver called for zone: '+str(zoneNbr))
        
        Key = ''
        zoneName = self.zoneID+str(zoneNbr)
        for ISYkey in self.ISYmap[zoneName]:
            if self.ISYmap[zoneName][ISYkey]['messana'] == 'mEnergySaving':
                Key = ISYkey
        return(Key)  



    def zoneSetSetpoint(self, value,  zoneNbr):
        #LOGGER.debug('zoneSetSetpoint called for zone: ' + str(zoneNbr))
        
        status = self.pushZoneDataIndividual(zoneNbr, 'mSetpoint', value)
        return(status)

    def getZoneSetPointISYdriver(self, zoneNbr):
        #LOGGER.debug('getZoneSetpointISYdriver called for zone: '+str(zoneNbr))
        
        Key = ''
        zoneName = self.zoneID+str(zoneNbr)
        for ISYkey in self.ISYmap[zoneName]:
            if self.ISYmap[zoneName][ISYkey]['messana'] == 'mSetpoint':
                Key = ISYkey
        return(Key)  
  

    def zoneEnableSchedule(self, value, zoneNbr):
        #LOGGER.debug('zoneEnableSchedule called for zone: ' + str(zoneNbr))
        
        status = self.pushZoneDataIndividual(zoneNbr, 'mScheduleOn', value)
        return(status)


    def getZoneEnableScheduleISYdriver(self, zoneNbr):
        #LOGGER.debug('getZoneEnableScheduleISYdriver called for zone: '+str(zoneNbr))
        
        Key = ''
        zoneName = self.zoneID+str(zoneNbr)
        for ISYkey in self.ISYmap[zoneName]:
            if self.ISYmap[zoneName][ISYkey]['messana'] == 'mScheduleOn':
                Key = ISYkey
        return(Key) 

    def zonesetCurrentDPt(self, value,  zoneNbr):
        #LOGGER.debug('zonesetCurrentDPt called for zone: ' + str(zoneNbr))
        
        status = self.pushZoneDataIndividual(zoneNbr, 'mCurrentSetpointDP', value)
        return(status)

    def getZonesetCurrentDPtISYdriver(self, zoneNbr):
        #LOGGER.debug('getZonesetCurrentDPtISYdriver called for zone: '+str(zoneNbr))
        
        Key = ''
        zoneName = self.zoneID+str(zoneNbr)
        for ISYkey in self.ISYmap[zoneName]:
            if self.ISYmap[zoneName][ISYkey]['messana'] == 'mCurrentSetpointDP':
                Key = ISYkey
        return(Key)  

    def zonesetCurrentRH(self, value,  zoneNbr):
        #LOGGER.debug('zonesetCurrentRH called for zone: ' + str(zoneNbr))
        
        status = self.pushZoneDataIndividual(zoneNbr, 'mCurrentSetpointRH', value)
        return(status)

    def getZonesetCurrentRHISYdriver(self, zoneNbr):
        #LOGGER.debug('getZonesetCurrentRHISYdriver called for zone: '+str(zoneNbr))
        
        Key = ''
        zoneName = self.zoneID+str(zoneNbr)
        for ISYkey in self.ISYmap[zoneName]:
            if self.ISYmap[zoneName][ISYkey]['messana'] == 'mCurrentSetpointRH':
                Key = ISYkey
        return(Key)  

    def zonesetDehumDpt(self, value,  zoneNbr):
        #LOGGER.debug('zonesetDehumDpt called for zone: ' + str(zoneNbr))
        
        status = self.pushZoneDataIndividual(zoneNbr, 'mDehumSetpointDP', value)
        return(status)

    def getZonesetDehumDPtISYdriver(self, zoneNbr):
        #LOGGER.debug('getZonesetDehumDPtISYdriver called for zone: '+str(zoneNbr))
        Key = ''
        zoneName = self.zoneID+str(zoneNbr)
        for ISYkey in self.ISYmap[zoneName]:
            if self.ISYmap[zoneName][ISYkey]['messana'] == 'mDehumSetpointDP':
                Key = ISYkey
        return(Key)  

    def zonesetDehumRH(self, value,  zoneNbr):
        #LOGGER.debug('zonesetDehumRH called for zone: ' + str(zoneNbr))
        
        status = self.pushZoneDataIndividual(zoneNbr, 'mDehumSetpointRH', value)
        return(status)

    def getZonesetDehumRHISYdriver(self, zoneNbr):
        #LOGGER.debug('getZonesetDehumRHISYdriver called for zone: '+str(zoneNbr))
        Key = ''
        zoneName = self.zoneID+str(zoneNbr)
        for ISYkey in self.ISYmap[zoneName]:
            if self.ISYmap[zoneName][ISYkey]['messana'] == 'mDehumSetpointRH':
                Key = ISYkey
        return(Key)  

    def zonesetHumRH(self, value,  zoneNbr):
        #LOGGER.debug('zonesetHumRH called for zone: ' + str(zoneNbr))
        
        status = self.pushZoneDataIndividual(zoneNbr, 'mHumSetpointRH', value)
        return(status)

    def getZonesetHumRHISYdriver(self, zoneNbr):
        #LOGGER.debug('getZonesetHumRHISYdriver called for zone: '+str(zoneNbr))
        Key = ''
        zoneName = self.zoneID+str(zoneNbr)
        for ISYkey in self.ISYmap[zoneName]:
            if self.ISYmap[zoneName][ISYkey]['messana'] == 'mHumSetpointRH':
                Key = ISYkey
        return(Key)  

    def zonesetHumDpt(self, value,  zoneNbr):
        #LOGGER.debug('zonesetDehumDpt called for zone: ' + str(zoneNbr))
        
        status = self.pushZoneDataIndividual(zoneNbr, 'mHumSetpointDP', value)
        return(status)

    def getZonesetHumDPtISYdriver(self, zoneNbr):
        #LOGGER.debug('getZonesetDehumDPtISYdriver called for zone: '+str(zoneNbr))
        Key = ''
        zoneName = self.zoneID+str(zoneNbr)
        for ISYkey in self.ISYmap[zoneName]:
            if self.ISYmap[zoneName][ISYkey]['messana'] == 'mHumSetpointDP':
                Key = ISYkey
        return(Key)  

    def zonesetCO2 (self, value,  zoneNbr):
        #LOGGER.debug('zonesetDehumDpt called for zone: ' + str(zoneNbr))
        
        status = self.pushZoneDataIndividual(zoneNbr, 'mCO2', value)
        return(status)

    def getZonesetCO2ISYdriver(self, zoneNbr):
        #LOGGER.debug('getZonesetDehumDPtISYdriver called for zone: '+str(zoneNbr))
        Key = ''
        zoneName = self.zoneID+str(zoneNbr)
        for ISYkey in self.ISYmap[zoneName]:
            if self.ISYmap[zoneName][ISYkey]['messana'] == 'mCO2':
                Key = ISYkey
        return(Key)  

    def getZoneISYdriverInfo(self, mKey, zoneNbr):
        info = {}
        zoneStr = self.zoneID+str(zoneNbr)
        if mKey in self.setupFile['nodeDef'][zoneStr]['sts']:
            keys = list(self.setupFile['nodeDef'][zoneStr]['sts'][mKey].keys())
            info['driver'] = keys[0]
            tempData =  self.GETNodeData(self.zoneID, zoneNbr, mKey)
            if tempData['statusOK']:
                val = tempData['data']        
                if val in  ['Celcius', 'Fahrenheit']:
                    if val == 'Celcius':
                        val = 0
                    else:  
                        val = 1 
                info['value'] = val
            else:
                info['value'] = ''
            editor = self.setupFile['nodeDef'][zoneStr]['sts'][mKey][keys[0]]

            info['uom'] = self.setupFile['editors'][editor]['ISYuom']
        return(info)


    ###################################################################        
    #MacroZone

    def updateMacrozoneData(self,  level, macrozoneNbr):
        #LOGGER.debug('updatMacrozoneData: ' + str(macrozoneNbr))

        keys =[]
        if level == 'all':
            #LOGGER.debug('ALL update macrozone ' + str(macrozoneNbr))
            keys =  self.macrozonePullKeys(macrozoneNbr)
        elif level == 'active':
            #LOGGER.debug('ACTIVE update macrozone ' + str(macrozoneNbr))
            keys =  self.macrozoneActiveKeys(macrozoneNbr)
        
        self.dataOK = True
        for mKey in keys:
            self.data = self.pullMacrozoneDataIndividual(macrozoneNbr, mKey)
            self.dataOK = self.dataOK and self.data['statusOK']
        return(self.dataOK)


    def pullMacrozoneDataIndividual(self, macrozoneNbr, mKey): 
        #LOGGER.debug('pullMacroZoneDataIndividual: ' +str(macrozoneNbr)  + ' ' + mKey)    
        return(self.pullNodeDataIndividual(macrozoneNbr, self.macrozoneID, mKey))

    def pushMacrozoneDataIndividual(self, macrozoneNbr, mKey, value):
        #LOGGER.debug('pushMacroZoneDataIndividual: ' +str(macrozoneNbr)  + ' ' + mKey + ' ' + str(value))  
        return(self.pushNodeDataIndividual(macrozoneNbr, self.macrozoneID, mKey, value))

    def macrozonePullKeys(self, macrozoneNbr):
        #LOGGER.debug('macrozonePullKeys')
        return( self.getNodeKeys (macrozoneNbr, self.macrozoneID, 'GETstr'))

    def macrozonePushKeys(self, macrozoneNbr):
        #LOGGER.debug('macrozonePushKeys')
        return( self.getNodeKeys (macrozoneNbr, self.macrozoneID, 'PUTstr'))
  
    def macrozoneActiveKeys(self, macrozoneNbr):
        #LOGGER.debug('macrozoneActiveKeys')
        return( self.getNodeKeys (macrozoneNbr, self.macrozoneID, 'Active'))    

    def getMacrozoneCount(self):
        return(self.mSystem[self.systemID]['data']['mMacrozoneCount'])


    def getMacrozoneName(self, macroZoneNbr):
        tempName = self.pullNodeDataIndividual(macroZoneNbr, self.macrozoneID, 'mName')
        if tempName['statusOK']:
            return(tempName['data'])
        else:
            return('NA')

    def getMacrozoneCapability(self, macrozoneNbr): 
        #LOGGER.debug('getMacrozoneCapability for ' + str(macrozoneNbr))        
        self.getNodeCapability(self.macrozoneID, macrozoneNbr)

    def getMacrozoneAddress(self, macrozoneNbr):
        return(self.macrozoneID + str(macrozoneNbr))

    def getMacrozoneMessanaISYkey(self, ISYkey, macrozoneNbr):
        macrozoneName = self.macrozoneID+str(macrozoneNbr)
        return(self.ISYmap[macrozoneName][ISYkey]['messana'])

    def getMacrozoneISYValue(self, ISYkey, macrozoneNbr):
        macrozoneName = self.macrozoneID+str(macrozoneNbr)
        messanaKey = self.ISYmap[macrozoneName][ISYkey]['messana']
        try:
            data = self.pullMacrozoneDataIndividual(macrozoneNbr, messanaKey)
            if data['statusOK']:
                val = data['data']        
                if val in  ['Celcius', 'Fahrenheit']:
                    if val == 'Celcius':
                        val = 0
                    else:  
                        val = 1 
                systemValue = val
                status = True
            else:
                systemValue = None
                status = False
        except:
            status = False
            systemValue = None
        return (status, systemValue)


    def getMacrozoneISYdriverInfo(self, mKey, macrozoneNbr):
        info = {}
        macrozoneStr = self.macrozoneID+str(macrozoneNbr)
        if mKey in self.setupFile['nodeDef'][macrozoneStr]['sts']:
            keys = list(self.setupFile['nodeDef'][macrozoneStr]['sts'][mKey].keys())
            info['driver'] = keys[0]
            tempData =  self.GETNodeData(self.macrozoneID, macrozoneNbr, mKey)
            if tempData['statusOK']:
                val = tempData['data']        
                if val in  ['Celcius', 'Fahrenheit']:
                    if val == 'Celcius':
                        val = 0
                    else:  
                        val = 1 
                info['value'] = val
            else:
                info['value'] = ''
            editor = self.setupFile['nodeDef'][macrozoneStr]['sts'][mKey][keys[0]]

            info['uom'] = self.setupFile['editors'][editor]['ISYuom']
        return(info)

    def macrozoneSetStatus(self, value, macrozoneNbr):
        #LOGGER.debug(' macrozoneSetstatus called for macrozone: ' + str(macrozoneNbr))
        
        status = self.pushMacrozoneDataIndividual(macrozoneNbr, 'mStatus', value)
        return(status)
 

    def getMacrozoneStatusISYdriver(self, macrozoneNbr):
        #LOGGER.debug('getMacrozoneStatusISYdriver called for macrozone: '+str(macrozoneNbr))
        
        Key = ''
        macrozoneName = self.macrozoneID+str(macrozoneNbr)
        for ISYkey in self.ISYmap[macrozoneName]:
            if self.ISYmap[macrozoneName][ISYkey]['messana'] == 'mStatus':
                Key = ISYkey
        return(Key)  
        


    def macrozoneSetSetpoint(self, value,  macrozoneNbr):
        #LOGGER.debug('macrozoneSetSetpoint called for macrozone: ' + str(macrozoneNbr))
        
        status = self.pushMacrozoneDataIndividual(macrozoneNbr, 'mSetpoint', value)
        return(status)

    def getMacrozoneSetPointISYdriver(self, macrozoneNbr):
        #LOGGER.debug('getMacrozoneSetpointISYdriver called for macrozone: '+str(macrozoneNbr))
        
        Key = ''
        macrozoneName = self.macrozoneID+str(macrozoneNbr)
        for ISYkey in self.ISYmap[macrozoneName]:
            if self.ISYmap[macrozoneName][ISYkey]['messana'] == 'mSetpoint':
                Key = ISYkey
        return(Key)  
  

    def macrozoneEnableSchedule(self, value, macrozoneNbr):
        #LOGGER.debug('macrozoneEnableSchedule called for macrozone: ' + str(macrozoneNbr))
        
        status = self.pushMacrozoneDataIndividual(macrozoneNbr, 'mScheduleOn', value)
        return(status)


    def getMacrozoneEnableScheduleISYdriver(self, macrozoneNbr):
        #LOGGER.debug('getMacrozoneEnableScheduleISYdriver called for macrozone: '+str(macrozoneNbr))
        
        Key = ''
        macrozoneName = self.macrozoneID+str(macrozoneNbr)
        for ISYkey in self.ISYmap[macrozoneName]:
            if self.ISYmap[macrozoneName][ISYkey]['messana'] == 'mScheduleOn':
                Key = ISYkey
        return(Key) 






    ##############################################################
    # Hot Cold Change Over
    def updateHcCoData(self, level,  HcCoNbr):
        #LOGGER.debug('updatHcCoData: ' + str(HcCoNbr))
        keys =[]
        if level == 'all':
            #LOGGER.debug('ALL update Hot Cold CO ' + str(HcCoNbr))
            keys =  self.HcCoPullKeys(HcCoNbr)
        elif level == 'active':
            #LOGGER.debug('ACTIVE update Hot Cold CO  ' + str(HcCoNbr))
            keys =  self.HcCoActiveKeys(HcCoNbr)
        
        self.dataOK = True
        for mKey in keys:
            self.data = self.pullHcCoDataIndividual(HcCoNbr, mKey)
            self.dataOK = self.dataOK and self.data['statusOK']
        return(self.dataOK)

    def getHcCoCapability(self, HcCoNbr): 
        #LOGGER.debug('getHC_COCapability for ' + str(HcCoNbr))        
        self.getNodeCapability(self.HotColdcoID , HcCoNbr)

    def pullHcCoDataIndividual(self, HcCoNbr, mKey): 
        #LOGGER.debug('pullHC_CODataIndividual: ' +str(HcCoNbr)  + ' ' + mKey)    
        return(self.pullNodeDataIndividual(HcCoNbr, self.HotColdcoID , mKey))

    def pushHcCoDataIndividual(self, HcCoNbr, mKey, value):
        #LOGGER.debug('pushHC_CODataIndividual: ' +str(HcCoNbr)  + ' ' + mKey + ' ' + str(value))  
        return(self.pushNodeDataIndividual(HcCoNbr, self.HotColdcoID , mKey, value))

    def HcCoPullKeys(self, HcCoNbr):
        #LOGGER.debug('hc_coPullKeys')
        return( self.getNodeKeys (HcCoNbr, self.HotColdcoID , 'GETstr'))

    def HcCoPushKeys(self, HcCoNbr):
        #LOGGER.debug('hc_coPushKeys')
        return( self.getNodeKeys (HcCoNbr, self.HotColdcoID , 'PUTstr'))
  
    def HcCoActiveKeys(self, HcCoNbr):
        #LOGGER.debug('hc_coActiveKeys')
        return( self.getNodeKeys (HcCoNbr, self.HotColdcoID , 'Active'))    

    def getHcCoCount(self):
        return(self.mSystem[ self.systemID]['data']['mhc_coCount'])
        
    def getHcCoName(self, HcCoNbr):
        tempName = self.pullNodeDataIndividual(HcCoNbr, self.HotColdcoID, 'mName')
        if tempName['statusOK']:
            return(tempName['data'])
        else:
            return('NA')
            
    def getHcCoAddress(self, HcCoNbr):
        return(self.HotColdcoID + str(HcCoNbr))


    def HcCoSetMode(self, value, HcCoNbr):
        #LOGGER.debug('HcCoSetMode called for Hot Cold: ' + str(HcCoNbr))
        
        status = self.pushHcCoDataIndividual(HcCoNbr, 'mMode', value)
        return(status)


    def getHcCoISYdriverInfo(self, mKey, HcCoNbr):
        info = {}
        HcCoStr = self.HotColdcoID+str(HcCoNbr)
        if mKey in self.setupFile['nodeDef'][HcCoStr]['sts']:
            keys = list(self.setupFile['nodeDef'][HcCoStr]['sts'][mKey].keys())
            info['driver'] = keys[0]
            tempData =  self.GETNodeData(self.HotColdcoID, HcCoNbr, mKey)
            if tempData['statusOK']:
                val = tempData['data']        
                if val in  ['Celcius', 'Fahrenheit']:
                    if val == 'Celcius':
                        val = 0
                    else:  
                        val = 1 
                info['value'] = val
            else:
                info['value'] = ''
            editor = self.setupFile['nodeDef'][HcCoStr]['sts'][mKey][keys[0]]
            info['uom'] = self.setupFile['editors'][editor]['ISYuom']
        return(info)

    def getHcCoISYValue(self, ISYkey, HcCoNbr):
        HcCoName = self.HotColdcoID+str(HcCoNbr)
        messanaKey = self.ISYmap[HcCoName][ISYkey]['messana']
        try:
            data = self.pullHcCoDataIndividual(HcCoNbr, messanaKey)
            if data['statusOK']:
                val = data['data']        
                if val in  ['Celcius', 'Fahrenheit']:
                    if val == 'Celcius':
                        val = 0
                    else:  
                        val = 1 
                systemValue = val
                status = True
            else:
                systemValue = None
                status = False
        except:
            status = False
            systemValue = None
        return (status, systemValue)

    def getHcCoMessanaISYkey(self, ISYkey, HcCoNbr):
        HcCoName = self.HotColdcoID+str(HcCoNbr)
        return(self.ISYmap[HcCoName][ISYkey]['messana'])

    def getHcCoSetModeISYdriver(self, HcCoNbr):
        #LOGGER.debug('getHcCoSetModeISYdriver called for Hot Cold: '+str(HcCoNbr))
        Key = ''
        HcCoName = self.HotColdcoID+str(HcCoNbr)
        for ISYkey in self.ISYmap[HcCoName]:
            if self.ISYmap[HcCoName][ISYkey]['messana'] == 'mMode':
                Key = ISYkey
        return(Key) 

    def HcCoAdaptiveComfort(self, value, HcCoNbr):
        #LOGGER.debug('HcCoAdaptiveComfort called for Hot Cold: ' + str(HcCoNbr))
        
        status = self.pushHcCoDataIndividual(HcCoNbr, 'mAdaptiveComfort', value)
        return(status)


    def getHcCoAdaptiveComfortISYdriver(self, HcCoNbr):
        #LOGGER.debug('getHcCoAdaptiveComfortISYdriver called for Hot Cold: '+str(HcCoNbr))
        Key = ''
        HcCoName = self.HotColdcoID+str(HcCoNbr)
        for ISYkey in self.ISYmap[HcCoName]:
            if self.ISYmap[HcCoName][ISYkey]['messana'] == 'mAdaptiveComfort':
                Key = ISYkey
        return(Key) 

    ####################################################
    #ATU
   
    def getAtuCapability(self, atuNbr): 
        #LOGGER.debug('getAtuCapability for ' + str(atuNbr))             
        self.getNodeCapability(self.atuID, atuNbr)
    
    def updateAtuData(self,  level, atuNbr):
        #LOGGER.debug('updateAtuData: ' + str(atuNbr))

        keys =[]
        if level == 'all':
            #LOGGER.debug('ALL update atu ' + str(atuNbr))
            keys =  self.atuPullKeys(atuNbr)
        elif level == 'active':
            #LOGGER.debug('ACTIVE update atu ' + str(atuNbr))
            keys =  self.atuActiveKeys(atuNbr)
        
        self.dataOK = True
        for mKey in keys:
            self.data = self.pullAtuDataIndividual(atuNbr, mKey)
            self.dataOK = self.dataOK and self.data['statusOK']
        return(self.dataOK)
    

    def getAtuMessanaISYkey(self, ISYkey, atuNbr):
        atuName = self.atuID+str(atuNbr)
        return(self.ISYmap[atuName][ISYkey]['messana'])

    def getAtuISYValue(self, ISYkey, atuNbr):
        atuName = self.atuID+str(atuNbr)
        messanaKey = self.ISYmap[atuName][ISYkey]['messana']
        try:
            data = self.pullAtuDataIndividual(atuNbr, messanaKey)
            if data['statusOK']:
                val = data['data']        
                if val in  ['Celcius', 'Fahrenheit']:
                    if val == 'Celcius':
                        val = 0
                    else:  
                        val = 1 
                systemValue = val
                status = True
            else:
                systemValue = None
                status = False
        except:
            status = False
            systemValue = None
        return (status, systemValue)


    def pullAtuDataIndividual(self, atuNbr, mKey): 
        #LOGGER.debug('pullAtuDataIndividual: ' +str(atuNbr)  + ' ' + mKey)    
        return(self.pullNodeDataIndividual(atuNbr, self.atuID, mKey))

    def pushAtuDataIndividual(self, ATUNbr, mKey, value):
        #LOGGER.debug('pushATUDataIndividual: ' +str(ATUNbr)  + ' ' + mKey + ' ' + str(value))  
        return(self.pushNodeDataIndividual(ATUNbr, self.atuID, mKey, value))

    def atuPullKeys(self, ATUNbr): 
        #LOGGER.debug('atusPullKeys')
        return( self.getNodeKeys (ATUNbr, self.atuID, 'GETstr'))

    def atuPushKeys(self, ATUNbr):
        #LOGGER.debug('atusPushKeys')
        return( self.getNodeKeys (ATUNbr, self.atuID, 'PUTstr'))
  
    def atuActiveKeys(self, ATUNbr):
        #LOGGER.debug('atusActiveKeys')
        return( self.getNodeKeys (ATUNbr, self.atuID, 'Active'))    
  
    def getAtuCount(self):
        return(self.mSystem[ self.systemID]['data']['mATUcount'])

    
    def getAtuName(self, atuNbr):
        tempName = self.pullNodeDataIndividual(atuNbr, self.atuID, 'mName')
        if tempName['statusOK']:
            return(tempName['data'])
        else:
            return('NA')
            
    def getAtuAddress(self, atuNbr):
        return(self.atuID + str(atuNbr))

    def getAtuISYdriverInfo(self, mKey, atuNbr):
        info = {}
        atuStr = self.atuID+str(atuNbr)
        if mKey in self.setupFile['nodeDef'][atuStr]['sts']:
            keys = list(self.setupFile['nodeDef'][atuStr]['sts'][mKey].keys())
            info['driver'] = keys[0]
            tempData =  self.GETNodeData(self.atuID, atuNbr, mKey)
            if tempData['statusOK']:
                val = tempData['data']        
                if val in  ['Celcius', 'Fahrenheit']:
                    if val == 'Celcius':
                        val = 0
                    else:  
                        val = 1 
                info['value'] = val
            else:
                info['value'] = ''
            editor = self.setupFile['nodeDef'][atuStr]['sts'][mKey][keys[0]]
            info['uom'] = self.setupFile['editors'][editor]['ISYuom']
        return(info)

    def atuSetStatus(self, value, atuNbr):
        #LOGGER.debug ('atuSetStatus')
        status = self.pushAtuDataIndividual(atuNbr, 'mStatus', value)
        return(status)
 
    def getAtuStatusISYdriver(self, atuNbr):
        #LOGGER.debug ('getAtuStatusISYdriver called')
        Key = ''
        atuName = self.atuID+str(atuNbr)
        for ISYkey in self.ISYmap[atuName]:
            if self.ISYmap[atuName][ISYkey]['messana'] == 'mStatus':
                Key = ISYkey
        return(Key)  
  
    def atuSetHrv(self, value, atuNbr):
        #LOGGER.debug ('atuSetHRV called')
        status = self.pushAtuDataIndividual(atuNbr, 'mHRVOn', value)
        return(status)

    def getAtuHrvISYdriver(self, atuNbr):
        #LOGGER.debug ('getAtuHrvISYdriver called')
        atuName = self.atuID+str(atuNbr)
        for ISYkey in self.ISYmap[atuName]:
            if self.ISYmap[atuName][ISYkey]['messana'] == 'mHRVOn':
                Key = ISYkey
        return(Key)  

    def atuSetFlowlevel(self, value, atuNbr):
        #LOGGER.debug ('atuSetFlowlevel called')
        status = self.pushAtuDataIndividual(atuNbr, 'mFlowLevel', value)
        return(status)

    def getAtuSetFlowlevelISYdriver(self, atuNbr):
        #LOGGER.debug ('getAtuSetPointISYdriver called')
        atuName = self.atuID+str(atuNbr)
        for ISYkey in self.ISYmap[atuName]:
            if self.ISYmap[atuName][ISYkey]['messana'] == 'mFlowLevel':
                Key = ISYkey
        return(Key)  
        
    def atuSetHum(self, value, atuNbr):
        #LOGGER.debug ('atuSetHum called')
        status = self.pushAtuDataIndividual(atuNbr, 'mHUMOn', value)
        return(status)

    def getAtuSetHumISYdriver(self, atuNbr):
        #LOGGER.debug ('getAtuSetHumISYdriver called')
        atuName = self.atuID+str(atuNbr)
        for ISYkey in self.ISYmap[atuName]:
            if self.ISYmap[atuName][ISYkey]['messana'] == 'mHUMOn':
                Key = ISYkey
        return(Key)  

    def atuSetInt(self, value, atuNbr):
        #LOGGER.debug ('atuSetInt called')
        status = self.pushAtuDataIndividual(atuNbr, 'mINTOn', value)
        return(status)

    def getAtuSetIntISYdriver(self, atuNbr):
        #LOGGER.debug ('getAtuSetIntISYdriver called')
        atuName = self.atuID+str(atuNbr)
        for ISYkey in self.ISYmap[atuName]:
            if self.ISYmap[atuName][ISYkey]['messana'] == 'mINTOn':
                Key = ISYkey
        return(Key)  

    def atuSetNtd(self, value, atuNbr):
        #LOGGER.debug ('atuSetNtd called')
        status = self.pushAtuDataIndividual(atuNbr, 'mNTDOn', value)
        return(status)

    def getAtuSetNtdISYdriver(self, atuNbr):
        #LOGGER.debug ('getAtuSetNtdISYdriver called')
        atuName = self.atuID+str(atuNbr)
        for ISYkey in self.ISYmap[atuName]:
            if self.ISYmap[atuName][ISYkey]['messana'] == 'mNTDOn':
                Key = ISYkey
        return(Key)  

    def atuSetHumSetpointRH(self, value, atuNbr):
        #LOGGER.debug ('atuSetHumSetpointRH called')
        status = self.pushAtuDataIndividual(atuNbr, 'mHumSetpointRH', value)
        return(status)

    def getAtuSetHumSetpointRHISYdriver(self, atuNbr):
        #LOGGER.debug ('getAtuSetHumSetpointRHISYdriver called')
        atuName = self.atuID+str(atuNbr)
        for ISYkey in self.ISYmap[atuName]:
            if self.ISYmap[atuName][ISYkey]['messana'] == 'mHumSetpointRH':
                Key = ISYkey
        return(Key)

    def atuSetHumSetpointDP(self, value, atuNbr):
        #LOGGER.debug ('atuSetHumSetpointDP called')
        status = self.pushAtuDataIndividual(atuNbr, 'mHumSetpointDP', value)
        return(status)

    def getAtuSetHumSetpointDPISYdriver(self, atuNbr):
        #LOGGER.debug ('getAtuSetHumSetpointRHISYdriver called')
        atuName = self.atuID+str(atuNbr)
        for ISYkey in self.ISYmap[atuName]:
            if self.ISYmap[atuName][ISYkey]['messana'] == 'mHumSetpointDP':
                Key = ISYkey
        return(Key)  

    def atuSetDehumSetpointRH(self, value, atuNbr):
        #LOGGER.debug ('atuSetDehumSetpointRH called')
        status = self.pushAtuDataIndividual(atuNbr, 'mDehumSetpointRH', value)
        return(status)

    def getAtuSetDehumSetpointRHISYdriver(self, atuNbr):
        #LOGGER.debug ('getAtuSetDehumSetpointRHISYdriver called')
        atuName = self.atuID+str(atuNbr)
        for ISYkey in self.ISYmap[atuName]:
            if self.ISYmap[atuName][ISYkey]['messana'] == 'mDehumSetpointRH':
                Key = ISYkey
        return(Key)  


    def atuSetDehumSetpointDP(self, value, atuNbr):
        #LOGGER.debug ('atuSetDehumSetpointDP called')
        status = self.pushAtuDataIndividual(atuNbr, 'mDehumSetpointDP', value)
        return(status)

    def getAtuSetDehumSetpointDPISYdriver(self, atuNbr):
        #LOGGER.debug ('getAtuSetDehumSetpointDPISYdriver called')
        atuName = self.atuID+str(atuNbr)
        for ISYkey in self.ISYmap[atuName]:
            if self.ISYmap[atuName][ISYkey]['messana'] == 'mDehumSetpointDP':
                Key = ISYkey
        return(Key)

    def atuSetCurrentSetpointRH(self, value, atuNbr):
        #LOGGER.debug ('atuSetCurrentSetpointRH called')
        status = self.pushAtuDataIndividual(atuNbr, 'mCurrentSetpointRH', value)
        return(status)

    def getAtuSetCurrentSetpointRHISYdriver(self, atuNbr):
        #LOGGER.debug ('getAtuSetCurrentSetpointRHISYdriver called')
        atuName = self.atuID+str(atuNbr)
        for ISYkey in self.ISYmap[atuName]:
            if self.ISYmap[atuName][ISYkey]['messana'] == 'mCurrentSetpointRH':
                Key = ISYkey
        return(Key)  

    def atuSetCurrentSetpointDP(self, value, atuNbr):
        #LOGGER.debug ('atuSetCurrentSetpointDP called')
        status = self.pushAtuDataIndividual(atuNbr, 'mCurrentSetpointDP', value)
        return(status)

    def getAtuSetCurrentSetpointDPISYdriver(self, atuNbr):
        #LOGGER.debug ('getAtuSetCurrentSetpointDPISYdriver called')
        atuName = self.atuID+str(atuNbr)
        for ISYkey in self.ISYmap[atuName]:
            if self.ISYmap[atuName][ISYkey]['messana'] == 'mCurrentSetpointDP':
                Key = ISYkey
        return(Key)  



    #################################################################
    #Fan Coils
    def updateFanCoilData(self, level, FanCoilNbr):
        #LOGGER.debug('updatFanCoilData: ' + str(FanCoilNbr))
        keys =[]
        if level == 'all':
            #LOGGER.debug('ALL update Fan Coil ' + str(FanCoilNbr))
            keys =  self.fan_coilPullKeys(FanCoilNbr)
        elif level == 'active':
            #LOGGER.debug('ACTIVE update Fan Coil  ' + str(FanCoilNbr))
            keys =  self.fan_coilActiveKeys(FanCoilNbr)
        
        self.dataOK = True
        for mKey in keys:
            self.data = self.pullFanCoilDataIndividual(FanCoilNbr, mKey)
            self.dataOK = self.dataOK and self.data['statusOK']
        return(self.dataOK)

    
    def getFanCoilName(self, fanCoilNbr):
        tempName = self.pullNodeDataIndividual(fanCoilNbr, self.fcID, 'mName')
        if tempName['statusOK']:
            return(tempName['data'])
        else:
            return('NA')
            
    def getFanCoilAddress(self, fanCoilNbr):
        return(self.fcID + str(fanCoilNbr))  

    def getFanCoilCapability(self, FanCoilNbr): 
        #LOGGER.debug('getFanCoilCapability for ' + str(FanCoilNbr))              
        self.getNodeCapability(self.fcID, FanCoilNbr)

    def pullFanCoilDataIndividual(self, FanCoilNbr, mKey): 
        #LOGGER.debug('pullFanCoilDataIndividual: ' +str(FanCoilNbr)  + ' ' + mKey)    
        return(self.pullNodeDataIndividual(FanCoilNbr, self.fcID, mKey))

    def pushFanCoilDataIndividual(self, FanCoilNbr, mKey, value):
        #LOGGER.debug('pushFanCoilDataIndividual: ' +str(FanCoilNbr)  + ' ' + mKey + ' ' + str(value))  
        return(self.pushNodeDataIndividual(FanCoilNbr, self.fcID, mKey, value))

    def fan_coilPullKeys(self, FanCoilNbr):
        #LOGGER.debug('fan_coilPullKeys')
        return( self.getNodeKeys (FanCoilNbr, self.fcID, 'GETstr'))

    def fan_coilPushKeys(self, FanCoilNbr):
        #LOGGER.debug('fan_coilPushKeys')
        return( self.getNodeKeys (FanCoilNbr, self.fcID, 'PUTstr'))
  
    def fan_coilActiveKeys(self, FanCoilNbr):
        #LOGGER.debug('fan_coilActiveKeys')
        return( self.getNodeKeys (FanCoilNbr, self.fcID, 'Active'))    
    
    def getFanCoilCount(self):
        return(self.mSystem[ self.systemID]['data']['mFanCoilCount'])

    def getFanCoilISYdriverInfo(self, mKey, FanCoilNbr):
        info = {}
        FanCoilStr = self.fcID+str(FanCoilNbr)
        if mKey in self.setupFile['nodeDef'][FanCoilStr]['sts']:
            keys = list(self.setupFile['nodeDef'][FanCoilStr]['sts'][mKey].keys())
            info['driver'] = keys[0]
            tempData =  self.GETNodeData(self.fcID, FanCoilNbr, mKey)
            if tempData['statusOK']:
                val = tempData['data']        
                if val in  ['Celcius', 'Fahrenheit']:
                    if val == 'Celcius':
                        val = 0
                    else:  
                        val = 1 
                info['value'] = val
            else:
                info['value'] = ''
            editor = self.setupFile['nodeDef'][FanCoilStr]['sts'][mKey][keys[0]]

            info['uom'] = self.setupFile['editors'][editor]['ISYuom']
        return(info)

    def getFanCoilMessanaISYkey(self, ISYkey, fanCoilNbr):
        fanCoilName = self.fcID+str(fanCoilNbr)
        return(self.ISYmap[fanCoilName][ISYkey]['messana'])

    def fanCoilSetCoolingSpeed(self, value, FanCoilNbr):
        #LOGGER.debug ('fanCoilSetCoolingSpeed called')
        status = self.pushFanCoilDataIndividual(FanCoilNbr, 'mCoolingSpeed', value)
        return(status)
 
    def getFanCoilCoolingSpeedISYdriver(self, FanCoilNbr):
        #LOGGER.debug ('getFanCoilCoolingSpeedISYdriver called')
        Key = ''
        fanCoilName = self.fcID+str(FanCoilNbr)
        for ISYkey in self.ISYmap[fanCoilName]:
            if self.ISYmap[fanCoilName][ISYkey]['messana'] == 'mCoolingSpeed':
                Key = ISYkey
        return(Key) 

    def getFanCoilISYValue(self, ISYkey, fanCoilNbr):
        fanCoilName = self.fcID+str(fanCoilNbr)
        messanaKey = self.ISYmap[fanCoilName][ISYkey]['messana']
        try:
            data = self.pullFanCoilDataIndividual(fanCoilNbr, messanaKey)
            if data['statusOK']:
                val = data['data']        
                if val in  ['Celcius', 'Fahrenheit']:
                    if val == 'Celcius':
                        val = 0
                    else:  
                        val = 1 
                systemValue = val
                status = True
            else:
                systemValue = None
                status = False
        except:
            status = False
            systemValue = None
        return (status, systemValue)

    def fanCoilSetHeatingSpeed(self, value, FanCoilNbr):
        #LOGGER.debug ('fanCoilSetHeatingSpeed called')
        status = self.pushFanCoilDataIndividual(FanCoilNbr, 'mHeatingSpeed', value)
        return(status)
 
    def getFanCoilHeatingSpeedISYdriver(self, FanCoilNbr):
        #LOGGER.debug ('getFanCoilHeatingSpeedISYdriver called')
        Key = ''
        fanCoilName = self.fcID+str(FanCoilNbr)
        for ISYkey in self.ISYmap[fanCoilName]:
            if self.ISYmap[fanCoilName][ISYkey]['messana'] == 'mHeatingSpeed':
                Key = ISYkey
        return(Key) 


    def fanCoilSetStatus(self, value, FanCoilNbr):
        #LOGGER.debug ('fanCoilSetStatus called')
        status = self.pushFanCoilDataIndividual(FanCoilNbr, 'mStatus', value)
        return(status)
 
    def getFanCoilStatusISYdriver(self, FanCoilNbr):
        #LOGGER.debug ('getFanCoilHeatingSpeedISYdriver called')
        Key = ''
        fanCoilName = self.fcID+str(FanCoilNbr)
        for ISYkey in self.ISYmap[fanCoilName]:
            if self.ISYmap[fanCoilName][ISYkey]['messana'] == 'mStatus':
                Key = ISYkey
        return(Key) 

    #############################################################
    #EnergySources
    def updateEnergySourceData(self, level, EnergySourceNbr):
        #LOGGER.debug('updatEnergySourceData: ' + str(EnergySourceNbr))
        keys =[]
        if level == 'all':
            #LOGGER.debug('ALL update Energy Source ' + str(EnergySourceNbr))
            keys =  self.energySourcePullKeys(EnergySourceNbr)
        elif level == 'active':
            #LOGGER.debug('ACTIVE update Energy Source  ' + str(EnergySourceNbr))
            keys =  self.energySourceActiveKeys(EnergySourceNbr)
        
        self.dataOK = True
        for mKey in keys:
            self.data = self.pullEnergySourceDataIndividual(EnergySourceNbr, mKey)
            self.dataOK = self.dataOK and self.data['statusOK']
        return(self.dataOK)

        
    def getEnergySourceCount(self):
        return(self.mSystem[ self.systemID]['data']['mEnergySourceCount'])

    
    def getEnergySourceName(self, energySourceNbr):
        tempName = self.pullNodeDataIndividual(energySourceNbr, self.energySourceID, 'mName')
        if tempName['statusOK']:
            return(tempName['data'])
        else:
            return('NA')
            
    def getEnergySourceAddress(self, energySourceNbr):
        return(self.energySourceID + str(energySourceNbr))     

    def getEnergySourceCapability(self, EnergySourceNbr): 
        #LOGGER.debug('getEnergySourceCapability for ' + str(EnergySourceNbr))          
        self.getNodeCapability( self.energySourceID, EnergySourceNbr)

    def pullEnergySourceDataIndividual(self, EnergySourceNbr, mKey): 
        #LOGGER.debug('pullEnergySourceDataIndividual: ' +str(EnergySourceNbr)  + ' ' + mKey)    
        return(self.pullNodeDataIndividual(EnergySourceNbr,  self.energySourceID, mKey))

    def pushEnergySourceDataIndividual(self, EnergySourceNbr, mKey, value):
        #LOGGER.debug('pushEnergySourceDataIndividual: ' +str(EnergySourceNbr)  + ' ' + mKey + ' ' + str(value))  
        return(self.pushNodeDataIndividual(EnergySourceNbr,  self.energySourceID, mKey, value))

    def energySourcePullKeys(self, EnergySourceNbr):
        #LOGGER.debug('energySourcePullKeys')
        return( self.getNodeKeys (EnergySourceNbr,  self.energySourceID, 'GETstr'))

    def energySourcePushKeys(self, EnergySourceNbr):
        #LOGGER.debug('EnergySourcePushKeys')
        return( self.getNodeKeys (EnergySourceNbr,  self.energySourceID, 'PUTstr'))
  
    def energySourceActiveKeys(self, EnergySourceNbr):
        #LOGGER.debug('energySourceActiveKeys')
        return( self.getNodeKeys (EnergySourceNbr,  self.energySourceID, 'Active'))    
    
    def getEnergySourceISYdriverInfo(self, mKey, EnergySourceNbr):
        info = {}
        EnergySourceStr = self.energySourceID+str(EnergySourceNbr)
        if mKey in self.setupFile['nodeDef'][EnergySourceStr]['sts']:
            keys = list(self.setupFile['nodeDef'][EnergySourceStr]['sts'][mKey].keys())
            info['driver'] = keys[0]
            tempData =  self.GETNodeData(self.energySourceID, EnergySourceNbr, mKey)
            if tempData['statusOK']:
                val = tempData['data']        
                if val in  ['Celcius', 'Fahrenheit']:
                    if val == 'Celcius':
                        val = 0
                    else:  
                        val = 1 
                info['value'] = val
            else:
                info['value'] = ''
            editor = self.setupFile['nodeDef'][EnergySourceStr]['sts'][mKey][keys[0]]

            info['uom'] = self.setupFile['editors'][editor]['ISYuom']
        return(info)

    def getEnergySourceISYValue(self, ISYkey, energySourceNbr):
        energySourceName = self.energySourceID+str(energySourceNbr)
        messanaKey = self.ISYmap[energySourceName][ISYkey]['messana']
        try:
            data = self.pullEnergySourceDataIndividual(energySourceNbr, messanaKey)
            if data['statusOK']:
                val = data['data']        
                if val in  ['Celcius', 'Fahrenheit']:
                    if val == 'Celcius':
                        val = 0
                    else:  
                        val = 1 
                systemValue = val
                status = True
            else:
                systemValue = None
                status = False
        except:
            status = False
            systemValue = None
        return (status, systemValue)

    def getEnergySourceMessanaISYkey(self, ISYkey, energySourceNbr):
        energySourceName = self.energySourceID+str(energySourceNbr)
        return(self.ISYmap[energySourceName][ISYkey]['messana'])

   
    #####################################################
    #Buffer Tank
    
  
    def getBufferTankCapability(self, bufTankNbr): 
        #LOGGER.debug('getBufferTankCapability for ' + str(bufTankNbr))              
        self.getNodeCapability(self.bufferTankID, bufTankNbr)

    def getBufferTankMessanaISYkey(self, ISYkey, bufTankNbr):
        bufTankName = self.bufferTankID+str(bufTankNbr)
        return(self.ISYmap[bufTankName][ISYkey]['messana'])

    def bufferTankPullKeys(self, bufTankNbr): 
        #LOGGER.debug('bufTankPullKeys')
        return( self.getNodeKeys (bufTankNbr, self.bufferTankID, 'GETstr'))

    def bufferTankPushKeys(self, bufTankNbr):
        #LOGGER.debug('bufTankPushKeys')
        return( self.getNodeKeys (bufTankNbr, self.bufferTankID, 'PUTstr'))
  
    def bufferTankActiveKeys(self, bufTankNbr):
        #LOGGER.debug('bufTankActiveKeys')
        return( self.getNodeKeys (bufTankNbr, self.bufferTankID, 'Active'))           

    def updateBufferTankData(self,  level, bufTankNbr):
        #LOGGER.debug('updateBufferTankData: ' + str(bufTankNbr))
        keys =[]
        if level == 'all':
            #LOGGER.debug('ALL update buffer tank ' + str(bufTankNbr))
            keys =  self.bufferTankPullKeys(bufTankNbr)
        elif level == 'active':
            #LOGGER.debug('ACTIVE update buffer tank ' + str(bufTankNbr))
            keys =  self.bufferTankActiveKeys(bufTankNbr)
        
        self.dataOK = True
        for mKey in keys:
            self.data = self.pullBufferTankDataIndividual(bufTankNbr, mKey)
            self.dataOK = self.dataOK and self.data['statusOK']
        return(self.dataOK)
            

    def getBufferTankISYValue(self, ISYkey, bufTankNbr):
        bufTankName = self.bufferTankID+str(bufTankNbr)
        messanaKey = self.ISYmap[bufTankName][ISYkey]['messana']
        try:
            data = self.pullBufferTankDataIndividual(bufTankNbr, messanaKey)
            if data['statusOK']:
                val = data['data']        
                if val in  ['Celcius', 'Fahrenheit']:
                    if val == 'Celcius':
                        val = 0
                    else:  
                        val = 1 
                systemValue = val
                status = True
            else:
                systemValue = None
                status = False
        except:
            status = False
            systemValue = None
        return (status, systemValue)

    def pullBufferTankDataIndividual(self, bufTankNbr, mKey): 
        #LOGGER.debug('pullBufferTankDataIndividual: ' +str(bufTankNbr)  + ' ' + mKey)    
        return(self.pullNodeDataIndividual(bufTankNbr, self.bufferTankID, mKey))

    def pushBufferTankDataIndividual(self, bufTankNbr, mKey, value):
        #LOGGER.debug('pushBufferTankDataIndividual: ' +str(bufTankNbr)  + ' ' + mKey + ' ' + str(value))  

        if mKey == 'mStatus':
            BTdata = {}
            BTdata = self.pullNodeDataIndividual(bufTankNbr, self.bufferTankID, 'mMode')
            if BTdata['data'] != 0:
                return(self.pushNodeDataIndividual(bufTankNbr, self.bufferTankID, mKey, value))
            else:
                LOGGER.error('Mode = 0, Cannot set status if mode = 0')
                return(False)
        else:
             return(self.pushNodeDataIndividual(bufTankNbr, self.bufferTankID, mKey, value))
 
    def getBufferTankCount(self):
        return(self.mSystem[ self.systemID]['data']['mBufTankCount'])


    def getBufferTankName(self, bufTankNbr):
        tempName = self.pullNodeDataIndividual(bufTankNbr, self.bufferTankID, 'mName')
        if tempName['statusOK']:
            return(tempName['data'])
        else:
            return('NA')
            
    def getBufferTankAddress(self, bufTankNbr):
        return(self.bufferTankID + str(bufTankNbr))

    def getBufferTankISYdriverInfo(self, mKey, bufTankNbr):
        info = {}
        bufTankStr = self.bufferTankID+str(bufTankNbr)
        if mKey in self.setupFile['nodeDef'][bufTankStr]['sts']:
            keys = list(self.setupFile['nodeDef'][bufTankStr]['sts'][mKey].keys())
            info['driver'] = keys[0]
            tempData =  self.GETNodeData(self.bufferTankID, bufTankNbr, mKey)
            if tempData['statusOK']:
                val = tempData['data']        
                if val in  ['Celcius', 'Fahrenheit']:
                    if val == 'Celcius':
                        val = 0
                    else:  
                        val = 1 
                info['value'] = val
            else:
                info['value'] = ''
            editor = self.setupFile['nodeDef'][bufTankStr]['sts'][mKey][keys[0]]
            info['uom'] = self.setupFile['editors'][editor]['ISYuom']
        return(info)


    def bufferTankSetStatus(self, value, bufTankNbr):
        #LOGGER.debug ('bufferTankSetStatus')
        status = self.pushBufferTankDataIndividual(bufTankNbr, 'mStatus', value)
        return(status)
 
    def getBufferTankStatusISYdriver(self, bufTankNbr):
        #LOGGER.debug ('getBufferTankStatusISYdriver called')
        Key = ''
        bufTankName = self.bufferTankID+str(bufTankNbr)
        for ISYkey in self.ISYmap[bufTankName]:
            if self.ISYmap[bufTankName][ISYkey]['messana'] == 'mStatus':
                Key = ISYkey
        return(Key) 

    def bufferTankSetSetMode(self, value, bufTankNbr):
        #LOGGER.debug ('bufferTankSetSetMode')
        status = self.pushAtuDataIndividual(bufTankNbr, 'mMode', value)
        return(status)
 
    def getBufferTankSetModeISYdriver(self, bufTankNbr):
        #LOGGER.debug ('getBufferTankSetModeISYdriver called')
        Key = ''
        bufTankName = self.bufferTankID+str(bufTankNbr)
        for ISYkey in self.ISYmap[bufTankName]:
            if self.ISYmap[bufTankName][ISYkey]['messana'] == 'mMode':
                Key = ISYkey
        return(Key)  
    def bufferTankTempStatus(self, value, bufTankNbr):
        #LOGGER.debug ('bufferTankTempStatus')
        status = self.pushAtuDataIndividual(bufTankNbr, 'mTempMode', value)
        return(status)
 
    def getBufferTankTempStatusISYdriver(self, bufTankNbr):
        #LOGGER.debug ('getBufferTankTempStatusISYdriver called')
        Key = ''
        bufTankName = self.bufferTankID+str(bufTankNbr)
        for ISYkey in self.ISYmap[bufTankName]:
            if self.ISYmap[bufTankName][ISYkey]['messana'] == 'mTempMode':
                Key = ISYkey
        return(Key)  
  

        #Domestic Hot Water
 
    ##################################################################
    # Domestic Hot Water
    def updateDHWData(self, level, DHWNbr):
        #LOGGER.debug('updatDHWData: ' + str(DHWNbr))
        keys =[]
        if level == 'all':
            #LOGGER.debug('ALL update  Domestic Hot Water ' + str(DHWNbr))
            keys =  self.DHWPullKeys(DHWNbr)
        elif level == 'active':
            #LOGGER.debug('ACTIVE update Domestic Hot Water ' + str(DHWNbr))
            keys =  self.DHWActiveKeys(DHWNbr)
        
        self.dataOK = True
        for mKey in keys:
            self.data = self.pullDHWDataIndividual(DHWNbr, mKey)
            self.dataOK = self.dataOK and self.data['statusOK']
        return(self.dataOK)

    def getDHWCapability(self, DHWNbr): 
        #LOGGER.debug('getDHWCapability for '+str(DHWNbr))                      
        self.getNodeCapability(self.dhwID, DHWNbr)

    def pullDHWDataIndividual(self, DHWNbr, mKey): 
        #LOGGER.debug('pullDHWDataIndividual: ' +str(DHWNbr)  + ' ' + mKey)    
        return(self.pullNodeDataIndividual(DHWNbr, self.dhwID, mKey))

    def pushDHWDataIndividual(self, DHWNbr, mKey, value):
        #LOGGER.debug('pushDHWDataIndividual: ' +str(DHWNbr)  + ' ' + mKey + ' ' + str(value))  
        return(self.pushNodeDataIndividual(DHWNbr, self.dhwID, mKey, value))


    def DHWPullKeys(self, DHWNbr):
        #LOGGER.debug('DHWPullKeys')
        return( self.getNodeKeys (DHWNbr, self.dhwID, 'GETstr'))

    def DHWPushKeys(self, DHWNbr):
        #LOGGER.debug('DHWPushKeys')
        return( self.getNodeKeys (DHWNbr, self.dhwID, 'PUTstr'))
  
    def DHWActiveKeys(self, DHWNbr):
        #LOGGER.debug('DHWActiveKeys')
        return( self.getNodeKeys (DHWNbr, self.dhwID, 'active'))    

    def getDomesticHotWaterCount(self):
        return(self.mSystem[ self.systemID]['data']['mDHWcount'])

    def getDomesticHotWaterName(self, DHWNbr):
        tempName = self.pullNodeDataIndividual(DHWNbr, self.dhwID, 'mName')
        if tempName['statusOK']:
            return(tempName['data'])
        else:
            return('NA')
            
    def getDomesticHotWaterAddress(self, DHWNbr):
        return(self.dhwID + str(DHWNbr))

    def hotWaterSetStatus(self, value, DHWNbr):
        #LOGGER.debug ('hotWaterSetStatus')
        status = self.pushAtuDataIndividual(DHWNbr, 'mStatus', value)
        return(status)
 
    def getHotWaterStatusISYdriver(self, DHWNbr):
        #LOGGER.debug ('getHotWaterStatusISYdriver called')
        Key = ''
        DHWName = self.dhwID+str(DHWNbr)
        for ISYkey in self.ISYmap[DHWName]:
            if self.ISYmap[DHWName][ISYkey]['messana'] == 'mStatus':
                Key = ISYkey
        return(Key)  
  
    def getHotWaterISYdriverInfo(self, mKey, DHWNbr):
        info = {}
        DHWStr = self.dhwID+str(DHWNbr)
        if mKey in self.setupFile['nodeDef'][DHWStr]['sts']:
            keys = list(self.setupFile['nodeDef'][DHWStr]['sts'][mKey].keys())
            info['driver'] = keys[0]
            tempData =  self.GETNodeData(self.dhwID, DHWNbr, mKey)
            if tempData['statusOK']:
                val = tempData['data']        
                if val in  ['Celcius', 'Fahrenheit']:
                    if val == 'Celcius':
                        val = 0
                    else:  
                        val = 1 
                info['value'] = val
            else:
                info['value'] = ''
            editor = self.setupFile['nodeDef'][DHWStr]['sts'][mKey][keys[0]]
            info['uom'] = self.setupFile['editors'][editor]['ISYuom']
        return(info)

    def hotWaterSetTargetTempt(self, value, DHWNbr):
        #LOGGER.debug ('hotWaterSetTargetTempt')
        status = self.pushAtuDataIndividual(DHWNbr, 'mTargetTemp', value)
        return(status)
 
    def getHotWaterSetTargetTempISYdriver(self, DHWNbr):
        #LOGGER.debug ('getHotWaterSetTargetTempISYdriver called')
        Key = ''
        DHWName = self.dhwID+str(DHWNbr)
        for ISYkey in self.ISYmap[DHWName]:
            if self.ISYmap[DHWName][ISYkey]['messana'] == 'mTargetTemp':
                Key = ISYkey
        return(Key)  

    def getHotWaterISYValue(self, ISYkey, dhwNbr):
        dhwName = self.dhwID+str(dhwNbr)
        messanaKey = self.ISYmap[dhwName][ISYkey]['messana']
        try:
            data = self.pullDHWDataIndividual(dhwNbr, messanaKey)
            if data['statusOK']:
                val = data['data']        
                if val in  ['Celcius', 'Fahrenheit']:
                    if val == 'Celcius':
                        val = 0
                    else:  
                        val = 1 
                systemValue = val
                status = True
            else:
                systemValue = None
                status = False
        except:
            status = False
            systemValue = None
        return (status, systemValue)

    def getHotWaterMessanaISYkey(self, ISYkey, dhwNbr):
        dhwName = self.dhwID+str(dhwNbr)
        return(self.ISYmap[dhwName][ISYkey]['messana'])        