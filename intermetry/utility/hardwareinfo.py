import psutil
#dependency ---> pip3 install gputil
import GPUtil
import sys
import os
sys.path.append("../..")
#from log.log import *
import time # for debugging

def parseRequest(pText):
    global gpus
    funcmap = {
                "sensors": sensors,
                "gpu": gpu,
                "cpu": cpu,
                "cpu_all": cpu_all,
                "cpu_numcores": cpu_numcores,
                "ram_percent": ram_percent,
                "ram_total": ram_total,
                "ram_used": ram_used,
                "nic_address": nic_address,
                "nic_io": nic_io,
                "nic_linkspeed": nic_linkspeed,
                "nic_mtu": nic_mtu,
                "nic_isup": nic_isup
            }
    # old request style:
    #   cpu,cpu_all,cpu_numcores,sensors_fans,gpu_name,gpu_temp,gpu_utilization...
    #   
    # 
    # new request style:
    #   cpu|cpu_all|cpu_numcores|hwmon.1.temp1|gpu.0.name|gpu.0.mem_info_vram_used|gpu.0.mem_info_vram_total|gpu.0.gpu_busy_percent|gpu.0.mem_busy_percent...
    # 
    # Requesting "hwmon" gives the entire array/hashmap with all 'sensorgroups'.
    # "hwmon.1" gives all sensors from sensorgroup /sys/class/hwmon/hwmon1.
    # "hwmon.1.temp1" would give you just that sensor's data.
    requests = pText.split("|")
    returnstring = ""
    for request in requests:
        time1 = time.time()
        try:
            split = request.split("|")
            returnstring += "{}|".format(funcmap[split[0]](split[1:]))
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

#read all sensors (currently HWMON only)
def sensors(*args):
    try:
        if args[0][0].isdecimal(): # e.g. "hwmon.1", "hwmon.3.temp1", ...
           filter_groupid = int(args[0])
           filter_type = None
        else: # e.g. "hwmon.fans", "hwmon.temp", ...
            filter_groupid = None
            filter_type = args[0]
    except:
        filter_groupid = None
        filter_type = None
    
    try:
        if filter_groupid:
            filter_sensorlabel = args[0][1]
    except:
        filter_sensorlabel = None

    try: # Check for the presence of hwmon. This should expose various types of data like fan RPM, fan PWM 0-255, and temperatures.
        directory = os.listdir("/sys/class/hwmon")
    except:
        return False
    readout = []
    for sensorgroup in directory:
        if filter_groupid != None and sensorgroup != "hwmon{}".format(filter_groupid):
            continue
        sensors = {"group": sensorgroup, "content": []}
        loadParam("/sys/class/hwmon/{}/name".format(sensorgroup), "grouplabel", sensors)
