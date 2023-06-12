# -*- coding: utf-8 -*-
"""
Created on Mon Apr 17 06:32:06 2023

@author: echaksr
"""

import re
import logging
import parse_alarm_main
conf=parse_alarm_main.Setting('alarm-collect-settings.cfg')
logFile = conf.get_setting('MAIN', "logFile")
logging.basicConfig(filename=logFile, level=logging.DEBUG,format="%(asctime)s %(message)s")

from datetime import datetime

def parse_heartbeat_alarm(conf,object,lookup_dict=None):
	if object.BasicParsedAlarm["ElementManagerIP"] != None:
		object.BasicParsedAlarm["Node"] = object.BasicParsedAlarm["ElementManagerIP"]
		logging.debug( "INTEGRATION: EMS Heartbeat" )
	else:
		logging.debug( "INTEGRATION: NE Heartbeat" )

	if object.BasicParsedAlarm["Customer"] != "EGOC":
		object.BasicParsedAlarm["Customer"] = object.BasicParsedAlarm["AdditionalString"]

		object.BasicParsedAlarm["AlertGroup"] = "EMS Heartbeat"
		object.BasicParsedAlarm["AlertKey"] = object.BasicParsedAlarm["Node"] + "|" + object.BasicParsedAlarm["Agent"]
		object.BasicParsedAlarm["NodeAlias"] = object.BasicParsedAlarm["Node"]
		object.BasicParsedAlarm["Summary"] = "Heartbeat notification received from " + object.BasicParsedAlarm["Node"] + " (" + conf.get_setting('INTEGRATION', 'Name') + ")"
		object.BasicParsedAlarm["Severity"] = 1
		object.BasicParsedAlarm["Type"] = 13
		# Duplicated assignements due to SNMP based integrations

		object.BasicParsedAlarm["X733SpecificProb"] = "EMS Heartbeat"
		object.BasicParsedAlarm["X733EventType"] = 1

		object.BasicParsedAlarm["X733ProbableCause"] = 1009
		object.BasicParsedAlarm["FirstOccurrence"] = object.BasicParsedAlarm["ReceivedAtProbe"]
		object.BasicParsedAlarm["LastOccurrence"] = object.BasicParsedAlarm["FirstOccurrence"]
		object.BasicParsedAlarm["Identifier"] = object.BasicParsedAlarm["Customer"] + "|" + object.BasicParsedAlarm["Node"] + "|" + object.BasicParsedAlarm["AlertGroup"] + "|" + object.BasicParsedAlarm["Manager"]

    
    
