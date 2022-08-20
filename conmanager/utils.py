def parse(read):
    if read[0] == "conmanager": #External packet
        #Import the data. 
        data = eval(read[1][3], {'__builtins__': None}) #'{__builtins': None} so that you can't execute code. Just strings and stuff.
        external = True
        orig_device = read[1][1]
        orig_module = read[1][2]
        try: #Check for packet_id
            packet_id = read[1][4]
        except:
            packet_id = None
    else: #Internal packet
        external = False
        orig_device = None
        orig_module = read[0]
        try: #Check for packet_id
            packet_id = read[2]
        except:
            packet_id = None

    if type(read[1]) == list or type(read[1]) == tuple:
        action = read[1][0]
        params = read[1][1:]
    else:
        action = read[1][0]
        params = []
    return {"external": external, "origdevice": orig_device, "origmodule": orig_module, "action": action, "params": params}

def respond(read, msg):
    global queue_out
    if read.external: #External packet
        #conmanager ---> audiocontrol: ("recvdata", orig_device, orig_modname, data)
        if type(msg) != bytes:
            msg = bytes(msg, "utf-8")
        queue_out.put(("conmanager", ("senddata", read.orig_device, read.orig_modname, msg, read.packet_id)))
    else: #Internal packet
        queue_out.put((read.orig_modname, msg, read.packet_id)) #Put msg in additional parentheses or not? I'd say no.

def send(target_device, target_module, msg):
    global queue_out
    if target_device == None: #internal

    else: #external
        