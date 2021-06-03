import time

def errout(psErrMsg):
    psErrMsg = "{}: {}\n".format(time.asctime(), psErrMsg)
    print(psErrMsg)
    hFile = open("errorlog.txt", "a")
    hFile.write(psErrMsg)
    hFile.close()

def log(psMsg):
    psMsg = "{}: {}\n".format(time.asctime(), psMsg)
    print(psMsg)
    hFile = open("log.txt", "a")
    hFile.write(psMsg)
    hFile.close()
