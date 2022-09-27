import os
import sys
import time
import queue
import xml.dom.minidom
from datetime import datetime, timedelta
#dependency PIL?
from PIL import ImageTk, Image


#NO!    #dependency: pip3 install tkhtmlview
#       #from tkhtmlview import HTMLLabel
#incompatible with python3.10;  #dependency: pip install cefpython3==66.0
#                               #from cefpython3 import cefpython as cef
#dependency: pip install tkinterhtml
#from tkinterhtml import HTMLFrame
#Screw HTML. I'm doing tkinter + XML manually.

sys.path.append("..")
sys.path.append("hwdisplay")
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

class windowmanager(object):

    #def findNode(self, pNode, pName):
    #    for child in pNode.childNodes:
    #        if child.nodeName == pName:
    #                return child
    
    def getNode(self, pNode, pName):
        for child in pNode["childNodes"]:
            if child["name"] == pName:
                return child

    def getValues(self, pNode):
        #print("DEBUG@getValues: entry {}".format(pNode.nodeName))
        retValues = {"attributes": {}, "childNodes": []}
        for element in pNode.childNodes:
            if element == None:
                continue
            #Problem: Text between tags is its own element. even "\n\n   "... FML. <tag>text<tag2>moretext</tag2>evenmoretext</tag>
            retValues["childNodes"].append(self.getValues(element))
        try: #If has attributes:
            for attribute in pNode.attributes.values():
                retValues["attributes"][attribute.name] = attribute.value
        except: #else: do nothing.
            pass
        try:
            retValues["name"] = retValues["attributes"]["name"]
        except:
            retValues["name"] = pNode.nodeName
        try:
            retValues["attributes"]["page"]
        except:
            retValues["attributes"]["page"] = None
        retValues["nodeName"] = pNode.nodeName
        retValues["nodeValue"] = pNode.nodeValue
        retValues["self"] = pNode
        #print("DEBUG@getValues: end")
        return retValues
    
    def getVariable(self, pDisplay, pName):
        return pDisplay["variables"][pName]
    
    def hasAttribute(self, pElement, pAttribute):
        try:
            print("DEBUG@hasAttribute: try")
            print("DEBUG@hasAttribute: pElement {}".format(pElement))
            print("DEBUG@hasAttribute: attributes {}".format(pElement["attributes"]))

            pElement["attributes"][pAttribute]
            return True
        except:
            return False

    
    def loadElement(self, pDisplay, pElement):
        print("DEBUG@loadElement: entry pElement {}".format(pElement))

        element = {}
        match pElement["nodeName"]:
            case "pagecontroller":
                print("DEBUG@loadElement: pagecontroller {}|{}".format(pDisplay["window"], pElement))
                pass #Todo
            case "label":
                print("DEBUG@loadElement: label")
                element["type"] = "label"
                x = pElement["attributes"]["x"]
                y = pElement["attributes"]["y"]
                try:
                    try:
                        text = pElement["childNodes"][0]["nodeValue"]
                    except:
                        text = pElement["attributes"]["text"]
                    element["handle"] = tk.Label(pDisplay["window"], text = text)
                    print("DEBUG@loadElement: label text {} x {} y {}".format(text, x, y))
                except: #if has variable="variablename"
                    textvariable = pDisplay["variables"][pElement["attributes"]["variable"]]["variable"]
                    element["handle"] = tk.Label(pDisplay["window"], textvariable = textvariable)
                    print("DEBUG@loadElement: label textvariable {} x {} y {}".format(textvariable.get(), x, y))
                
                
                #element["handle"].pack()
                element["handle"].place(x = x, y = y)
                print("DEBUG@loadElement: label placed {} x {} y {}".format(element["handle"].place_info(), element["handle"].winfo_x, element["handle"].winfo_y))
            case "image":
                print("DEBUG@loadElement: image")
                element["type"] = "label"
                x = pElement["attributes"]["x"]
                y = pElement["attributes"]["y"]
                path = "{}/{}".format(pDisplay["fullbasepath"], pElement["attributes"]["image"])
                print("DEBUG@loadElement: image path {}".format(path))
                element["image"] = ImageTk.PhotoImage(file = path)
                element["handle"] = tk.Label(pDisplay["window"], image = element["image"])
                element["handle"].place(x = x, y = y)

            case "variable":
                print("DEBUG@loadElement: variable")
                temp = {}
                temp["variable"] = StringVar(pDisplay["window"])
                temp["variable"].set("DEBUGSTRING") #DEBUG #todo
                temp["every"] = pElement["attributes"]["every"]
                temp["function"] = eval('pDisplay["controller"].{}'.format(pElement["attributes"]["function"]))
