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
from Crypto.PublicKey import RSA        # To generate / import key
from Crypto.Cipher import PKCS1_OAEP    # To do padding stuff
from Crypto.Signature import pkcs1_15   # To sign packets
from Crypto.Hash import SHA256          # To create hashes 
#key = RSA.generate(4096)
#pen = pkcs1_15.new(key)
#hash = SHA256.new(data=b'ToBeHashedData')
#hashvalue = hash.hexdigest()
#signature = pen.sign(hash)
#
#
#publickey = key.publickey()
#publicpen = pkcs1_15.new(publickey)
#try:
#   publicpen.verify(hash, signature)
#except:
#   print("invalid signature!")
#

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
            config.read(basepath + '/config.ini') # Why was this missing? # And why is a duplicate of it at the very bottom? Also why does it stop working if I remove the duplicate?
            safepath = os.path.realpath(basepath + "/../") + "/"

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

            #load private key
            privatekey_path = "./conmanager/keys/{}.priv".format(own_name)
            privatekey_file_exists = os.path.isfile(privatekey_path)
            if privatekey_file_exists:
                privatekey_file = open(privatekey_path, "r")
                key_private = self.importKey(privatekey_file.read())
                key_public = key_private[0].publickey()#self.getKey("publickey")
            else:
                privatekey_file = open(privatekey_path, "w")
                key_private = RSA.generate(4096)
                key_public = key_private[0].publickey()
                privatekey_file.write(str(key_private.exportKey(), "utf8").replace("\n", "\\n"))

            privatekey_file.close()

            
            update_lastrequested = datetime.datetime.now() #datetime.datetime.fromtimestamp(pathlib.Path(basepath + "/keychain.ini").stat().st_mtime)
            privatekey_lastupdated = datetime.datetime.fromtimestamp(pathlib.Path(privatekey_path).stat().st_mtime)
            try:
                admin_name = config["config"]["admin"]
            except KeyError:
                admin_name = False
            
            standardport = config["config"]["port"] # Can I haz customisation? ó.ò  Ò.Ó NO! (Maybe later.)

            
            
            
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
            listensocket.bind(('', int(standardport)))
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
                #params:
                #[0] = action (not important)
                #[1] = target_device
                #[2] = target_module
                #[3] = data
                #[4] = packet_id
                if action == "listdevices":
                    #print("conmanager: Gonna list the devices!")
                    temp_return = []
                    for connection in sockets:
                        if connection[0] != False:
                            temp_return.append(connection[3])
                    queue_out.put((originator, ("devicelist", temp_return)))
                elif action == "senddata":
                    #print("conmanager: Gonna send the data!")
                    for connection in sockets:
                        #connection: [socket, (ip, 42069), (key_RSA, key_PKCS1OAEP, key_PKCS1_15), device_name, recvbuffer]
                        if connection[3] == params[1] or params[1] == "broadcast":
                            #print("Found the connection to send to!")
                            packet_hasID = len(params) >= 5
                            if packet_hasID:
                                packet_id = params[4]
                            else:
                                packet_id = 0
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
                            if type(packet_id) != bytes:
                                packet_id = packet_id.to_bytes(4, 'big') # max packet_id = 4294967295. Good enough for 136,099300834 years @ 1 packet/s.
                            orig_name = bytes(read[0], "utf8")
                            orig_namelen = bytes([len(orig_name)])
                            target_name = bytes(params[2], "utf8")
                            target_namelen = bytes([len(target_name)])
                            data_len = len(params[3]).to_bytes(4, 'big')
                            data = params[3]
                            #Sign data
                            hash = SHA256.new(data=data)
                            signature = key_private[2].sign(hash)
                            signature_len = len(signature).to_bytes(2, 'big')
                            #print("DEBUG: conmanager: signature: {}. signature_len: {}".format(hash, connection[2]))
                            #Compile packet
                            try:
                                packet = packet_id + orig_namelen + orig_name + target_namelen + target_name + signature_len + signature + data_len + data
                            except Exception as msg:
                                queue_out.put((originator, ("sentdata", (False, "data must be bytes"))))
                                errout("CONMANAGER: Unable to finalize the string to be encrypted and sent: {}".format(msg))
                                continue
                            #print("DEBUG: conmanager: packet: {}".format(packet))
                            try:
                                packet_size = 128
                                while len(packet):
                                    enc = self.encrypt(packet[0:packet_size], connection[2]) # Padding and stuff fucks up the nice 128 size...
                                    #enc = self.encrypt(packet[0:86], connection[2]) # Padding and stuff fucks up the nice 128 size...
                                    # 95 still too long # 86 seems to be the maximum size.
                                    # 64 works. I'ma leave it at this for now. ~~Todo
                                    connection[0].sendall(enc)
                                    packet = packet[packet_size:]
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
                    print("conmanager: Unknown action: {}. Debug: {}".format(action, read))
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
            for i in range(len(sockets)):
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
                            temp_recv = connection[0].recv(512)
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
                            #packet = packet_id + orig_namelen + orig_name + target_namelen + target_name + signature_len + signature + data_len + data
                            #       4 byte, 1 byte, oname, 1 byte, tname, 1 byte, signature, 4 byte, data
                            #example packet: b'1234\x04name\x05tname\x00\x09signature\x00\x00\x00\x04data'
                            #print("DEBUG: conmanager: sockets[i][4]: {}".format(sockets[i][4]))
                            #print("DEBUG: conmanager: -----")
                            packet_id = sockets[i][4][0:4]
                            #print(packet_id)
                            orig_modnamelen = sockets[i][4][4]
                            #print(orig_modnamelen)
                            orig_modname = (sockets[i][4])[5:orig_modnamelen + 5]
                            #print(orig_modname)
                            target_modnamelen = sockets[i][4][5 + orig_modnamelen]
                            #print(target_modnamelen)
                            target_modname = (sockets[i][4])[6 + orig_modnamelen:target_modnamelen + 6 + orig_modnamelen]
                            #print(target_modname)
                            signature_len = int.from_bytes((sockets[i][4])[target_modnamelen + 6 + orig_modnamelen: target_modnamelen + 8 + orig_modnamelen], 'big')
                            #print(signature_len)
                            signature = (sockets[i][4])[target_modnamelen + 8 + orig_modnamelen: target_modnamelen + 8 + orig_modnamelen + signature_len]
                            #print(signature)
                            data_len = int.from_bytes(sockets[i][4][target_modnamelen + 8 + orig_modnamelen + signature_len:target_modnamelen + 12 + orig_modnamelen + signature_len], 'big')   #~~Todo: Possible bug: b'11' converts to 11, not 12593
                            #print(data_len)
                            data = sockets[i][4][target_modnamelen + 12 + orig_modnamelen + signature_len:target_modnamelen + 12 + orig_modnamelen + data_len + signature_len]
                            #print(data)
                            #print("-----")
                            #print("DEBUG: conmanager: packet_id: {}\norig_modnamelen:{}\norig_modname:{}\ntarget_modnamelen:{}\ntarget_modname:{}\nsignature_len:{}\nsignature:{}\ndata_len:{}\ndata:{}".format(packet_id, orig_modnamelen, orig_modname, target_modnamelen, target_modname, signature_len, signature, data_len, data))
                        except Exception as msg:
                            errout("CONMANAGER: unable to receive packet: {}".format(msg))
                            break
                        if len(data) < data_len or len(signature) < signature_len or len(target_modname) < target_modnamelen or len(orig_modname) < orig_modnamelen:
                            #if the packet is fragmented, do not proceed!
                            #print("DEBUG: conmanager: fragmented packet.")
                            #time.sleep(0.1)
                            break
                        #print("recvd something!")
                        #print(sockets[i][4])
                        hash = SHA256.new(data=data)
                        try:
                            connection[2][2].verify(hash, signature)
                            print("DEBUG: conmanager: signature verified!")
                            queue_out.put((target_modname.decode("utf-8"), ("recvdata", connection[3], orig_modname.decode("utf-8"), data)))
                        except Exception as msg:
                            errout("CONMANAGER: {}. target_modname: {}, orig_modname: {}, orig_device: {}, data: {}".format(msg, target_modname, orig_modname, connection[3], data))
                        sockets[i][4] = sockets[i][4][target_modnamelen + 12 + orig_modnamelen + data_len + signature_len:]

    
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
        return (keyRSA, keyPKCS1_OAEP, pkcs1_15.new(keyRSA))

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

    def getKey(self, name):
        global config
        publickey_file = open("./conmanager/keys/{}.pub".format(name), "r")
        key = self.importKey(publickey_file.read())
        publickey_file.close()
        return key
    
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
    config.read(basepath + '/config.ini')
    
       
mainclass = conmanager()
