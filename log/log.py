import time

def initLog(pModulename):
    global modulename
    modulename = pModulename

def errout(message):
    global modulename
    try:
        message = "{} @ {}: {}\n".format(time.asctime(), modulename.upper, message)
    except:
        message = "{}: {}\n".format(time.asctime(), message)
    
    print(message)
    hFile = open("errorlog.txt", "a")
    hFile.write(message)
    hFile.close()


def log(message):
    global modulename
    try:
        message = "{} @ {}: {}\n".format(time.asctime(), modulename.upper, message)
    except:
        message = "{}: {}\n".format(time.asctime(), message)
    print(message)
    hFile = open("log.txt", "a")
    hFile.write(message)
    hFile.close()
