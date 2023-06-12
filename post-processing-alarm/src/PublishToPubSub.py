# -*- coding: utf-8 -*-
"""
Created on Mon Apr  3 07:40:15 2023

@author: echaksr
"""

from google.cloud import pubsub_v1
import json



def sendTopubSubTopic(message,project_id,topic_id):
    data = str(json.dumps(message))
    data = data.encode('utf-8')
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)
    future = publisher.publish(
        topic_path, data
    )
    return future.result()

#sendTopubSubTopic(alarmInput,project_id,topic_id)  
