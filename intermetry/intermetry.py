from datetime import datetime, timedelta
import sys
from time import sleep
sys.path.append("intermetry/utility")
import hardwareinfo as hwinfo
sys.path.append("../..")
from log.log import *


class intermetry(object):

    def __init__(self):
        global heartbeat_frequency, heartbeat_next, heartbeats, conmanager, devicelist
        initLog("intermetry")
        heartbeat_frequency = timedelta(seconds=30)
        heartbeat_next = datetime.now() + heartbeat_frequency
        conmanager = "conmanager"
        '''
        deviceList contains:
            devicename, lastheartbeatDatetime, moduleList
        '''
        devicelist = []

    def initcore(self, out_q, in_q):
        global queue_out, queue_in
        queue_out = out_q
        queue_in = in_q

    def heartbeat(self):
        #print("INTERMETRY has broadcast a heartbeat")
        queue_out.put((conmanager, ("senddata", "broadcast", "intermetry", b"heartbeat")))
        queue_out.put((conmanager, ("listdevices")))

    def run(self):
        global heartbeat_frequency, heartbeat_next
        log("intermetry: running")
        self.heartbeat()
        
        while True:
            time.sleep(0.01)
            if heartbeat_next <= datetime.now():
                heartbeat_next = datetime.now() + heartbeat_frequency
                self.heartbeat()
            
            if not queue_in.empty():
                read = queue_in.get()
                #print("INTERMETRY has received: {}".format(read))
                originator = read[0]
                if type(read[1]) == list or type(read[1]) == tuple:
                    action = read[1][0]
                else:
                    action = read[1]
                if action == "devicelist":
                    for device in list(devicelist):
                        device_isFound = False
                        for device2 in read[1][1]:
                            if device[0] == device2:
                                device_isFound = True
                        if not device_isFound:
                            devicelist.remove(device)
                    for device2 in read[1][1]:
                        device_isFound = False
                        for device in list(devicelist):
                            if device[0] == device2:
                                device_isFound = True
                        if not device_isFound:
                            devicelist.append([device2, datetime.now(), False])
                elif action == "recvdata":
                    orig_device = read[1][1]
                    orig_module = read[1][2]
                    try:
                        data = read[1][3].decode("utf-8")
                    except:
                        data = read[1][3]
                    #Update heartbeat timer
                    for i in range(len(devicelist)):
                        if orig_device == devicelist[i][0]:
                            devicelist[i][1] = datetime.now()
                    if data == "heartbeat":
                        log("intermetry: Got a heartbeat from {}. {}".format(orig_device, read))
                    elif data[0:12] == "hardwareinfo":
                        try:
                            tempStr = data[13:]
                            packetID = tempStr[:tempStr.find(":")]
                            request = tempStr[tempStr.find(":") + 1:]
                            queue_out.put((conmanager, ("senddata", orig_device, orig_module, bytes("hardwareinfo:{}:{}".format(packetID, hwinfo.parseRequest(request)), "utf-8"))))
                        except Exception as msg:
                            errout("INTERMETRY: error while processing a hardwaredata packet from {}@{}: {}".format(orig_module, orig_device, msg))
                    else:
                        errout("INTERMETRY: Dunno what to do with this packet: {}/{}/{}".format(orig_device, orig_module, data))
                elif action == "sentdata":
                    errout("INTERMETRY: unknown action: {}".format(read))
mainclass = intermetry()
