import time
import psutil
import math
import pulsectl
#dependency ---> pip3 import gputil
import GPUtil
import json # for string deserialization
import random

usageramps=("▁", "▂", "▃", "▄", "▅", "▆", "▇", "█", "█") #<--- Duplicate at the end to prevent tuple index out of range error, while keeping maths simple / reducing number of instructions 

def initController(pInQueue, pOutQueue, pDisplay, pTarget):
	global inQueue, outQueue, display, target, packets, datapoints
	inQueue = pInQueue
	outQueue = pOutQueue
	display = pDisplay
	target = pTarget
	packets = []
	datapoints = {"cpu": [], "gpu": [], "ram": [], "nic": [], "cpu_temp": [], "gpu_temp": [], "nic_io": []}

def addDatapoint(pName, pValue):
	global datapoints
	try:
		datapoints[pName]
	except:
		datapoints[pName] = []
	datapoints[pName].append(pValue)
	if len(datapoints[pName]) > 100:
		datapoints[pName].pop(0)

def requestalldata(pVar):
	time1 = time.time()
	print("debug@requestalldata: entry")
	global inQueue, outQueue, display, target, packets, values
	values = {}
	id = random.randbytes(4)
	# For a list of currently implemented requestable datapoints, see hardwareinfo.py
	request = "cpu|cpu_all|ram_percent|ram_used|ram_total|gpu|nic_address|nic_io|nic_linkspeed|nic_mtu|nic_isup|sensors.temp|sensors.fan|sensors.power"
	packets.append(id)
	# outQueue.put makes CPU utilization on all cores rise to 25% if start.py is run in VS code. In terminal this does not happen. Probably because VS code runs as a snap.
	outQueue.put({"dstModule": "intermetry", "dstDevice": target, "data": "hardwareinfo:{}".format(request), "packetID": id})
	while not inQueue.empty():
		time.sleep(0.01)
		read = inQueue.get()
		if len(packets) > 0:
			if read[0] == "conmanager" and read[1][0] == "recvdata" and read[1][1] == target:
				try:
					split = read[1][3].decode("utf-8").split(":")
					index = packets.index(read[1][4]) # If packetID not in packets, error is thrown. Existance of packet is assured here.
					packets.remove(read[1][4])
					if split[0] == "hardwareinfo":
						#data = read[1][3][13:].decode("utf-8").split("|")
						data = json.loads(read[1][3][13:].decode("utf-8"))
				except Exception as e:
					continue
				for element in data:
					addDatapoint(element, data[element])
					values[element] = data[element]
	print("debug@requestalldata: exit. Time taken: {}".format(time.time() - time1))

def makeGraph(pData, pHeight):
	width = len(pData)
	if width == 0:
		return ""
	dividers=["▏", "▔", "▕", "▁"]
	nth = 100 / pHeight
	returnString = "{}\n".format(dividers[3] * (width + 2))
	for i in range(pHeight):
		returnString += dividers[0]
		for j in pData:
			temp = float(j) - nth * (pHeight - i - 1)
			if temp > nth:
				returnString += usageramps[7]
			elif temp >= 0:
				returnString += usageramps[int(temp / (nth / 7))]
			else:
				returnString += " "
		returnString += "{}\n".format(dividers[2])
	returnString += dividers[1] * (width + 2)
	return returnString


def cpuPercent(pVar):
	global values
	try: # Make sure variable is initialized. Otherwise expect uncaught exception.
		values["cpu"]
	except:
		return False
	pVar.set("{}%".format(values["cpu"]))

def cpuPercentGraph(pVar):
	global datapoints
	try: # Make sure variable is initialized. Otherwise expect uncaught exception.
		datapoints["cpu"]
	except:
		return False
	graph = makeGraph(datapoints["cpu"][-15:], 4)
	pVar.set(graph)

def cpuAll(pVar):
	global values
	try:
		values["cpu_all"]
	except:
		return False
	ramps = ""
	for n in values["cpu_all"]:
		n = float(n)
		ramps = "{}{}".format(ramps, usageramps[int(n / 12.5)])
	
	pVar.set(ramps)