#        print("DEBUG: {}".format(sensorgroup))
        dircontent = os.listdir("/sys/class/hwmon/{}".format(sensorgroup))
        for element in dircontent:
            try: # check for label and type filter
                if filter_type != None and not element.startswith(filter_type):
                    continue
                if filter_sensorlabel != None and not element.startswith(filter_sensorlabel):
                    continue
            except:
                pass
            # For amdgpu documentation on HWMON interfaces check: https://docs.kernel.org/gpu/amdgpu/thermal.html
            if element[0:3] == "fan" and element[-6:] == "_input": # check if element == fan*_input
                fanID = element[3:].split("_")[0]
                params = {"id": fanID, "type": "fan"}
                # fanX_enable ---> indicates whether the fan is spinning
                # fanX_input = fanX_target --> contains fan RPM
                # fanX_min
                # fanX_max
                loadParam("/sys/class/hwmon/{}/fan{}_enable".format(sensorgroup, fanID), "label", params)
                loadParam("/sys/class/hwmon/{}/fan{}_input".format(sensorgroup, fanID), "value", params)
                loadParam("/sys/class/hwmon/{}/fan{}_min".format(sensorgroup, fanID), "min", params)
                loadParam("/sys/class/hwmon/{}/fan{}_max".format(sensorgroup, fanID), "max", params)
            elif element[0:4] == "freq" and element[-6:] == "_label": # check if element == freq*_label
                freqID = element[4:].split("_")[0]
                params = {"id": freqID, "type": "freq"}
                # freqX_label
                # freqX_input ---> contains value of frequency
                loadParam("/sys/class/hwmon/{}/freq{}_label".format(sensorgroup, freqID), "label", params)
                loadParam("/sys/class/hwmon/{}/freq{}_input".format(sensorgroup, freqID), "value", params)
            elif element[0:5] == "power" and element[-6:] == "_label": # check if element == power*_label
                powerID = element[5:].split("_")[0]
                params = {"id": powerID, "type": "power"}
                # powerX_label
                # powerX_average ---> contains power draw; for amdgpu: in microWatts (e.g. 36000000 means 36 Watt)
                # powerX_cap ---> for overclocking only.
                # powerX_cap_default ---> for overclocking only.
                # powerX_cap_max ---> for overclocking only.
                # powerX_cap_min ---> for overclocking only.
                loadParam("/sys/class/hwmon/{}/power{}_label".format(sensorgroup, powerID), "label", params)
                loadParam("/sys/class/hwmon/{}/power{}_average".format(sensorgroup, powerID), "value", params)
                loadParam("/sys/class/hwmon/{}/power{}_cap".format(sensorgroup, powerID), "cap", params)
                loadParam("/sys/class/hwmon/{}/power{}_cap_default".format(sensorgroup, powerID), "cap_default", params)
                loadParam("/sys/class/hwmon/{}/power{}_cap_max".format(sensorgroup, powerID), "cap_max", params)
                loadParam("/sys/class/hwmon/{}/power{}_cap_min".format(sensorgroup, powerID), "cap_min", params)
            elif element[0:4] == "temp" and element[-6:] == "_input": # check if element == temp*_input
                tempID = element[4:].split("_")[0]
                params = {"id": tempID, "type": "temp"}
                # tempX_label
                # tempX_crit
                # tempX_crit_hyst
                # tempX_emergency
                # tempX_input ---> contains temperature; for amdgpu: in milli-degrees (e.g. 16800 means 16.8°C)
                loadParam("/sys/class/hwmon/{}/temp{}_label".format(sensorgroup, tempID), "label", params)
                loadParam("/sys/class/hwmon/{}/temp{}_input".format(sensorgroup, tempID), "value", params)
                loadParam("/sys/class/hwmon/{}/temp{}_crit".format(sensorgroup, tempID), "crit", params)
                loadParam("/sys/class/hwmon/{}/temp{}_crit_hyst".format(sensorgroup, tempID), "crit_hyst", params)
                loadParam("/sys/class/hwmon/{}/temp{}_emergency".format(sensorgroup, tempID), "emergency", params)
                loadParam("/sys/class/hwmon/{}/temp{}_alarm".format(sensorgroup, tempID), "alarm", params)
                loadParam("/sys/class/hwmon/{}/temp{}_min".format(sensorgroup, tempID), "min", params)
                loadParam("/sys/class/hwmon/{}/temp{}_max".format(sensorgroup, tempID), "max", params)
            elif element[0:2] == "in" and element[-6:] == "_label": # check if element == in*_label
                inID = element[2:].split("_")[0]
                params = {"id": inID, "type": "in"}
                # inX_label
                # inX_input ---> contains voltage
                loadParam("/sys/class/hwmon/{}/in{}_label".format(sensorgroup, inID), "label", params)
                loadParam("/sys/class/hwmon/{}/in{}_input".format(sensorgroup, inID), "value", params)
            else:
                continue

            sensors["content"].append(params)
            # What about in0_input and in0_label? Idk. I can't make sense of what "in" is supposed to mean.
        readout.append(sensors)
    return readout


#get GPU info (uses sysfs files at /sys/class/drm/card*/device/)
def gpu():
    global gpus
    dircontent = os.listdir("/sys/class/drm")
    gpus = []
    for element in dircontent: # First list all available GPUs
        if element[0:4] == "card" and element.find("-") == -1:
            gpus.append({"sysfsDir": "/sys/class/drm/{}/device".format(element)})
    for gpu in gpus:
        gpu["sensors"] = {}
        # see this for documentation: https://kernel.org/doc/html/latest/gpu/amdgpu/driver-misc.html
        trytoloadthis = ["gpu_busy_percent", "max_link_speed", "max_link_width", "mem_busy_percent", "mem_info_gtt_total", "mem_info_gtt_used", "mem_info_vis_vram_total", "mem_info_vis_vram_used", "mem_info_vram_total", "mem_info_vram_used", "mem_info_vram_vendor", "power_state", "pp_cur_state", "pp_dpm_dcefclk", "pp_dpm_fclk", "pp_dpm_mclk", "pp_dpm_pcie", "pp_dpm_sclk", "pp_dpm_socclk", "thermal_throttling_logging", "vbios_version"]
        # Explanation to some stuff even I wasn't sure at first: 
        # mem_info_gtt_*: Memory allocated / used for "graphics translation table"
        # mem_info_vis_vram_*: "visible" memory, whatever that means; in my case it did not appear to differ from mem_info_vram_* value-wise.
        # pp_dpm_fclk: Infinity fabric clock
        # pp_dpm_sclk: Shader clock
        # pp_dpm_mclk: Memory clock
        # pp_dpm_socclk: SOC clock?
        for element in trytoloadthis:
            loadParam("{}/{}".format(gpu["sysfsDir"], element), element, gpu["sensors"])
    return gpus

#Read the contents of a file into a hashmap. Pseudocode: hashmap[paramname] = read(filepath)
def loadParam(filepath, paramname, hashmap):
    try:
        read = __readfile(filepath)
        if read[-1] == "\n":
            read = read[:-1]
        hashmap[paramname] = read
    except:
        pass

def __readfile(filename):
    handle = open(filename, "r")
    read = handle.read()
    handle.close()
    return read

'''
#GPU name #legacy nvidia-smi functions that cause lag
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
'''

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

