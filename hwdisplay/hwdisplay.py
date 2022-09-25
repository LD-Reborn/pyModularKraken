from email.errors import FirstHeaderLineIsContinuationDefect
from http.client import SWITCHING_PROTOCOLS
import os
import sys
import time
from uuid import getnode
import xml.dom.minidom
from datetime import datetime, timedelta

from symbol import try_stmt

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

    #def findNode(self, pNode, pName):
    #    for child in pNode.childNodes:
    #        if child.nodeName == pName:
    #                return child
    
    def getNode(self, pNode, pName):
        for child in pNode["childNodes"]:
            if child["name"] == pName:
                return child

    def getValues(self, pNode):
        retValues = {"attributes": {}, "childNodes": []}
        for element in pNode.childNodes:
            if element == None:
                continue
            #Problem: Text between tags is its own element. even "\n\n   "... FML. <tag>text<tag2>moretext</tag2>evenmoretext</tag>
            retValues["childNodes"].append(self.getValues(pNode))
        for attribute in pNode.attributes.values():
            retValues["attributes"][attribute.name] = attribute.value
        try:
            retValues["name"] = retValues["attributes"]["name"]
        except:
            retValues["name"] = pNode.nodeName
        try:
            retValues["attributes"]["page"]
        except:
            retValues["attributes"]["page"] = None
        retValues["tagName"] = pNode.tagName
        retValues["nodeValue"] = pNode.nodeValue
        retValues["self"] = pNode
        return retValues
    
    def loadElement(self, pGui, pElement):
        match pElement["tagName"]:
            case "pagecontroller":
                pass #Todo
            case "label":
                pass #Todo
            case "image":
                pass #Todo
            case "variable":
                pass #Todo
            case "canvas":
                pass #Todo


    def loadPage(self, pDisplay, pPage):
        elementtypes = {""}
        for element in pDisplay["body"]["childNodes"]:
            if element["attributes"]["page"] == pPage or element["attributes"]["page"] == None:
                self.loadElement(self, pDisplay["window"], element)

    def getCurrentPage(self, display):
        if display["pages"] == {}:
            display["pages"]["current"] = None
            for element in display["body"]["childNodes"]:
                if element["tagName"] == "pagecontroller":
                    try:
                        display["pages"]["current"] = element["attributes"]["default"]
                    except:
                        pass
                    for page in element["childNodes"]:
                        display["pages"][page["name"]] = [] # Will store elements like labels, images, etc. thus empty for now.
        try:
            return display["pages"]["current"]
        except KeyError:
            raise Exception("Formatting error: Please make sure you have a page controller containing pages")

    def initDisplay(self, pDisplay):
        pDisplay["collection"] = self.getValues(pDisplay["collection"])
        pDisplay["window"] = tk.Tk()
        pDisplay["head"] = self.getNode(self, pDisplay["collection"], "head")
        pDisplay["body"] = self.getnode(self, pDisplay["collection"], "body")
        pDisplay["pages"] = {}
        for element in pDisplay["head"]["childNodes"]:
            pDisplay["head"][element["name"]] = element["childNodes"][0]["nodeValue"] #To get text from <tag>text</tag>, get it's 0-th child's (aka. text node) value
        pDisplay["window"].geometry("%dx%d+%d+%d" % (pDisplay["head"]["width"], pDisplay["head"]["height"], pDisplay["head"]["x"], pDisplay["head"]["y"]))
        #todo: .config(bg=backgroundcolor)
        #todo: Attributes like: .attributes('-fullscreen', True) or .wm_attributes('-topmost', True)
        #todo: .title("user selected title")
        self.loadPage(self, pDisplay self.getCurrentPage(self, pDisplay))
        

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
            tempDisplay["basepath"] = basepath + '/' + display
            tempDisplay["DOMTree"] = xml.dom.minidom.parse(tempDisplay["basepath"] + '/' + display + '.xml')
            tempDisplay["collection"] = tempDisplay["DOMTree"].documentElement
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
