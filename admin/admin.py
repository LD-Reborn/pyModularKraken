from datetime import datetime, timedelta
import sys
import os
sys.path.append("..")
from log.log import *
import random

class admin(object):

    def __init__(self):
        global conmanager, basepath, safepath
        initLog("admin")
        conmanager = "conmanager"
        basepath = os.path.dirname(os.path.realpath(__file__))
        safepath = os.path.realpath(basepath + "/../") + "/"
        #print(safepath)
        pass


    def initcore(self, out_q, in_q):
        global queue_out, queue_in
        queue_out = out_q
        queue_in = in_q

    def run(self):
        log("intermetry has started!")
        
        while True:
            time.sleep(0.1)
            if not queue_in.empty():
                read = queue_in.get()
                #print("ADMIN: {}".format(read))
                originator = read[0]
                if type(read[1]) == list or type(read[1]) == tuple:
                    action = read[1][0]
                else:
                    action = read[1]
                if action == "recvdata":
                    orig_device = read[1][1]
                    orig_module = read[1][2]
                    try:
                        data = read[1][3].decode("utf-8")
                    except:
                        data = read[1][3]
                    
                    if data[0:11] == "requestfile":
                        #print("admin: incoming file request from {} for file {}".format(orig_device, data[12:]))
                        filepath = data[12:]
                        if os.path.commonprefix((os.path.realpath(filepath), safepath)) != safepath:
                            errout("admin: directory traversal attack prevented: orig_device {}; orig_module {}; data {}".format(orig_device, orig_module, data))
                        elif not os.path.isfile(filepath):
                            queue_out.put(("conmanager", ("senddata", orig_device, orig_module, b'filenotfounderror ' + bytes(filepath, "utf8"), random.randbytes(4))))
                        else:
                            temp_file = open(filepath, "rb")
                            temp_read = temp_file.read()
                            temp_file.close()
                            queue_out.put(("conmanager", ("senddata", orig_device, orig_module, b'updatefile ' + bytes([len(filepath)]) + bytes(filepath, "utf8") + temp_read.__len__().to_bytes(4, 'big') + temp_read, random.randbytes(4))))
                    else:
                        print("Dunno what to do with this packet: {}/{}/{}".format(orig_device, orig_module, data))
                elif action == "sentdata":
                    print("admin: unknown action: {}".format(read))
mainclass = admin()
