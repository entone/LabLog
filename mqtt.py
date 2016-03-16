import paho.mqtt.client as mqtt
from influxdb.exceptions import InfluxDBClientError
from lablog import config
from lablog import db
from lablog.interfaces.sensornode import Node
import humongolus
import logging
import datetime
import time

clients = {}

logging.basicConfig(level=config.LOG_LEVEL)

es = db.init_elasticsearch()
db.create_index(es)
influx = db.init_influxdb()
db.create_shards(influx)

ES = db.init_elasticsearch()
INFLUX = db.init_influxdb()
MONGO = db.init_mongodb()
MQ = db.init_mq()
humongolus.settings(logging, MONGO)

def on_connect(client, userdata, flags, rc):
    logging.info("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    for sub, f in subscriptions.iteritems():
        client.subscribe(sub)

def on_message(client, userdata, msg):
    logging.info(msg.topic+" "+str(msg.payload))
    for sub, f in subscriptions.iteritems():
        if mqtt.topic_matches_sub(sub, msg.topic):
            f(client, userdata, msg)

def client_data(client, userdata, msg):
    n, client_id, data = msg.topic.split("/")
    try:
        n = Node.find_one({'id':client_id})
        n.go(INFLUX, MQ, data=msg.payload)
        n._last_run = datetime.datetime.utcnow()
        n.save()
        clients.setdefault(client_id, {})
    except InfluxDBClientError as e:
        clients.setdefault(client_id, {})
        logging.error(e)
    except Exception as e:
        logging.error(e)

def new_client(client, userdata, msg):
    clients.setdefault(msg.payload, {})

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

subscriptions = {
    '/+/data': client_data,
    '/broadcast/new': new_client,
}

client.connect("mqtt", 1883, 60)

client.loop_start()

while True:
    for c in clients.keys():
        try:
            logging.info(datetime.datetime.utcnow())
            logging.info("6,1")
            client.publish("/{}".format(c), "6,1", qos=1)
        except Exception as e:
            logging.error(e)
        time.sleep(1)
        try:
            logging.info(datetime.datetime.utcnow())
            logging.info("6,0")
            client.publish("/{}".format(c), "6,0", qos=1)
        except Exception as e:
            logging.error(e)
        time.sleep(1)
    else:
        time.sleep(.1)