def gpuPercent(pVar):
	global values
	gpuID = 0 # Change this if you have multiple GPUs and it isn't picking up the correct one. Default: 0
	try:
		gpuBusy = values["gpu"][gpuID]["sensors"]["gpu_busy_percent"]
	except:
		return False
	pVar.set("{: >2}%".format(gpuBusy))

def gpuMemused(pVar):
	global values
	gpuID = 0 # Change this if you have multiple GPUs and it isn't picking up the correct one. Default: 0
	try:
		vramUsed = values["gpu"][gpuID]["sensors"]["mem_info_vram_used"]
		vramTotal = values["gpu"][gpuID]["sensors"]["mem_info_vram_total"]
	except:
		return False
	pVar.set("{:.0f} / {:.0f} MB".format(int(vramUsed) / 1048576, int(vramTotal) / 1048576))
	
def gpuMemusedPercent(pVar):
	global values
	gpuID = 0 # Change this if you have multiple GPUs and it isn't picking up the correct one. Default: 0
	try:
		vramUsed = values["gpu"][gpuID]["sensors"]["mem_info_vram_used"]
		vramTotal = values["gpu"][gpuID]["sensors"]["mem_info_vram_total"]
	except:
		return False
	pVar.set("{: >2}%".format(int(int(vramUsed) / int(vramTotal) * 100)))

def gpuPercentGraph(pVar):
	global datapoints
	gpuID = 0 # Change this if you have multiple GPUs and it isn't picking up the correct one. Default: 0
	try: # Make sure variable is initialized. Otherwise expect uncaught exception.
		
		datapointsGPUUtil = []
		for datapoint in datapoints["gpu"]:
			datapointsGPUUtil.append(datapoint[gpuID]["sensors"]["gpu_busy_percent"])
		
	except Exception as e:
		return False
	graph = makeGraph(datapointsGPUUtil[-15:], 4)
	pVar.set(graph)

def ramPercent(pVar):
	global values
	try:
		values["ram_percent"]
	except:
		return False
	pVar.set("{:.1f}%".format(float(values["ram_percent"])))

def ramUsage(pVar):
	global values
	try:
		values["ram_percent"]
		values["ram_total"]
		values["ram_used"]
	except:
		return False
	pVar.set("{:.2f} / {:.2f} GB".format(int(values["ram_used"]) / 1073741824, int(values["ram_total"]) / 1073741824))

def ramPercentGraph(pVar):
	global datapoints
	try: # Make sure variable is initialized. Otherwise expect uncaught exception.
		datapoints["ram_percent"]
	except:
		return False
	graph = makeGraph(datapoints["ram_percent"][-15:], 4)
	pVar.set(graph)

def nic1Data(pVar, pNic = "enp5s0"):
	try: # Make sure variable is initialized. Otherwise expect uncaught exception.
		values["nic_address"], values["nic_io"], values["nic_mtu"], values["nic_isup"], values["nic_linkspeed"]
	except:
		return False
	try: # Try to extract enp5s0's address from string containing %nicname%=%nicaddress%,%nicname%=%nicaddress,[...]
		address = values["nic_address"].split("{}=".format(pNic))[1].split(",")[0]
	except: # If it can't be found, set it to NaN
		address = "unknown"
	try: # same procedure but with nic_mtu
		mtu = values["nic_mtu"].split("{}=".format(pNic))[1].split(",")[0]
	except: # If it can't be found, set it to NaN
		mtu = "NaN"
	try: # same procedure but with nic_linkspeed
		linkspeed = humanreadable(float(values["nic_linkspeed"].split("{}=".format(pNic))[1].split(",")[0]) * 1000000)
	except: # If it can't be found, set it to NaN
		linkspeed = "NaN"
	try: # same procedure but with nic_isup
		isup = values["nic_isup"].split("{}=".format(pNic))[1].split(",")[0]
	except: # If it can't be found, set it to NaN
		isup = "False"
	pVar.set("{}\n{} @ {}".format(address, linkspeed, mtu))

