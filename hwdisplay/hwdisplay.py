#---> Discord functionality
#https://discord.com/channels/336642139381301249/1003409840900685945
#https://discord.com/developers/docs/topics/rpc
#https://qwertyquerty.github.io/pypresence/html/doc/client.html#set_voice_settings

# importing tkinter for gui
import tkinter as tk
from tkinter import *
# dependency ---> pip install screeninfo
from screeninfo import get_monitors
from configparser import ConfigParser
import importlib
import threading
import time


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

def init():
    global VERSION, MONITOR, config, window, window_x, window_y, window_w, window_h, canvas
    VERSION = "v0.1"
    MONITOR = "HDMI-0"
    
    config = ConfigParser()
    config.read("config.ini")


    #find correct monitor
    for m in get_monitors():
        if m.name == config_port:
            window_x = m.x
            window_y = m.y
            window_w = m.width
            window_h = m.height
            break

    # creating window
    window = tk.Tk()
    
    # setting attribute
    window.geometry("%dx%d+%d+%d" % (window_w, window_h, window_x, window_y))
    window.config(bg=config_theme.bgcolor)
    window.attributes('-fullscreen', True)
    window.wm_attributes("-topmost", True)
    window.title("utilTouchbar {}".format(VERSION))
    
    #window_bg = PhotoImage(file=config_bg)
    #label = tk.Label(window, image=window_bg)
    #label.pack()
    canvas = Canvas(window, width=config_theme.width, height=config_theme.height, bg=config_theme.bgcolor, highlightthickness=0)
    #canvas.create_text(300, 50, text="Test 123", fill="green", font=('Helvetica 15 bold'))
    canvas.pack()
    
    config_theme.run(window, canvas)
    
    updateThread = RepeatEvery(0.5, config_theme.update, (window, canvas))
    updateThread.start()
    
    window.mainloop()
    
    updateThread.stop()
