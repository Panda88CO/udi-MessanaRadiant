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





class messanaNode (object):
    def __init__ (self):
        # Note all xxIDs must be lower case without special characters (ISY requirement)
        #self.systemID = mISYcontrollerName
        #self.IPaddress = IPaddress
        #self.APIkey = APIkey

        self.APIstr = 'apikey=' + self.APIkey 

        self.IP ='http://'+ self.IPaddress
        self.systemAPI = '/api/system'
        self.RESPONSE_OK = '<Response [200]>'
        self.RESPONSE_NO_SUPPORT = '<Response [400]>'
        self.RESPONSE_NO_RESPONSE = '<Response [404]>'
        self.NaNlist= [-32768 , -3276.8 ]
        
        ''' 
        self.zoneID = 'zones'
        self.macrozoneID = 'macrozones'
        self.atuID = 'atus'
        self.dhwID = 'domhws'
        self.fcID = 'fancoils'
        self.energySourceID =  'energysys'
        self.HotColdcoID = 'hcco'
        self.bufferTankID = 'buftanks'
        self.supportedNodeList = [
                            self.zoneID,
                            self.macrozoneID,
                            self.atuID,
                            self.dhwID,
                            self.fcID,
                            self.energySourceID,
                            self.HotColdcoID,
                            self.bufferTankID  ] 
       
        
    
        

       

        #Dummy check to see if there is connection to Messana system)
        if not(self.checkMessanaConnection()):
            logging.error('Error Connecting to MessanaSystem')
        else:  
            #logging.info('Extracting Information about Messana System')
  
            self.zones = messanaZones(self.IPaddress , self.ApiKey )

            #Need SystemCapability function               
            #self.getSystemCapability()
            #self.updateSystemData('all')
            #logging.debug(self.systemID + ' added')
            self.addZones()
            self.addMacroZones()

            #self.addSystemDefStruct(self.systemID)

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
                self.addNodeDefStruct(esNbr,  self.energySourceID, esName)   

            for HcCoNbr in range(0,self.mSystem[ self.systemID]['data']['mhc_coCount']):
                self.getHcCoCapability(HcCoNbr)
                self.updateHcCoData('all', HcCoNbr)
                hccoName = self.HotColdcoID +str(HcCoNbr)
                self.addNodeDefStruct(HcCoNbr, self.HotColdcoID , hccoName)          
            
            for btNbr in range(0,self.mSystem[ self.systemID]['data']['mBufTankCount']):
                self.getBufferTankCapability(btNbr)
                self.updateBufferTankData('all', btNbr)
                btName = self.bufferTankID+str(btNbr)
                self.addNodeDefStruct(btNbr, self.bufferTankID, btName)     

            logging.info ('Creating Setup file')
            self.createSetupFiles('./profile/nodedef/nodedefs.xml','./profile/editor/editors.xml', './profile/nls/en_us.txt')
            self.ISYmap = self.createISYmapping()


        '''



    def setMessanaCredentials (self, mIPaddress, APIkey):
        self.mIPaddress = mIPaddress
        self.APIKeyVal = APIkey





   
    def GETsystemData(self, mKey):
        GETstr = self.IP+self.systemAPI+'/'+ mKey + '?' + self.APIstr 
        logging.debug('GETsystemData: {} '.format(GETstr) )

        #logging.debug( GETStr)
        try:
            systemTemp = requests.get(GETstr)
            #logging.debug(str(systemTemp))
            if str(systemTemp) == self.RESPONSE_OK:
                systemTemp = systemTemp.json()
                data = systemTemp[str(list(systemTemp.keys())[0])]

            else:
                logging.debug(str(mKey) + ' error')
            return(data) #No data for given keyword - remove from list 
        except Exception as e:
            logging.error('System GET operation failed for {}: {}'.format(mKey, e))
            return(None)



    def PUTsystemData(self, mKey, value):
        mData = {}
        PUTstr = self.IP+self.systemAPI+'/'+ mKey
        mData = {'value':value, 'apikey': self.APIkey}
        logging.debug('PUTsystemData :{} {}'.format(PUTstr, mData) )
        try:
            resp = requests.put(PUTstr, json=mData)
            #logging.debug(resp)
            return( str(resp) == self.RESPONSE_OK)

        except Exception as e:
            logging.error('Error PUT {}: {}'.format(PUTstr, e))
            return(None)
  
    def GETNodeData(self, nodeNbr, mKey):
        #logging.debug('GETNodeData: ' + mNodeKey + ' ' + str(nodeNbr)+ ' ' + mKey)
        GETstr =self.IP+'/api/'+self.nodeType+'/'+mKey+'/'+str(nodeNbr)+'?'+ self.APIStr 
        logging.debug('GETNodeData: {} '.format(GETstr) )
        try:
            Nodep = requests.get(GETstr)
            if str(Nodep) == self.RESPONSE_OK:
                Nodep = Nodep.json()
                data   = Nodep[str(list(Nodep.keys())[0])]
                return(data)
            else:
                return(None)
        except Exception as e:
            logging.error ('Error GETNodeData:{} : {}'.format(GETstr, e))
            return(None)

    def PUTNodeData(self, nodeNbr, mKey, value):
        mData = {}
        PUTstr = self.IP + +'/api/'+self.nodeType+'/'+mKey+'/'+str(nodeNbr)
        mData = {'id':nodeNbr, 'value': value, 'apikey' : self.APIkey }
        logging.debug('PUTNodeData :{} {}'.format(PUTstr, mData) )
        try:
            resp = requests.put(PUTstr, json=mData)
            if str(resp) == self.RESPONSE_OK:
                return(True)
            else:
                return(False)
        except Exception as e:
            logging.error('Error PUTNodeData try/cartch {}:{}'.format(PUTStr, e))
            return(False)


 
    #pretty bad solution - just checking if a value can be extracted
    def checkMessanaConnection(self):
        sysData = self.GETSystemData('mApiVer') 
        return (sysData['statusOK'])
    


