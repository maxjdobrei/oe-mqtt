#Maximilian Dobrei, Carleton University 101103400
#Last modified: August 4th 2022
#please review proxy.py for more details on the PubEproxy class

from proxy import PubEproxy
import socket
import sys
import getopt

if __name__ == '__main__':
    
    #defaults
    self_address = "127.0.2.1"
    broker_address = "127.0.0.1"
    debug = False

    if len(sys.argv) > 1:
            try:
                opts, args = getopt.getopt(sys.argv[1:], "hda:b:")
            except getopt.GetoptError:
                print("Usage: python3 eproxy.py -a <self_ip_address> -b <broker_ip_address> ")
                sys.exit(2)

            for opt, arg in opts:
                if opt == "-h":
                    print("Usage: python3 eproxy.py -a <self_ip_address> -b <broker_ip_address> ")
                    sys.exit()
                elif opt == "-a":
                    self_address = arg
                elif opt == "-b":
                    broker_address = arg
                elif opt == "-d":
                    debug = True
                   

    ep = PubEproxy(self_address, broker_address, debug)
    ep.start_client_endpoint()