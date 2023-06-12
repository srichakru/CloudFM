import os
import logging
from flask import Flask,request,make_response
import parse_alarm_main
import PublishToPubSub
import huawei_ows_http_rules


conf=parse_alarm_main.Setting('alarm-collect-settings.cfg')
logFile = conf.get_setting('MAIN', "logFile")
host=conf.get_setting('MAIN', "host")
port= conf.get_setting('MAIN',"port")
URI=conf.get_setting('MAIN',"URI")
pubSubTopic = conf.get_setting("PUBSUB", "post_processing_topic_id")
pubSubproject = conf.get_setting("PUBSUB", "project_id")
#lookup_dict = parse_alarm_main.get_lookups(conf.get_setting("INTEGRATION", "IntegrationLookupJson"))
alarmFields = parse_alarm_main.get_lookups(conf.get_setting('MAIN', "AlarmFieldsJson"))
logging.basicConfig(filename=logFile, level=logging.DEBUG,format="%(asctime)s %(message)s")

logging.basicConfig(filename=logFile, level=logging.DEBUG,format="%(asctime)s %(message)s")
logging.debug("Webhook collector listening at URL http://"+host+":"+port+URI);
logging.debug('--------------------------------------------------------------------------');

app = Flask(__name__)
@app.route(URI, methods=['GET', 'POST'])
def hello_world():
    data = request.json
    webhookAlarm = parse_alarm_main.NetworkAlarm(data,request.remote_addr)
    webhookAlarm.Trap["networkAlarm"] = webhookAlarm.Trap["networkAlarm"]["digiarray"][0]
    logging.debug(webhookAlarm.Trap["networkAlarm"])
    logging.debug(webhookAlarm.Trap["peerAddress"])
    webhookAlarm.set_default_alarm_fields(alarmFields)
    webhookAlarm.parse_alarm_main(conf)
    huawei_ows_http_rules.parse_alarm(conf, webhookAlarm)
    webhookAlarm.set_update_fields(alarmFields)
    messageToPublish={"Alarm":webhookAlarm.BasicParsedAlarm,"updatedFields":webhookAlarm.UpdateFields}
    logging.debug("Message to publish - " + str(messageToPublish))

    res=PublishToPubSub.sendTopubSubTopic(messageToPublish,pubSubproject,pubSubTopic)
    if res:
        logging.debug("Data published to Pubsub : " + res)

    response = make_response("<h1>Success</h1>")
    response.status_code = 200
    return response

if __name__ == "__main__":
    app.run(debug=True,host=host,port=int(os.environ.get('PORT', port)))
