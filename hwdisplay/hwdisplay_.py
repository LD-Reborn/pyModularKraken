from datetime import datetime, timedelta
import time
import sys
sys.path.append("..")
from log.log import *

class hwdisplay(object):

    def __init__(self):
        initLog("hwdisplay")
        global packetID
        packetID = 0
        log("hwdisplay: OK")
        pass
    
    def initcore(self, pOutQueue, pInQueue):
        global outQueue, inQueue
        outQueue = pOutQueue
        inQueue = pInQueue

    def run(self):
        global packetID
        log("hwdisplay: running")
        while (True):
            time.sleep(5)
            packetID += 1
            outQueue.put(("conmanager", ("senddata", "ifd", "intermetry", bytes("hardwareinfo:{}:cpu,cpu_all,ram_percent,ram_total,ram_used,gpu_name,gpu_temp,gpu_utilization,gpu_memused,gpu_memtotal,gpu_memusedPercent".format(packetID), "utf-8"))))
        
        while True:
            if not inQueue.empty():
                read = inQueue.get()
                print("INTERMETRY: {}".format(read))    
mainclass = hwdisplay()
