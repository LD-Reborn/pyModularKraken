from log.log import *
import configparser
import importlib
import threading
import queue
import time
import imp
import os

def test(): # what?
    pass


if __name__ == "__main__":
    #import module names from .ini
    config = configparser.ConfigParser(allow_no_value=True)
    basepath = os.path.dirname(os.path.realpath(__file__))
    config.read(basepath + '/config.ini')
    modulelist = config["modules"]
    modules = []
    print("DEBUG modulelist: {}".format(modulelist))
    #initiate modules and deliver queues
    for module in modulelist:
        print("DEBUG: module {}".format(module))
        print("DEBUG: modulelist[module] {}".format(modulelist[module]))
        if modulelist[module] == None:
            modulefolder = module
        else:
            modulefolder = modulelist[module]
        log(module)
        hImport = imp.load_source(module, basepath + "/" + modulefolder + "/" + module + ".py")
        try:
            ModuleClass = hImport.mainclass
            
            modulequeue_in = queue.Queue()
            modulequeue_out = queue.Queue()
            ModuleClass.initcore(modulequeue_in, modulequeue_out)
            modules.append((module, ModuleClass, modulequeue_in, modulequeue_out))
        except AttributeError as msg:
            errout("CORE: Error loading module. {}".format(msg))
    for module in modules:
        thread = threading.Thread(target=module[1].run)
        thread.start()

    while True:
        time.sleep(0.01)
        for module in modules:
            #module = (modulename, ModuleClass, modulequeue_in, modulequeue_out)
            if not module[2].empty():
                read = module[2].get()
                print("CORE has received: {}".format(read))
                if len(read) < 2:
                    errout("CORE: Unfit parameter size:{}".format(read))
                else:
                    if read[0] == "core":
                        if read[1] == "getmodulelist":
                            aModules = []
                            for mod in modules:
                                aModules.append(mod[0])
                            module[3].put(("core", "modulelist", aModules))
                        #elif read[1] == "getmodulelistverbose":

                    else:
                        for target in modules:
                            if target[0] == read[0] or (type(read[0]) == list and target[0] in read[0]):
                                #print("CORE - found!")
                                #print(target)
                                read = list(read) # Why? - Sincerely: 3am me.
                                read[0] = module[0] # Why? - Sincerely: 3am me.
                                target[3].put(read)
                                break # Do not break if in a list? ~~ToDo
                module[2].task_done()
