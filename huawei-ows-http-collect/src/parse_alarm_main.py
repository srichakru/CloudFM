# -*- coding: utf-8 -*-
"""
Created on Mon Apr 10 13:32:16 2023

@author: echaksr
"""

import socket
import configparser
import time
import re
import json
import PublishToPubSub



#Trap={"peerAddress": "172.29.222.68", "networkAlarm": {"1.3.6.1.2.1.1.3.0": "610043116", "1.3.6.1.6.3.1.1.4.1.0": "enterprises.23629.1.5.2.2.5", "1.3.6.1.4.1.23629.1.5.2.2.1": "[hsm01:10.200.0.164 / messages / 2021 Sep  1 11:07:09 / smartd[12532] / 1]"}}
#jsonTrap =json.dumps(Trap)

class NetworkAlarm:                  
    def __init__(self):
        self.Trap={"peerAddress": "172.29.222.68", "networkAlarm": {"1.3.6.1.2.1.1.3.0": "610043116", "1.3.6.1.6.3.1.1.4.1.0": "enterprises.23629.1.5.2.2.6", "1.3.6.1.4.1.23629.1.5.2.2.1": "[hsm01:10.200.0.165 / messages deducplication / 2023 Apr  1 11:07:09 / smartd[12532] / 3]"}}
        self.BasicParsedAlarm={}
        self.UpdateFields={}
    
    def __init__(self,data,peerAddress):
        self.Trap = {}
        self.Trap["peerAddress"] = peerAddress
        self.Trap["networkAlarm"] = data
        self.BasicParsedAlarm={}
        self.UpdateFields={}
        
        

    def convertToJson(self):
        jsonAlarm = json.dumps(self.Trap)
        return jsonAlarm

        return self.Trap
    
                  
    def set_default_alarm_fields(self,alarmFieldDict):
        #print(alarmFieldDict["AlarmFields"])
        for key, val in alarmFieldDict["AlarmFields"].items():
            self.BasicParsedAlarm[key] = val
        
        
    def parse_alarm_main(self,conf):
        curTime = time.time()
        self.BasicParsedAlarm["Customer"] = conf.get_setting('INTEGRATION', 'CustomerName')
        pod = socket.gethostname()
        podList = pod.split('-')
        deployList = (podList[:-2 ])
        deployName = ""
        for _ in deployList:
            if deployName == "":
                deployName = _
            else:
                deployName = deployName + "-" + _
        self.BasicParsedAlarm["ReceivedAtProbe"] = curTime
        self.BasicParsedAlarm["ElementManagerIP"] = conf.get_setting('INTEGRATION', 'ElementManagerIP')
        if self.BasicParsedAlarm["ElementManagerIP"]=="PeerAddress":
            self.BasicParsedAlarm["ElementManagerIP"]=self.Trap["peerAddress"]
        self.BasicParsedAlarm["Manager"]=conf.get_setting('INTEGRATION', 'Manager')+"@"+deployName+":"+conf.get_setting('INTEGRATION', 'CommandPortSet')
        self.BasicParsedAlarm["Agent"]=conf.get_setting('INTEGRATION', 'Manager').upper()
        #notify=self.Trap["networkAlarm"]["1.3.6.1.6.3.1.1.4.1.0"]
        self.BasicParsedAlarm["Node"]=self.Trap["peerAddress"]
        self.BasicParsedAlarm["NodeAlias"]=self.Trap["peerAddress"]
        
        
        #print(self.Trap)
        #print(self.BasicParsedAlarm)

    def set_update_fields(self,alarmFieldDict):
        for key in alarmFieldDict["UpdateFields"]:
            self.UpdateFields[str(key)]=self.BasicParsedAlarm[str(key)]
            
          

        
class SnmpTrap(NetworkAlarm):
    def __init__(self,varbind,peerAddress="0.0.0.0"):
        

        self.Trap = dict()
        self.Trap["peerAddress"] = peerAddress
        self.Trap["networkAlarm"] = varbind
        self.BasicParsedAlarm={}
        self.UpdateFields={}
               
    def __init__(self):
        self.Trap={"peerAddress": "172.29.222.68", "networkAlarm": {"1.3.6.1.2.1.1.3.0": "610043116", "1.3.6.1.6.3.1.1.4.1.0": "enterprises.23629.1.5.2.2.6", "1.3.6.1.4.1.23629.1.5.2.2.1": "[hsm01:10.200.0.165 / messages notify / 2023 Apr  1 11:07:09 / smartd[12532] / 3]"}}
        self.BasicParsedAlarm={}
        self.UpdateFields={}
            
    def getSNMPTrap(self):
        return self.Trap
    
    def convertv2_to_v1(self):
        notify=self.Trap["networkAlarm"]["1.3.6.1.6.3.1.1.4.1.0"]
        notify=re.sub("^enterprises",".1.3.6.1.4.1",notify)
        notify=re.sub("iso","1",notify)
        v1Alarm={}
        v1Alarm["notify"]=notify
        enterprise_search=re.search("\.([0-9]+)\.[0-9]+$",notify)
        if enterprise_search.group(1)=="0":
            enterprise_extract=re.search("(.*)\.[0-9]+\.[0-9]+$",notify)
            enterprise=enterprise_extract.group(1)
        else:
            enterprise_extract=re.search("(.*)\.[0-9]+$",notify)
            enterprise=enterprise_extract.group(1)
        specificTrap=re.search(".*\.([0-9]+)$",notify)
        v1Alarm["enterprise"]=enterprise
        v1Alarm["specificTrap"]=specificTrap.group(1)
        v1Alarm["genericTrap"]="6"
        varbinds={}
        for key,val in self.Trap["networkAlarm"].items():
            var_search= re.search(".*\.([0-9]+)$",key)
            varbinds[var_search.group(1)] = val
        self.Trap["v1Alarm"] = v1Alarm
        self.Trap["varbinds"] = varbinds
        

        
 
            
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
"""
if __name__ == '__main__':

    conf=Setting('alarm-settings.cfg')
    lookup_dict = get_lookups(conf.get_setting("INTEGRATION", "IntegrationLookupJson"))
    alarmFields = get_lookups(conf.get_setting('MAIN', "AlarmFieldsJson"))
    
    
    
    networkTrap = SnmpTrap()
    networkTrap.convertv2_to_v1()
    
    #Set all fields by default
    networkTrap.set_default_alarm_fields(alarmFields)
    
    #Set the main alarm fields based on the settings.cfg file
    networkTrap.parse_alarm_main(conf)
    
    import thales_generic_snmp
    
    # Alarm processing
    thales_generic_snmp.parse_alarm(conf,networkTrap,lookup_dict)
    
    # Fields that will be updated on the record if its a reinsert
    networkTrap.set_update_fields(alarmFields)
    messageToPublish={"Alarm":networkTrap.BasicParsedAlarm,"updatedFields":networkTrap.UpdateFields}
    #print(networkTrap.BasicParsedAlarm)

    project_id = "mongo-db-382501"
    topic_id = "mela-alerts-topic"
    #topic_id = "test-topic"
    print(messageToPublish)
    
    PublishToPubSub.sendTopubSubTopic(messageToPublish, project_id, topic_id)
"""