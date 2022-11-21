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
	#global inQueue, outQueue, display, target, packets, sensors_temperatures, sensors_fans, cpu, cpu_all, ram_percent, ram_total, gpu_utilization, gpu_memused, gpu_memusedPercent, gpu_memtotal, gpu_temp, nic_address, nic_io, nic_linkspeed, nic_mtu, nic_isup
	global inQueue, outQueue, display, target, packets, values
	values = {}
	#cpu = None # Define early to prevent access on undefined variable. 
	#cpu_all = []
	#ram_percent = None
	#ram_total = None
	#gpu_utilization = None
	#gpu_memused = None
	#gpu_memusedPercent = None
	#gpu_temp = None
	#nic_address = None
	#nic_io = None
	#nic_linkspeed = None
	#nic_mtu = None
	#nic_isup = None
	#read = {dstModule: "destination module", dstDevice: "destination device", data: "data"}
	id = random.randbytes(4)
	# For a list of currently implemented requestable datapoints, see hardwareinfo.py
	request = "cpu|cpu_all|ram_percent|ram_total|gpu|nic_address|nic_io|nic_linkspeed|nic_mtu|nic_isup|sensors.temp|sensors.fan"
	packets.append(id)
	# outQueue.put makes CPU utilization on all cores rise to 25% if start.py is run in VS code. In terminal this does not happen.
	outQueue.put({"dstModule": "intermetry", "dstDevice": target, "data": "hardwareinfo:{}".format(request), "packetID": id})
	while not inQueue.empty():
		time.sleep(0.01)
		read = inQueue.get()
		if len(packets) > 0:
			#try:
			#	packets.index()
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
				print("DEBUG @ hexa -----")
				print(data)
				print("-----")
				for element in data:
					addDatapoint(element, data[element])
					values[element] = data[element]
					
				#cpu = data["cpu"] #data[0]
				#cpu_all = data["cpu_all"]#data[1][1:-1].split(", ")
				#ram_percent = data["ram_percent"]#data[2]
				#ram_total = data["ram_total"]#data[3]
				#gpu_utilization = data[""]#data[4]
				#gpu_memused = #data[5]
				#gpu_memusedPercent = #data[6]
				#gpu_memtotal = #data[7]
				#gpu_temp = #data[8]
				#nic_address = #data[9]
				#nic_io = #data[10]
				#nic_linkspeed = #data[11]
				#nic_mtu = #data[12]
				#nic_isup = #data[13]
				#sensors_temperatures = data[14]
				#sensors_fans = data[15]
				#addDatapoint("cpu", cpu)
				#addDatapoint("gpu", gpu_utilization)
				#addDatapoint("ram", ram_percent)
				#addDatapoint("gpu_temp", gpu_temp)
				##addDatapoint("cpu_temp", cpu_temp) # todo add cpu_temp to hardwareinfo
				#addDatapoint("nic_io", nic_io)
#				#datapoints = {"cpu": [], "gpu": [], "ram": [], "nic": [], "cpu_temp": [], "gpu_temp": [], "nic_io": []}

			#---> ['conmanager', ('recvdata', 'ifd', 'intermetry', b"hardwareinfo:b'd\\xa3(\\xf3\\xb7\\x85*\\x1a':50.0|[54.5, 44.4, 55.6, 54.5, 50.0, 50.0, 55.6, 45.5, 50.0, 70.0, 60.0, 58.3, 45.5, 44.4, 33.3, 36.4]|34.9|16719659008|12.0|519.0|6.33544921875|49.0|lo=127.0.0.1,enp5s0=192.168.2.166,ztrf2vegnr=192.168.192.101,ztr2qy64cl=10.147.20.101,anbox0=192.168.250.1|lo=1184531/1184531,enp5s0=58362229/3353709404,enp6s0=0/0,ztrf2vegnr=15511/190354,ztr2qy64cl=15478/500,anbox0=0/0|lo=0,enp5s0=1000,enp6s0=0,ztrf2vegnr=10,ztr2qy64cl=10,anbox0=65535|lo=65536,enp5s0=1500,enp6s0=1500,ztrf2vegnr=2800,ztr2qy64cl=2800,anbox0=1500|lo=True,enp5s0=True,enp6s0=False,ztrf2vegnr=True,ztr2qy64cl=True,anbox0=False|")]
			#print(read)
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
#	print("debug@cpupercent: WIP")
	ramps = ""
	for n in values["cpu_all"]:
		n = float(n)
		ramps = "{}{}".format(ramps, usageramps[int(n / 12.5)])
	
	pVar.set(ramps)

def gpuPercent(pVar):

	global values
	gpuID = 0 # Change this if you have multiple GPUs and it isn't picking up the correct one. Default: 0
	try:
		values["gpu"]
	except:
		return False
	pVar.set("{:.2f}%".format(int(values["gpu"][gpuID]["sensors"]["gpu_busy_percent"]) / 1000))

#	global gpu_utilization
#	try:#
#		gpu_utilization
#	except:
#		return False
#	setString = "{:.1f}%".format(float(gpu_utilization))
#	if len(setString) < 5:
#		setString = " {}".format(setString)
#	pVar.set(setString)

def gpuMemused(pVar):
	global gpu_memused, gpu_memtotal
	try:
		gpu_memused
		gpu_memtotal
	except:
		return False
	pVar.set("{:d} / {:d} MB".format(int(float(gpu_memused)), int(float(gpu_memtotal))))


def gpuPercentGraph(pVar):
	global datapoints
	try: # Make sure variable is initialized. Otherwise expect uncaught exception.
		datapoints["gpu"]
	except:
		return False
	graph = makeGraph(datapoints["gpu"][-15:], 4)
	pVar.set(graph)


def ramPercent(pVar):
	#ram_percent = data[2]
	#ram_total = data[3]
	global values
	try:
		values["ram_percent"]
	except:
		return False
	pVar.set("{:.1f}%".format(float(values["ram_percent"])))

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
	print("debug@cpupercent: NIY")

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
	pVar.set("{:.2f}°C".format(int(values["sensors.temp"][cputempSensorgroup]["content"][cputempSensorID]["value"]) / 1000))

def tgpu(pVar):
	global values
	gputempSensorgroup = "amdgpu"
	gputempSensorID = "junction"
	try:
		values["sensors.temp"]
	except:
		return False
	pVar.set("{:.2f}°C".format(int(values["sensors.temp"][gputempSensorgroup]["content"][gputempSensorID]["value"]) / 1000))

def tsys(pVar):
	print("debug@cpupercent: NIY")



#Convert [n] bit/s into appropriately prefixed units. I.e. 7649 becomes 7,46 Kbit/see
def humanreadable(size):
    byteSuffixes = ['bit/s', 'Kbit/s', 'Mbit', 'Gbit', 'Tbit', 'Pbit']
    i = 0
    while size >= 1000 and i < len(byteSuffixes) - 1:
        size /= 1000
        i += 1
    f = ('%.2f' % size).rstrip('0').rstrip('.')
    return '{} {}'.format(f, byteSuffixes[i])

#Convert [n] bit/s into appropriately prefixed units. I.e. 7649 becomes 7,46 Kbit/see
def humanreadable1024(size):
    byteSuffixes = ['bit/s', 'KiBit/s', 'MiBit', 'GiBit', 'TiBit', 'PiBit']
    i = 0
    while size >= 1024 and i < len(byteSuffixes) - 1:
        size /= 1024
        i += 1
    f = ('%.2f' % size).rstrip('0').rstrip('.')
    return '{} {}'.format(f, byteSuffixes[i])