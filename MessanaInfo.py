#!/usr/bin/env python3
import requests
#from subprocess import call
import json
import os

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
            #logging.debug(resp)
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


    def update_name(self):
        logging.debug('update_name: atu:{}'.format(self.node_nbr ))
        temp = self.GET_node_data(self.node_nbr , 'name')
        if temp:
            self.name = temp

    def update_status(self):
        logging.debug('update_status {}'.format(self.node_nbr))    
        return( self.GET_node_data(self.node_nbr , 'status'))

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
        return(self.GET_node_data(self.node_nbr , 'setpoint'))

        


        ''' 
        messana.zoneID = 'zones'
        messana.macrozoneID = 'macrozones'
        messana.atuID = 'atus'
        messana.dhwID = 'domhws'
        messana.fcID = 'fancoils'
        messana.energySourceID =  'energysys'
        messana.HotColdcoID = 'hcco'
        messana.bufferTankID = 'buftanks'
        messana.supportedNodeList = [
                            messana.zoneID,
                            messana.macrozoneID,
                            messana.atuID,
                            messana.dhwID,
                            messana.fcID,
                            messana.energySourceID,
                            messana.HotColdcoID,
                            messana.bufferTankID  ] 
       
        
    
        

       

        #Dummy check to see if there is connection to Messana system)
        if not(messana.checkMessanaConnection()):
            logging.error('Error Connecting to MessanaSystem')
        else:  
            #logging.info('Extracting Information about Messana System')
  
            messana.zones = messanaZones(messana.IPaddress , messana.ApiKey )

            #Need SystemCapability function               
            #messana.getSystemCapability()
            #messana.updateSystemData('all')
            #logging.debug(messana.systemID + ' added')
            messana.addZones()
            messana.addMacroZones()

            #messana.addSystemDefStruct(messana.systemID)

            for zoneNbr in range(0,messana.mSystem[ messana.systemID]['data']['mZoneCount']):
                messana.getZoneCapability(zoneNbr)
                messana.updateZoneData('all', zoneNbr)
                zoneName = messana.zoneID+str(zoneNbr)
                messana.addNodeDefStruct(zoneNbr, messana.zoneID, zoneName )
        
            for macrozoneNbr in range(0,messana.mSystem[ messana.systemID]['data']['mMacrozoneCount']):
                messana.getMacrozoneCapability(macrozoneNbr)
                messana.updateMacrozoneData('all', macrozoneNbr)
                macrozoneName = messana.macrozoneID+str(macrozoneNbr)
                messana.addNodeDefStruct(macrozoneNbr, messana.macrozoneID, macrozoneName )
            
            for atuNbr in range(0,messana.mSystem[ messana.systemID]['data']['mATUcount']):
                messana.getAtuCapability(atuNbr)
                messana.updateAtuData('all', atuNbr)
                atuName = messana.atuID+str(atuNbr)
                messana.addNodeDefStruct(atuNbr, messana.atuID, atuName )
    
            for dhwNbr in range(0,messana.mSystem[ messana.systemID]['data']['mDHWcount']):
                messana.getDHWCapability(dhwNbr)
                messana.updateDHWData('all', dhwNbr)
                dhwName = messana.dhwID+str(dhwNbr)
                messana.addNodeDefStruct(dhwNbr, messana.dhwID, dhwName )

            for fcNbr in range(0,messana.mSystem[ messana.systemID]['data']['mFanCoilCount']):
                messana.getFanCoilCapability(fcNbr)
                messana.updateFanCoilData('all', fcNbr)
                fcName = messana.fcID+str(fcNbr)
                messana.addNodeDefStruct(fcNbr, messana.fcID, fcName )
        
            for esNbr in range(0,messana.mSystem[ messana.systemID]['data']['mEnergySourceCount']):
                messana.getEnergySourceCapability(esNbr)
                messana.updateEnergySourceData('all', esNbr)
                esName =  messana.energySourceID+str(esNbr)
                messana.addNodeDefStruct(esNbr,  messana.energySourceID, esName)   

            for HcCoNbr in range(0,messana.mSystem[ messana.systemID]['data']['mhc_coCount']):
                messana.getHcCoCapability(HcCoNbr)
                messana.updateHcCoData('all', HcCoNbr)
                hccoName = messana.HotColdcoID +str(HcCoNbr)
                messana.addNodeDefStruct(HcCoNbr, messana.HotColdcoID , hccoName)          
            
            for btNbr in range(0,messana.mSystem[ messana.systemID]['data']['mBufTankCount']):
                messana.getBufferTankCapability(btNbr)
                messana.updateBufferTankData('all', btNbr)
                btName = messana.bufferTankID+str(btNbr)
                messana.addNodeDefStruct(btNbr, messana.bufferTankID, btName)     

            logging.info ('Creating Setup file')
            messana.createSetupFiles('./profile/nodedef/nodedefs.xml','./profile/editor/editors.xml', './profile/nls/en_us.txt')
            messana.ISYmap = messana.createISYmapping()


        '''



    def setMessanaCredentials (messana, mIPaddress, APIkey):
        messana.mIPaddress = mIPaddress
        messana.APIKeyVal = APIkey






 
    #pretty bad solution - just checking if a value can be extracted
    def checkMessanaConnection(messana):
        sysData = messana.GETSystemData('mApiVer') 
        return (sysData['statusOK'])
    


