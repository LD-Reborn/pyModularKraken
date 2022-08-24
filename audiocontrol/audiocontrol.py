import pulsectl
import sys
sys.path.append("..")
from log.log import *
from conmanager import utils

"""
Commands:
listsources
    returns: index:'name','description','mute','channels','volumes'|index:'name','description','mute','channels','volumes'|...
listsinks
    returns: index:'name','description','mute','channels','volumes'|index:'name','description','mute','channels','volumes'|...
getdefaultsource
    returns: id
setdefaultsource    id
getdefaultsink
    returns: id
setdefaultsink      id
getvolume           sink/source, id
    returns: volume_tuple
setvolume           sink/source, id, volume
incvolume           sink/source, id, value
decvolume           sink/source, id, value
getmute             sink/source, id
    returns: 0/1
setmute             sink/source, id, 1/0
togglemute          sink/source, id
    returns: new_mutevalue
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
        global pulse
        log("running")
        while True:
            time.sleep(0.05)
            if not queue_in.empty():
                    read = queue_in.get()
                    #External packet: ("conmanager", ("recvdata", ))
                    #Internal packet:
                    read = utils.parse(read)
                    if type(read[1]) == list or type(read[1]) == tuple:
                        action = read[1][0]
                    else:
                        action = read[1]
                    
                    match action:
                        case "listsources":
                            sources = pulse.source_list()
                            senddata = ""
                            for source in sources:
                                senddata += "{}:'{}','{}','{}','{}','{}'|".format(source.index, source.description, source.mute, source.channels, source.volumes)
                            senddata = senddata[:-1]
                            utils.respond(read, senddata)
                        case "listsinks":
                            sinks = pulse.sink_list()
                            senddata = ""
                            for sink in sinks:
                                senddata += "{}:'{}','{}','{}','{}','{}'|".format(sink.index, sink.description, sink.mute, sink.channels, sink.volumes)
                            senddata = senddata[:-1]
                            utils.respond(read, senddata)
                        case "getdefaultsource":
                            default_source = pulse.server_info().default_source_name
                            index = pulse.get_source_by_name(default_source)
                            utils.respond(read, index)
                        case "getdefaultsink":
                            default_sink = pulse.server_info().default_sink_name
                            index = pulse.get_sink_by_name(default_sink)
                            utils.respond(read, index)
                        case "setdefaultsource":
                            try:
                                id = read.params[0]
                            except:
                                utils.respond(read, (False, "missing parameter: id"))
                                continue
                            sources = pulse.source_list()
                            for source in sources:
                                if source.index == id:
                                    pulse.source_default_set(source)
                                    utils.respond(read, (True))
                        case "setdefaultsink":
                            try:
                                id = read.params[0]
                            except:
                                utils.respond(read, (False, "missing parameter: id"))
                                continue
                            sinks = pulse.sink_list()
                            for sink in sinks:
                                if sink.index == id:
                                    pulse.sink_default_set(source)
                                    utils.respond(read, (True))
                        case "getvolume":
                            try:
                                type = read.params[0]
                            except:
                                utils.respond(read, (False, "missing parameter: type"))
                                continue
                            try:
                                id = read.params[1]
                            except:
                                utils.respond(read, (False, "missing parameter: id"))
                                continue
                            if type == 0 or type == "0" or type == "sink":
                                sinks = pulse.sink_list()
                                for sink in sinks:
                                    if sink.index == id:
                                        utils.respond(read, (True, sink.volumes))
                        case "setvolume":
                            pass
                        case "incvolume":
                            pass
                        case "decvolume":
                            pass
                        case "getmute":
                            pass
                        case "setmute":
                            pass
                        case "togglemute":
                            pass
mainclass = audiocontrol()