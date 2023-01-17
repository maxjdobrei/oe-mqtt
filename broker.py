#Maximilian Dobrei, Carleton University 101103400
#Last modified: August 4th 2022
#an MQTT Broker, embedded in a python script using AMQTT as the broker implementation.

#NOTE!
#This script is based on the AMQTT Broker usage example found at https://amqtt.readthedocs.io/en/latest/references/broker.html
#The original authors of that script are https://github.com/Yakifo and other contributors to the AMQTT project, who in turn are adding on to the work done on HBMQTT by https://github.com/beerfactory
#!NOTE

import asyncio
from amqtt.broker import Broker
import logging
import getopt
import sys

#this is a *coroutine* function as described by asyncio.
async def b_coroutine():
    #below is a python dictionary that describes various settings for the broker
    settings = {
        "listeners": {
            "default": {
                "max-connections": 5,             #for testing purposes the number of maximum connections is low.
                "type": "tcp"
            },
            "my-tcp1": {
                "bind": "127.0.0.1:1883"         #we want to listen for localhost connections, 1883 is the mqtt standard port
            }
        },
        "auth": {
            "allow-anonymous": "true"           #for convenience, won't be using the optional username/password security feature.
        },
        "topic-check": {
            "enabled": True,
            "plugins": ["topic_acl"],
            "acl": {
                "anonymous": [
                    "#"         # the '#' symbol is used as a wildcard and matches any and all topic names.
                ],
            }
        }
    }
    #instantiate a broker object as defined by AMQTT
    mqtt_broker = Broker(settings, None, None)
    #we cant simply call broker.start(), we need to use the asyncio syntax "await" as it will actually schedule the function to run, and wait for it to terminate.
    await mqtt_broker.start()

if __name__ == '__main__':
    
    formatter = "[%(asctime)s] :: %(levelname)s :: %(name)s :: %(message)s"
    logging.basicConfig(level=logging.INFO, format=formatter)
    
    if len(sys.argv) > 1:
        try:
            opts, args = getopt.getopt(sys.argv[1:], "d")
        except getopt.GetoptError:
            print("Usage: python3 broker.py \nyou can use the optional flag -d for more output like so:\n python3 broker.py -d")
            sys.exit(2)

        for opt, arg in opts:
            if opt == "-d":
                logging.basicConfig(level=logging.DEBUG, format=formatter, force=True)
                
    #run_until_complete ensures that coroutine will finish before anything else gets executed.
    #in this case, since b_coroutine awaits the cmopletion of the start() function, this ensures the broker finishes setting itself up
    asyncio.get_event_loop().run_until_complete(b_coroutine())
    #once the broker has been started and is actively listening for connections, we want this to loop indefinitely until a shutdown signal is given.
    asyncio.get_event_loop().run_forever()