###################################################################



    def pullSystemDataIndividual(messana, mKey):
        #logging.debug('MessanaInfo pull System Data: ' + mKey)
        return(messana.GETSystemData(mKey) )
                 

    def pushSystemDataIndividual(messana, mKey, value):
        sysData={}
        #logging.debug('MessanaInfo push System Data: ' + mKey)       
        sysData = messana.PUTSystemData(mKey, value)
        if sysData['statusOK']:
            return(True)
        else:
            logging.error(sysData['error'])
            return(False) 

     



    def systemSetStatus (messana, value):
        #logging.debug('systemSetstatus called')
        status = messana.pushSystemDataIndividual('mStatus', value)
        return(status)

    def systemSetEnergySave (messana, value):
        #logging.debug('systemSetEnergySave called')
        status = messana.pushSystemDataIndividual('mEnergySaving', value)
        return(status)
        
    def systemSetback (messana, value):
        #logging.debug('setSetback called')
        status = messana.pushSystemDataIndividual('mSetback', value)
        return(status)

    def getSystemAddress(messana):
        return(messana.systemID)


    # Zones
    def getZoneCapability(messana, zoneNbr):
        #logging.debug('getZoneCapability for ' + str(zoneNbr)) 
        messana.getNodeCapability(messana.zoneID, zoneNbr)

    def addZoneDefStruct(messana, zoneNbr, nodeId):
        messana.addNodeDefStruct(zoneNbr, messana.zoneID, nodeId)

    def updateZoneData(messana, level, zoneNbr):
        #logging.debug('updatZoneData: ' + str(zoneNbr))

        keys =[]
        if level == 'all':
            #logging.debug('ALL update zone ' + str(zoneNbr))
            keys =  messana.zonePullKeys(zoneNbr)
        elif level == 'active':
            #logging.debug('ACTIVE update zone ' + str(zoneNbr))
            keys =  messana.zoneActiveKeys(zoneNbr)
        
        messana.dataOK = True
        for mKey in keys:
            messana.data = messana.pullZoneDataIndividual(zoneNbr, mKey)
            messana.dataOK = messana.dataOK and messana.data['statusOK']
        return(messana.dataOK)

    def pullZoneDataIndividual(messana, zoneNbr, mKey): 
        #logging.debug('pullZoneDataIndividual: ' +str(zoneNbr)  + ' ' + mKey)    
        return(messana.pullNodeDataIndividual(zoneNbr, messana.zoneID, mKey))


    def pushZoneDataIndividual(messana, zoneNbr, mKey, value):
        #logging.debug('pushZoneDataIndividual: ' +str(zoneNbr)  + ' ' + mKey + ' ' + str(value))  
        return(messana.pushNodeDataIndividual(zoneNbr, messana.zoneID, mKey, value))

    def zonePullKeys(messana, zoneNbr):
        #logging.debug('zonePullKeys')
        messana.tempZoneKeys =  messana.getNodeKeys (zoneNbr, messana.zoneID, 'GETstr')
        return( messana.tempZoneKeys)

    def zonePushKeys(messana, zoneNbr):
        #logging.debug('zonePushKeys')
        return( messana.getNodeKeys (zoneNbr, messana.zoneID, 'PUTstr'))
  
    def zoneActiveKeys(messana, zoneNbr):
        #logging.debug('zoneActiveKeys')
        return( messana.getNodeKeys (zoneNbr, messana.zoneID, 'Active'))

    def getZoneCount(messana):
        return(messana.mSystem[ messana.systemID]['data']['mZoneCount'])

    def getZoneName(messana, zoneNbr):
        tempName = messana.pullNodeDataIndividual(zoneNbr, messana.zoneID, 'mName')
        if tempName['statusOK']:
            return(tempName['data'])
        else:
            return('NA')

    def getZoneAddress(messana, zoneNbr):
        return(messana.zoneID + str(zoneNbr))


    def getZoneMessanaISYkey(messana, ISYkey, zoneNbr):
        zoneName = messana.zoneID+str(zoneNbr)
        return(messana.ISYmap[zoneName][ISYkey]['messana'])

    def getZoneISYValue(messana, ISYkey, zoneNbr):
        zoneName = messana.zoneID+str(zoneNbr)
        messanaKey = messana.ISYmap[zoneName][ISYkey]['messana']
        #systemPullKeys = messana.zonePullKeys(zoneNbr)
        try:
            data = messana.pullZoneDataIndividual(zoneNbr, messanaKey)
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


    def checkZoneCommand(messana, cmd, zoneNbr):
        exists = True
        mCmd = messana.mSystem[messana.zoneID]['ISYnode']['accepts'][cmd]['ISYeditor']
        
        if mCmd != None:
            if mCmd in messana.mSystem[messana.zoneID]['SensorCapability'][zoneNbr]:
                if messana.mSystem[messana.zoneID]['SensorCapability'][zoneNbr][mCmd] == 0:
                    exists = False
        return(exists)



    def zoneSetStatus(messana, value, zoneNbr):
        #logging.debug(' zoneSetstatus called for zone: ' + str(zoneNbr))
        
        status = messana.pushZoneDataIndividual(zoneNbr, 'mStatus', value)
        return(status)
 

    def getZoneStatusISYdriver(messana, zoneNbr):
        #logging.debug('getZoneStatusISYdriver called for zone: '+str(zoneNbr))
        
        Key = ''
        zoneName = messana.zoneID+str(zoneNbr)
        for ISYkey in messana.ISYmap[zoneName]:
            if messana.ISYmap[zoneName][ISYkey]['messana'] == 'mStatus':
                Key = ISYkey
        return(Key)  
        

    def zoneSetEnergySave(messana, value, zoneNbr):
        #logging.debug(' zoneSetEnergySave called for zone: ' + str(zoneNbr))
        
        status = messana.pushZoneDataIndividual(zoneNbr, 'mEnergySaving', value)
        return(status)
    
    def getZoneEnergySaveISYdriver(messana, zoneNbr):
        #logging.debug('getZoneEnergySaveISYdriver called for zone: '+str(zoneNbr))
        
        Key = ''
        zoneName = messana.zoneID+str(zoneNbr)
        for ISYkey in messana.ISYmap[zoneName]:
            if messana.ISYmap[zoneName][ISYkey]['messana'] == 'mEnergySaving':
                Key = ISYkey
        return(Key)  



    def zoneSetSetpoint(messana, value,  zoneNbr):
        #logging.debug('zoneSetSetpoint called for zone: ' + str(zoneNbr))
        
        status = messana.pushZoneDataIndividual(zoneNbr, 'mSetpoint', value)
        return(status)

    def getZoneSetPointISYdriver(messana, zoneNbr):
        #logging.debug('getZoneSetpointISYdriver called for zone: '+str(zoneNbr))
        
        Key = ''
        zoneName = messana.zoneID+str(zoneNbr)
        for ISYkey in messana.ISYmap[zoneName]:
            if messana.ISYmap[zoneName][ISYkey]['messana'] == 'mSetpoint':
                Key = ISYkey
        return(Key)  
  

    def zoneEnableSchedule(messana, value, zoneNbr):
        #logging.debug('zoneEnableSchedule called for zone: ' + str(zoneNbr))
        
        status = messana.pushZoneDataIndividual(zoneNbr, 'mScheduleOn', value)
        return(status)


    def getZoneEnableScheduleISYdriver(messana, zoneNbr):
        #logging.debug('getZoneEnableScheduleISYdriver called for zone: '+str(zoneNbr))
        
        Key = ''
        zoneName = messana.zoneID+str(zoneNbr)
        for ISYkey in messana.ISYmap[zoneName]:
            if messana.ISYmap[zoneName][ISYkey]['messana'] == 'mScheduleOn':
                Key = ISYkey
        return(Key) 

    def zonesetCurrentDPt(messana, value,  zoneNbr):
        #logging.debug('zonesetCurrentDPt called for zone: ' + str(zoneNbr))
        
        status = messana.pushZoneDataIndividual(zoneNbr, 'mCurrentSetpointDP', value)
        return(status)

    def getZonesetCurrentDPtISYdriver(messana, zoneNbr):
        #logging.debug('getZonesetCurrentDPtISYdriver called for zone: '+str(zoneNbr))
        
        Key = ''
        zoneName = messana.zoneID+str(zoneNbr)
        for ISYkey in messana.ISYmap[zoneName]:
            if messana.ISYmap[zoneName][ISYkey]['messana'] == 'mCurrentSetpointDP':
                Key = ISYkey
        return(Key)  

    def zonesetCurrentRH(messana, value,  zoneNbr):
        #logging.debug('zonesetCurrentRH called for zone: ' + str(zoneNbr))
        
        status = messana.pushZoneDataIndividual(zoneNbr, 'mCurrentSetpointRH', value)
        return(status)

    def getZonesetCurrentRHISYdriver(messana, zoneNbr):
        #logging.debug('getZonesetCurrentRHISYdriver called for zone: '+str(zoneNbr))
        
        Key = ''
        zoneName = messana.zoneID+str(zoneNbr)
        for ISYkey in messana.ISYmap[zoneName]:
            if messana.ISYmap[zoneName][ISYkey]['messana'] == 'mCurrentSetpointRH':
                Key = ISYkey
        return(Key)  

    def zonesetDehumDpt(messana, value,  zoneNbr):
        #logging.debug('zonesetDehumDpt called for zone: ' + str(zoneNbr))
        
        status = messana.pushZoneDataIndividual(zoneNbr, 'mDehumSetpointDP', value)
        return(status)

    def getZonesetDehumDPtISYdriver(messana, zoneNbr):
        #logging.debug('getZonesetDehumDPtISYdriver called for zone: '+str(zoneNbr))
        Key = ''
        zoneName = messana.zoneID+str(zoneNbr)
        for ISYkey in messana.ISYmap[zoneName]:
            if messana.ISYmap[zoneName][ISYkey]['messana'] == 'mDehumSetpointDP':
                Key = ISYkey
        return(Key)  

    def zonesetDehumRH(messana, value,  zoneNbr):
        #logging.debug('zonesetDehumRH called for zone: ' + str(zoneNbr))
        
        status = messana.pushZoneDataIndividual(zoneNbr, 'mDehumSetpointRH', value)
        return(status)

    def getZonesetDehumRHISYdriver(messana, zoneNbr):
        #logging.debug('getZonesetDehumRHISYdriver called for zone: '+str(zoneNbr))
        Key = ''
        zoneName = messana.zoneID+str(zoneNbr)
        for ISYkey in messana.ISYmap[zoneName]:
            if messana.ISYmap[zoneName][ISYkey]['messana'] == 'mDehumSetpointRH':
                Key = ISYkey
        return(Key)  

    def zonesetHumRH(messana, value,  zoneNbr):
        #logging.debug('zonesetHumRH called for zone: ' + str(zoneNbr))
        
        status = messana.pushZoneDataIndividual(zoneNbr, 'mHumSetpointRH', value)
        return(status)

    def getZonesetHumRHISYdriver(messana, zoneNbr):
        #logging.debug('getZonesetHumRHISYdriver called for zone: '+str(zoneNbr))
        Key = ''
        zoneName = messana.zoneID+str(zoneNbr)
        for ISYkey in messana.ISYmap[zoneName]:
            if messana.ISYmap[zoneName][ISYkey]['messana'] == 'mHumSetpointRH':
                Key = ISYkey
        return(Key)  

    def zonesetHumDpt(messana, value,  zoneNbr):
        #logging.debug('zonesetDehumDpt called for zone: ' + str(zoneNbr))
        
        status = messana.pushZoneDataIndividual(zoneNbr, 'mHumSetpointDP', value)
        return(status)

    def getZonesetHumDPtISYdriver(messana, zoneNbr):
        #logging.debug('getZonesetDehumDPtISYdriver called for zone: '+str(zoneNbr))
        Key = ''
        zoneName = messana.zoneID+str(zoneNbr)
        for ISYkey in messana.ISYmap[zoneName]:
            if messana.ISYmap[zoneName][ISYkey]['messana'] == 'mHumSetpointDP':
                Key = ISYkey
        return(Key)  

    def zonesetCO2 (messana, value,  zoneNbr):
        #logging.debug('zonesetDehumDpt called for zone: ' + str(zoneNbr))
        
        status = messana.pushZoneDataIndividual(zoneNbr, 'mCO2', value)
        return(status)

    def getZonesetCO2ISYdriver(messana, zoneNbr):
        #logging.debug('getZonesetDehumDPtISYdriver called for zone: '+str(zoneNbr))
        Key = ''
        zoneName = messana.zoneID+str(zoneNbr)
        for ISYkey in messana.ISYmap[zoneName]:
            if messana.ISYmap[zoneName][ISYkey]['messana'] == 'mCO2':
                Key = ISYkey
        return(Key)  

    def getZoneISYdriverInfo(messana, mKey, zoneNbr):
        info = {}
        zoneStr = messana.zoneID+str(zoneNbr)
        if mKey in messana.setupFile['nodeDef'][zoneStr]['sts']:
            keys = list(messana.setupFile['nodeDef'][zoneStr]['sts'][mKey].keys())
            info['driver'] = keys[0]
            tempData =  messana.GETNodeData(messana.zoneID, zoneNbr, mKey)
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
            editor = messana.setupFile['nodeDef'][zoneStr]['sts'][mKey][keys[0]]

            info['uom'] = messana.setupFile['editors'][editor]['ISYuom']
        return(info)


    ###################################################################        
    #MacroZone

    def updateMacrozoneData(messana,  level, macrozoneNbr):
        #logging.debug('updatMacrozoneData: ' + str(macrozoneNbr))

        keys =[]
        if level == 'all':
            #logging.debug('ALL update macrozone ' + str(macrozoneNbr))
            keys =  messana.macrozonePullKeys(macrozoneNbr)
        elif level == 'active':
            #logging.debug('ACTIVE update macrozone ' + str(macrozoneNbr))
            keys =  messana.macrozoneActiveKeys(macrozoneNbr)
        
        messana.dataOK = True
        for mKey in keys:
            messana.data = messana.pullMacrozoneDataIndividual(macrozoneNbr, mKey)
            messana.dataOK = messana.dataOK and messana.data['statusOK']
        return(messana.dataOK)


    def pullMacrozoneDataIndividual(messana, macrozoneNbr, mKey): 
        #logging.debug('pullMacroZoneDataIndividual: ' +str(macrozoneNbr)  + ' ' + mKey)    
        return(messana.pullNodeDataIndividual(macrozoneNbr, messana.macrozoneID, mKey))

    def pushMacrozoneDataIndividual(messana, macrozoneNbr, mKey, value):
        #logging.debug('pushMacroZoneDataIndividual: ' +str(macrozoneNbr)  + ' ' + mKey + ' ' + str(value))  
        return(messana.pushNodeDataIndividual(macrozoneNbr, messana.macrozoneID, mKey, value))

    def macrozonePullKeys(messana, macrozoneNbr):
        #logging.debug('macrozonePullKeys')
        return( messana.getNodeKeys (macrozoneNbr, messana.macrozoneID, 'GETstr'))

    def macrozonePushKeys(messana, macrozoneNbr):
        #logging.debug('macrozonePushKeys')
        return( messana.getNodeKeys (macrozoneNbr, messana.macrozoneID, 'PUTstr'))
  
    def macrozoneActiveKeys(messana, macrozoneNbr):
        #logging.debug('macrozoneActiveKeys')
        return( messana.getNodeKeys (macrozoneNbr, messana.macrozoneID, 'Active'))    

    def getMacrozoneCount(messana):
        return(messana.mSystem[messana.systemID]['data']['mMacrozoneCount'])


    def getMacrozoneName(messana, macroZoneNbr):
        tempName = messana.pullNodeDataIndividual(macroZoneNbr, messana.macrozoneID, 'mName')
        if tempName['statusOK']:
            return(tempName['data'])
        else:
            return('NA')

    def getMacrozoneCapability(messana, macrozoneNbr): 
        #logging.debug('getMacrozoneCapability for ' + str(macrozoneNbr))        
        messana.getNodeCapability(messana.macrozoneID, macrozoneNbr)

    def getMacrozoneAddress(messana, macrozoneNbr):
        return(messana.macrozoneID + str(macrozoneNbr))

    def getMacrozoneMessanaISYkey(messana, ISYkey, macrozoneNbr):
        macrozoneName = messana.macrozoneID+str(macrozoneNbr)
        return(messana.ISYmap[macrozoneName][ISYkey]['messana'])

    def getMacrozoneISYValue(messana, ISYkey, macrozoneNbr):
        macrozoneName = messana.macrozoneID+str(macrozoneNbr)
        messanaKey = messana.ISYmap[macrozoneName][ISYkey]['messana']
        try:
            data = messana.pullMacrozoneDataIndividual(macrozoneNbr, messanaKey)
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


    def getMacrozoneISYdriverInfo(messana, mKey, macrozoneNbr):
        info = {}
        macrozoneStr = messana.macrozoneID+str(macrozoneNbr)
        if mKey in messana.setupFile['nodeDef'][macrozoneStr]['sts']:
            keys = list(messana.setupFile['nodeDef'][macrozoneStr]['sts'][mKey].keys())
            info['driver'] = keys[0]
            tempData =  messana.GETNodeData(messana.macrozoneID, macrozoneNbr, mKey)
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
            editor = messana.setupFile['nodeDef'][macrozoneStr]['sts'][mKey][keys[0]]

            info['uom'] = messana.setupFile['editors'][editor]['ISYuom']
        return(info)

    def macrozoneSetStatus(messana, value, macrozoneNbr):
        #logging.debug(' macrozoneSetstatus called for macrozone: ' + str(macrozoneNbr))
        
        status = messana.pushMacrozoneDataIndividual(macrozoneNbr, 'mStatus', value)
        return(status)
 

    def getMacrozoneStatusISYdriver(messana, macrozoneNbr):
        #logging.debug('getMacrozoneStatusISYdriver called for macrozone: '+str(macrozoneNbr))
        
        Key = ''
        macrozoneName = messana.macrozoneID+str(macrozoneNbr)
        for ISYkey in messana.ISYmap[macrozoneName]:
            if messana.ISYmap[macrozoneName][ISYkey]['messana'] == 'mStatus':
                Key = ISYkey
        return(Key)  
        


    def macrozoneSetSetpoint(messana, value,  macrozoneNbr):
        #logging.debug('macrozoneSetSetpoint called for macrozone: ' + str(macrozoneNbr))
        
        status = messana.pushMacrozoneDataIndividual(macrozoneNbr, 'mSetpoint', value)
        return(status)

    def getMacrozoneSetPointISYdriver(messana, macrozoneNbr):
        #logging.debug('getMacrozoneSetpointISYdriver called for macrozone: '+str(macrozoneNbr))
        
        Key = ''
        macrozoneName = messana.macrozoneID+str(macrozoneNbr)
        for ISYkey in messana.ISYmap[macrozoneName]:
            if messana.ISYmap[macrozoneName][ISYkey]['messana'] == 'mSetpoint':
                Key = ISYkey
        return(Key)  
  

    def macrozoneEnableSchedule(messana, value, macrozoneNbr):
        #logging.debug('macrozoneEnableSchedule called for macrozone: ' + str(macrozoneNbr))
        
        status = messana.pushMacrozoneDataIndividual(macrozoneNbr, 'mScheduleOn', value)
        return(status)


    def getMacrozoneEnableScheduleISYdriver(messana, macrozoneNbr):
        #logging.debug('getMacrozoneEnableScheduleISYdriver called for macrozone: '+str(macrozoneNbr))
        
        Key = ''
        macrozoneName = messana.macrozoneID+str(macrozoneNbr)
        for ISYkey in messana.ISYmap[macrozoneName]:
            if messana.ISYmap[macrozoneName][ISYkey]['messana'] == 'mScheduleOn':
                Key = ISYkey
        return(Key) 






    ##############################################################
    # Hot Cold Change Over
    def updateHcCoData(messana, level,  HcCoNbr):
        #logging.debug('updatHcCoData: ' + str(HcCoNbr))
        keys =[]
        if level == 'all':
            #logging.debug('ALL update Hot Cold CO ' + str(HcCoNbr))
            keys =  messana.HcCoPullKeys(HcCoNbr)
        elif level == 'active':
            #logging.debug('ACTIVE update Hot Cold CO  ' + str(HcCoNbr))
            keys =  messana.HcCoActiveKeys(HcCoNbr)
        
        messana.dataOK = True
        for mKey in keys:
            messana.data = messana.pullHcCoDataIndividual(HcCoNbr, mKey)
            messana.dataOK = messana.dataOK and messana.data['statusOK']
        return(messana.dataOK)

    def getHcCoCapability(messana, HcCoNbr): 
        #logging.debug('getHC_COCapability for ' + str(HcCoNbr))        
        messana.getNodeCapability(messana.HotColdcoID , HcCoNbr)

    def pullHcCoDataIndividual(messana, HcCoNbr, mKey): 
        #logging.debug('pullHC_CODataIndividual: ' +str(HcCoNbr)  + ' ' + mKey)    
        return(messana.pullNodeDataIndividual(HcCoNbr, messana.HotColdcoID , mKey))

    def pushHcCoDataIndividual(messana, HcCoNbr, mKey, value):
        #logging.debug('pushHC_CODataIndividual: ' +str(HcCoNbr)  + ' ' + mKey + ' ' + str(value))  
        return(messana.pushNodeDataIndividual(HcCoNbr, messana.HotColdcoID , mKey, value))

    def HcCoPullKeys(messana, HcCoNbr):
        #logging.debug('hc_coPullKeys')
        return( messana.getNodeKeys (HcCoNbr, messana.HotColdcoID , 'GETstr'))

    def HcCoPushKeys(messana, HcCoNbr):
        #logging.debug('hc_coPushKeys')
        return( messana.getNodeKeys (HcCoNbr, messana.HotColdcoID , 'PUTstr'))
  
    def HcCoActiveKeys(messana, HcCoNbr):
        #logging.debug('hc_coActiveKeys')
        return( messana.getNodeKeys (HcCoNbr, messana.HotColdcoID , 'Active'))    

    def getHcCoCount(messana):
        return(messana.mSystem[ messana.systemID]['data']['mhc_coCount'])
        
    def getHcCoName(messana, HcCoNbr):
        tempName = messana.pullNodeDataIndividual(HcCoNbr, messana.HotColdcoID, 'mName')
        if tempName['statusOK']:
            return(tempName['data'])
        else:
            return('NA')
            
    def getHcCoAddress(messana, HcCoNbr):
        return(messana.HotColdcoID + str(HcCoNbr))


    def HcCoSetMode(messana, value, HcCoNbr):
        #logging.debug('HcCoSetMode called for Hot Cold: ' + str(HcCoNbr))
        
        status = messana.pushHcCoDataIndividual(HcCoNbr, 'mMode', value)
        return(status)


    def getHcCoISYdriverInfo(messana, mKey, HcCoNbr):
        info = {}
        HcCoStr = messana.HotColdcoID+str(HcCoNbr)
        if mKey in messana.setupFile['nodeDef'][HcCoStr]['sts']:
            keys = list(messana.setupFile['nodeDef'][HcCoStr]['sts'][mKey].keys())
            info['driver'] = keys[0]
            tempData =  messana.GETNodeData(messana.HotColdcoID, HcCoNbr, mKey)
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
            editor = messana.setupFile['nodeDef'][HcCoStr]['sts'][mKey][keys[0]]
            info['uom'] = messana.setupFile['editors'][editor]['ISYuom']
        return(info)

    def getHcCoISYValue(messana, ISYkey, HcCoNbr):
        HcCoName = messana.HotColdcoID+str(HcCoNbr)
        messanaKey = messana.ISYmap[HcCoName][ISYkey]['messana']
        try:
            data = messana.pullHcCoDataIndividual(HcCoNbr, messanaKey)
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

    def getHcCoMessanaISYkey(messana, ISYkey, HcCoNbr):
        HcCoName = messana.HotColdcoID+str(HcCoNbr)
        return(messana.ISYmap[HcCoName][ISYkey]['messana'])

    def getHcCoSetModeISYdriver(messana, HcCoNbr):
        #logging.debug('getHcCoSetModeISYdriver called for Hot Cold: '+str(HcCoNbr))
        Key = ''
        HcCoName = messana.HotColdcoID+str(HcCoNbr)
        for ISYkey in messana.ISYmap[HcCoName]:
            if messana.ISYmap[HcCoName][ISYkey]['messana'] == 'mMode':
                Key = ISYkey
        return(Key) 

    def HcCoAdaptiveComfort(messana, value, HcCoNbr):
        #logging.debug('HcCoAdaptiveComfort called for Hot Cold: ' + str(HcCoNbr))
        
        status = messana.pushHcCoDataIndividual(HcCoNbr, 'mAdaptiveComfort', value)
        return(status)


    def getHcCoAdaptiveComfortISYdriver(messana, HcCoNbr):
        #logging.debug('getHcCoAdaptiveComfortISYdriver called for Hot Cold: '+str(HcCoNbr))
        Key = ''
        HcCoName = messana.HotColdcoID+str(HcCoNbr)
        for ISYkey in messana.ISYmap[HcCoName]:
            if messana.ISYmap[HcCoName][ISYkey]['messana'] == 'mAdaptiveComfort':
                Key = ISYkey
        return(Key) 

    ####################################################
    #ATU
   
    def getAtuCapability(messana, atuNbr): 
        #logging.debug('getAtuCapability for ' + str(atuNbr))             
        messana.getNodeCapability(messana.atuID, atuNbr)
    
    def updateAtuData(messana,  level, atuNbr):
        #logging.debug('updateAtuData: ' + str(atuNbr))

        keys =[]
        if level == 'all':
            #logging.debug('ALL update atu ' + str(atuNbr))
            keys =  messana.atuPullKeys(atuNbr)
        elif level == 'active':
            #logging.debug('ACTIVE update atu ' + str(atuNbr))
            keys =  messana.atuActiveKeys(atuNbr)
        
        messana.dataOK = True
        for mKey in keys:
            messana.data = messana.pullAtuDataIndividual(atuNbr, mKey)
            messana.dataOK = messana.dataOK and messana.data['statusOK']
        return(messana.dataOK)
    

    def getAtuMessanaISYkey(messana, ISYkey, atuNbr):
        atuName = messana.atuID+str(atuNbr)
        return(messana.ISYmap[atuName][ISYkey]['messana'])

    def getAtuISYValue(messana, ISYkey, atuNbr):
        atuName = messana.atuID+str(atuNbr)
        messanaKey = messana.ISYmap[atuName][ISYkey]['messana']
        try:
            data = messana.pullAtuDataIndividual(atuNbr, messanaKey)
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


    def pullAtuDataIndividual(messana, atuNbr, mKey): 
        #logging.debug('pullAtuDataIndividual: ' +str(atuNbr)  + ' ' + mKey)    
        return(messana.pullNodeDataIndividual(atuNbr, messana.atuID, mKey))

    def pushAtuDataIndividual(messana, ATUNbr, mKey, value):
        #logging.debug('pushATUDataIndividual: ' +str(ATUNbr)  + ' ' + mKey + ' ' + str(value))  
        return(messana.pushNodeDataIndividual(ATUNbr, messana.atuID, mKey, value))

    def atuPullKeys(messana, ATUNbr): 
        #logging.debug('atusPullKeys')
        return( messana.getNodeKeys (ATUNbr, messana.atuID, 'GETstr'))

    def atuPushKeys(messana, ATUNbr):
        #logging.debug('atusPushKeys')
        return( messana.getNodeKeys (ATUNbr, messana.atuID, 'PUTstr'))
  
    def atuActiveKeys(messana, ATUNbr):
        #logging.debug('atusActiveKeys')
        return( messana.getNodeKeys (ATUNbr, messana.atuID, 'Active'))    
  
    def getAtuCount(messana):
        return(messana.mSystem[ messana.systemID]['data']['mATUcount'])

    
    def getAtuName(messana, atuNbr):
        tempName = messana.pullNodeDataIndividual(atuNbr, messana.atuID, 'mName')
        if tempName['statusOK']:
            return(tempName['data'])
        else:
            return('NA')
            
    def getAtuAddress(messana, atuNbr):
        return(messana.atuID + str(atuNbr))

    def getAtuISYdriverInfo(messana, mKey, atuNbr):
        info = {}
        atuStr = messana.atuID+str(atuNbr)
        if mKey in messana.setupFile['nodeDef'][atuStr]['sts']:
            keys = list(messana.setupFile['nodeDef'][atuStr]['sts'][mKey].keys())
            info['driver'] = keys[0]
            tempData =  messana.GETNodeData(messana.atuID, atuNbr, mKey)
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
            editor = messana.setupFile['nodeDef'][atuStr]['sts'][mKey][keys[0]]
            info['uom'] = messana.setupFile['editors'][editor]['ISYuom']
        return(info)

    def atuSetStatus(messana, value, atuNbr):
        #logging.debug ('atuSetStatus')
        status = messana.pushAtuDataIndividual(atuNbr, 'mStatus', value)
        return(status)
 
    def getAtuStatusISYdriver(messana, atuNbr):
        #logging.debug ('getAtuStatusISYdriver called')
        Key = ''
        atuName = messana.atuID+str(atuNbr)
        for ISYkey in messana.ISYmap[atuName]:
            if messana.ISYmap[atuName][ISYkey]['messana'] == 'mStatus':
                Key = ISYkey
        return(Key)  
  
    def atuSetHrv(messana, value, atuNbr):
        #logging.debug ('atuSetHRV called')
        status = messana.pushAtuDataIndividual(atuNbr, 'mHRVOn', value)
        return(status)

    def getAtuHrvISYdriver(messana, atuNbr):
        #logging.debug ('getAtuHrvISYdriver called')
        atuName = messana.atuID+str(atuNbr)
        for ISYkey in messana.ISYmap[atuName]:
            if messana.ISYmap[atuName][ISYkey]['messana'] == 'mHRVOn':
                Key = ISYkey
        return(Key)  

    def atuSetFlowlevel(messana, value, atuNbr):
        #logging.debug ('atuSetFlowlevel called')
        status = messana.pushAtuDataIndividual(atuNbr, 'mFlowLevel', value)
        return(status)

    def getAtuSetFlowlevelISYdriver(messana, atuNbr):
        #logging.debug ('getAtuSetPointISYdriver called')
        atuName = messana.atuID+str(atuNbr)
        for ISYkey in messana.ISYmap[atuName]:
            if messana.ISYmap[atuName][ISYkey]['messana'] == 'mFlowLevel':
                Key = ISYkey
        return(Key)  
        
    def atuSetHum(messana, value, atuNbr):
        #logging.debug ('atuSetHum called')
        status = messana.pushAtuDataIndividual(atuNbr, 'mHUMOn', value)
        return(status)

    def getAtuSetHumISYdriver(messana, atuNbr):
        #logging.debug ('getAtuSetHumISYdriver called')
        atuName = messana.atuID+str(atuNbr)
        for ISYkey in messana.ISYmap[atuName]:
            if messana.ISYmap[atuName][ISYkey]['messana'] == 'mHUMOn':
                Key = ISYkey
        return(Key)  

    def atuSetInt(messana, value, atuNbr):
        #logging.debug ('atuSetInt called')
        status = messana.pushAtuDataIndividual(atuNbr, 'mINTOn', value)
        return(status)

    def getAtuSetIntISYdriver(messana, atuNbr):
        #logging.debug ('getAtuSetIntISYdriver called')
        atuName = messana.atuID+str(atuNbr)
        for ISYkey in messana.ISYmap[atuName]:
            if messana.ISYmap[atuName][ISYkey]['messana'] == 'mINTOn':
                Key = ISYkey
        return(Key)  

    def atuSetNtd(messana, value, atuNbr):
        #logging.debug ('atuSetNtd called')
        status = messana.pushAtuDataIndividual(atuNbr, 'mNTDOn', value)
        return(status)

    def getAtuSetNtdISYdriver(messana, atuNbr):
        #logging.debug ('getAtuSetNtdISYdriver called')
        atuName = messana.atuID+str(atuNbr)
        for ISYkey in messana.ISYmap[atuName]:
            if messana.ISYmap[atuName][ISYkey]['messana'] == 'mNTDOn':
                Key = ISYkey
        return(Key)  

    def atuSetHumSetpointRH(messana, value, atuNbr):
        #logging.debug ('atuSetHumSetpointRH called')
        status = messana.pushAtuDataIndividual(atuNbr, 'mHumSetpointRH', value)
        return(status)

    def getAtuSetHumSetpointRHISYdriver(messana, atuNbr):
        #logging.debug ('getAtuSetHumSetpointRHISYdriver called')
        atuName = messana.atuID+str(atuNbr)
        for ISYkey in messana.ISYmap[atuName]:
            if messana.ISYmap[atuName][ISYkey]['messana'] == 'mHumSetpointRH':
                Key = ISYkey
        return(Key)

    def atuSetHumSetpointDP(messana, value, atuNbr):
        #logging.debug ('atuSetHumSetpointDP called')
        status = messana.pushAtuDataIndividual(atuNbr, 'mHumSetpointDP', value)
        return(status)

    def getAtuSetHumSetpointDPISYdriver(messana, atuNbr):
        #logging.debug ('getAtuSetHumSetpointRHISYdriver called')
        atuName = messana.atuID+str(atuNbr)
        for ISYkey in messana.ISYmap[atuName]:
            if messana.ISYmap[atuName][ISYkey]['messana'] == 'mHumSetpointDP':
                Key = ISYkey
        return(Key)  

    def atuSetDehumSetpointRH(messana, value, atuNbr):
        #logging.debug ('atuSetDehumSetpointRH called')
        status = messana.pushAtuDataIndividual(atuNbr, 'mDehumSetpointRH', value)
        return(status)

    def getAtuSetDehumSetpointRHISYdriver(messana, atuNbr):
        #logging.debug ('getAtuSetDehumSetpointRHISYdriver called')
        atuName = messana.atuID+str(atuNbr)
        for ISYkey in messana.ISYmap[atuName]:
            if messana.ISYmap[atuName][ISYkey]['messana'] == 'mDehumSetpointRH':
                Key = ISYkey
        return(Key)  


    def atuSetDehumSetpointDP(messana, value, atuNbr):
        #logging.debug ('atuSetDehumSetpointDP called')
        status = messana.pushAtuDataIndividual(atuNbr, 'mDehumSetpointDP', value)
        return(status)

    def getAtuSetDehumSetpointDPISYdriver(messana, atuNbr):
        #logging.debug ('getAtuSetDehumSetpointDPISYdriver called')
        atuName = messana.atuID+str(atuNbr)
        for ISYkey in messana.ISYmap[atuName]:
            if messana.ISYmap[atuName][ISYkey]['messana'] == 'mDehumSetpointDP':
                Key = ISYkey
        return(Key)

    def atuSetCurrentSetpointRH(messana, value, atuNbr):
        #logging.debug ('atuSetCurrentSetpointRH called')
        status = messana.pushAtuDataIndividual(atuNbr, 'mCurrentSetpointRH', value)
        return(status)

    def getAtuSetCurrentSetpointRHISYdriver(messana, atuNbr):
        #logging.debug ('getAtuSetCurrentSetpointRHISYdriver called')
        atuName = messana.atuID+str(atuNbr)
        for ISYkey in messana.ISYmap[atuName]:
            if messana.ISYmap[atuName][ISYkey]['messana'] == 'mCurrentSetpointRH':
                Key = ISYkey
        return(Key)  

    def atuSetCurrentSetpointDP(messana, value, atuNbr):
        #logging.debug ('atuSetCurrentSetpointDP called')
        status = messana.pushAtuDataIndividual(atuNbr, 'mCurrentSetpointDP', value)
        return(status)

    def getAtuSetCurrentSetpointDPISYdriver(messana, atuNbr):
        #logging.debug ('getAtuSetCurrentSetpointDPISYdriver called')
        atuName = messana.atuID+str(atuNbr)
        for ISYkey in messana.ISYmap[atuName]:
            if messana.ISYmap[atuName][ISYkey]['messana'] == 'mCurrentSetpointDP':
                Key = ISYkey
        return(Key)  



    #################################################################
    #Fan Coils
    def updateFanCoilData(messana, level, FanCoilNbr):
        #logging.debug('updatFanCoilData: ' + str(FanCoilNbr))
        keys =[]
        if level == 'all':
            #logging.debug('ALL update Fan Coil ' + str(FanCoilNbr))
            keys =  messana.fan_coilPullKeys(FanCoilNbr)
        elif level == 'active':
            #logging.debug('ACTIVE update Fan Coil  ' + str(FanCoilNbr))
            keys =  messana.fan_coilActiveKeys(FanCoilNbr)
        
        messana.dataOK = True
        for mKey in keys:
            messana.data = messana.pullFanCoilDataIndividual(FanCoilNbr, mKey)
            messana.dataOK = messana.dataOK and messana.data['statusOK']
        return(messana.dataOK)

    
    def getFanCoilName(messana, fanCoilNbr):
        tempName = messana.pullNodeDataIndividual(fanCoilNbr, messana.fcID, 'mName')
        if tempName['statusOK']:
            return(tempName['data'])
        else:
            return('NA')
            
    def getFanCoilAddress(messana, fanCoilNbr):
        return(messana.fcID + str(fanCoilNbr))  

    def getFanCoilCapability(messana, FanCoilNbr): 
        #logging.debug('getFanCoilCapability for ' + str(FanCoilNbr))              
        messana.getNodeCapability(messana.fcID, FanCoilNbr)

    def pullFanCoilDataIndividual(messana, FanCoilNbr, mKey): 
        #logging.debug('pullFanCoilDataIndividual: ' +str(FanCoilNbr)  + ' ' + mKey)    
        return(messana.pullNodeDataIndividual(FanCoilNbr, messana.fcID, mKey))

    def pushFanCoilDataIndividual(messana, FanCoilNbr, mKey, value):
        #logging.debug('pushFanCoilDataIndividual: ' +str(FanCoilNbr)  + ' ' + mKey + ' ' + str(value))  
        return(messana.pushNodeDataIndividual(FanCoilNbr, messana.fcID, mKey, value))

    def fan_coilPullKeys(messana, FanCoilNbr):
        #logging.debug('fan_coilPullKeys')
        return( messana.getNodeKeys (FanCoilNbr, messana.fcID, 'GETstr'))

    def fan_coilPushKeys(messana, FanCoilNbr):
        #logging.debug('fan_coilPushKeys')
        return( messana.getNodeKeys (FanCoilNbr, messana.fcID, 'PUTstr'))
  
    def fan_coilActiveKeys(messana, FanCoilNbr):
        #logging.debug('fan_coilActiveKeys')
        return( messana.getNodeKeys (FanCoilNbr, messana.fcID, 'Active'))    
    
    def getFanCoilCount(messana):
        return(messana.mSystem[ messana.systemID]['data']['mFanCoilCount'])

    def getFanCoilISYdriverInfo(messana, mKey, FanCoilNbr):
        info = {}
        FanCoilStr = messana.fcID+str(FanCoilNbr)
        if mKey in messana.setupFile['nodeDef'][FanCoilStr]['sts']:
            keys = list(messana.setupFile['nodeDef'][FanCoilStr]['sts'][mKey].keys())
            info['driver'] = keys[0]
            tempData =  messana.GETNodeData(messana.fcID, FanCoilNbr, mKey)
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
            editor = messana.setupFile['nodeDef'][FanCoilStr]['sts'][mKey][keys[0]]

            info['uom'] = messana.setupFile['editors'][editor]['ISYuom']
        return(info)

    def getFanCoilMessanaISYkey(messana, ISYkey, fanCoilNbr):
        fanCoilName = messana.fcID+str(fanCoilNbr)
        return(messana.ISYmap[fanCoilName][ISYkey]['messana'])

    def fanCoilSetCoolingSpeed(messana, value, FanCoilNbr):
        #logging.debug ('fanCoilSetCoolingSpeed called')
        status = messana.pushFanCoilDataIndividual(FanCoilNbr, 'mCoolingSpeed', value)
        return(status)
 
    def getFanCoilCoolingSpeedISYdriver(messana, FanCoilNbr):
        #logging.debug ('getFanCoilCoolingSpeedISYdriver called')
        Key = ''
        fanCoilName = messana.fcID+str(FanCoilNbr)
        for ISYkey in messana.ISYmap[fanCoilName]:
            if messana.ISYmap[fanCoilName][ISYkey]['messana'] == 'mCoolingSpeed':
                Key = ISYkey
        return(Key) 

    def getFanCoilISYValue(messana, ISYkey, fanCoilNbr):
        fanCoilName = messana.fcID+str(fanCoilNbr)
        messanaKey = messana.ISYmap[fanCoilName][ISYkey]['messana']
        try:
            data = messana.pullFanCoilDataIndividual(fanCoilNbr, messanaKey)
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

    def fanCoilSetHeatingSpeed(messana, value, FanCoilNbr):
        #logging.debug ('fanCoilSetHeatingSpeed called')
        status = messana.pushFanCoilDataIndividual(FanCoilNbr, 'mHeatingSpeed', value)
        return(status)
 
    def getFanCoilHeatingSpeedISYdriver(messana, FanCoilNbr):
        #logging.debug ('getFanCoilHeatingSpeedISYdriver called')
        Key = ''
        fanCoilName = messana.fcID+str(FanCoilNbr)
        for ISYkey in messana.ISYmap[fanCoilName]:
            if messana.ISYmap[fanCoilName][ISYkey]['messana'] == 'mHeatingSpeed':
                Key = ISYkey
        return(Key) 


    def fanCoilSetStatus(messana, value, FanCoilNbr):
        #logging.debug ('fanCoilSetStatus called')
        status = messana.pushFanCoilDataIndividual(FanCoilNbr, 'mStatus', value)
        return(status)
 
    def getFanCoilStatusISYdriver(messana, FanCoilNbr):
        #logging.debug ('getFanCoilHeatingSpeedISYdriver called')
        Key = ''
        fanCoilName = messana.fcID+str(FanCoilNbr)
        for ISYkey in messana.ISYmap[fanCoilName]:
            if messana.ISYmap[fanCoilName][ISYkey]['messana'] == 'mStatus':
                Key = ISYkey
        return(Key) 

    #############################################################
    #EnergySources
    def updateEnergySourceData(messana, level, EnergySourceNbr):
        #logging.debug('updatEnergySourceData: ' + str(EnergySourceNbr))
        keys =[]
        if level == 'all':
            #logging.debug('ALL update Energy Source ' + str(EnergySourceNbr))
            keys =  messana.energySourcePullKeys(EnergySourceNbr)
        elif level == 'active':
            #logging.debug('ACTIVE update Energy Source  ' + str(EnergySourceNbr))
            keys =  messana.energySourceActiveKeys(EnergySourceNbr)
        
        messana.dataOK = True
        for mKey in keys:
            messana.data = messana.pullEnergySourceDataIndividual(EnergySourceNbr, mKey)
            messana.dataOK = messana.dataOK and messana.data['statusOK']
        return(messana.dataOK)

        
    def getEnergySourceCount(messana):
        return(messana.mSystem[ messana.systemID]['data']['mEnergySourceCount'])

    
    def getEnergySourceName(messana, energySourceNbr):
        tempName = messana.pullNodeDataIndividual(energySourceNbr, messana.energySourceID, 'mName')
        if tempName['statusOK']:
            return(tempName['data'])
        else:
            return('NA')
            
    def getEnergySourceAddress(messana, energySourceNbr):
        return(messana.energySourceID + str(energySourceNbr))     

    def getEnergySourceCapability(messana, EnergySourceNbr): 
        #logging.debug('getEnergySourceCapability for ' + str(EnergySourceNbr))          
        messana.getNodeCapability( messana.energySourceID, EnergySourceNbr)

    def pullEnergySourceDataIndividual(messana, EnergySourceNbr, mKey): 
        #logging.debug('pullEnergySourceDataIndividual: ' +str(EnergySourceNbr)  + ' ' + mKey)    
        return(messana.pullNodeDataIndividual(EnergySourceNbr,  messana.energySourceID, mKey))

    def pushEnergySourceDataIndividual(messana, EnergySourceNbr, mKey, value):
        #logging.debug('pushEnergySourceDataIndividual: ' +str(EnergySourceNbr)  + ' ' + mKey + ' ' + str(value))  
        return(messana.pushNodeDataIndividual(EnergySourceNbr,  messana.energySourceID, mKey, value))

    def energySourcePullKeys(messana, EnergySourceNbr):
        #logging.debug('energySourcePullKeys')
        return( messana.getNodeKeys (EnergySourceNbr,  messana.energySourceID, 'GETstr'))

    def energySourcePushKeys(messana, EnergySourceNbr):
        #logging.debug('EnergySourcePushKeys')
        return( messana.getNodeKeys (EnergySourceNbr,  messana.energySourceID, 'PUTstr'))
  
    def energySourceActiveKeys(messana, EnergySourceNbr):
        #logging.debug('energySourceActiveKeys')
        return( messana.getNodeKeys (EnergySourceNbr,  messana.energySourceID, 'Active'))    
    
    def getEnergySourceISYdriverInfo(messana, mKey, EnergySourceNbr):
        info = {}
        EnergySourceStr = messana.energySourceID+str(EnergySourceNbr)
        if mKey in messana.setupFile['nodeDef'][EnergySourceStr]['sts']:
            keys = list(messana.setupFile['nodeDef'][EnergySourceStr]['sts'][mKey].keys())
            info['driver'] = keys[0]
            tempData =  messana.GETNodeData(messana.energySourceID, EnergySourceNbr, mKey)
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
            editor = messana.setupFile['nodeDef'][EnergySourceStr]['sts'][mKey][keys[0]]

            info['uom'] = messana.setupFile['editors'][editor]['ISYuom']
        return(info)

    def getEnergySourceISYValue(messana, ISYkey, energySourceNbr):
        energySourceName = messana.energySourceID+str(energySourceNbr)
        messanaKey = messana.ISYmap[energySourceName][ISYkey]['messana']
        try:
            data = messana.pullEnergySourceDataIndividual(energySourceNbr, messanaKey)
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

    def getEnergySourceMessanaISYkey(messana, ISYkey, energySourceNbr):
        energySourceName = messana.energySourceID+str(energySourceNbr)
        return(messana.ISYmap[energySourceName][ISYkey]['messana'])

   
    #####################################################
    #Buffer Tank
    
  
    def getBufferTankCapability(messana, bufTankNbr): 
        #logging.debug('getBufferTankCapability for ' + str(bufTankNbr))              
        messana.getNodeCapability(messana.bufferTankID, bufTankNbr)

    def getBufferTankMessanaISYkey(messana, ISYkey, bufTankNbr):
        bufTankName = messana.bufferTankID+str(bufTankNbr)
        return(messana.ISYmap[bufTankName][ISYkey]['messana'])

    def bufferTankPullKeys(messana, bufTankNbr): 
        #logging.debug('bufTankPullKeys')
        return( messana.getNodeKeys (bufTankNbr, messana.bufferTankID, 'GETstr'))

    def bufferTankPushKeys(messana, bufTankNbr):
        #logging.debug('bufTankPushKeys')
        return( messana.getNodeKeys (bufTankNbr, messana.bufferTankID, 'PUTstr'))
  
    def bufferTankActiveKeys(messana, bufTankNbr):
        #logging.debug('bufTankActiveKeys')
        return( messana.getNodeKeys (bufTankNbr, messana.bufferTankID, 'Active'))           

    def updateBufferTankData(messana,  level, bufTankNbr):
        #logging.debug('updateBufferTankData: ' + str(bufTankNbr))
        keys =[]
        if level == 'all':
            #logging.debug('ALL update buffer tank ' + str(bufTankNbr))
            keys =  messana.bufferTankPullKeys(bufTankNbr)
        elif level == 'active':
            #logging.debug('ACTIVE update buffer tank ' + str(bufTankNbr))
            keys =  messana.bufferTankActiveKeys(bufTankNbr)
        
        messana.dataOK = True
        for mKey in keys:
            messana.data = messana.pullBufferTankDataIndividual(bufTankNbr, mKey)
            messana.dataOK = messana.dataOK and messana.data['statusOK']
        return(messana.dataOK)
            

    def getBufferTankISYValue(messana, ISYkey, bufTankNbr):
        bufTankName = messana.bufferTankID+str(bufTankNbr)
        messanaKey = messana.ISYmap[bufTankName][ISYkey]['messana']
        try:
            data = messana.pullBufferTankDataIndividual(bufTankNbr, messanaKey)
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

    def pullBufferTankDataIndividual(messana, bufTankNbr, mKey): 
        #logging.debug('pullBufferTankDataIndividual: ' +str(bufTankNbr)  + ' ' + mKey)    
        return(messana.pullNodeDataIndividual(bufTankNbr, messana.bufferTankID, mKey))

    def pushBufferTankDataIndividual(messana, bufTankNbr, mKey, value):
        #logging.debug('pushBufferTankDataIndividual: ' +str(bufTankNbr)  + ' ' + mKey + ' ' + str(value))  

        if mKey == 'mStatus':
            BTdata = {}
            BTdata = messana.pullNodeDataIndividual(bufTankNbr, messana.bufferTankID, 'mMode')
            if BTdata['data'] != 0:
                return(messana.pushNodeDataIndividual(bufTankNbr, messana.bufferTankID, mKey, value))
            else:
                logging.error('Mode = 0, Cannot set status if mode = 0')
                return(False)
        else:
             return(messana.pushNodeDataIndividual(bufTankNbr, messana.bufferTankID, mKey, value))
 
    def getBufferTankCount(messana):
        return(messana.mSystem[ messana.systemID]['data']['mBufTankCount'])


    def getBufferTankName(messana, bufTankNbr):
        tempName = messana.pullNodeDataIndividual(bufTankNbr, messana.bufferTankID, 'mName')
        if tempName['statusOK']:
            return(tempName['data'])
        else:
            return('NA')
            
    def getBufferTankAddress(messana, bufTankNbr):
        return(messana.bufferTankID + str(bufTankNbr))

    def getBufferTankISYdriverInfo(messana, mKey, bufTankNbr):
        info = {}
        bufTankStr = messana.bufferTankID+str(bufTankNbr)
        if mKey in messana.setupFile['nodeDef'][bufTankStr]['sts']:
            keys = list(messana.setupFile['nodeDef'][bufTankStr]['sts'][mKey].keys())
            info['driver'] = keys[0]
            tempData =  messana.GETNodeData(messana.bufferTankID, bufTankNbr, mKey)
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
            editor = messana.setupFile['nodeDef'][bufTankStr]['sts'][mKey][keys[0]]
            info['uom'] = messana.setupFile['editors'][editor]['ISYuom']
        return(info)


    def bufferTankSetStatus(messana, value, bufTankNbr):
        #logging.debug ('bufferTankSetStatus')
        status = messana.pushBufferTankDataIndividual(bufTankNbr, 'mStatus', value)
        return(status)
 
    def getBufferTankStatusISYdriver(messana, bufTankNbr):
        #logging.debug ('getBufferTankStatusISYdriver called')
        Key = ''
        bufTankName = messana.bufferTankID+str(bufTankNbr)
        for ISYkey in messana.ISYmap[bufTankName]:
            if messana.ISYmap[bufTankName][ISYkey]['messana'] == 'mStatus':
                Key = ISYkey
        return(Key) 

    def bufferTankSetSetMode(messana, value, bufTankNbr):
        #logging.debug ('bufferTankSetSetMode')
        status = messana.pushAtuDataIndividual(bufTankNbr, 'mMode', value)
        return(status)
 
    def getBufferTankSetModeISYdriver(messana, bufTankNbr):
        #logging.debug ('getBufferTankSetModeISYdriver called')
        Key = ''
        bufTankName = messana.bufferTankID+str(bufTankNbr)
        for ISYkey in messana.ISYmap[bufTankName]:
            if messana.ISYmap[bufTankName][ISYkey]['messana'] == 'mMode':
                Key = ISYkey
        return(Key)  
    def bufferTankTempStatus(messana, value, bufTankNbr):
        #logging.debug ('bufferTankTempStatus')
        status = messana.pushAtuDataIndividual(bufTankNbr, 'mTempMode', value)
        return(status)
 
    def getBufferTankTempStatusISYdriver(messana, bufTankNbr):
        #logging.debug ('getBufferTankTempStatusISYdriver called')
        Key = ''
        bufTankName = messana.bufferTankID+str(bufTankNbr)
        for ISYkey in messana.ISYmap[bufTankName]:
            if messana.ISYmap[bufTankName][ISYkey]['messana'] == 'mTempMode':
                Key = ISYkey
        return(Key)  
  

        #Domestic Hot Water
 
    ##################################################################
    # Domestic Hot Water
    def updateDHWData(messana, level, DHWNbr):
        #logging.debug('updatDHWData: ' + str(DHWNbr))
        keys =[]
        if level == 'all':
            #logging.debug('ALL update  Domestic Hot Water ' + str(DHWNbr))
            keys =  messana.DHWPullKeys(DHWNbr)
        elif level == 'active':
            #logging.debug('ACTIVE update Domestic Hot Water ' + str(DHWNbr))
            keys =  messana.DHWActiveKeys(DHWNbr)
        
        messana.dataOK = True
        for mKey in keys:
            messana.data = messana.pullDHWDataIndividual(DHWNbr, mKey)
            messana.dataOK = messana.dataOK and messana.data['statusOK']
        return(messana.dataOK)

    def getDHWCapability(messana, DHWNbr): 
        #logging.debug('getDHWCapability for '+str(DHWNbr))                      
        messana.getNodeCapability(messana.dhwID, DHWNbr)

    def pullDHWDataIndividual(messana, DHWNbr, mKey): 
        #logging.debug('pullDHWDataIndividual: ' +str(DHWNbr)  + ' ' + mKey)    
        return(messana.pullNodeDataIndividual(DHWNbr, messana.dhwID, mKey))

    def pushDHWDataIndividual(messana, DHWNbr, mKey, value):
        #logging.debug('pushDHWDataIndividual: ' +str(DHWNbr)  + ' ' + mKey + ' ' + str(value))  
        return(messana.pushNodeDataIndividual(DHWNbr, messana.dhwID, mKey, value))


    def DHWPullKeys(messana, DHWNbr):
        #logging.debug('DHWPullKeys')
        return( messana.getNodeKeys (DHWNbr, messana.dhwID, 'GETstr'))

    def DHWPushKeys(messana, DHWNbr):
        #logging.debug('DHWPushKeys')
        return( messana.getNodeKeys (DHWNbr, messana.dhwID, 'PUTstr'))
  
    def DHWActiveKeys(messana, DHWNbr):
        #logging.debug('DHWActiveKeys')
        return( messana.getNodeKeys (DHWNbr, messana.dhwID, 'active'))    

    def getDomesticHotWaterCount(messana):
        return(messana.mSystem[ messana.systemID]['data']['mDHWcount'])

    def getDomesticHotWaterName(messana, DHWNbr):
        tempName = messana.pullNodeDataIndividual(DHWNbr, messana.dhwID, 'mName')
        if tempName['statusOK']:
            return(tempName['data'])
        else:
            return('NA')
            
    def getDomesticHotWaterAddress(messana, DHWNbr):
        return(messana.dhwID + str(DHWNbr))

    def hotWaterSetStatus(messana, value, DHWNbr):
        #logging.debug ('hotWaterSetStatus')
        status = messana.pushAtuDataIndividual(DHWNbr, 'mStatus', value)
        return(status)
 
    def getHotWaterStatusISYdriver(messana, DHWNbr):
        #logging.debug ('getHotWaterStatusISYdriver called')
        Key = ''
        DHWName = messana.dhwID+str(DHWNbr)
        for ISYkey in messana.ISYmap[DHWName]:
            if messana.ISYmap[DHWName][ISYkey]['messana'] == 'mStatus':
                Key = ISYkey
        return(Key)  
  
    def getHotWaterISYdriverInfo(messana, mKey, DHWNbr):
        info = {}
        DHWStr = messana.dhwID+str(DHWNbr)
        if mKey in messana.setupFile['nodeDef'][DHWStr]['sts']:
            keys = list(messana.setupFile['nodeDef'][DHWStr]['sts'][mKey].keys())
            info['driver'] = keys[0]
            tempData =  messana.GETNodeData(messana.dhwID, DHWNbr, mKey)
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
            editor = messana.setupFile['nodeDef'][DHWStr]['sts'][mKey][keys[0]]
            info['uom'] = messana.setupFile['editors'][editor]['ISYuom']
        return(info)

    def hotWaterSetTargetTempt(messana, value, DHWNbr):
        #logging.debug ('hotWaterSetTargetTempt')
        status = messana.pushAtuDataIndividual(DHWNbr, 'mTargetTemp', value)
        return(status)
 
    def getHotWaterSetTargetTempISYdriver(messana, DHWNbr):
        #logging.debug ('getHotWaterSetTargetTempISYdriver called')
        Key = ''
        DHWName = messana.dhwID+str(DHWNbr)
        for ISYkey in messana.ISYmap[DHWName]:
            if messana.ISYmap[DHWName][ISYkey]['messana'] == 'mTargetTemp':
                Key = ISYkey
        return(Key)  

    def getHotWaterISYValue(messana, ISYkey, dhwNbr):
        dhwName = messana.dhwID+str(dhwNbr)
        messanaKey = messana.ISYmap[dhwName][ISYkey]['messana']
        try:
            data = messana.pullDHWDataIndividual(dhwNbr, messanaKey)
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

    def getHotWaterMessanaISYkey(messana, ISYkey, dhwNbr):
        dhwName = messana.dhwID+str(dhwNbr)
        return(messana.ISYmap[dhwName][ISYkey]['messana'])        