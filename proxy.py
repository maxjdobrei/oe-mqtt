#Maximilian Dobrei, Carleton University 101103400
#Last modified: August 5th 2022
#object oriented class desgined to receive packets from a tcp client and forward them to another tcp client

import sys
import socket

from rsa_ciphers_n_signatures import *

from Crypto.PublicKey import RSA

class Proxy:
    def __init__(self, host_addr, host_port, target_addr, debug):
        self.host_addr = host_addr                           #address to listen on
        self.host_port = host_port
        self.target_addr = target_addr                       #address to forward packets to
        self.debug = debug


        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host_addr, host_port))

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self.private_key = generate_key()
        self.public_key = self.private_key.public_key()

        self.correspondant = False                         #a boolean value that indicates if this proxy has successfully connected with the proxy at the other endpoint
        self.correspondant_PUB_KEY = None                 #public key that has to be given by the proxy at the other endpoint



    def initialize_connection():
        pass

    def send_data():
        pass


	#a function for the client endpoint to use to try and exchange keys with the proxy at the broker endpoint, if one exists
    def handshake(self):
        
		#must try and do key exchange with other endpoint for further communications.
        self.client_socket.sendall(self.public_key.exportKey("PEM"))
        response = self.client_socket.recv(3096)
        if self.debug:
            print(f"pubk = {response}")
        
        try:
            self.correspondant_PUB_KEY = RSA.import_key(response) #try and import the key. If it's not a valid key, an error will be thrown
        except:
            #this exception triggers another except clause found in initialize_connection(), implemented in the child classes
            raise Exception("Failed to properly exchange public keys with decryptin proxy. Tring to establish connection with Broker directly instead.")


    def start_client_endpoint(self):
        if self.debug:
            print("starting...")
        
        self.server_socket.listen()
        #loop until interrupted
        while True:
            conn, addr = self.server_socket.accept()
            
            if self.debug:
                    print(f"Connected by {addr}")
            
            #estiablish connection to the broker endpoint, if one exists. Otherwise, establish connection to the broker
            try:
                self.initialize_connection()
            except:
                print("Cannot establish connection to the broker endpoint or the broker itself. Ending this connection")
                continue

            with conn:
				#loop until the communication has ended
                while True:
                    data = conn.recv(3096)
					
                    if self.debug:
                        print(f"\ndata receieved = {data}\n")
                    
                    if not data:
                        break
					#forward the data to next step in communication
                    try:
                        self.send_data(conn, data)
                    except:
                        break
            
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  #create a new socket to use with next connection. bypasses having to wait for the socket to be done timing out

    def start_broker_endpoint(self):
        if self.debug:
            print("starting...")
        self.server_socket.listen()
        while True:
            self.correspondant = False
            conn, addr = self.server_socket.accept()
            
            if self.debug:
                    print(f"Connected by {addr}")

            with conn:
                #connected to by a client endpoint, key exchange has to happen
                pubk = conn.recv(3096)
                
                if self.debug:
                    print(f"pubk = {pubk}")

                try:
                    self.correspondant_PUB_KEY = RSA.import_key(pubk)
                    conn.sendall(self.public_key.exportKey("PEM")) #in response to receiving the other proxies public key, send our own
                    self.correspondant = True
                except:
                    print("Key exchange with the encryption proxy has failed, ending this communication")
                    continue
                 
                #setup connection to the broker
                try:
                    self.initialize_connection()
                except:
                    print("Cannot establish connection to the broker. Ending this communication")
                    continue
				
                #loop until the communication has ended
                while True:
                    data = conn.recv(3096)
                    
                    if self.debug:
                        print(f"\ndata received = {data}\n")
                    
                    if not data:
                        break
                    
                    try:
                        self.send_data(conn, data)
                    except:
                        break
            
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#object oriented class desgined to send packets on behalf of an MQTT publisher, to a proxy that listens on behalf of the broker.
#encrypt sensitives data before forwarding when possible
class PubEproxy(Proxy):

    def __init__(self, host_addr, target_addr, debug):
        super().__init__(host_addr, 1884, target_addr, debug)

    def initialize_connection(self):
        try: 
            self.client_socket.connect((self.target_addr, 1884))
            self.handshake()
            self.correspondant = True
        except:
            try: 
                self.client_socket.connect((self.target_addr, 1883))
            except:
                raise Exception("")

    def send_data(self, connection, packet):
        #if connected to other endpoint, and this packet contains the payload (is a publish packet in accordance with the MQTT scheme)
        if self.correspondant and packet.startswith(b'2'):
            ciphertext = encrypt_msg(self.correspondant_PUB_KEY, packet)
            signature = sign_msg(self.private_key, ciphertext)
            combined = ciphertext + b'=SIGNATURE=' +signature #add a custom tag between the ciphertext and signature. makes it easy to split on the other end
            self.client_socket.sendall(combined)
        
        elif packet.startswith(b'\xe0'):                     #if the packet is a disconnect packet, according to the MQTT scheme
            self.client_socket.sendall(packet)
            self.client_socket.close()
            return

        else:
            self.client_socket.sendall(packet)           #if not connected to the other proxy, just forward the packet.
        
        response = self.client_socket.recv(3096)
        if not response:
            
            if self.debug:
                print("No response.")
            
            self.client_socket.close()
            return
        
        #send the response back to the MQTT publisher
        connection.sendall(response)

