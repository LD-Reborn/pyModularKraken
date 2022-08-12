import psutil
#dependency ---> pip3 install gputil
import GPUtil
import sys
sys.path.append("../..")
from log.log import *

def parseRequest(pText):
    funcmap = {"cpu": cpu, "cpu_all": cpu_all, "cpu_numcores": cpu_numcores, "ram_percent": ram_percent, "ram_total": ram_total, "ram_used": ram_used, "gpu_name": gpu_name, "gpu_temp": gpu_temp, "gpu_utilization": gpu_utilization, "gpu_memused": gpu_memused, "gpu_memtotal": gpu_memtotal, "gpu_memusedPercent": gpu_memusedPercent}
    requests = pText.split(",")
    returnstring = ""
    for request in requests:
        try:
            returnstring += "{}|".format(funcmap[request]())
        except Exception as msg:
            errout("HARDWAREINFO: unable to parse requested hardware info {}. Error: {}".format(request, msg))
    return returnstring

#CPU usage in percent
def cpu():
    return psutil.cpu_percent()

#CPU usage by cores in [percent[, percent[, percent[...]]]]. E.g.: [10.3, 7.4, 7.5, 7.9, 9.4, 7.0, 7.9, 8.4]
def cpu_all():
    return psutil.cpu_percent(percpu=True)

#CPU core count
def cpu_numcores():
    return psutil.cpu_count()

#RAM usage in percent
def ram_percent():
    return psutil.virtual_memory().percent

#RAM total amount in bytes
def ram_total():
    return psutil.virtual_memory().total

#RAM usage in bytes
def ram_used():
    return psutil.virtual_memory().used


#GPU name
def gpu_name():
    returnstring = ""
    for gpu in GPUtil.getGPUs():
    	returnstring += "{},".format(gpu.name)
    return returnstring[:-1]

#GPU temperature in °C
def gpu_temp():
    returnstring = ""
    for gpu in GPUtil.getGPUs():
    	returnstring += "{},".format(gpu.temperature)
    return returnstring[:-1]

#GPU compute utilization in percent
def gpu_utilization():
    returnstring = ""
    for gpu in GPUtil.getGPUs():
    	returnstring += "{},".format(gpu.load * 100)
    return returnstring[:-1]

#Used GPU memory in MB
def gpu_memused():
    returnstring = ""
    for gpu in GPUtil.getGPUs():
    	returnstring += "{},".format(gpu.memoryUsed)
    return returnstring[:-1]

#Total GPU memory in MB
def gpu_memtotal():
    returnstring = ""
    for gpu in GPUtil.getGPUs():
    	returnstring += "{},".format(gpu.memoryTotal)
    return returnstring[:-1]

#Used GPU memory in percent
def gpu_memusedPercent():
    returnstring = ""
    for gpu in GPUtil.getGPUs():
    	returnstring += "{},".format(gpu.memoryUsed / gpu.memoryTotal * 100)
    return returnstring[:-1]


def humanreadable(size):
    byteSuffixes = ['bit/s', 'Kbit/s', 'Mbit', 'Gbit', 'Tbit', 'Pbit']
    i = 0
    while size >= 1024 and i < len(byteSuffixes) - 1:
        size /= 1024.
        i += 1
    f = ('%.2f' % size).rstrip('0').rstrip('.')
    return '{} {}'.format(f, byteSuffixes[i])
