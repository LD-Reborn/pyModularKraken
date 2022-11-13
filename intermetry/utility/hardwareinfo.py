import psutil
#dependency ---> pip3 install gputil
import GPUtil
import sys
import os
sys.path.append("../..")
from log.log import *
import time # for debugging

def parseRequest(pText):
    global gpus
    funcmap = {"sensors_temperatures": sensors_temperatures, "sensors_fans": sensors_fans, "cpu": cpu, "cpu_all": cpu_all, "cpu_numcores": cpu_numcores, "ram_percent": ram_percent, "ram_total": ram_total, "ram_used": ram_used, "gpu_name": gpu_name, "gpu_temp": gpu_temp, "gpu_utilization": gpu_utilization, "gpu_memused": gpu_memused, "gpu_memtotal": gpu_memtotal, "gpu_memusedPercent": gpu_memusedPercent, "nic_address": nic_address, "nic_io": nic_io, "nic_linkspeed": nic_linkspeed, "nic_mtu": nic_mtu, "nic_isup": nic_isup}
    # old request style:
    #   cpu,cpu_all,cpu_numcores,sensors_fans,gpu_name,gpu_temp,gpu_utilization...
    #   
    # 
    # new request style:
    #   cpu|cpu_all|cpu_numcores|sensors_fans|gpu.0.name|gpu.0.temp|gpu.0.utilization
    # 
    # sensors_fans and gpu_temp will be replaced by hwmon readouts!
    #
    requests = pText.split(",")
    returnstring = ""
    if pText.find("gpu") > -1: # performance optimization
        #gpus = GPUtil.getGPUs() # Takes around 0.1 seconds to execute and causes lag spikes in Minecraft. Also Nvidia only.
        gpus = getGPUs() # YEE HAW own implementation it is! +100% supported vendors; (hopefully) -95% lag
    for request in requests:
        time1 = time.time()
        try:
            returnstring += "{}|".format(funcmap[request]())
        except Exception as msg:
            errout("HARDWAREINFO: unable to parse requested hardware info {}. Error: {}".format(request, msg))
        print("DEBUG@hardwareinfo request time {} for request {}".format(time.time() - time1, request))
    return returnstring

#All temperature values from psutil
def sensors_temperatures():
    return psutil.sensors_temperatures()

#All fanspeed values from psutil
def sensors_fans():
    return psutil.sensors_fans()


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

#read all sensors
def sensors_read():
    try: # Check for the presence of hwmon. This should expose various types of data like fan RPM, fan PWM 0-255, and temperatures.
        directory = os.listdir("/sys/class/hwmon")
    except:
        return False
    readout = []
    for sensorgroup in directory:
        sensors = {}
        #gpu["fan"] = {}
        #gpu["power"] = {}
        #gpu["frequency"] = {}
        #gpu["temperature"] = {}
        dircontent = os.listdir("/sys/class/hwmon/{}".format(sensorgroup))
        for element in dircontent:
            if element[0:3] == "fan" and element[-6:] == "_input": # check if element == fan*_input
                fanID = element[3:].split("_")[0]
                # fanX_enable ---> indicates whether the fan is spinning
                # fanX_input = fanX_target --> contains fan RPM
                # fanX_min
                # fanX_max
                fan_enable = __readfile("/sys/class/hwmon/{}/fan{}_enable".format(sensorgroup, fanID))
                fan_rpm = __readfile("/sys/class/hwmon/{}/fan{}_input".format(sensorgroup, fanID))
                fan_min = __readfile("/sys/class/hwmon/{}/fan{}_min".format(sensorgroup, fanID))
                fan_max = __readfile("/sys/class/hwmon/{}/fan{}_max".format(sensorgroup, fanID))
                sensors.append({"label": None, "type": "fan", "id": fanID, "fan_enable": fan_enable, "fan_rpm": fan_rpm, "fan_min": fan_min, "fan_max": fan_max})
            elif element[0:4] == "freq" and element[-6:] == "_label": # check if element == freq*_label
                freqID = element[4:].split("_")[0]
                # freqX_label
                # freqX_input ---> contains value of frequency
                freqLabel = __readfile("/sys/class/hwmon/{}/freq{}_label".format(sensorgroup, freqID))
                freq_value = __readfile("/sys/class/hwmon/{}/freq{}_input".format(sensorgroup, freqID))
                sensors.append({"label": freqLabel, "type": "freq", "id": freqID, "freq": freq_value})
            elif element[0:5] == "power" and element[-6:] == "_label": # check if element == power*_label
                powerID = element[5:].split("_")[0]
                # powerX_label
                # powerX_average ---> contains power draw
                # powerX_cap ---> for overclocking only.
                # powerX_cap_default ---> for overclocking only.
                # powerX_cap_max ---> for overclocking only.
                # powerX_cap_min ---> for overclocking only.
                powerLabel = __readfile("/sys/class/hwmon/{}/power{}_label".format(sensorgroup, freqID))
                power_value = __readfile("/sys/class/hwmon/{}/power{}_average".format(sensorgroup, freqID))
                power_cap = __readfile("/sys/class/hwmon/{}/power{}_cap".format(sensorgroup, freqID))
                power_cap_default = __readfile("/sys/class/hwmon/{}/power{}_cap_default".format(sensorgroup, freqID))
                power_cap_max = __readfile("/sys/class/hwmon/{}/power{}_cap_max".format(sensorgroup, freqID))
                power_cap_min = __readfile("/sys/class/hwmon/{}/power{}_cap_min".format(sensorgroup, freqID))
                sensors.append({"label": powerLabel, "type": "power", "id": powerID, "power_value": power_value, "power_cap": power_cap, "power_cap_default": power_cap_default, "power_cap_max": power_cap_max, "power_cap_min": power_cap_min})
            elif element[0:4] == "temp" and element[-6:] == "_label": # check if element == temp*_label
                tempID = element[4:].split("_")[0]
                # tempX_label
                # tempX_crit
                # tempX_crit_hyst
                # tempX_emergency
                # tempX_input ---> contains temperature in thousands of a degree
                tempLabel = __readfile("{}/temp{}_label".format(gpu["hwmonDir"], tempID))
                sensors.append({"label": tempLabel, "type": "temp", "id": tempID})
            # What about in0_input and in0_label? Idk. I can't make sense of what "in" is supposed to mean.


