from datetime import datetime, timedelte
import sys
sys.path.append("..")
from log.log import *

class intermetrymaster(object):

    def __init__(self):
        #print("Intermetry is still empty...")
        pass
    
    def initcore(self, pOutQueue, pInQueue):
        global outQueue, inQueue
        outQueue = pOutQueue
        inQueue = pInQueue

    def run(self):
        log("intermetry has started!")
        outQueue.put(("conmanager", ("senddata", "broadcast", "intermetry", b"This is a message from intermetry in PersonalCommander")))
        
        while True:
            if not inQueue.empty():
                read = inQueue.get()
                print("INTERMETRY: {}".format(read))    
mainclass = intermetry()
