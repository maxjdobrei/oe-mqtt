#Maximilian Dobrei, Carleton University 101103400
#Last modified: August 4th 2022
#An MQTT publisher embedded in a python script, using AMQTT for the publisher implementation

#NOTE!
#This script is based on the AMQTT Client Publisher example found at https://amqtt.readthedocs.io/en/latest/references/mqttclient.html
#The original authors of that script are https://github.com/Yakifo and other contributors to the AMQTT project, who in turn are adding on to the work done on HBMQTT by https://github.com/beerfactory
#!NOTE

import asyncio
import logging
import sys
import getopt

from amqtt.client import MQTTClient
from amqtt.mqtt.constants import QOS_0, QOS_1, QOS_2
logger = logging.getLogger(__name__)

async def publisher_coroutine(addr, topic, msg):
    C = MQTTClient("publisher1")
    await C.connect(addr)
    tasks = [
        asyncio.ensure_future(C.publish(topic, msg, qos=QOS_1)),
    ]
    await asyncio.wait(tasks)
    logger.info("messages published")
    await C.disconnect()


if __name__ == '__main__':
    formatter = "[%(asctime)s] %(name)s {%(filename)s:%(lineno)d} %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=formatter)

    #default settings to use for publishing a message
    broker_address = "mqtt://127.0.0.1:1883"
    application_message = b'THIS IS A TEST MESSAGE'
    topic_name = "TOPIC"

    if len(sys.argv) > 1:
        try:
            opts, args = getopt.getopt(sys.argv[1:], "hda:m:t:")
        except getopt.GetoptError:
            print("Usage: python3 publisher.py -a <ip_address:port> -t <topic_name> -m <message>")
            sys.exit(2)

        for opt, arg in opts:
            if opt == "-h":
                print("Usage: python3 publisher.py -a <ip_address:port> -t <topic_name> -m <message>")
                sys.exit()
            elif opt == "-a":
                broker_address = "mqtt://" + arg
            elif opt == "-m":
                application_message = arg.encode("UTF-8")
            elif opt == "-t":
                topic = arg
            elif opt == "-d":
                logging.basicConfig(level=logging.DEBUG, format=formatter, force=True)

    asyncio.get_event_loop().run_until_complete(publisher_coroutine(broker_address, topic_name, application_message))