#list GPUs (uses sysfs files at /sys/class/drm)
def getGPUs():
    global gpus
    dircontent = os.listdir("/sys/class/drm")
    gpus = []
    for element in dircontent:
        if element[0:4] == "card":
            gpus.append({"sysfsDir": "/sys/class/drm/{}".format(element)})
    
    if len(gpus) == 0:
        return {}
    
    for gpu in gpus:
        try: # Check for the presence of hwmon. This should expose various types of data like fan RPM, fan PWM 0-255, and temperatures.
            subdir = os.listdir("{}/device/hwmon".format(gpu["sysfsDir"]))
            gpu["hwmonDir"] = "{}/device/hwmon/{}".format(gpu["sysfsDir"], subdir)
        except:
            gpu["hwmonDir"] = False
        
        if gpu["hwmonDir"]:
            gpu["fan"] = {}
            gpu["power"] = {}
            gpu["frequency"] = {}
            gpu["temperature"] = {}
            dircontent = os.listdir(gpu["hwmonDir"])
            for element in dircontent:
                if element[0:3] == "fan" and element[-6:] == "_input": # check if element == fan*_input
                    fanID = element[3:].split("_")[0]
                    # fanX_enable ---> indicates whether the fan is spinning
                    # fanX_input = fanX_target --> contains fan RPM
                    # fanX_min
                    # fanX_max
                    gpu["fan"].append(fanID)
                elif element[0:4] == "freq" and element[-6:] == "_label": # check if element == freq*_label
                    freqID = element[4:].split("_")[0]
                    # freqX_label
                    # freqX_input ---> contains value of frequency
                    freqLabel = __readfile("{}/freq{}_label".format(gpu["hwmonDir"], freqID))
                    gpu["frequency"][freqID] = {"label": freqLabel} # e.g.: gpu["frequency"] = {"1": "sclk", "2": "mclk"}
                elif element[0:5] == "power" and element[-6:] == "_label": # check if element == power*_label
                    powerID = element[5:].split("_")[0]
                    # powerX_label
                    # powerX_average ---> contains power draw
                    # powerX_cap ---> for overclocking only.
                    # powerX_cap_default ---> for overclocking only.
                    # powerX_cap_max ---> for overclocking only.
                    # powerX_cap_min ---> for overclocking only.
                    powerLabel = __readfile("{}/power{}_label".format(gpu["hwmonDir"], powerID))
                    gpu["power"][powerID] = {"label": powerLabel} # e.g.: gpu["power"] = {"1": "PPT"}
                elif element[0:4] == "temp" and element[-6:] == "_label": # check if element == temp*_label
                    tempID = element[4:].split("_")[0]
                    # tempX_label
                    # tempX_crit
                    # tempX_crit_hyst
                    # tempX_emergency
                    # tempX_input ---> contains temperature in thousands of a degree
                    tempLabel = __readfile("{}/temp{}_label".format(gpu["hwmonDir"], tempID))
                    gpu["temperature"][tempID] = {"label": tempLabel}
                # What about in0_input and in0_label? Idk. I can't make sense of what "in" is supposed to mean.
def __readfile(filename):
    handle = open(filename, "r")
    read = handle.read()
    handle.close()
    return read

#GPU name
def gpu_name():
    returnstring = ""
    for gpu in gpus:
        returnstring += "{},".format(gpu.name)
    return returnstring[:-1]

#GPU temperature in °C
def gpu_temp():
    returnstring = ""
    for gpu in gpus:
        returnstring += "{},".format(gpu.temperature)
    return returnstring[:-1]

#GPU compute utilization in percent
def gpu_utilization():
    returnstring = ""
    for gpu in gpus:
        returnstring += "{},".format(gpu.load * 100)
    return returnstring[:-1]

#Used GPU memory in MB
def gpu_memused():
    returnstring = ""
    for gpu in gpus:
        returnstring += "{},".format(gpu.memoryUsed)
    return returnstring[:-1]

#Total GPU memory in MB
def gpu_memtotal():
    returnstring = ""
    for gpu in gpus:
        returnstring += "{},".format(gpu.memoryTotal)
    return returnstring[:-1]

#Used GPU memory in percent
def gpu_memusedPercent():
    returnstring = ""
    for gpu in gpus:
        returnstring += "{},".format(gpu.memoryUsed / gpu.memoryTotal * 100)
    return returnstring[:-1]

#All nic addresses in format: nic=address,nic2=address,...
def nic_address(pGetIPv6 = False): #With nic_address(True) you'll get multiple IPv6 addresses per NIC. Not a bug.
    returnstring = ""
    nics = psutil.net_if_addrs()
    for nic in nics:
        for address in nics[nic]:
            #print("DEBUG")
            #print(nic)
            #print(address)
            if address.family.value == 2 + 8 * pGetIPv6: #2 = IPv4. 10 = IPv6
                #print("is v4\n")
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