def nic1io(pVar, pNic = "enp5s0"):
	try: # Make sure variable is initialized. Otherwise expect uncaught exception.
		values["nic_io"]
	except:
		return False
	try:
		io_last2 = datapoints["nic_io"][-1].split("{}=".format(pNic))[1].split(",")[0]
		io_last1 = datapoints["nic_io"][-2].split("{}=".format(pNic))[1].split(",")[0]
		up = humanreadable(float(io_last2.split("/")[0]) - float(io_last1.split("/")[0]))
		down = humanreadable(float(io_last2.split("/")[1]) - float(io_last1.split("/")[1]))
		if len(up) < 13: # When it changes length, the whole label shifts. So bump it to a certain length.
			up = " " * (13 - len(up)) + up
		if len(down) < 13:
			down = " " * (13 - len(down)) + down
	except: # If it can't be found, set it to NaN
		up = "NaN"
		down = "NaN"
	pVar.set("{}▵\n{}▿".format(up, down))

def nic2Data(pVar):
	nic1Data(pVar, "enp6s0")

def nic2io(pVar):
	nic1io(pVar, "enp6s0")

def tcpu(pVar):
	global values
	cputempSensorgroup = "k10temp"
	cputempSensorID = "Tctl"
	try:
		values["sensors.temp"]
	except:
		return False
	pVar.set("{:.0f}°C".format(int(values["sensors.temp"][cputempSensorgroup]["content"][cputempSensorID]["value"]) / 1000))

def tgpu(pVar):
	global values
	gputempSensorgroup = "amdgpu"
	gputempSensorID = "junction"
	try:
		values["sensors.temp"]
	except:
		return False
	pVar.set("{:.0f}°C".format(int(values["sensors.temp"][gputempSensorgroup]["content"][gputempSensorID]["value"]) / 1000))

def tgpuMem(pVar):
	global values
	gputempSensorgroup = "amdgpu"
	gputempSensorID = "mem"
	try:
		values["sensors.temp"]
	except:
		return False
	pVar.set("{:.0f}°C".format(int(values["sensors.temp"][gputempSensorgroup]["content"][gputempSensorID]["value"]) / 1000))

def tgpuPPT(pVar):
	global values
	gputempSensorgroup = "amdgpu"
	gputempSensorID = "PPT"
	try:
		values["sensors.power"]
	except:
		return False
	pVar.set("{} W".format(int(values["sensors.power"][gputempSensorgroup]["content"][gputempSensorID]["value"]) / 1000000))

def tsys(pVar):
	global values
	tempSensorgroup = "gigabyte_wmi"
	tempSensorID = "1"
	try:
		values["sensors.temp"]
	except:
		return False
	pVar.set("{:.0f}°C".format(int(values["sensors.temp"][tempSensorgroup]["content"][tempSensorID]["value"]) / 1000))




#Convert [n] bit/s into appropriately prefixed units. I.e. 7649 becomes 7,46 Kbit/sec
def humanreadable(size):
    byteSuffixes = ['bit/s', 'Kbit/s', 'Mbit', 'Gbit', 'Tbit', 'Pbit']
    i = 0
    while size >= 1000 and i < len(byteSuffixes) - 1:
        size /= 1000
        i += 1
    f = ('%.2f' % size).rstrip('0').rstrip('.')
    return '{} {}'.format(f, byteSuffixes[i])

#Convert [n] bit/s into appropriately prefixed units. I.e. 7649 becomes 7,46 Kbit/sec
def humanreadable1024(size):
    byteSuffixes = ['bit/s', 'KiBit/s', 'MiBit', 'GiBit', 'TiBit', 'PiBit']
    i = 0
    while size >= 1024 and i < len(byteSuffixes) - 1:
        size /= 1024
        i += 1
    f = ('%.2f' % size).rstrip('0').rstrip('.')
    return '{} {}'.format(f, byteSuffixes[i])