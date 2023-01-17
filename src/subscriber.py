#Maximilian Dobrei, Carleton University 101103400
#Last modified: August 4th 2022
#An MQTT subscriber embedded in a python script, using AMQTT for the subscriber implementation

#NOTE!
#This script is based on the AMQTT Client Subscriber usage example found at https://amqtt.readthedocs.io/en/latest/references/mqttclient.html
#The original authors of that script are https://github.com/Yakifo and other contributors to the AMQTT project, who in turn are adding on to the work done on HBMQTT by https://github.com/beerfactory
#!NOTE

import logging
import asyncio
import sys
import getopt

from amqtt.client import MQTTClient, ClientException
from amqtt.mqtt.constants import QOS_0, QOS_1, QOS_2

logger = logging.getLogger(__name__)

async def subscriber_coroutine(addr, topic):
    C = MQTTClient("subscriber1")
    await C.connect(addr)
    await C.subscribe([
            (topic, QOS_1),
         ])
    try:
        for i in range(1, 100):
            message = await C.deliver_message()
            packet = message.publish_packet
            logger.info("Attempting to parse packet: ")
            logger.info(packet.variable_header.topic_name)
            logger.info(str(packet.payload.data))
            #print("%d:  %s => %s" % (i, packet.variable_header.topic_name, str(packet.payload.data)))
        await C.unsubscribe(['TEST'])
        await C.disconnect()
    except ClientException as ce:
        pass
        logger.error("Client exception: %s" % ce)

if __name__ == '__main__':
    formatter = "[%(asctime)s] %(name)s {%(filename)s:%(lineno)d} %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=formatter)

    #default settings to use for publishing a message
    broker_address = "mqtt://127.0.0.1:1883"
    topic_name = "TOPIC"

    if len(sys.argv) > 1:
        try:
            opts, args = getopt.getopt(sys.argv[1:], "hda:t:")
        except getopt.GetoptError:
            print("Usage: python3 subscriber.py -a <ip_address:port> -t <topic_name>")
            sys.exit(2)

        for opt, arg in opts:
            if opt == "-h":
                print("Usage: python3 subscriber.py -a <ip_address:port> -t <topic_name>")
                sys.exit()
            elif opt == "-a":
                broker_address = "mqtt://" + arg
            elif opt == "-t":
                topic = arg
            elif opt == "-d":
                logging.basicConfig(level=logging.DEBUG, format=formatter, force=True)

    asyncio.get_event_loop().run_until_complete(subscriber_coroutine(broker_address, topic_name))