#                print("DEBUG@loadElement: variablefunction {}".format(temp["function"](temp["variable"])))
                temp["repeatEvery"] = RepeatEvery(float(temp["every"]), temp["function"], temp["variable"])
                temp["repeatEvery"].start()
                pDisplay["variables"][pElement["name"]] = temp
            case "canvas":
                print("DEBUG@loadElement: canvas")
                pass #Todo
            case _:
                print("something else. {}".format(pElement))
            
        try: #postconfig
            print("DEBUG@loadElement: try")
            if self.hasAttribute(pElement, "color"):
                print("DEBUG@loadElement: color")
                element["handle"].config(fg = pElement["attributes"]["color"])
            elif self.hasAttribute(pElement, "colour"):
                print("DEBUG@loadElement: colour")
                element["handle"].config(fg = pElement["attributes"]["colour"])
            elif self.hasAttribute(pElement, "fg"):
                print("DEBUG@loadElement: fg")
                element["handle"].config(fg = pElement["attributes"]["fg"])
            else:
                element["handle"].config(fg = pDisplay["head"]["fg"])
            if self.hasAttribute(pElement, "bgcolor"):
                print("DEBUG@loadElement: bgcolor")
                element["handle"].config(bg = pElement["attributes"]["bgcolor"])
            elif self.hasAttribute(pElement, "bgcolour"):
                print("DEBUG@loadElement: bgcolour")
                element["handle"].config(bg = pElement["attributes"]["bgcolour"])
            elif self.hasAttribute(pElement, "bg"):
                print("DEBUG@loadElement: bg")
                element["handle"].config(bg = pElement["attributes"]["bg"])
            else:
                element["handle"].config(bg = pDisplay["head"]["bg"])
        except Exception as e:
            print("DEBUG@loadElement: ERROR {}".format(e))
            pass
        return element
        print("DEBUG@loadElement: end")


    def loadPage(self, pDisplay, pPage):
        print("DEBUG@loadPage: entry pPage: {}".format(pPage))
        elementtypes = {""}
        for element in pDisplay["body"]["childNodes"]:
            if element["nodeName"] != "#text" and (element["attributes"]["page"] == pPage or element["attributes"]["page"] == None):
                loadedElement = self.loadElement(pDisplay, element)
                pDisplay["pages"][pPage].append(loadedElement)
        print("DEBUG@loadPage: end")

    def getCurrentPage(self, display):
        print("DEBUG@getCurrentPage: entry")
        if display["pages"] == {}:
            display["pages"]["current"] = None
            for element in display["body"]["childNodes"]:
                if element["nodeName"] == "pagecontroller":
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
        print("DEBUG@initDisplay: entry")
        pDisplay["collection"] = self.getValues(pDisplay["collection"])
        pDisplay["window"] = tk.Tk()
        print("DEBUG@initDisplay: window {}".format(pDisplay["window"].winfo_geometry()))
        pDisplay["head"] = self.getNode(pDisplay["collection"], "head")
        pDisplay["body"] = self.getNode(pDisplay["collection"], "body")
        pDisplay["variables"] = {}
        pDisplay["pages"] = {}
        for element in pDisplay["head"]["childNodes"]:
            if element["name"] != "#text":
                pDisplay["head"][element["name"]] = element["childNodes"][0]["nodeValue"] #To get text from <tag>text</tag>, get it's 0-th child's (aka. text node) value
