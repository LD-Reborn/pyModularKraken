import time

def errout(message):
    message = "{}: {}\n".format(time.asctime(), message)
    print(message)
    hFile = open("errorlog.txt", "a")
    hFile.write(message)
    hFile.close()

def log(message):
    message = "{}: {}\n".format(time.asctime(), message)
    print(message)
    hFile = open("log.txt", "a")
    hFile.write(message)
    hFile.close()