#object oriented class desgined to receive packets on behalf of an MQTT broker. 
#decrypts the data if needed before forwarding to the MQTT broker
class PubDproxy(Proxy):

    def __init__(self, target_addr, debug):
        super().__init__(target_addr, 1884, target_addr, debug)

    def initialize_connection(self):
        try: 
            self.client_socket.connect((self.target_addr, 1883))
            if self.debug:
                print("established connection to broker\n")
        
        except:
            print("Cannot initialize connection to broker. Ending this communication")
            raise Exception()
    

    def send_data(self, connection, packet):
        #if we have a connection to the other endpoint, and the packet contains the custom signature indicating it has been encrypted
        if self.correspondant and (packet.find(b'=SIGNATURE=') != -1):
            
            disjoined = packet.split(b'=SIGNATURE=')
            ciphertext = disjoined[0]
            signature = disjoined[1]
            
            if self.debug:
                print("trying to verify...\n")
           
            if verify_msg(self.correspondant_PUB_KEY, ciphertext, signature):
                #signature has been validated, message is legitimate. do decryption
                if self.debug:
                    print("Verified.")
                original = decrypt_msg(self.private_key, ciphertext)
                if self.debug:
                    print(f"original message: {original}")
                self.client_socket.sendall(original)
            else:
                raise Exception("Digital signature is NOT valid. Ending this communication.")

        else:  #packet has not been encrypted, just forward it     
            self.client_socket.sendall(packet)
        
        response = self.client_socket.recv(3096)
        if not response:
            if self.debug:
                print("No response.")
            self.client_socket.close()
            return
        #send the response back to the client endpoint we received the packet from
        connection.sendall(response)

    def start_client_endpoint(self):
        if self.debug:
            print("starting...")
        
        self.server_socket.listen()
        #loop until interrupted
        while True:
            conn, addr = self.server_socket.accept()
            
            if self.debug:
                    print(f"Connected by {addr}")
            
            #estiablish connection to the broker endpoint, if one exists. Otherwise, establish connection to the broker
            try:
                self.initialize_connection()
            except:
                print("Cannot establish connection to the broker endpoint or the broker itself. Ending this connection")
                continue

            with conn:
				#loop until the communication has ended
                while True:
                    data = conn.recv(3096)
					
                    if self.debug:
                        print(f"\ndata receieved = {data}\n")
                    
                    if not data:
                        continue
					#forward the data to next step in communication
                    try:
                        self.send_data(conn, data)
                    except:
                        break
            
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  #create a new socket to use with next connection. bypasses having to wait for the socket to be done timing out


#object oriented class desgined to send packets to another proxy on behalf of an MQTT susbcriber,
#as well as decrypt packets that are sent from an encryption proxy on behalf of an MQTT broker
class SubDproxy(Proxy):

    def __init__(self, host_addr, target_addr, debug):
        super().__init__(host_addr, 1884, target_addr, debug)

    def initialize_connection(self):
        try: 
            self.client_socket.connect((self.target_addr, 1885))
            self.handshake()
            self.correspondant = True
        except:
            try: 
                self.client_socket.connect((self.target_addr, 1883))
            except:
                raise Exception()
                
    def send_data(self, connection, packet):
        #if we have a connection to the other endpoint, and the packet contains the custom signature indicating it has been encrypted   
        self.client_socket.sendall(packet)
        
        response = self.client_socket.recv(3096)
        if not response:
            if self.debug:
                print("No response.")
            self.client_socket.close()
            return
       
        if self.debug and self.correspondant:
            print(f"data from the encryption proxy: {response}")

        if self.correspondant and (response.find(b'=SIGNATURE=') != -1):
            
            disjoined = response.split(b'=SIGNATURE=')
            ciphertext = disjoined[0]
            signature = disjoined[1]
            
            if self.debug:
                print("trying to verify...")
           
            if verify_msg(self.correspondant_PUB_KEY, ciphertext, signature):
                #signature has been validated, message is legitimate. do decryption
                if self.debug:
                    print("Verified.")
                original = decrypt_msg(self.private_key, ciphertext)
                if self.debug:
                    print(f"original message: {original}")
                connection.sendall(original)
            else:
                raise Exception("Digital signature is NOT valid. Ending this communication.")
       
        #send the response back to the MQTT subscriber
        connection.sendall(response)

#object oriented class desgined to send packets on behalf of an MQTT broker, to another proxy that listens on behalf of an MQTT subscriber.
#encrypts sensitive data before forwarding packets when possible
class SubEproxy(Proxy):

    def __init__(self, target_addr, debug):
        super().__init__(target_addr, 1885, target_addr, debug)

    def initialize_connection(self):
        try: 
            self.client_socket.connect((self.target_addr, 1883))       
        except:
            raise Exception()
    

    def send_data(self, connection, packet):
        #if connected to other endpoint, and this packet contains the payload (is a publish packet in accordance with the MQTT scheme)
        self.client_socket.sendall(packet)          
        
        response = self.client_socket.recv(3096)
        if not response:
            
            if self.debug:
                print("No response.")
            
            self.client_socket.close()
            return
        
        if self.correspondant and response.startswith(b'2'):
            ciphertext = encrypt_msg(self.correspondant_PUB_KEY, response)
            signature = sign_msg(self.private_key, ciphertext)
            combined = ciphertext + b'=SIGNATURE=' +signature #add a custom tag between the ciphertext and signature. makes it easy to split on the other end
            connection.sendall(combined)
            return
        
        #send the response back to the client endpoint from which we've received this packet from
        connection.sendall(response)
    
    