#        print("DEBUG@initDisplay: basepath {}".format(pDisplay["basepath"]))
#        print("DEBUG@initDisplay: controller {}".format(pDisplay["head"]["controller"]))
#        print("DEBUG@initDisplay: full path {}".format("{}.{}".format(pDisplay["basepath"], pDisplay["head"]["controller"]).replace("/", ".")))
#        print("DEBUG@initDisplay: current path {}".format(sys.path))
        pDisplay["controller"] = importlib.import_module("{}.{}".format(pDisplay["basepath"], pDisplay["head"]["controller"]).replace("/", "."))
        pDisplay["controllerIn"] = queue.Queue()
        pDisplay["controllerOut"] = queue.Queue()
        pDisplay["controller"].initController(pDisplay["controllerIn"], pDisplay["controllerOut"], pDisplay, pDisplay["head"]["target"])
#        print("DEBUG@initDisplay: window generation:")
#        print("{}x{}+{}+{}".format(pDisplay["head"]["width"], pDisplay["head"]["height"], pDisplay["head"]["x"], pDisplay["head"]["y"]))
        pDisplay["window"].wm_geometry("{}x{}+{}+{}".format(pDisplay["head"]["width"], pDisplay["head"]["height"], pDisplay["head"]["x"], pDisplay["head"]["y"]))
        
        try:
            pDisplay["window"].title(pDisplay["head"]["title"])
        except:
            pass

        try:
            pDisplay["window"].config(bg=pDisplay["head"]["bg"])
        except:
            pDisplay["window"].config(bg="#000000")

        try:
            pDisplay["head"]["topmost"] #If this tag exists, make window topmost.
            pDisplay["window"].wm_attributes('-topmost', True)
        except:
            pass

        try:
            pDisplay["head"]["fullscreen"] #If this tag exists, make window full screen
            pDisplay["window"].attributes('-fullscreen', True)
        except:
            pass
#        print("DEBUG@initDisplay: window {}".format(pDisplay["window"].winfo_geometry()))

        pDisplay["window"].update()
        print("DEBUG@initDisplay: before loadPage")
        self.loadPage(pDisplay, self.getCurrentPage(pDisplay))
        print("DEBUG@initDisplay: after loadPage")
        pDisplay["loaded"] = 1
        pDisplay["window"].mainloop()

class hwdisplay(object):

    def __init__(self):
        initLog("hwdisplay")
        global packetID, VERSION, basepath, config, displays
        packetID = 0
        
        global VERSION, MONITOR, config, window, window_x, window_y, window_w, window_h, canvas
        VERSION = "v0.1"
        basepath = os.path.dirname(os.path.realpath(__file__))
        config = ConfigParser(allow_no_value=True)
        config.read(basepath + '/config.ini')
        displays = []
        for display in config["displays"]:
            print("DEBUG@__init__: display {}".format(display))
            tempDisplay = {}
            tempDisplay["fullbasepath"] = basepath + '/' + display
            tempDisplay["basepath"] = display
            tempDisplay["DOMTree"] = xml.dom.minidom.parse(tempDisplay["fullbasepath"] + '/' + display + '.xml')
            tempDisplay["collection"] = tempDisplay["DOMTree"].documentElement
            tempDisplay["loaded"] = 0
            wm = windowmanager() # I have to put the whole GUI stuff into a separate thread because tkinter requires tk.Tk() and mainloop() to be executed in the same thread.
            tempDisplay["mainloop"] = threading.Thread(target=wm.initDisplay, args=(tempDisplay,))
            tempDisplay["mainloop"].start()
#            tempDisplay["window"].mainloop()
            while tempDisplay["loaded"] < 1:
                time.sleep(0.1)
            displays.append(tempDisplay)
            print("DEBUG@__init__: display END")
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
        while True:
            time.sleep(0.01)
            if not inQueue.empty(): # Intermetry ---> core ---> hwdisplay ---> ALL displays. (Need implementation to add additional module slots into core module)
                read = inQueue.read()
                for display in displays:
                    display["controllerIn"].put(read)
            for display in displays:
                if not display["controllerOut"].empty():
                    read = display["controllerOut"].get()
                    #read = {dstModule: "destination module", dstDevice: "destination device", data: "data"}
                    outQueue.put(("conmanager", ("senddata", read["dstDevice"], read["dstModule"], bytes(read["data"], "utf-8"))))


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
