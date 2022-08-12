import os
import sys
import time
import socket
import datetime
import configparser
import hashlib
import pathlib
import atexit
from typing import AbstractSet # To close the TCP listen socket on exit
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
sys.path.append("..")
from log.log import *

class conmanager(object):

    def __init__(self):
        global config, basepath, key_private, key_public, sockets, own_ip, own_name, listensocket, standardport
        global update_lastrequested, privatekey_lastupdated, admin_name, safepath
        try:
            #init logging.
            initLog("conmanager")
            #load config info
            config = configparser.ConfigParser()
            basepath = os.path.dirname(os.path.realpath(__file__))
            config.read(basepath + '/keychain.ini') # Why was this missing? # And why is a duplicate of it at the very bottom? Also why does it stop working if I remove the duplicate?
            safepath = os.path.realpath(basepath + "/../") + "/"
            #load keychain
            privatekey_file_exists = os.path.isfile("./conmanager/privatekey")
            if privatekey_file_exists:
                privatekey_file = open("./conmanager/privatekey", "r")
                key_private = self.importKey(privatekey_file.read())
                key_public = key_private[0].publickey()#self.getKey("publickey")
            else:
                privatekey_file = open("./conmanager/privatekey", "w")
                key_private = RSA.generate(1024)
                key_public = key_private[0].publickey()
                privatekey_file.write(str(key_private.exportKey(), "utf8").replace("\n", "\\n"))

            privatekey_file.close()

            
            update_lastrequested = datetime.datetime.fromtimestamp(pathlib.Path(basepath + "/keychain.ini").stat().st_mtime)
            privatekey_lastupdated = datetime.datetime.fromtimestamp(pathlib.Path(basepath + "/privatekey").stat().st_mtime)
            try:
                admin_name = config["config"]["admin"]
            except KeyError:
                admin_name = False
            
            standardport = 42069 # Can I haz customisation? ó.ò  Ò.Ó NO! (Maybe later.)

            # get own IP
            tempsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            tempsock.connect(("8.8.8.8", 80))
            own_ip = tempsock.getsockname()[0]
            tempsock.close()
            print("conmanager info: own_ip: {}".format(own_ip))
            
            # find own name
            try:
                own_name = config["names"][own_ip]
            except Exception as msg:
                errout("CONMANAGER: startup error: Unable to find any name for this machine. Check key authority and/or device's ip settings. Full error: {}".format(msg))
                raise
            print("conmanager info: own_name: {}".format(own_name))
            #found = False
            #for index, ip in enumerate(config["names"]):
            #    print("Debug20210528:01 - 4.2: {} and {}".format(index, ip))
            #    if ip == own_ip:
            #        own_name = config["names"][own_ip] # I could have done it without a loop
            #        found = True
            #print("Debug20210528:01 - 5")
            #if not found: # There has to be a better solution;
            #    errout("CONMANAGER: startup error: Unable to find any name for this machine. Check key authority and/or network settings")


            '''
            Connections contain:
                Socket, (IP, Port), (publicKeyRSA, publicKeyPKCS1_OAEP), name, recvBuffer, stateAuthentication
                Socket, (IP, Port), (publicKeyRSA, publicKeyPKCS1_OAEP), name, recvBuffer

                stateAuthentication:
                    -1 = pubkey deviates from database entry; Check error logs for more info!
                     0 = No pubkey recvd; no traffic possible
                     1 = pubkey recvd; traffic possible
                    
                    
            '''
            sockets = []
            #initialize server socket
            listensocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            listensocket.bind(('', standardport))
            listensocket.listen(10)
            listensocket.setblocking(0) # Idk. Felt cute. Might rewrite later IN A WAY A SANE BEING WOULD ACTUALLY DO IT! (i.e. no busy-idle, etc.)
            listensocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)#debug #? To debug what? TELL ME, PAST SELF!!!
            atexit.register(self.closeListenSocket)
            #connect to all devices in the network
            for ip in config["names"]:
                if ip == own_ip:
                    continue
                
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    self.connect(sock, (ip, 42069))
                    log("conmanager: Conncted to {}".format(sock))
                except:
                    log("conmanager: Unable to connect to {}".format(ip))
                    sock.close()
                    sock = False
                try:
                    temp_key = self.getKey(config["names"][ip])
                except Exception as msg:
                    temp_key = False
                    errout("CONMANAGER: Unable to load key for {}: {}. Please check if it is correct.".format(ip, msg))
                temp_array = [sock, (ip, 42069), temp_key, config["names"][ip], b'']
                sockets.append(temp_array)
        except Exception as msg: # GOTTA CATCH 'EM ALL
            errout("CONMANAGER: CRITICAL startup error: {}".format(msg))
            raise # And release 'em all again :/ # Why? Because it's a critical error. The module didn't properly start.

    def initcore(self, out_q, in_q): # Rename initcore to something more meaningfull... Maybe passQueues?
        global queue_out, queue_in
        queue_out = out_q
        queue_in = in_q

    def run(self):
        global sockets, update_lastrequested
        log("conmanager has started!")
        print("update_lastrequested {}".format((datetime.datetime.now() - update_lastrequested).seconds))
        print("admin_name {}".format(admin_name))
        
        while True:
            #print("DEBUG: LOOP")
            time.sleep(0.01) # How to reduce CPU utilization: 1. utilize CPU less. You can thank me later.
            now = datetime.datetime.now()
            if admin_name and (now - update_lastrequested).seconds > 60: # Feel free to adjust the amount of seconds.
                print("Updating the keychain")
                queue_out.put(("conmanager", ("senddata", admin_name, "admin", b'requestfile conmanager/keychain.ini'))) # Sending myself mail. Relevant Mr Bean: https://www.youtube.com/watch?v=6Wqn5IaSub8
                update_lastrequested = now
            if not queue_in.empty():
                read = queue_in.get()
                print("conmanager has received: {}".format(read))
                originator = read[0]
                if type(read[1]) == list or type(read[1]) == tuple:
                    action = read[1][0]
                else:
                    action = read[1]
                params = read[1] #Yes, when no parameters are passed, params does equal action.
                if action == "listdevices":
                    #print("conmanager: Gonna list the devices!")
                    temp_return = []
                    for connection in sockets:
                        if connection[0] != False:
                            temp_return.append(connection[3])
                    queue_out.put((originator, ("devicelist", temp_return)))
                elif action == "senddata": #Performance issue: Takes 2-6 seconds for total execution
                    #print("conmanager: Gonna send the data!")
                    for connection in sockets:
                        if connection[3] == params[1] or params[1] == "broadcast":
                            #print("Found the connection to send to!")
                            packet_hasID = len(params) >= 5
                            if packet_hasID: packet_id = params[4]
                            if connection[0] == False: #If no socket connected towards destination
                                if packet_hasID:
                                    queue_out.put((originator, ("sentdata", (False, "No socket connected towards destination", connection[1], connection[3]), packet_id)))
                                else:
                                    queue_out.put((originator, ("sentdata", (False, "No socket connected towards destination", connection[1], connection[3]))))
                                continue

                            if type(connection[2]) is bool:
                                if packet_hasID:
                                    queue_out.put((originator, ("sentdata", (False, "Public key not loaded", connection[1], connection[3]), packet_id)))
                                else:
                                    queue_out.put((originator, ("sentdata", (False, "Public key not loaded", connection[1], connection[3]))))
                                continue
                            #Calculate all byte lengths and convert stuff to bytes to be glued together into a packet.
                            orig_name = bytes(read[0], "utf8")
                            orig_namelen = bytes([len(orig_name)])
                            target_name = bytes(params[2], "utf8")
                            target_namelen = bytes([len(target_name)])
                            data_len = len(params[3]).to_bytes(4, 'big') 
                            data = params[3]
                            try:
                                data = orig_namelen + orig_name + target_namelen + target_name + data_len + data
                            except Exception as msg:
                                queue_out.put((originator, ("sentdata", (False, "data must be bytes"))))
                                errout("CONMANAGER: Unable to finalize the string to be encrypted and sent: {}".format(msg))
                                continue
                            try:
                                while len(data):
                                    enc = self.encrypt(data[0:64], connection[2]) # Padding and stuff fucks up the nice 128 size...
                                    #enc = self.encrypt(data[0:86], connection[2]) # Padding and stuff fucks up the nice 128 size...
                                    # 95 still too long # 86 seems to be the maximum size.
                                    # 64 works. I'ma leave it at this for now. ~~Todo
                                    connection[0].sendall(enc)
                                    data = data[64:]
                                #print("Sent data to {}".format(connection))
                                if packet_hasID:
                                    queue_out.put((originator, ("sentdata", (True, False, connection[1], connection[3]), packet_id)))
                            except Exception as msg:
                                #print("Some error happened while sending data:")
                                #print(connection[2])
                                if packet_hasID:
                                    queue_out.put((originator, ("sentdata", (False, "Unable to send data to destination: {}".format(msg), connection[1], connection[3]), packet_id)))
                                else:
                                    queue_out.put((originator, ("sentdata", (False, "Unable to send data to destination: {}".format(msg), connection[1], connection[3]))))
                elif action == "recvdata":
                    DEBUG_time = time.time()
                    data = params[3]
                    if data[0:10] == b"updatefile":
                        #don't forget to check wether it's really coming from someone who is "admin"
                        #print("Ok, I'm going to have to update a file.")
                        if not (admin_name == params[1] and params[2] == "admin"):
                            errout("CONMANAGER: updatefile request sent from unauthorised source: origDevice: {} origModule: {} data: {}".format(params[1], params[2], data))
                            continue
                        file_namelen = data[11]
                        file_path = str(data[12:12 + file_namelen], "utf-8")
                        file_size = int.from_bytes(data[12 + file_namelen: 16 + file_namelen], 'big')
                        file_data = data[16 + file_namelen: 16 + file_namelen + file_size]

                        #print("Ok the file has this info: {} {} {}".format(file_namelen, file_path, file_size))
                        
                        if os.path.commonprefix((os.path.realpath(file_path), safepath)) != safepath:
                            errout("CONMANAGER: directory traversal attack prevented: origDevice {}; origModule {}; data {}".format(params[1], params[2], data))
                        
                        if not os.path.isfile(file_path):
                            #print("Great. The file actually exists")
                            pass
                        file_handle = open(safepath + file_path, "wb")
                        file_handle.write(file_data)
                        file_handle.close()
                        #print("File written")
                    elif data[0:10] == b"deletefile":
                        #don't forget to check wether it's really coming from someone who is "admin" ~~Todo
                        pass
                    else:
                        print("I don't know what to do with {}".format(data))
                        #don't forget to check wether it's really coming from someone who is "admin" ~~Todo
                        pass
                    print("DEBUG recvdata: {}".format(time.time() - DEBUG_time))
                else:
                    print("conmanager: Unknown action: {}".format(action))
                queue_in.task_done()
                
            try:
                DEBUG_time = time.time()
                #listensocket.setblocking(True)
                accept_socket, accept_address  = listensocket.accept()
                accept_socket.setblocking(0)
                print("NEW CONNECTION!!!")
                #print(accept_socket)
                connection_found = False
                for connection in sockets:
                    if connection[1][0] == accept_address[0] and type(connection[0]) != socket.socket: # if ip matches and not already connected
                        connection[0] = accept_socket
                        connection[1] = accept_address
                        connection_found = True
                    elif connection[1][0] == accept_address[0] and type(connection[0]) == socket.socket: # if ip matches and is already connected
                        errout("CONMANAGER: Already connected client tried to connect again. {}".format(accept_address))
                        if accept_address[1] == standardport:
                            connection[0].close()
                            connection[0] = accept_socket
                            connection[1] = accept_address
                            connection_found = True
                if not connection_found:
                    errout("CONMANAGER: Unknown connection. {}, {}".format(accept_address, accept_socket))
                print("DEBUG accept connections: {}".format(time.time() - DEBUG_time))
            except Exception as msg: # Maybe a more explicit exception catch? ~~Todo
                pass
            DEBUG_time = time.time()
            for i in range(len(sockets)): #Performance issue: Can sometimes take 11 seconds.
                connection = sockets[i] # Remind me tomorrow, when I remember why the fuck I made it this way # I still don't know why and can't be bothered to change it yet.
                if type(connection[0]) != socket.socket:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    try:
                        self.connect(connection[0], connection[1])
                        print(connection[0])
                    except:
                        sock.close()
                    pass
                else:
                    while True: # (Try to) fill up the recvBuffer with received data. (No reading out yet. Only filling up.)
                        # Negative implication of the while loop: flooding client with data could (1.) "trap" client in loop, and (2.) possibly cause RAM to overflow, crashing the client?
                        # (Would be interested to try out the attack's effectiveness.)
                        # Possible fix: timeout?
                        try:
                            temp_recv = connection[0].recv(128)
                            if not len(temp_recv): # Caution: This is not here for the reason you think! See comment on "BaseException" for clarity.
                                raise socket.timeout
                            
                            sockets[i][4] = sockets[i][4] + self.decrypt(temp_recv)
                        except socket.timeout:
                            print("SOCKET TIMED OUT!!!")
                            sockets[i][0] = False
                            break
                        except BaseException as msg: # This here is triggered when no data on connection[0] socket. [Errno 11] Resource temporarily unavailable
                            break # If no data: exit the while loop

                    while len(sockets[i][4]): # Read out recvBuffer
                        try:
                            orig_modnamelen = sockets[i][4][0]
                            orig_modname = (sockets[i][4])[1:orig_modnamelen + 1]
                            target_modnamelen = sockets[i][4][1 + orig_modnamelen]
                            target_modname = (sockets[i][4])[2 + orig_modnamelen:target_modnamelen + 2 + orig_modnamelen]
                            data_len = int.from_bytes(sockets[i][4][target_modnamelen + 2 + orig_modnamelen:target_modnamelen + 6 + orig_modnamelen], 'big')   #~~Todo: Possible bug: b'11' converts to 11, not 12593
                            data = sockets[i][4][target_modnamelen + 6 + orig_modnamelen:target_modnamelen + 6 + orig_modnamelen + data_len]
                        except:
                            break
                        if len(data) < data_len:
                            break
                        #print("recvd something!")
                        #print(sockets[i][4])
                        queue_out.put((target_modname.decode("utf-8"), ("recvdata", connection[3], orig_modname.decode("utf-8"), data)))
                        sockets[i][4] = sockets[i][4][target_modnamelen + 6 + orig_modnamelen + data_len:]
    
    def connect(self, socket, ip):
        try:
            socket.connect(ip)
        except:
            raise Exception
        socket.setblocking(0) # No. This has to be done a different way with no busy idle, etc. ~~Todo
    
    def importKey(self, key):
        if key[0:2] == "b'":
            key = bytes(key[2:-2], "utf-8").replace(b'\\n', b'\n')
        else:
            key = bytes(key, "utf-8").replace(b'\\n', b'\n')
        keyRSA = RSA.importKey(key)
        keyPKCS1_OAEP = PKCS1_OAEP.new(keyRSA)
        print("DEBUG importKey: imported a key {}".format(keyPKCS1_OAEP))
        return (keyRSA, keyPKCS1_OAEP)

   #def importKey(self, key): #
   #     if key[0:2] == "b'":
   #         key = bytes(key[2:-2], "utf-8").replace(b'\\n', b'\n')
   #     else:
   #         key = bytes(key, "utf-8").replace(b'\\n', b'\n')
   #     return RSA.importKey(key)

    def saveIni(self):
        global basepath, config
        temp_file = open(basepath + "/keychain.ini", "w")
        with temp_file as configfile:
            config.write(configfile)

    def getKey(self, ip):
        global config
        return self.importKey(self.config['keychain'][ip])
    
    def exportKey(self, key):
        return key.exportKey()
    
    def decrypt(self, data):
        global key_private
        #return PKCS1_OAEP.new(key_private).decrypt(data)
        return key_private[1].decrypt(data)
    
    def encrypt(self, data, key):
        #return PKCS1_OAEP.new(key).encrypt(data) # Removed PKCS1_OAEP.new for performance reasons.
        return key[1].encrypt(data)

    def closeListenSocket(self):
        global listensocket
        print("conmanager [function closeListenSocket]: Closing listen socket.")
        listensocket.close()
        print("conmanager [function closeListenSocket]: Closed listen socket.")
    
    config = configparser.ConfigParser()
    basepath = os.path.dirname(os.path.realpath(__file__))
    config.read(basepath + '/keychain.ini')
    
       
mainclass = conmanager()
