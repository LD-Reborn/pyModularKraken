import pulsectl
import sys
sys.path.append("..")
from log.log import *

"""
Commands:
listsources
    returns: index:'name','description'|index:'name','description'|...
listsinks
    returns: index:'name','description'|index:'name','description'|...
getdefaultsource
getdefaultsink
getvolume           sink/source, id
setvolume           sink/source, id, volume
incvolume           sink/source, id, value
decvolume           sink/source, id, value
getmute             sink/source, id
setmute             sink/source, id, 1/0
togglemute          sink/source, id
"""


class audiocontrol(object):

    def __init__(self):
        global pulse
        initLog("audiocontrol")
        pulse = pulsectl.Pulse("audiocontrol")
    
    def initcore(self, out_q, in_q):
        global queue_out, queue_in
        queue_out = out_q
        queue_in = in_q
    
    def run(self):
        log("running")
        