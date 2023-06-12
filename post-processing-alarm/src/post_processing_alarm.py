# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 06:40:52 2023

@author: echaksr
"""


import json
import configparser
import pymongo
import logging

def get_lookups(fileName):
    f =  open(fileName, 'r') 
    dict_lookup = json.loads(f.read())
    f.close()
    return dict_lookup     
    
class Setting(object):

    def __init__(self, cfg_path):
        self.cfg = configparser.ConfigParser()
        self.cfg.read(cfg_path)

    def get_setting(self, section, my_setting):
        try:        
            ret = self.cfg.get(section, my_setting)
        except configparser.NoOptionError:
            ret = None
        return ret

## Defining the log file 
conf=Setting('post-processing-settings.cfg')
logFile = conf.get_setting('MAIN', "logFile")
logging.basicConfig(filename=logFile, level=logging.DEBUG,format="%(asctime)s %(message)s")

## Basic Enrichment
def eai_enrichment(mainAlarm,conf):
   
    mongoClusterConnStr =  conf.get_setting("MONGO", "connectionStr")
    customer = mainAlarm["Customer"]
    mongoDb = conf.get_setting("MONGO", "inv_database")
    mongoNodeColName = customer + "-Node"
    mongoLocationColName = customer + "-Location"
    mongoClusterConnStr =  conf.get_setting("MONGO", "connectionStr")
    myclient = pymongo.MongoClient(mongoClusterConnStr)
    mydb = myclient[mongoDb]
    mongoNodeColl = mydb[customer + "-Node"]
    mongoLocationColl = mydb[customer + "-Location"]
    logging.debug("ENRICHMENT: Inventory tables - " + mongoNodeColName + ", " + mongoLocationColName)
    if mainAlarm["NodeAlias"] == "":
        mainAlarm["NodeAlias"] = mainAlarm["Node"]
    nodeAlias = mainAlarm["NodeAlias"]
    logging.debug("ENRICHMENT: NodeAlias - " + nodeAlias)
    nodeInv = {}
    locationInv = {}
    if  nodeAlias != "":
        nodeInv = mongoNodeColl.find_one({ "Name": nodeAlias },{'_id': False})
    if nodeInv != None:
        locationInv = mongoLocationColl.find_one({"siteID":nodeInv["SiteName"]},{'_id': False})
    else:
        nodeInv = {}
    myclient.close()
    if locationInv == None:
        locationInv = {}
    mainAlarm["nodeInventory"] = nodeInv
    mainAlarm["locationInventory"] = locationInv
    
    #EnrichmentFlag set to 1
    mainAlarm["Grade"] = 1
    logging.debug("ENRICHMENT: Enrichment completed. Updating alarm Grade = 1 ")
    return mainAlarm
    

def process_new_row(mainAlarm):
    if mainAlarm["Type"]==2:
        mainAlarm["ClearTime"] = mainAlarm["LastOccurrence"]
    mainAlarm["OriginalSeverity"] = mainAlarm["Severity"]
    
# TODO
def process_deduplication(AlarmToPublish):
    mainAlarm = AlarmToPublish["Alarm"]
    updateFields = AlarmToPublish["updatedFields"]
    alertsCollection = conf.get_setting("MONGO", "alerts_collection")
    alertsDb = conf.get_setting("MONGO", "alerts_database")
    mongoClusterConnStr =  conf.get_setting("MONGO", "connectionStr")
    myclient = pymongo.MongoClient(mongoClusterConnStr)
    mydb = myclient[alertsDb]
    mongoalertsColl = mydb[alertsCollection]
    identifier = mainAlarm["Identifier"]
    oldAlarm = mongoalertsColl.find_one({ "_id": identifier })
    if oldAlarm == None:
        mainAlarm["_id"] = identifier
        result = mongoalertsColl.insert_one(mainAlarm)
    else:
        ## Deduplication logic
        logging.debug("Entering deduplication logic")
        tallyInc = 1
        if oldAlarm["Type"] == 1 and mainAlarm["Type"] == 2 and mainAlarm["LastOccurrence"] >= oldAlarm["LastOccurrence"] :
            updateFields["ClearedBy"] = "Deduplication"
            updateFields["ClearTime"] = mainAlarm["LastOccurrence"]
            updateFields["Severity"]  = 0
            updateFields["Archived"] = 0
            tallyInc = 0
        AlarmToPublish={"Alarm":mainAlarm,"updatedFields":updateFields}
        #logging.debug("Alarm to publish: " + str(AlarmToPublish))
        result = mongoalertsColl.update_one({'_id': identifier}, {'$inc': {"Tally": tallyInc},'$set':updateFields })
    myclient.close()

            
            


## TODO
def eai_alarm_mapping(mainAlarm,nodeInv,locationInv):
    return mainAlarm
"""
if __name__ == '__main__':
    jsonData={'Alarm': {'Acknowledged': 0, 'Acknowledger': '', 'AcknowledgeTime': 0, 'AdditionalDate': 0, 'AdditionalInt': 0, 'AdditionalString': 'MCMCID: MC17U_0106 | manager:ENM01 | SubNetwork=SABAH,SubNetwork=KKRN11,MeContext=S100A_S01415OD_T3_KGKINOLOSODON,ManagedElement=1,Equipment=1,DigitalCable=1_1_RI_F 775674981 | DUW3101 connector RI_F. faultySide=objectAConnector RI_F. Not in operation', 'Agent': 'HUAWEI-OWS-HTTP', 'AlertCode': 0, 'AlertGroup': 'ET_EQUIPMENT_ALARM', 'AlertKey': 'SubNetwork=SABAH,SubNetwork=KKRN11,MeContext=S100A_S01415OD_T3_KGKINOLOSODON,ManagedElement=1,Equipment=1,DigitalCable=1_1_RI_F 775674981', 'AlertName': '', 'Archived': 0, 'Auto_Notification': 0, 'AutoClearTT': 0, 'AutoEmail_Notification_Status': 0, 'AutoTT': 0, 'AutoTT_Delay': 0, 'BackhaulAccessType': '', 'BackhaulType': '', 'ChangeRequest_Id': '', 'Circle': '', 'Class': 1010827, 'ClearedBy': '', 'ClearTime': 1673333240000, 'CLLI_CD': '', 'CNSInd': '', 'CNSType': '', 'Collocated': '', 'ControlNE': '', 'ControlNE_SiteID': '', 'CorrelatedSilos': '', 'Customer': 'TEST-OF-CNTRY', 'DestinationObjectID': '', 'DestMessageID': '', 'DeviceModel': '', 'DownAckSupported': 0, 'DRMS': '', 'ElementManagerIP': '10.132.0.40', 'EMS_Name': '', 'EventId': '775674981', 'ExpireTime': 0, 'ExtendedAttr': '', 'ExternalEvent': '', 'FDN': 101, 'FirstOccurrence': 1673333190, 'Flash': 0, 'FMSKeyword': '', 'Grade': 0, 'HideForXsec': 0, 'HostName': '', 'Identifier': 'S100A_S01415OD_T3_KGKINOLOSODON|775674981|HUAWEI-OWS-HTTP|huawei-ows-http@huawei-ows-http-collect:6795', 'ImpactFlag': 0, 'InternalLast': 0, 'JournalEntries': 0, 'LastJournalEntry': '', 'LastOccurrence': 1673333190, 'Location': '', 'LocationFirstOccurrence': '', 'LocationLastOccurrence': '', 'Manager': 'huawei-ows-http@huawei-ows-http-collect:6795', 'MSO': '', 'MultiSilo_Flag': 0, 'NMX_EI_ID': 0, 'NMXGenerated': 0, 'Node': '3779B-Taman Kerubong Jaya-RTN 02', 'NodeAlias': '', 'NodeIP': '', 'NodeStatus': '', 'NodeType': '', 'Notification_Delay': 0, 'Notification_Status': 0, 'NotificationID': 0, 'Object': '', 'ObjectStatus': '', 'OEMMarketVendor': '', 'OldRow': 0, 'OriginalSeverity': 0, 'OwnerGID': 0, 'OwnerUID': 0, 'ParentEvent': 0, 'ParentServerName': '', 'PhysicalCard': '', 'PhysicalPort': 0, 'PhysicalShelf': 0, 'PhysicalSlot': 0, 'Poll': 0, 'ProbeSubSecondId': 0, 'ProcessedByImpact': 0, 'ReceivedAtAggregation': 0, 'ReceivedAtProbe': 1681737980.1359527, 'Region': '', 'Service': '', 'ServiceAffecting': 0, 'ServiceStatus': '', 'Severity': 1, 'SiteID': '', 'SiteName': '', 'SitePriority': 0, 'SiteStatus': '', 'SLA': 0, 'StateChange': 0, 'SubManager': '', 'Summary': 'New alarm ( DigitalCable_CableFailure ) on S100A_S01415OD_T3_KGKINOLOSODON : EQUIPMENT_MALFUNCTION', 'SuppressEscl': 0, 'Tally': 1, 'Threshold': '', 'TicketData': '', 'TimeZone': 0, 'TMTransBeginTime': 0, 'TMTransState': 0, 'TT_Flag': 0, 'TT_ID': '', 'TTClosureTime': 0, 'TTCreationTime': 0, 'Type': 2, 'URL': 'S01415', 'VoiceCall_Notification_Status': 0, 'X733CorrNotif': '', 'X733EventType': 4, 'X733ProbableCause': 4010, 'X733SpecificProb': 'DigitalCable_CableFailure'}, 'updatedFields': {'Summary': 'New alarm ( DigitalCable_CableFailure ) on S100A_S01415OD_T3_KGKINOLOSODON : EQUIPMENT_MALFUNCTION', 'X733SpecificProb': 'DigitalCable_CableFailure', 'Severity': 1, 'LastOccurrence': 1673333190, 'AutoTT': 0}}

    #print(jsonData)

    conf=Setting('post-processing-settings.cfg')
    mainAlarm=jsonData["Alarm"]
    updateFields = jsonData["updatedFields"]
    
    # Check if it is an already enriched alarm
    if mainAlarm["Grade"] == 0:
        enrichedAlarm = eai_enrichment(mainAlarm,conf)
    process_new_row(mainAlarm)
    alarmToPublish = {"Alarm":enrichedAlarm,"updatedFields":updateFields}
    logging.debug("Alarm To Publish : " + str(alarmToPublish))
        
"""      
        
        
    

    