import os
import sys
import time
import socket
import datetime
import configparser
import hashlib
import pathlib
import atexit # To close the TCP listen socket on exit
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
sys.path.append("..")
from log.log import *

class conmanager(object):

    def __init__(self):
        global config, basepath, hPrivKey, hPubKey, aConnections, sOwnIP, sOwnName, sockListen, standardport
        global updateLastRequested, privatekeyLastUpdated, adminName, safepath
        try:
            #load config info
            config = configparser.ConfigParser()
            basepath = os.path.dirname(os.path.realpath(__file__))
            config.read(basepath + '/keychain.ini') # Why was this missing? # And why is a duplicate of it at the very bottom? Also why does it stop working if I remove the duplicate?
            safepath = os.path.realpath(basepath + "/../") + "/"
            #load keychain
            privatekeyFile_bExists = os.path.isfile("./conmanager/privatekey")
            if privatekeyFile_bExists:
                privatekeyFile = open("./conmanager/privatekey", "r")
                hPrivKey = self.importKey(privatekeyFile.read())
                hPubKey = hPrivKey.publickey()#self.getKey("publickey")
            else:
                privatekeyFile = open("./conmanager/privatekey", "w")
                hPrivKey = RSA.generate(1024)
                hPubKey = hPrivKey.publickey()
                privatekeyFile.write(str(hPrivKey.exportKey(), "utf8").replace("\n", "\\n"))

            privatekeyFile.close()

            
            updateLastRequested = datetime.datetime.fromtimestamp(pathlib.Path(basepath + "/keychain.ini").stat().st_mtime)
            privatekeyLastUpdated = datetime.datetime.fromtimestamp(pathlib.Path(basepath + "/privatekey").stat().st_mtime)
            try:
                adminName = config["config"]["admin"]
            except KeyError:
                adminName = False
            
            standardport = 42069 # Can I haz customisation? ó.ò  Ò.Ó NO! (Maybe later.)

            # get own IP
            tempsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            tempsock.connect(("8.8.8.8", 80))
            sOwnIP = tempsock.getsockname()[0]
            tempsock.close()
            print("conmanager info: sOwnIP: {}".format(sOwnIP))
            
            # find own name
            try:
                sOwnName = config["names"][sOwnIP]
            except Exception as msg:
                errout("conmanager startup error: Unable to find any name for this machine. Check key authority and/or device's ip settings. Full error: {}".format(msg))
                raise
            print("conmanager info: sOwnName: {}".format(sOwnName))
            #bFound = False
            #for index, ip in enumerate(config["names"]):
            #    print("Debug20210528:01 - 4.2: {} and {}".format(index, ip))
            #    if ip == sOwnIP:
            #        sOwnName = config["names"][sOwnIP] # I could have done it without a loop
            #        bFound = True
            #print("Debug20210528:01 - 5")
            #if not bFound: # There has to be a better solution;
            #    errout("conmanager startup error: Unable to find any name for this machine. Check key authority and/or network settings")


            '''
            Connections contain:
                Socket, (IP, Port), hPublicKey, name, recvBuffer, stateAuthentication
                Socket, (IP, Port), hPublicKey, name, recvBuffer

                stateAuthentication:
                    -1 = pubkey deviates from database entry; Check error logs for more info!
                     0 = No pubkey recvd; no traffic possible
                     1 = pubkey recvd; traffic possible
                    
                    
            '''
            aConnections = []
            #initialize server socket
            sockListen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sockListen.bind(('', standardport))
            sockListen.listen(10)
            sockListen.setblocking(0) # Idk. Felt cute. Might rewrite later IN A WAY A SANE BEING WOULD ACTUALLY DO IT! (i.e. no busy-idle, etc.)
            sockListen.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)#debug #? To debug what? TELL ME, PAST SELF!!!
            atexit.register(self.closeListenSocket)
            #connect to all devices in the network
            for ip in config["names"]:
                if ip == sOwnIP:
                    continue
                
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    self.connect(sock, (ip, 42069))
                    print("Conncted to:")
                    print(sock)
                except:
                    print("Unable to connect to:")
                    print(ip)
                    sock.close()
                    sock = False
                try:
                    tempKey = self.getKey(config["names"][ip])
                except Exception as msg:
                    tempKey = False
                aTemp = [sock, (ip, 42069), tempKey, config["names"][ip], b'']
                aConnections.append(aTemp)
        except Exception as msg: # GOTTA CATCH 'EM ALL
            errout("conmanager CRITICAL startup error: {}".format(msg))
            raise # And release 'em all again :/

    def initcore(self, pOutQueue, pInQueue): # Rename initcore to something more meaningfull... Maybe passQueues?
        global outQueue, inQueue
        outQueue = pOutQueue
        inQueue = pInQueue

    def run(self):
        global aConnections, updateLastRequested
        log("Conmanager has started!")
        print("updateLastRequested {}".format((datetime.datetime.now() - updateLastRequested).seconds))
        print("adminName {}".format(adminName))
        while True:
            time.sleep(0.01)
            now = datetime.datetime.now()
            if adminName and (now - updateLastRequested).seconds > 60: # Feel free to adjust the amound of seconds.
                print("Updating the keychain")
                outQueue.put(("conmanager", ("senddata", adminName, "admin", b'requestfile conmanager/keychain.ini'))) # Sending myself mail. Relevant Mr Bean: https://www.youtube.com/watch?v=6Wqn5IaSub8
                updateLastRequested = now
            
            if not inQueue.empty():
                read = inQueue.get()
                print("CONMANAGER has received: {}".format(read))
                originator = read[0]
                if type(read[1]) == list or type(read[1]) == tuple:
                    action = read[1][0]
                else:
                    action = read[1]
                if action == "listdevices":
                    #print("Conmanager: Gonna list the devices!")
                    aReturn = []
                    for connection in aConnections:
                        if connection[0] != False:
                            aReturn.append(connection[3])
                    outQueue.put((originator, ("devicelist", aReturn)))
                elif action == "senddata":
                    #print("Conmanager: Gonna send the data!")
                    for connection in aConnections:
                        if connection[3] == read[1][1] or read[1][1] == "broadcast":
                            #print("Found the connection to send to!")
                            bPacket = len(read[1]) >= 5
                            if bPacket: packetID = read[1][4]
                            if connection[0] == False:
                                #print("No connected socket etc. :{}".format(connection))
                                #print(connection)
                                if bPacket:
                                    outQueue.put((originator, ("sentdata", (False, "No socket connected towards destination", connection[1], connection[3]), packetID)))
                                else:
                                    outQueue.put((originator, ("sentdata", (False, "No socket connected towards destination", connection[1], connection[3]))))
                                continue
                            #print("And it's alive!")
                            sOrigName = bytes(read[0], "utf8")
                            iOrigNameLen = bytes([len(sOrigName)])
                            sTargetName = bytes(read[1][2], "utf8")
                            iTargetNameLen = bytes([len(sTargetName)])
                            iDataLen = len(read[1][3]).to_bytes(4, 'big')
                            sData = read[1][3]
                            try:
                                sData = iOrigNameLen + sOrigName + iTargetNameLen + sTargetName + iDataLen + sData
                            except Exception as msg:
                                outQueue.put((originator, ("sentdata", (False, "data must be bytes"))))
                                errout("conmanager: Unable to finalize the string to be encrypted and sent: {}".format(msg))
                                continue
                            try:
                                while len(sData):
                                    enc = self.encrypt(sData[0:64], connection[2]) # Padding and shit fucks up the nice 128 size... 
                                    # 95 still too long
                                    # 64 works. I'ma leave it at this for now. ~~Todo
                                    connection[0].sendall(enc)
                                    sData = sData[64:]
                                print("Sent data to {}".format(connection))
                                if bPacket:
                                    outQueue.put((originator, ("sentdata", (True, False, connection[1], connection[3]), packetID)))
                            except Exception as msg:
                                #print("Some error happened while sending data:")
                                #print(connection[2])
                                if bPacket:
                                    outQueue.put((originator, ("sentdata", (False, "Unable to send data to destination: {}".format(msg), connection[1], connection[3]), packetID)))
                                else:
                                    outQueue.put((originator, ("sentdata", (False, "Unable to send data to destination: {}".format(msg), connection[1], connection[3]))))
                                
                elif action == "recvdata":
                    data = read[1][3]
                    if data[0:10] == b"updatefile":
                        #don't forget to check wether it's really coming from someone who is "admin"
                        print("Ok, I'm going to have to update a file.")
                        if not (adminName == read[1][1] and read[1][2] == "admin"):
                            errout("conmanager: updatefile request sent from unauthorised source: origDevice: {} origModule: {} data: {}".format(read[1][1], read[1][2], data))
                            continue
                        iFilenameLen = data[11]
                        sFilePath = str(data[12:12 + iFilenameLen], "utf-8")
                        iFileSize = int.from_bytes(data[12 + iFilenameLen: 16 + iFilenameLen], 'big')
                        sFile = data[16 + iFilenameLen: 16 + iFilenameLen + iFileSize]

                        print("Ok the file has this info: {} {} {}".format(iFilenameLen, sFilePath, iFileSize))
                        
                        if os.path.commonprefix((os.path.realpath(sFilePath), safepath)) != safepath:
                            errout("conmanager: directory traversal attack prevented: origDevice {}; origModule {}; data {}".format(read[1][1], read[1][2], data))
                        
                        if not os.path.isfile(sFilePath):
                            print("Great. The file actually exists")
                            pass
                        hFile = open(safepath + sFilePath, "wb")
                        hFile.write(sFile)
                        hFile.close()
                        print("File written")
                    elif data[0:10] == b"deletefile":
                        #don't forget to check wether it's really coming from someone who is "admin"
                        pass
                    else:
                        print("I don't know what to do with {}".format(data))
                        #don't forget to check wether it's really coming from someone who is "admin"
                        pass
                else:
                    print("Conmanager: Unknown action: {}".format(action))
                inQueue.task_done()
            try:
                #sockListen.setblocking(True)
                hCon, aAddr  = sockListen.accept()
                hCon.setblocking(0)
                print("NEW CONNECTION!!!")
                #print(hCon)
                bFound = False
                for connection in aConnections:
                    if connection[1][0] == aAddr[0] and type(connection[0]) != socket.socket: # if ip matches and not already connected
                        connection[0] = hCon
                        connection[1] = aAddr
                        bFound = True
                    elif connection[1][0] == aAddr[0] and type(connection[0]) == socket.socket: # if ip matches and is already connected
                        errout("conmanager: Already connected client tried to connect again. {}".format(aAddr))
                        if aAddr[1] == standardport:
                            connection[0].close()
                            connection[0] = hCon
                            connection[1] = aAddr
                            bFound = True
                if not bFound:
                    errout("conmanager: Unknown connection. {}, {}".format(aAddr, hCon))
            except Exception as msg: # Maybe a more explicit exception catch? ~~Todo
                pass
            for i in range(len(aConnections)):
                connection = aConnections[i] # Remind me tomorrow, when I remember why the fuck I made it this way # I still don't know why and can't yet be bothered to change it.
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
                            sTemp = connection[0].recv(128)
                            if not len(sTemp): # Caution: This is not here for the reason you think! See comment on "BaseException" for clarity.
                                raise socket.timeout
                            
                            aConnections[i][4] = aConnections[i][4] + self.decrypt(sTemp)
                        except socket.timeout:
                            print("SOCKET TIMED OUT!!!")
                            aConnections[i][0] = False
                            break
                        except BaseException as msg: # This here is triggered when no data on connection[0] socket. [Errno 11] Resource temporarily unavailable
                            break # If no data: exit the while loop

                    while len(aConnections[i][4]): # Read out recvBuffer
                        iOrigModNameLen = aConnections[i][4][0]
                        sOrigModName = (aConnections[i][4])[1:iOrigModNameLen + 1]
                        iTargetModNameLen = aConnections[i][4][1 + iOrigModNameLen]
                        sTargetModName = (aConnections[i][4])[2 + iOrigModNameLen:iTargetModNameLen + 2 + iOrigModNameLen]
                        iDataLen = int.from_bytes(aConnections[i][4][iTargetModNameLen + 2 + iOrigModNameLen:iTargetModNameLen + 6 + iOrigModNameLen], 'big')   #~~Todo: Possible bug: b'11' converts to 11, not 12593
                        sData = aConnections[i][4][iTargetModNameLen + 6 + iOrigModNameLen:iTargetModNameLen + 6 + iOrigModNameLen + iDataLen]
                        
                        if len(sData) < iDataLen:
                            break
                        print("recvd something!")
                        print(aConnections[i][4])
                        outQueue.put((sTargetModName.decode("utf-8"), ("recvdata", connection[3], sOrigModName.decode("utf-8"), sData)))
                        aConnections[i][4] = aConnections[i][4][iTargetModNameLen + 6 + iOrigModNameLen + iDataLen:]
                                                                
    def connect(self, pSock, aIP):
        global hPubKey
        try:
            pSock.connect(aIP)
        except:
            raise Exception
        pSock.setblocking(0) # No. This has to be done a different way with no busy idle, etc.
    
    def importKey(self, psKey):
        if psKey[0:2] == "b'":
            psKey = bytes(psKey[2:-2], "utf-8").replace(b'\\n', b'\n')
        else:
            psKey = bytes(psKey, "utf-8").replace(b'\\n', b'\n')
        #return RSA.importKey(psKey)
        return RSA.importKey(psKey)

    def saveIni(self):
        global basepath, config
        hOp = open(basepath + "/keychain.ini", "w")
        with hOp as configfile:
            config.write(configfile)
    
    def getKey(self, psIP):
        global config
        return self.importKey(self.config['keychain'][psIP])
    
    def exportKey(self, phKey):
        return phKey.exportKey()
    
    def decrypt(self, psData):
        global hPrivKey
        return PKCS1_OAEP.new(hPrivKey).decrypt(psData)
    
    def encrypt(self, psData, phKey):
        return PKCS1_OAEP.new(phKey).encrypt(psData)

    def closeListenSocket(self):
        global sockListen
        print("CONMANAGER [function closeListenSocket]: Closing listen socket.")
        sockListen.close()
        print("CONMANAGER [function closeListenSocket]: Closed listen socket.")
    
    config = configparser.ConfigParser()
    basepath = os.path.dirname(os.path.realpath(__file__))
    config.read(basepath + '/keychain.ini')
    
       
mainclass = conmanager()
