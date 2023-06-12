# -*- coding: utf-8 -*-
"""
Created on Fri Mar 31 07:23:52 2023

@author: echaksr
"""

from concurrent.futures import TimeoutError
from google.cloud import pubsub_v1
import json
import configparser
import post_processing_alarm
import PublishToPubSub
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
    
conf=Setting('post-processing-settings.cfg')
subscription_id = conf.get_setting("PUBSUB", "post_processing_sub_id")
project_id = conf.get_setting("PUBSUB", "project_id")
alerts_topic = conf.get_setting("PUBSUB", "alerts_topic_id")
logFile = conf.get_setting('MAIN', "logFile")

logging.basicConfig(filename=logFile, level=logging.DEBUG,format="%(asctime)s %(message)s")
#subscription_id = "mela-alerts-topic-sub"
# Number of seconds the subscriber should listen for messages
timeout = 20.0


subscriber = pubsub_v1.SubscriberClient()
# The `subscription_path` method creates a fully qualified identifier
# in the form `projects/{project_id}/subscriptions/{subscription_id}`
subscription_path = subscriber.subscription_path(project_id, subscription_id)

def callback(message: pubsub_v1.subscriber.message.Message) -> None:
    
    alarm = message.data.decode("utf-8")
    jsonData=json.loads(alarm)
    mainAlarm=jsonData["Alarm"]
    logging.debug("Processing alarm with id : " +mainAlarm["Identifier"] )
    updateFields = jsonData["updatedFields"]
    post_processing_alarm.process_new_row(mainAlarm)
    enrichedAlarm = post_processing_alarm.eai_enrichment(mainAlarm,conf)
    alarmToPublish = {"Alarm":enrichedAlarm,"updatedFields":updateFields}
    logging.debug("Alarm To publish before- " + str(alarmToPublish))
    post_processing_alarm.process_deduplication(alarmToPublish)
    logging.debug("Alarm To publish after- " + str(alarmToPublish))
    #PublishToPubSub.sendTopubSubTopic(alarmToPublish, project_id, alerts_topic)
    
    message.ack()

streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
print(f"Listening for messages on {subscription_path}..\n")

# Wrap subscriber in a 'with' block to automatically call close() when done.
with subscriber:
    try:
        # When `timeout` is not set, result() will block indefinitely,
        # unless an exception is encountered first.
        logging.debug("Listening to Subscriber : " +subscription_path)
        streaming_pull_future.result()

    except TimeoutError:
        streaming_pull_future.cancel()  # Trigger the shutdown.
        streaming_pull_future.result()  # Block until the shutdown is complete.