def parse_alarm(conf,object,lookup_dict=None):
	if object.Trap["networkAlarm"].get('dataType') == "Heartbeat":
		parse_heartbeat_alarm(conf,object)
	else:
		standardalarmseverity = object.Trap["networkAlarm"].get('standardalarmseverity')
		severity = object.Trap["networkAlarm"].get('severity')
		cleartime = str(object.Trap["networkAlarm"].get('cleartime'))
		devicename = object.Trap["networkAlarm"].get('devicename')
		node= object.Trap["networkAlarm"].get('node')
		alarmname = object.Trap["networkAlarm"].get('alarmname')
		summary = object.Trap["networkAlarm"].get('summary')
		extendedattr = object.Trap["networkAlarm"].get('extendedattr')
		alertgroup = object.Trap["networkAlarm"].get('alertgroup')
		alertkey = object.Trap["networkAlarm"].get('alertkey')
		alarmserialnumber = object.Trap["networkAlarm"].get('alarmserialnumber')
		sitecode = object.Trap["networkAlarm"].get('sitecode')
		location = object.Trap["networkAlarm"].get('location')
		mcmcid = object.Trap["networkAlarm"].get('mcmcid')
		manager = object.Trap["networkAlarm"].get('manager')
		domain = object.Trap["networkAlarm"].get('domain')
		firstoccurrence = str(object.Trap["networkAlarm"].get('firstoccurrence'))
		lastoccurrence = str(object.Trap["networkAlarm"].get('lastoccurrence'))


	if standardalarmseverity != None:
		object.BasicParsedAlarm["Severity"] = int(standardalarmseverity)
		object.BasicParsedAlarm["Type"] = 1
	elif severity != None:
		object.BasicParsedAlarm["Severity"] = int(severity)
		object.BasicParsedAlarm["Type"] = 1
	if cleartime != "0":
		object.BasicParsedAlarm["Severity"] = 1
		object.BasicParsedAlarm["Type"] = 2
		object.BasicParsedAlarm["ClearTime"] = int(cleartime)
	if devicename != None:
		object.BasicParsedAlarm["Node"] = devicename.strip()
	elif node != None:
		object.BasicParsedAlarm["Node"] = node.strip()
	object.BasicParsedAlarm["NodeAlias"] = object.BasicParsedAlarm["Node"]

	if alarmname != None:
		object.BasicParsedAlarm["X733SpecificProb"] = alarmname
	if summary!= None :
		object.BasicParsedAlarm["Summary"] = summary
	if extendedattr != None:
		AdditionalString_tmp = extendedattr

	if alertgroup != None:
		object.BasicParsedAlarm["AlertGroup"] = alertgroup

	if alertkey != None:
		object.BasicParsedAlarm["AlertKey"] = alertkey

	if alarmserialnumber != None:
		object.BasicParsedAlarm["EventId"] = alarmserialnumber

	if summary != None:
		alarmObject = re.search(".*keyObj=(.*)",summary)
		if (alarmObject):
			object.BasicParsedAlarm["Object"] = alarmObject.group(1)

	if extendedattr!= None:
		location = re.search(".*NeLocation:([^|]+).*",extendedattr)
		if location:
			object.BasicParsedAlarm["Location"] = location.group(1).strip()


	if sitecode != None:
		object.BasicParsedAlarm["URL"] = sitecode


	if location != None:
		object.BasicParsedAlarm["Location"] = location

	if mcmcid != None:
		object.BasicParsedAlarm["AdditionalString"] = "MCMCID: " + mcmcid


	additionalString = "manager:" + manager
			
	if re.search("ENM",manager) :
		object.BasicParsedAlarm["AdditionalString"] = object.BasicParsedAlarm["AdditionalString"] + " | " + additionalString + " | " + object.BasicParsedAlarm["AlertKey"] + " | " + AdditionalString_tmp
	else:
		object.BasicParsedAlarm["AdditionalString"] = object.BasicParsedAlarm["AdditionalString"] + " | " + additionalString + " | " + AdditionalString_tmp


	if domain == "100":
		object.BasicParsedAlarm["FDN"] = "100_2G"
	elif domain == "102":
		object.BasicParsedAlarm["FDN"] = "102_4G"
	else:
		object.BasicParsedAlarm["FDN"] = domain


	if alertgroup != None:
		if re.search("PROCESSING_ERROR_ALARM",alertgroup)  or re.search("Processing Error Alarm",alertgroup):
			object.BasicParsedAlarm["X733EventType"] = 3
			object.BasicParsedAlarm["X733ProbableCause"] = 4003
		elif re.search("EQUIPMENT_ALARM",alertgroup)  or re.search("Equipment Alarm",alertgroup):
			object.BasicParsedAlarm["X733EventType"] = 4
			object.BasicParsedAlarm["X733ProbableCause"] = 4010
		elif re.search("COMMUNICATION_ALARM",alertgroup)  or re.search("Communication Alarm",alertgroup): 
			object.BasicParsedAlarm["X733EventType"] = 1
			object.BasicParsedAlarm["X733ProbableCause"] = 1008
		elif re.search("QUALITY_OF_SERVICE_ALARM",alertgroup)  or re.search("Quality of Service Alarm",alertgroup):
			object.BasicParsedAlarm["X733EventType"] = 2
			object.BasicParsedAlarm["X733ProbableCause"] = 1007
		elif re.search("ENVIRONMENTAL_ALARM",alertgroup)  or re.search("Environmental Alarm",alertgroup):
			object.BasicParsedAlarm["X733EventType"] = 5
			object.BasicParsedAlarm["X733ProbableCause"] = 100174
		else:
			object.BasicParsedAlarm["X733EventType"] = 0
			object.BasicParsedAlarm["X733ProbableCause"] = 0



	# Parsing alarm timestamps
	if  firstoccurrence != None:
		fo = re.search("(.*)000$",firstoccurrence)
		if fo:
			object.BasicParsedAlarm["FirstOccurrence"] = int(fo.group(1))


	if  lastoccurrence != None:
		lo = re.search("(.*)000$",lastoccurrence)
		if (lo):
			object.BasicParsedAlarm["LastOccurrence"] = int(lo.group(1))

	object.BasicParsedAlarm["Identifier"] = object.BasicParsedAlarm["Node"] + "|" + object.BasicParsedAlarm["EventId"] + "|" + object.BasicParsedAlarm["Agent"] + "|" + object.BasicParsedAlarm["Manager"]