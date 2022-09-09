import os
import sys
import time
from datetime import datetime, timedelta

#NO!    #dependency: pip3 install tkhtmlview
#       #from tkhtmlview import HTMLLabel
#incompatible with python3.10;  #dependency: pip install cefpython3==66.0
#                               #from cefpython3 import cefpython as cef
#dependency: pip install tkinterhtml
#from tkinterhtml import HTMLFrame

sys.path.append("..")
import importlib
import threading
import time
import tkinter as tk
from configparser import ConfigParser
from tkinter import *

from log.log import *
# dependency ---> pip install screeninfo
from screeninfo import get_monitors

#https://stackoverflow.com/questions/5564009/executing-a-function-with-a-parameter-every-x-seconds-in-python
class RepeatEvery(threading.Thread):
    def __init__(self, interval, func, *args, **kwargs):
        threading.Thread.__init__(self)
        self.interval = interval  # seconds between calls
        self.func = func          # function to call
        self.args = args          # optional positional argument(s) for call
        self.kwargs = kwargs      # optional keyword argument(s) for call
        self.runable = True
    def run(self):
        while self.runable:
            self.func(*self.args, **self.kwargs)
            time.sleep(self.interval)
    def stop(self):
        self.runable = False

class hwdisplay(object):

    def __init__(self):
        initLog("hwdisplay")
        global packetID
        packetID = 0
        
        global VERSION, MONITOR, config, window, window_x, window_y, window_w, window_h, canvas
        VERSION = "v0.1"
        basepath = os.path.dirname(os.path.realpath(__file__))
        config = ConfigParser(allow_no_value=True)
        config.read(basepath + '/config.ini')
        displays = []
        for display in config["displays"]:
            tempDisplay = {}
            tempDisplay[]
            tempDisplay.config = ConfigParser()
            displays.append(display)
        #
        #COLOR_BG = config.get("colors", "bg")
        #COLOR_FG = config.get("colors", "fg")
        #COLOR_BUTTONBG = config.get("colors", "buttonbg").split(",")
        #COLOR_BUTTONFG = config.get("colors", "buttonfg").split(",")
        #try:
        #    MONITOR = config.get("displays", "monitor")
        #    #find correct monitor
        #    for m in get_monitors():
        #        if m.name == MONITOR:
        #            window_x = m.x
        #            window_y = m.y
        #            window_w = m.width
        #            window_h = m.height
        #            break
        #except:
        #    MONITOR = None
        #    window_x = config.get("displays", "x")
        #    window_y = config.get("displays", "y")
        #    window_w = config.get("displays", "w")
        #    window_h = config.get("displays", "h")

        # creating window
        #window = tk.Tk()
        
        # setting attribute
        #window.geometry("%dx%d+%d+%d" % (window_w, window_h, window_x, window_y))
        #window.config(bg=COLOR_BG)
        #window.attributes('-fullscreen', True)
        #window.wm_attributes("-topmost", True)
        #window.title("utilTouchbar {}".format(VERSION))
        
        #window_bg = PhotoImage(file=config_bg)
        #label = tk.Label(window, image=window_bg)
        #label.pack()
        #canvas = Canvas(window, width=window_w, height=window_h, bg=COLOR_BG, highlightthickness=0)
        #canvas.create_text(300, 50, text="Test 123", fill="green", font=('Helvetica 15 bold'))
        #canvas.pack()
        log("hwdisplay: OK")
    
    def initcore(self, pOutQueue, pInQueue):
        global outQueue, inQueue
        outQueue = pOutQueue
        inQueue = pInQueue
    
    def update(self):
        pass

    def run(self):
        pass
        #updateThread = RepeatEvery(0.5, self.update, (window, canvas))
        #updateThread.start()
        
        #window.mainloop()
        
        #updateThread.stop()
        
        #global packetID
        #log("hwdisplay: running")
        #while (True):
        #    time.sleep(5)
        #    packetID += 1
        #    outQueue.put(("conmanager", ("senddata", "ifd", "intermetry", bytes("hardwareinfo:{}:cpu,cpu_all,ram_percent,ram_total,ram_used,gpu_name,gpu_temp,gpu_utilization,gpu_memused,gpu_memtotal,gpu_memusedPercent".format(packetID), "utf-8"))))
        #
        #while True:
        #    if not inQueue.empty():
        #        read = inQueue.get()
        #        print("INTERMETRY: {}".format(read))    
mainclass = hwdisplay()
