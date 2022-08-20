from datetime import datetime, timedelte
import sys
sys.path.append("..")
from log.log import *

class helloworld_alice(object):

    def __init__(self):
        #print("Intermetry is still empty...")
        pass
    
    def initcore(self, pOutQueue, pInQueue):
        global outQueue, inQueue
        outQueue = pOutQueue
        inQueue = pInQueue

    def run(self):
        log("alice started!")
        outQueue.put(("conmanager", ("senddata", "broadcast", "bob", b"This is a message from alice")))
        
        while True:
            if not inQueue.empty():
                read = inQueue.get()
                print("INTERMETRY: {}".format(read))    
mainclass = helloworld_alice()
