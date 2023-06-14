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
