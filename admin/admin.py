from datetime import datetime, timedelta
import sys
import os
sys.path.append("..")
from log.log import *

class admin(object):

    def __init__(self):
        global conmanager, basepath, safepath
        conmanager = "conmanager"
        basepath = os.path.dirname(os.path.realpath(__file__))
        safepath = os.path.realpath(basepath + "/../") + "/"
        print(safepath)
        pass
    
    def initcore(self, pOutQueue, pInQueue):
        global outQueue, inQueue
        outQueue = pOutQueue
        inQueue = pInQueue

    def run(self):
        log("intermetry has started!")
        
        while True:
            if not inQueue.empty():
                read = inQueue.get()
                print("ADMIN: {}".format(read))
                originator = read[0]
                if type(read[1]) == list or type(read[1]) == tuple:
                    action = read[1][0]
                else:
                    action = read[1]
                if action == "recvdata":
                    origDevice = read[1][1]
                    origModule = read[1][2]
                    try:
                        data = read[1][3].decode("utf-8")
                    except:
                        data = read[1][3]
                    
                    if data[0:11] == "requestfile":
                        print("admin: incoming file request from {} for file {}".format(origDevice, data[12:]))
                        filepath = data[12:]
                        if os.path.commonprefix((os.path.realpath(filepath), safepath)) != safepath:
                            errout("admin: directory traversal attack prevented: origDevice {}; origModule {}; data {}".format(origDevice, origModule, data))
                        elif not os.path.isfile(filepath):
                            outQueue.put(("conmanager", ("senddata", origDevice, origModule, b'filenotfounderror ' + bytes(filepath, "utf8"))))
                        else:
                            tempFile = open(filepath, "rb")
                            tempRead = tempFile.read()
                            tempFile.close()
                            outQueue.put(("conmanager", ("senddata", origDevice, origModule, b'updatefile ' + bytes([len(filepath)]) + bytes(filepath, "utf8") + tempRead.__len__().to_bytes(4, 'big') + tempRead)))
                    else:
                        print("Dunno what to do with this packet: {}/{}/{}".format(origDevice, origModule, data))
                elif action == "sentdata":
                    print("Intermetry: unknown action: {}".format(read))
mainclass = admin()
