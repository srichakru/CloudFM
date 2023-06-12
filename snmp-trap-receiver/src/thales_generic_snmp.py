# -*- coding: utf-8 -*-
"""
Created on Tue Apr 11 07:27:42 2023

@author: echaksr
"""
import re

from datetime import datetime


    
    
def parse_alarm(conf,object,lookup_dict):
    enterprise = object.Trap["v1Alarm"]["enterprise"]
    sp_trap=object.Trap["v1Alarm"]["specificTrap"]
    if enterprise==".1.3.6.1.4.1.23629.1.5.2.2":
        if sp_trap =="5":
            OS_EventId = "SNMPTRAP-SAFENET-APPLIANCE-MIB-diskDriveAttentionNotify"
            object.BasicParsedAlarm["AlertGroup"] = "diskDriveAttentionNotify"
            ssLogReference=object.Trap["varbinds"]["1"]
            ssLogReference = ssLogReference[1:-1]
            object.BasicParsedAlarm["Class"]=1010823
            var_extract = ssLogReference.split("/")
            epoch = datetime(1970, 1, 1)
            object.BasicParsedAlarm["FirstOccurrence"] = (datetime.strptime(var_extract[2], " %Y %b  %d %H:%M:%S ") - epoch).total_seconds()
            object.BasicParsedAlarm["LastOccurrence"] = (datetime.strptime(var_extract[2], " %Y %b  %d %H:%M:%S ") - epoch).total_seconds()
            sev_type=lookup_dict["thales-SAFENET-APPLIANCE-MIB_userSeverityAndType"][var_extract[4].strip()]
            sevTypeArr = sev_type.split(",")
            if int(sevTypeArr[1]) == 2:
                object.BasicParsedAlarm["ClearTime"] = (datetime.strptime(var_extract[2], " %Y %b  %d %H:%M:%S ") - epoch).total_seconds()
                object.BasicParsedAlarm["ClearedBy"] = "deduplication"                
            object.BasicParsedAlarm["Severity"] = int(sevTypeArr[0])
            object.BasicParsedAlarm["Type"] = int(sevTypeArr[1])
            nodeIP = re.search(".*\:(.*)$",var_extract[0])
            object.BasicParsedAlarm["NodeIP"] = nodeIP.group(1)
            object.BasicParsedAlarm["Summary"] = var_extract[1].strip()
            object.BasicParsedAlarm["AlertKey"] = var_extract[3].strip()
            object.BasicParsedAlarm["X733SpecificProb"] = object.BasicParsedAlarm["AlertGroup"]
            object.BasicParsedAlarm["X733EventType"] = 4
            object.BasicParsedAlarm["X733ProbableCause"] = int(lookup_dict["thales-SAFENET-APPLIANCE-MIB_userX733ProbableCause"][OS_EventId])
            object.BasicParsedAlarm["Identifier"] = object.BasicParsedAlarm["Node"] + "|" + object.BasicParsedAlarm["AlertGroup"] + "|" +  object.BasicParsedAlarm["Agent"] + "|" +object.BasicParsedAlarm["Manager"]
        if sp_trap =="6":
            OS_EventId = "SNMPTRAP-SAFENET-APPLIANCE-MIB-ntlsAttentionNotify"
            object.BasicParsedAlarm["AlertGroup"] = "ntlsAttentionNotify"
            ssLogReference=object.Trap["varbinds"]["1"]
            ssLogReference = ssLogReference[1:-1]
            object.BasicParsedAlarm["Class"]=1010823
            var_extract = ssLogReference.split("/")
            epoch = datetime(1970, 1, 1)
            object.BasicParsedAlarm["FirstOccurrence"] = (datetime.strptime(var_extract[2], " %Y %b  %d %H:%M:%S ") - epoch).total_seconds()
            object.BasicParsedAlarm["LastOccurrence"] = (datetime.strptime(var_extract[2], " %Y %b  %d %H:%M:%S ") - epoch).total_seconds()
            sev_type=lookup_dict["thales-SAFENET-APPLIANCE-MIB_userSeverityAndType"][var_extract[4].strip()]
            sevTypeArr = sev_type.split(",")
            if int(sevTypeArr[1]) == 2:
                object.BasicParsedAlarm["ClearTime"] = (datetime.strptime(var_extract[2], " %Y %b  %d %H:%M:%S ") - epoch).total_seconds()
                object.BasicParsedAlarm["ClearedBy"] = "deduplication"                
            object.BasicParsedAlarm["Severity"] = int(sevTypeArr[0])
            object.BasicParsedAlarm["Type"] = int(sevTypeArr[1])
            nodeIP = re.search(".*\:(.*)$",var_extract[0])
            object.BasicParsedAlarm["NodeIP"] = nodeIP.group(1)
            object.BasicParsedAlarm["Summary"] = var_extract[1].strip()
            object.BasicParsedAlarm["AlertKey"] = var_extract[3].strip()
            object.BasicParsedAlarm["X733SpecificProb"] = object.BasicParsedAlarm["AlertGroup"]
            object.BasicParsedAlarm["X733EventType"] = 4
            object.BasicParsedAlarm["X733ProbableCause"] = int(lookup_dict["thales-SAFENET-APPLIANCE-MIB_userX733ProbableCause"][OS_EventId])
            object.BasicParsedAlarm["Identifier"] = object.BasicParsedAlarm["Node"] + "|" + object.BasicParsedAlarm["AlertGroup"] + "|" +  object.BasicParsedAlarm["Agent"] + "|" +object.BasicParsedAlarm["Manager"]
            
        else:
            object.BasicParsedAlarm["Summary"] = "No rules found for enterprise "+enterprise + " and sp trap " + sp_trap
    else:
        object.BasicParsedAlarm["Summary"] = "No rules found for enterprise "+enterprise + " and sp trap " + sp_trap

            
            
            
            

            
            
                
    
