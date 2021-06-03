from datetime import datetime, timedelta
import sys
from time import sleep
sys.path.append("..")
from log.log import *

class intermetry(object):

    def __init__(self):
        global heartbeatFrequency, heartbeatNext, conmanager, devicelist
        heartbeatFrequency = timedelta(seconds=30)
        heartbeatNext = datetime.now() + heartbeatFrequency
        conmanager = "conmanager"
        '''
        deviceList contains:
            devicename, lastheartbeatDatetime, moduleList
        '''
        devicelist = []
    def initcore(self, pOutQueue, pInQueue):
        global outQueue, inQueue
        outQueue = pOutQueue
        inQueue = pInQueue

    def heartbeat(self):
        outQueue.put((conmanager, ("senddata", "broadcast", "intermetry", b"heartbeat")))
        outQueue.put((conmanager, ("listdevices")))

    def run(self):
        global heartbeatFrequency, heartbeatNext
        log("intermetry has started!")
        self.heartbeat()
        
        while True:
            time.sleep(0.01)
            if heartbeatNext <= datetime.now():
                heartbeatNext = datetime.now() + heartbeatFrequency
                self.heartbeat()
            
            if not inQueue.empty():
                read = inQueue.get()
                print("INTERMETRY has received: {}".format(read))
                originator = read[0]
                if type(read[1]) == list or type(read[1]) == tuple:
                    action = read[1][0]
                else:
                    action = read[1]
                if action == "devicelist":
                    for device in list(devicelist):
                        bFound = False
                        for device2 in read[1][1]:
                            if device[0] == device2:
                                bFound = True
                        if not bFound:
                            devicelist.remove(device)
                    for device2 in read[1][1]:
                        bFound = False
                        for device in list(devicelist):
                            if device[0] == device2:
                                bFound = True
                        if not bFound:
                            devicelist.append([device2, datetime.now(), False])
                elif action == "recvdata":
                    origDevice = read[1][1]
                    origModule = read[1][2]
                    try:
                        data = read[1][3].decode("utf-8")
                    except:
                        data = read[1][3]
                    #Update heartbeat timer
                    for i in range(len(devicelist)):
                        if origDevice == devicelist[i][0]:
                            devicelist[i][1] = datetime.now()
                    if data == "heartbeat":
                        print("Got a heartbeat from {}".format(origDevice))
                    else:
                        print("Dunno what to do with this packet: {}/{}/{}".format(origDevice, origModule, data))
                elif action == "sentdata":
                    print("Intermetry: unknown action: {}".format(read))
mainclass = intermetry()
