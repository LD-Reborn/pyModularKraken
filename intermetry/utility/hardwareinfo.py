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

#All nic addresses in format: nic=address,nic2=address,...
def nic_address(pGetIPv6 = False): #With nic_address(True) you'll get multiple IPv6 addresses per NIC. Not a bug.
    returnstring = ""
    nics = psutil.net_if_addrs()
    for nic in nics:
        for address in nics[nic]:
            print("DEBUG")
            print(nic)
            print(address)
            if address.family.value == 2 + 8 * pGetIPv6: #2 = IPv4. 10 = IPv6
                print("is v4\n")
                returnstring += "{}={},".format(nic, address.address)
    return returnstring[:-1]

#All nic TOTAL up/down byte values in format: nic=up/down, nic2=up/down,...
def nic_io():
    returnstring = ""
    nics = psutil.net_io_counters(pernic=True)
    for nic in nics:
        returnstring += "{}={}/{},".format(nic, nics[nic].bytes_sent, nics[nic].bytes_recv)
    return returnstring[:-1]

#All nic linkspeeds in MB/s in format: nic=linkspeed, nic2=linkspeed,...
#Link speed seems to jump to 65535 if you unplug the cable from respective nic. Developers might have had a few drinks. Relatable.
def nic_linkspeed():
    returnstring = ""
    nics = psutil.net_if_stats()
    for nic in nics:
        returnstring += "{}={},".format(nic, nics[nic].speed)
    return returnstring[:-1]

#All nic mtu in format: nic=mtu, nic2=mtu,...
def nic_mtu():
    returnstring = ""
    nics = psutil.net_if_stats()
    for nic in nics:
        returnstring += "{}={},".format(nic, nics[nic].mtu)
    return returnstring[:-1]

#All nic up status in format: nic=isup, nic2=isup,...
#Testing has showed that unplugging the cable does make the returned value flip to False. Haven't tested Wifi though.
def nic_isup():
    returnstring = ""
    nics = psutil.net_if_stats()
    for nic in nics:
        returnstring += "{}={},".format(nic, nics[nic].isup)
    return returnstring[:-1]

#Convert [n] bit/s into appropriately prefixed units. I.e. 7649 becomes 7,46 Kbit/see
def humanreadable(size):
    byteSuffixes = ['bit/s', 'Kbit/s', 'Mbit', 'Gbit', 'Tbit', 'Pbit']
    i = 0
    while size >= 1024 and i < len(byteSuffixes) - 1:
        size /= 1024.
        i += 1
    f = ('%.2f' % size).rstrip('0').rstrip('.')
    return '{} {}'.format(f, byteSuffixes[i])