###################################################################



    def pullSystemDataIndividual(self, mKey):
        #logging.debug('MessanaInfo pull System Data: ' + mKey)
        return(self.GETSystemData(mKey) )
                 

    def pushSystemDataIndividual(self, mKey, value):
        sysData={}
        #logging.debug('MessanaInfo push System Data: ' + mKey)       
        sysData = self.PUTSystemData(mKey, value)
        if sysData['statusOK']:
            return(True)
        else:
            logging.error(sysData['error'])
            return(False) 

     



    def systemSetStatus (self, value):
        #logging.debug('systemSetstatus called')
        status = self.pushSystemDataIndividual('mStatus', value)
        return(status)

    def systemSetEnergySave (self, value):
        #logging.debug('systemSetEnergySave called')
        status = self.pushSystemDataIndividual('mEnergySaving', value)
        return(status)
        
    def systemSetback (self, value):
        #logging.debug('setSetback called')
        status = self.pushSystemDataIndividual('mSetback', value)
        return(status)

    def getSystemAddress(self):
        return(self.systemID)


    # Zones
    def getZoneCapability(self, zoneNbr):
        #logging.debug('getZoneCapability for ' + str(zoneNbr)) 
        self.getNodeCapability(self.zoneID, zoneNbr)

    def addZoneDefStruct(self, zoneNbr, nodeId):
        self.addNodeDefStruct(zoneNbr, self.zoneID, nodeId)

    def updateZoneData(self, level, zoneNbr):
        #logging.debug('updatZoneData: ' + str(zoneNbr))

        keys =[]
        if level == 'all':
            #logging.debug('ALL update zone ' + str(zoneNbr))
            keys =  self.zonePullKeys(zoneNbr)
        elif level == 'active':
            #logging.debug('ACTIVE update zone ' + str(zoneNbr))
            keys =  self.zoneActiveKeys(zoneNbr)
        
        self.dataOK = True
        for mKey in keys:
            self.data = self.pullZoneDataIndividual(zoneNbr, mKey)
            self.dataOK = self.dataOK and self.data['statusOK']
        return(self.dataOK)

    def pullZoneDataIndividual(self, zoneNbr, mKey): 
        #logging.debug('pullZoneDataIndividual: ' +str(zoneNbr)  + ' ' + mKey)    
        return(self.pullNodeDataIndividual(zoneNbr, self.zoneID, mKey))


    def pushZoneDataIndividual(self, zoneNbr, mKey, value):
        #logging.debug('pushZoneDataIndividual: ' +str(zoneNbr)  + ' ' + mKey + ' ' + str(value))  
        return(self.pushNodeDataIndividual(zoneNbr, self.zoneID, mKey, value))

    def zonePullKeys(self, zoneNbr):
        #logging.debug('zonePullKeys')
        self.tempZoneKeys =  self.getNodeKeys (zoneNbr, self.zoneID, 'GETstr')
        return( self.tempZoneKeys)

    def zonePushKeys(self, zoneNbr):
        #logging.debug('zonePushKeys')
        return( self.getNodeKeys (zoneNbr, self.zoneID, 'PUTstr'))
  
    def zoneActiveKeys(self, zoneNbr):
        #logging.debug('zoneActiveKeys')
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
        #logging.debug(' zoneSetstatus called for zone: ' + str(zoneNbr))
        
        status = self.pushZoneDataIndividual(zoneNbr, 'mStatus', value)
        return(status)
 

    def getZoneStatusISYdriver(self, zoneNbr):
        #logging.debug('getZoneStatusISYdriver called for zone: '+str(zoneNbr))
        
        Key = ''
        zoneName = self.zoneID+str(zoneNbr)
        for ISYkey in self.ISYmap[zoneName]:
            if self.ISYmap[zoneName][ISYkey]['messana'] == 'mStatus':
                Key = ISYkey
        return(Key)  
        

    def zoneSetEnergySave(self, value, zoneNbr):
        #logging.debug(' zoneSetEnergySave called for zone: ' + str(zoneNbr))
        
        status = self.pushZoneDataIndividual(zoneNbr, 'mEnergySaving', value)
        return(status)
    
    def getZoneEnergySaveISYdriver(self, zoneNbr):
        #logging.debug('getZoneEnergySaveISYdriver called for zone: '+str(zoneNbr))
        
        Key = ''
        zoneName = self.zoneID+str(zoneNbr)
        for ISYkey in self.ISYmap[zoneName]:
            if self.ISYmap[zoneName][ISYkey]['messana'] == 'mEnergySaving':
                Key = ISYkey
        return(Key)  



    def zoneSetSetpoint(self, value,  zoneNbr):
        #logging.debug('zoneSetSetpoint called for zone: ' + str(zoneNbr))
        
        status = self.pushZoneDataIndividual(zoneNbr, 'mSetpoint', value)
        return(status)

    def getZoneSetPointISYdriver(self, zoneNbr):
        #logging.debug('getZoneSetpointISYdriver called for zone: '+str(zoneNbr))
        
        Key = ''
        zoneName = self.zoneID+str(zoneNbr)
        for ISYkey in self.ISYmap[zoneName]:
            if self.ISYmap[zoneName][ISYkey]['messana'] == 'mSetpoint':
                Key = ISYkey
        return(Key)  
  

    def zoneEnableSchedule(self, value, zoneNbr):
        #logging.debug('zoneEnableSchedule called for zone: ' + str(zoneNbr))
        
        status = self.pushZoneDataIndividual(zoneNbr, 'mScheduleOn', value)
        return(status)


    def getZoneEnableScheduleISYdriver(self, zoneNbr):
        #logging.debug('getZoneEnableScheduleISYdriver called for zone: '+str(zoneNbr))
        
        Key = ''
        zoneName = self.zoneID+str(zoneNbr)
        for ISYkey in self.ISYmap[zoneName]:
            if self.ISYmap[zoneName][ISYkey]['messana'] == 'mScheduleOn':
                Key = ISYkey
        return(Key) 

    def zonesetCurrentDPt(self, value,  zoneNbr):
        #logging.debug('zonesetCurrentDPt called for zone: ' + str(zoneNbr))
        
        status = self.pushZoneDataIndividual(zoneNbr, 'mCurrentSetpointDP', value)
        return(status)

    def getZonesetCurrentDPtISYdriver(self, zoneNbr):
        #logging.debug('getZonesetCurrentDPtISYdriver called for zone: '+str(zoneNbr))
        
        Key = ''
        zoneName = self.zoneID+str(zoneNbr)
        for ISYkey in self.ISYmap[zoneName]:
            if self.ISYmap[zoneName][ISYkey]['messana'] == 'mCurrentSetpointDP':
                Key = ISYkey
        return(Key)  

    def zonesetCurrentRH(self, value,  zoneNbr):
        #logging.debug('zonesetCurrentRH called for zone: ' + str(zoneNbr))
        
        status = self.pushZoneDataIndividual(zoneNbr, 'mCurrentSetpointRH', value)
        return(status)

    def getZonesetCurrentRHISYdriver(self, zoneNbr):
        #logging.debug('getZonesetCurrentRHISYdriver called for zone: '+str(zoneNbr))
        
        Key = ''
        zoneName = self.zoneID+str(zoneNbr)
        for ISYkey in self.ISYmap[zoneName]:
            if self.ISYmap[zoneName][ISYkey]['messana'] == 'mCurrentSetpointRH':
                Key = ISYkey
        return(Key)  

    def zonesetDehumDpt(self, value,  zoneNbr):
        #logging.debug('zonesetDehumDpt called for zone: ' + str(zoneNbr))
        
        status = self.pushZoneDataIndividual(zoneNbr, 'mDehumSetpointDP', value)
        return(status)

    def getZonesetDehumDPtISYdriver(self, zoneNbr):
        #logging.debug('getZonesetDehumDPtISYdriver called for zone: '+str(zoneNbr))
        Key = ''
        zoneName = self.zoneID+str(zoneNbr)
        for ISYkey in self.ISYmap[zoneName]:
            if self.ISYmap[zoneName][ISYkey]['messana'] == 'mDehumSetpointDP':
                Key = ISYkey
        return(Key)  

    def zonesetDehumRH(self, value,  zoneNbr):
        #logging.debug('zonesetDehumRH called for zone: ' + str(zoneNbr))
        
        status = self.pushZoneDataIndividual(zoneNbr, 'mDehumSetpointRH', value)
        return(status)

    def getZonesetDehumRHISYdriver(self, zoneNbr):
        #logging.debug('getZonesetDehumRHISYdriver called for zone: '+str(zoneNbr))
        Key = ''
        zoneName = self.zoneID+str(zoneNbr)
        for ISYkey in self.ISYmap[zoneName]:
            if self.ISYmap[zoneName][ISYkey]['messana'] == 'mDehumSetpointRH':
                Key = ISYkey
        return(Key)  

    def zonesetHumRH(self, value,  zoneNbr):
        #logging.debug('zonesetHumRH called for zone: ' + str(zoneNbr))
        
        status = self.pushZoneDataIndividual(zoneNbr, 'mHumSetpointRH', value)
        return(status)

    def getZonesetHumRHISYdriver(self, zoneNbr):
        #logging.debug('getZonesetHumRHISYdriver called for zone: '+str(zoneNbr))
        Key = ''
        zoneName = self.zoneID+str(zoneNbr)
        for ISYkey in self.ISYmap[zoneName]:
            if self.ISYmap[zoneName][ISYkey]['messana'] == 'mHumSetpointRH':
                Key = ISYkey
        return(Key)  

    def zonesetHumDpt(self, value,  zoneNbr):
        #logging.debug('zonesetDehumDpt called for zone: ' + str(zoneNbr))
        
        status = self.pushZoneDataIndividual(zoneNbr, 'mHumSetpointDP', value)
        return(status)

    def getZonesetHumDPtISYdriver(self, zoneNbr):
        #logging.debug('getZonesetDehumDPtISYdriver called for zone: '+str(zoneNbr))
        Key = ''
        zoneName = self.zoneID+str(zoneNbr)
        for ISYkey in self.ISYmap[zoneName]:
            if self.ISYmap[zoneName][ISYkey]['messana'] == 'mHumSetpointDP':
                Key = ISYkey
        return(Key)  

    def zonesetCO2 (self, value,  zoneNbr):
        #logging.debug('zonesetDehumDpt called for zone: ' + str(zoneNbr))
        
        status = self.pushZoneDataIndividual(zoneNbr, 'mCO2', value)
        return(status)

    def getZonesetCO2ISYdriver(self, zoneNbr):
        #logging.debug('getZonesetDehumDPtISYdriver called for zone: '+str(zoneNbr))
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
        #logging.debug('updatMacrozoneData: ' + str(macrozoneNbr))

        keys =[]
        if level == 'all':
            #logging.debug('ALL update macrozone ' + str(macrozoneNbr))
            keys =  self.macrozonePullKeys(macrozoneNbr)
        elif level == 'active':
            #logging.debug('ACTIVE update macrozone ' + str(macrozoneNbr))
            keys =  self.macrozoneActiveKeys(macrozoneNbr)
        
        self.dataOK = True
        for mKey in keys:
            self.data = self.pullMacrozoneDataIndividual(macrozoneNbr, mKey)
            self.dataOK = self.dataOK and self.data['statusOK']
        return(self.dataOK)


    def pullMacrozoneDataIndividual(self, macrozoneNbr, mKey): 
        #logging.debug('pullMacroZoneDataIndividual: ' +str(macrozoneNbr)  + ' ' + mKey)    
        return(self.pullNodeDataIndividual(macrozoneNbr, self.macrozoneID, mKey))

    def pushMacrozoneDataIndividual(self, macrozoneNbr, mKey, value):
        #logging.debug('pushMacroZoneDataIndividual: ' +str(macrozoneNbr)  + ' ' + mKey + ' ' + str(value))  
        return(self.pushNodeDataIndividual(macrozoneNbr, self.macrozoneID, mKey, value))

    def macrozonePullKeys(self, macrozoneNbr):
        #logging.debug('macrozonePullKeys')
        return( self.getNodeKeys (macrozoneNbr, self.macrozoneID, 'GETstr'))

    def macrozonePushKeys(self, macrozoneNbr):
        #logging.debug('macrozonePushKeys')
        return( self.getNodeKeys (macrozoneNbr, self.macrozoneID, 'PUTstr'))
  
    def macrozoneActiveKeys(self, macrozoneNbr):
        #logging.debug('macrozoneActiveKeys')
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
        #logging.debug('getMacrozoneCapability for ' + str(macrozoneNbr))        
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
        #logging.debug(' macrozoneSetstatus called for macrozone: ' + str(macrozoneNbr))
        
        status = self.pushMacrozoneDataIndividual(macrozoneNbr, 'mStatus', value)
        return(status)
 

    def getMacrozoneStatusISYdriver(self, macrozoneNbr):
        #logging.debug('getMacrozoneStatusISYdriver called for macrozone: '+str(macrozoneNbr))
        
        Key = ''
        macrozoneName = self.macrozoneID+str(macrozoneNbr)
        for ISYkey in self.ISYmap[macrozoneName]:
            if self.ISYmap[macrozoneName][ISYkey]['messana'] == 'mStatus':
                Key = ISYkey
        return(Key)  
        


    def macrozoneSetSetpoint(self, value,  macrozoneNbr):
        #logging.debug('macrozoneSetSetpoint called for macrozone: ' + str(macrozoneNbr))
        
        status = self.pushMacrozoneDataIndividual(macrozoneNbr, 'mSetpoint', value)
        return(status)

    def getMacrozoneSetPointISYdriver(self, macrozoneNbr):
        #logging.debug('getMacrozoneSetpointISYdriver called for macrozone: '+str(macrozoneNbr))
        
        Key = ''
        macrozoneName = self.macrozoneID+str(macrozoneNbr)
        for ISYkey in self.ISYmap[macrozoneName]:
            if self.ISYmap[macrozoneName][ISYkey]['messana'] == 'mSetpoint':
                Key = ISYkey
        return(Key)  
  

    def macrozoneEnableSchedule(self, value, macrozoneNbr):
        #logging.debug('macrozoneEnableSchedule called for macrozone: ' + str(macrozoneNbr))
        
        status = self.pushMacrozoneDataIndividual(macrozoneNbr, 'mScheduleOn', value)
        return(status)


    def getMacrozoneEnableScheduleISYdriver(self, macrozoneNbr):
        #logging.debug('getMacrozoneEnableScheduleISYdriver called for macrozone: '+str(macrozoneNbr))
        
        Key = ''
        macrozoneName = self.macrozoneID+str(macrozoneNbr)
        for ISYkey in self.ISYmap[macrozoneName]:
            if self.ISYmap[macrozoneName][ISYkey]['messana'] == 'mScheduleOn':
                Key = ISYkey
        return(Key) 






    ##############################################################
    # Hot Cold Change Over
    def updateHcCoData(self, level,  HcCoNbr):
        #logging.debug('updatHcCoData: ' + str(HcCoNbr))
        keys =[]
        if level == 'all':
            #logging.debug('ALL update Hot Cold CO ' + str(HcCoNbr))
            keys =  self.HcCoPullKeys(HcCoNbr)
        elif level == 'active':
            #logging.debug('ACTIVE update Hot Cold CO  ' + str(HcCoNbr))
            keys =  self.HcCoActiveKeys(HcCoNbr)
        
        self.dataOK = True
        for mKey in keys:
            self.data = self.pullHcCoDataIndividual(HcCoNbr, mKey)
            self.dataOK = self.dataOK and self.data['statusOK']
        return(self.dataOK)

    def getHcCoCapability(self, HcCoNbr): 
        #logging.debug('getHC_COCapability for ' + str(HcCoNbr))        
        self.getNodeCapability(self.HotColdcoID , HcCoNbr)

    def pullHcCoDataIndividual(self, HcCoNbr, mKey): 
        #logging.debug('pullHC_CODataIndividual: ' +str(HcCoNbr)  + ' ' + mKey)    
        return(self.pullNodeDataIndividual(HcCoNbr, self.HotColdcoID , mKey))

    def pushHcCoDataIndividual(self, HcCoNbr, mKey, value):
        #logging.debug('pushHC_CODataIndividual: ' +str(HcCoNbr)  + ' ' + mKey + ' ' + str(value))  
        return(self.pushNodeDataIndividual(HcCoNbr, self.HotColdcoID , mKey, value))

    def HcCoPullKeys(self, HcCoNbr):
        #logging.debug('hc_coPullKeys')
        return( self.getNodeKeys (HcCoNbr, self.HotColdcoID , 'GETstr'))

    def HcCoPushKeys(self, HcCoNbr):
        #logging.debug('hc_coPushKeys')
        return( self.getNodeKeys (HcCoNbr, self.HotColdcoID , 'PUTstr'))
  
    def HcCoActiveKeys(self, HcCoNbr):
        #logging.debug('hc_coActiveKeys')
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
        #logging.debug('HcCoSetMode called for Hot Cold: ' + str(HcCoNbr))
        
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
        #logging.debug('getHcCoSetModeISYdriver called for Hot Cold: '+str(HcCoNbr))
        Key = ''
        HcCoName = self.HotColdcoID+str(HcCoNbr)
        for ISYkey in self.ISYmap[HcCoName]:
            if self.ISYmap[HcCoName][ISYkey]['messana'] == 'mMode':
                Key = ISYkey
        return(Key) 

    def HcCoAdaptiveComfort(self, value, HcCoNbr):
        #logging.debug('HcCoAdaptiveComfort called for Hot Cold: ' + str(HcCoNbr))
        
        status = self.pushHcCoDataIndividual(HcCoNbr, 'mAdaptiveComfort', value)
        return(status)


    def getHcCoAdaptiveComfortISYdriver(self, HcCoNbr):
        #logging.debug('getHcCoAdaptiveComfortISYdriver called for Hot Cold: '+str(HcCoNbr))
        Key = ''
        HcCoName = self.HotColdcoID+str(HcCoNbr)
        for ISYkey in self.ISYmap[HcCoName]:
            if self.ISYmap[HcCoName][ISYkey]['messana'] == 'mAdaptiveComfort':
                Key = ISYkey
        return(Key) 

    ####################################################
    #ATU
   
    def getAtuCapability(self, atuNbr): 
        #logging.debug('getAtuCapability for ' + str(atuNbr))             
        self.getNodeCapability(self.atuID, atuNbr)
    
    def updateAtuData(self,  level, atuNbr):
        #logging.debug('updateAtuData: ' + str(atuNbr))

        keys =[]
        if level == 'all':
            #logging.debug('ALL update atu ' + str(atuNbr))
            keys =  self.atuPullKeys(atuNbr)
        elif level == 'active':
            #logging.debug('ACTIVE update atu ' + str(atuNbr))
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
        #logging.debug('pullAtuDataIndividual: ' +str(atuNbr)  + ' ' + mKey)    
        return(self.pullNodeDataIndividual(atuNbr, self.atuID, mKey))

    def pushAtuDataIndividual(self, ATUNbr, mKey, value):
        #logging.debug('pushATUDataIndividual: ' +str(ATUNbr)  + ' ' + mKey + ' ' + str(value))  
        return(self.pushNodeDataIndividual(ATUNbr, self.atuID, mKey, value))

    def atuPullKeys(self, ATUNbr): 
        #logging.debug('atusPullKeys')
        return( self.getNodeKeys (ATUNbr, self.atuID, 'GETstr'))

    def atuPushKeys(self, ATUNbr):
        #logging.debug('atusPushKeys')
        return( self.getNodeKeys (ATUNbr, self.atuID, 'PUTstr'))
  
    def atuActiveKeys(self, ATUNbr):
        #logging.debug('atusActiveKeys')
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
        #logging.debug ('atuSetStatus')
        status = self.pushAtuDataIndividual(atuNbr, 'mStatus', value)
        return(status)
 
    def getAtuStatusISYdriver(self, atuNbr):
        #logging.debug ('getAtuStatusISYdriver called')
        Key = ''
        atuName = self.atuID+str(atuNbr)
        for ISYkey in self.ISYmap[atuName]:
            if self.ISYmap[atuName][ISYkey]['messana'] == 'mStatus':
                Key = ISYkey
        return(Key)  
  
    def atuSetHrv(self, value, atuNbr):
        #logging.debug ('atuSetHRV called')
        status = self.pushAtuDataIndividual(atuNbr, 'mHRVOn', value)
        return(status)

    def getAtuHrvISYdriver(self, atuNbr):
        #logging.debug ('getAtuHrvISYdriver called')
        atuName = self.atuID+str(atuNbr)
        for ISYkey in self.ISYmap[atuName]:
            if self.ISYmap[atuName][ISYkey]['messana'] == 'mHRVOn':
                Key = ISYkey
        return(Key)  

    def atuSetFlowlevel(self, value, atuNbr):
        #logging.debug ('atuSetFlowlevel called')
        status = self.pushAtuDataIndividual(atuNbr, 'mFlowLevel', value)
        return(status)

    def getAtuSetFlowlevelISYdriver(self, atuNbr):
        #logging.debug ('getAtuSetPointISYdriver called')
        atuName = self.atuID+str(atuNbr)
        for ISYkey in self.ISYmap[atuName]:
            if self.ISYmap[atuName][ISYkey]['messana'] == 'mFlowLevel':
                Key = ISYkey
        return(Key)  
        
    def atuSetHum(self, value, atuNbr):
        #logging.debug ('atuSetHum called')
        status = self.pushAtuDataIndividual(atuNbr, 'mHUMOn', value)
        return(status)

    def getAtuSetHumISYdriver(self, atuNbr):
        #logging.debug ('getAtuSetHumISYdriver called')
        atuName = self.atuID+str(atuNbr)
        for ISYkey in self.ISYmap[atuName]:
            if self.ISYmap[atuName][ISYkey]['messana'] == 'mHUMOn':
                Key = ISYkey
        return(Key)  

    def atuSetInt(self, value, atuNbr):
        #logging.debug ('atuSetInt called')
        status = self.pushAtuDataIndividual(atuNbr, 'mINTOn', value)
        return(status)

    def getAtuSetIntISYdriver(self, atuNbr):
        #logging.debug ('getAtuSetIntISYdriver called')
        atuName = self.atuID+str(atuNbr)
        for ISYkey in self.ISYmap[atuName]:
            if self.ISYmap[atuName][ISYkey]['messana'] == 'mINTOn':
                Key = ISYkey
        return(Key)  

    def atuSetNtd(self, value, atuNbr):
        #logging.debug ('atuSetNtd called')
        status = self.pushAtuDataIndividual(atuNbr, 'mNTDOn', value)
        return(status)

    def getAtuSetNtdISYdriver(self, atuNbr):
        #logging.debug ('getAtuSetNtdISYdriver called')
        atuName = self.atuID+str(atuNbr)
        for ISYkey in self.ISYmap[atuName]:
            if self.ISYmap[atuName][ISYkey]['messana'] == 'mNTDOn':
                Key = ISYkey
        return(Key)  

    def atuSetHumSetpointRH(self, value, atuNbr):
        #logging.debug ('atuSetHumSetpointRH called')
        status = self.pushAtuDataIndividual(atuNbr, 'mHumSetpointRH', value)
        return(status)

    def getAtuSetHumSetpointRHISYdriver(self, atuNbr):
        #logging.debug ('getAtuSetHumSetpointRHISYdriver called')
        atuName = self.atuID+str(atuNbr)
        for ISYkey in self.ISYmap[atuName]:
            if self.ISYmap[atuName][ISYkey]['messana'] == 'mHumSetpointRH':
                Key = ISYkey
        return(Key)

    def atuSetHumSetpointDP(self, value, atuNbr):
        #logging.debug ('atuSetHumSetpointDP called')
        status = self.pushAtuDataIndividual(atuNbr, 'mHumSetpointDP', value)
        return(status)

    def getAtuSetHumSetpointDPISYdriver(self, atuNbr):
        #logging.debug ('getAtuSetHumSetpointRHISYdriver called')
        atuName = self.atuID+str(atuNbr)
        for ISYkey in self.ISYmap[atuName]:
            if self.ISYmap[atuName][ISYkey]['messana'] == 'mHumSetpointDP':
                Key = ISYkey
        return(Key)  

    def atuSetDehumSetpointRH(self, value, atuNbr):
        #logging.debug ('atuSetDehumSetpointRH called')
        status = self.pushAtuDataIndividual(atuNbr, 'mDehumSetpointRH', value)
        return(status)

    def getAtuSetDehumSetpointRHISYdriver(self, atuNbr):
        #logging.debug ('getAtuSetDehumSetpointRHISYdriver called')
        atuName = self.atuID+str(atuNbr)
        for ISYkey in self.ISYmap[atuName]:
            if self.ISYmap[atuName][ISYkey]['messana'] == 'mDehumSetpointRH':
                Key = ISYkey
        return(Key)  


    def atuSetDehumSetpointDP(self, value, atuNbr):
        #logging.debug ('atuSetDehumSetpointDP called')
        status = self.pushAtuDataIndividual(atuNbr, 'mDehumSetpointDP', value)
        return(status)

    def getAtuSetDehumSetpointDPISYdriver(self, atuNbr):
        #logging.debug ('getAtuSetDehumSetpointDPISYdriver called')
        atuName = self.atuID+str(atuNbr)
        for ISYkey in self.ISYmap[atuName]:
            if self.ISYmap[atuName][ISYkey]['messana'] == 'mDehumSetpointDP':
                Key = ISYkey
        return(Key)

    def atuSetCurrentSetpointRH(self, value, atuNbr):
        #logging.debug ('atuSetCurrentSetpointRH called')
        status = self.pushAtuDataIndividual(atuNbr, 'mCurrentSetpointRH', value)
        return(status)

    def getAtuSetCurrentSetpointRHISYdriver(self, atuNbr):
        #logging.debug ('getAtuSetCurrentSetpointRHISYdriver called')
        atuName = self.atuID+str(atuNbr)
        for ISYkey in self.ISYmap[atuName]:
            if self.ISYmap[atuName][ISYkey]['messana'] == 'mCurrentSetpointRH':
                Key = ISYkey
        return(Key)  

    def atuSetCurrentSetpointDP(self, value, atuNbr):
        #logging.debug ('atuSetCurrentSetpointDP called')
        status = self.pushAtuDataIndividual(atuNbr, 'mCurrentSetpointDP', value)
        return(status)

    def getAtuSetCurrentSetpointDPISYdriver(self, atuNbr):
        #logging.debug ('getAtuSetCurrentSetpointDPISYdriver called')
        atuName = self.atuID+str(atuNbr)
        for ISYkey in self.ISYmap[atuName]:
            if self.ISYmap[atuName][ISYkey]['messana'] == 'mCurrentSetpointDP':
                Key = ISYkey
        return(Key)  



    #################################################################
    #Fan Coils
    def updateFanCoilData(self, level, FanCoilNbr):
        #logging.debug('updatFanCoilData: ' + str(FanCoilNbr))
        keys =[]
        if level == 'all':
            #logging.debug('ALL update Fan Coil ' + str(FanCoilNbr))
            keys =  self.fan_coilPullKeys(FanCoilNbr)
        elif level == 'active':
            #logging.debug('ACTIVE update Fan Coil  ' + str(FanCoilNbr))
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
        #logging.debug('getFanCoilCapability for ' + str(FanCoilNbr))              
        self.getNodeCapability(self.fcID, FanCoilNbr)

    def pullFanCoilDataIndividual(self, FanCoilNbr, mKey): 
        #logging.debug('pullFanCoilDataIndividual: ' +str(FanCoilNbr)  + ' ' + mKey)    
        return(self.pullNodeDataIndividual(FanCoilNbr, self.fcID, mKey))

    def pushFanCoilDataIndividual(self, FanCoilNbr, mKey, value):
        #logging.debug('pushFanCoilDataIndividual: ' +str(FanCoilNbr)  + ' ' + mKey + ' ' + str(value))  
        return(self.pushNodeDataIndividual(FanCoilNbr, self.fcID, mKey, value))

    def fan_coilPullKeys(self, FanCoilNbr):
        #logging.debug('fan_coilPullKeys')
        return( self.getNodeKeys (FanCoilNbr, self.fcID, 'GETstr'))

    def fan_coilPushKeys(self, FanCoilNbr):
        #logging.debug('fan_coilPushKeys')
        return( self.getNodeKeys (FanCoilNbr, self.fcID, 'PUTstr'))
  
    def fan_coilActiveKeys(self, FanCoilNbr):
        #logging.debug('fan_coilActiveKeys')
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
        #logging.debug ('fanCoilSetCoolingSpeed called')
        status = self.pushFanCoilDataIndividual(FanCoilNbr, 'mCoolingSpeed', value)
        return(status)
 
    def getFanCoilCoolingSpeedISYdriver(self, FanCoilNbr):
        #logging.debug ('getFanCoilCoolingSpeedISYdriver called')
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
        #logging.debug ('fanCoilSetHeatingSpeed called')
        status = self.pushFanCoilDataIndividual(FanCoilNbr, 'mHeatingSpeed', value)
        return(status)
 
    def getFanCoilHeatingSpeedISYdriver(self, FanCoilNbr):
        #logging.debug ('getFanCoilHeatingSpeedISYdriver called')
        Key = ''
        fanCoilName = self.fcID+str(FanCoilNbr)
        for ISYkey in self.ISYmap[fanCoilName]:
            if self.ISYmap[fanCoilName][ISYkey]['messana'] == 'mHeatingSpeed':
                Key = ISYkey
        return(Key) 


    def fanCoilSetStatus(self, value, FanCoilNbr):
        #logging.debug ('fanCoilSetStatus called')
        status = self.pushFanCoilDataIndividual(FanCoilNbr, 'mStatus', value)
        return(status)
 
    def getFanCoilStatusISYdriver(self, FanCoilNbr):
        #logging.debug ('getFanCoilHeatingSpeedISYdriver called')
        Key = ''
        fanCoilName = self.fcID+str(FanCoilNbr)
        for ISYkey in self.ISYmap[fanCoilName]:
            if self.ISYmap[fanCoilName][ISYkey]['messana'] == 'mStatus':
                Key = ISYkey
        return(Key) 

    #############################################################
    #EnergySources
    def updateEnergySourceData(self, level, EnergySourceNbr):
        #logging.debug('updatEnergySourceData: ' + str(EnergySourceNbr))
        keys =[]
        if level == 'all':
            #logging.debug('ALL update Energy Source ' + str(EnergySourceNbr))
            keys =  self.energySourcePullKeys(EnergySourceNbr)
        elif level == 'active':
            #logging.debug('ACTIVE update Energy Source  ' + str(EnergySourceNbr))
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
        #logging.debug('getEnergySourceCapability for ' + str(EnergySourceNbr))          
        self.getNodeCapability( self.energySourceID, EnergySourceNbr)

    def pullEnergySourceDataIndividual(self, EnergySourceNbr, mKey): 
        #logging.debug('pullEnergySourceDataIndividual: ' +str(EnergySourceNbr)  + ' ' + mKey)    
        return(self.pullNodeDataIndividual(EnergySourceNbr,  self.energySourceID, mKey))

    def pushEnergySourceDataIndividual(self, EnergySourceNbr, mKey, value):
        #logging.debug('pushEnergySourceDataIndividual: ' +str(EnergySourceNbr)  + ' ' + mKey + ' ' + str(value))  
        return(self.pushNodeDataIndividual(EnergySourceNbr,  self.energySourceID, mKey, value))

    def energySourcePullKeys(self, EnergySourceNbr):
        #logging.debug('energySourcePullKeys')
        return( self.getNodeKeys (EnergySourceNbr,  self.energySourceID, 'GETstr'))

    def energySourcePushKeys(self, EnergySourceNbr):
        #logging.debug('EnergySourcePushKeys')
        return( self.getNodeKeys (EnergySourceNbr,  self.energySourceID, 'PUTstr'))
  
    def energySourceActiveKeys(self, EnergySourceNbr):
        #logging.debug('energySourceActiveKeys')
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
        #logging.debug('getBufferTankCapability for ' + str(bufTankNbr))              
        self.getNodeCapability(self.bufferTankID, bufTankNbr)

    def getBufferTankMessanaISYkey(self, ISYkey, bufTankNbr):
        bufTankName = self.bufferTankID+str(bufTankNbr)
        return(self.ISYmap[bufTankName][ISYkey]['messana'])

    def bufferTankPullKeys(self, bufTankNbr): 
        #logging.debug('bufTankPullKeys')
        return( self.getNodeKeys (bufTankNbr, self.bufferTankID, 'GETstr'))

    def bufferTankPushKeys(self, bufTankNbr):
        #logging.debug('bufTankPushKeys')
        return( self.getNodeKeys (bufTankNbr, self.bufferTankID, 'PUTstr'))
  
    def bufferTankActiveKeys(self, bufTankNbr):
        #logging.debug('bufTankActiveKeys')
        return( self.getNodeKeys (bufTankNbr, self.bufferTankID, 'Active'))           

    def updateBufferTankData(self,  level, bufTankNbr):
        #logging.debug('updateBufferTankData: ' + str(bufTankNbr))
        keys =[]
        if level == 'all':
            #logging.debug('ALL update buffer tank ' + str(bufTankNbr))
            keys =  self.bufferTankPullKeys(bufTankNbr)
        elif level == 'active':
            #logging.debug('ACTIVE update buffer tank ' + str(bufTankNbr))
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
        #logging.debug('pullBufferTankDataIndividual: ' +str(bufTankNbr)  + ' ' + mKey)    
        return(self.pullNodeDataIndividual(bufTankNbr, self.bufferTankID, mKey))

    def pushBufferTankDataIndividual(self, bufTankNbr, mKey, value):
        #logging.debug('pushBufferTankDataIndividual: ' +str(bufTankNbr)  + ' ' + mKey + ' ' + str(value))  

        if mKey == 'mStatus':
            BTdata = {}
            BTdata = self.pullNodeDataIndividual(bufTankNbr, self.bufferTankID, 'mMode')
            if BTdata['data'] != 0:
                return(self.pushNodeDataIndividual(bufTankNbr, self.bufferTankID, mKey, value))
            else:
                logging.error('Mode = 0, Cannot set status if mode = 0')
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
        #logging.debug ('bufferTankSetStatus')
        status = self.pushBufferTankDataIndividual(bufTankNbr, 'mStatus', value)
        return(status)
 
    def getBufferTankStatusISYdriver(self, bufTankNbr):
        #logging.debug ('getBufferTankStatusISYdriver called')
        Key = ''
        bufTankName = self.bufferTankID+str(bufTankNbr)
        for ISYkey in self.ISYmap[bufTankName]:
            if self.ISYmap[bufTankName][ISYkey]['messana'] == 'mStatus':
                Key = ISYkey
        return(Key) 

    def bufferTankSetSetMode(self, value, bufTankNbr):
        #logging.debug ('bufferTankSetSetMode')
        status = self.pushAtuDataIndividual(bufTankNbr, 'mMode', value)
        return(status)
 
    def getBufferTankSetModeISYdriver(self, bufTankNbr):
        #logging.debug ('getBufferTankSetModeISYdriver called')
        Key = ''
        bufTankName = self.bufferTankID+str(bufTankNbr)
        for ISYkey in self.ISYmap[bufTankName]:
            if self.ISYmap[bufTankName][ISYkey]['messana'] == 'mMode':
                Key = ISYkey
        return(Key)  
    def bufferTankTempStatus(self, value, bufTankNbr):
        #logging.debug ('bufferTankTempStatus')
        status = self.pushAtuDataIndividual(bufTankNbr, 'mTempMode', value)
        return(status)
 
    def getBufferTankTempStatusISYdriver(self, bufTankNbr):
        #logging.debug ('getBufferTankTempStatusISYdriver called')
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
        #logging.debug('updatDHWData: ' + str(DHWNbr))
        keys =[]
        if level == 'all':
            #logging.debug('ALL update  Domestic Hot Water ' + str(DHWNbr))
            keys =  self.DHWPullKeys(DHWNbr)
        elif level == 'active':
            #logging.debug('ACTIVE update Domestic Hot Water ' + str(DHWNbr))
            keys =  self.DHWActiveKeys(DHWNbr)
        
        self.dataOK = True
        for mKey in keys:
            self.data = self.pullDHWDataIndividual(DHWNbr, mKey)
            self.dataOK = self.dataOK and self.data['statusOK']
        return(self.dataOK)

    def getDHWCapability(self, DHWNbr): 
        #logging.debug('getDHWCapability for '+str(DHWNbr))                      
        self.getNodeCapability(self.dhwID, DHWNbr)

    def pullDHWDataIndividual(self, DHWNbr, mKey): 
        #logging.debug('pullDHWDataIndividual: ' +str(DHWNbr)  + ' ' + mKey)    
        return(self.pullNodeDataIndividual(DHWNbr, self.dhwID, mKey))

    def pushDHWDataIndividual(self, DHWNbr, mKey, value):
        #logging.debug('pushDHWDataIndividual: ' +str(DHWNbr)  + ' ' + mKey + ' ' + str(value))  
        return(self.pushNodeDataIndividual(DHWNbr, self.dhwID, mKey, value))


    def DHWPullKeys(self, DHWNbr):
        #logging.debug('DHWPullKeys')
        return( self.getNodeKeys (DHWNbr, self.dhwID, 'GETstr'))

    def DHWPushKeys(self, DHWNbr):
        #logging.debug('DHWPushKeys')
        return( self.getNodeKeys (DHWNbr, self.dhwID, 'PUTstr'))
  
    def DHWActiveKeys(self, DHWNbr):
        #logging.debug('DHWActiveKeys')
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
        #logging.debug ('hotWaterSetStatus')
        status = self.pushAtuDataIndividual(DHWNbr, 'mStatus', value)
        return(status)
 
    def getHotWaterStatusISYdriver(self, DHWNbr):
        #logging.debug ('getHotWaterStatusISYdriver called')
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
        #logging.debug ('hotWaterSetTargetTempt')
        status = self.pushAtuDataIndividual(DHWNbr, 'mTargetTemp', value)
        return(status)
 
    def getHotWaterSetTargetTempISYdriver(self, DHWNbr):
        #logging.debug ('getHotWaterSetTargetTempISYdriver called')
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