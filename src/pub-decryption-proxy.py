#Maximilian Dobrei, Carleton University 101103400
#Last modified: August 4th 2022
#please review proxy.py for more details on the PubDproxy class

from proxy import PubDproxy
import socket
import sys
import getopt

if __name__ == '__main__':
    
    broker_address = "127.0.0.1"
    debug = False

    if len(sys.argv) > 1:
            try:
                opts, args = getopt.getopt(sys.argv[1:], "hdb:")
            except getopt.GetoptError:
                print("Usage: python3 dproxy.py -b <broker_ip_address> ")
                sys.exit(2)

            for opt, arg in opts:
                if opt == "-h":
                    print("Usage: python3 dproxy.py -a <self_ip_address> -b <broker_ip_address> ")
                    sys.exit()
                elif opt == "-b":
                    broker_address = arg
                elif opt == "-d":
                    debug = True

    dp = PubDproxy(broker_address, debug)
    dp.start_broker_endpoint()