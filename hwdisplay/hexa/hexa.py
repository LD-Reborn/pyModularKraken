import time
import psutil
import math
import pulsectl
#dependency ---> pip3 import gputil
import GPUtil
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
	datapoints[pName].append(pValue)
	if len(datapoints[pName]) > 100:
		datapoints[pName].pop(0)

def requestalldata(pVar):
	time1 = time.time()
	print("debug@requestalldata: entry")
	global inQueue, outQueue, display, target, packets, cpu, cpu_all, ram_percent, ram_total, gpu_utilization, gpu_memused, gpu_memusedPercent, gpu_temp, nic_address, nic_io, nic_linkspeed, nic_mtu, nic_isup
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
	#Currently implemented:
	#	"cpu" "cpu_all" "cpu_numcores"
	#	"ram_percent" "ram_total" "ram_used"
	#	"gpu_name" "gpu_temp" "gpu_utilization" "gpu_memused" "gpu_memtotal" "gpu_memusedPercent"
    #	"nic_address" "nic_io" "nic_linkspeed" "nic_mtu" "nic_isup"
	request = "cpu,cpu_all,ram_percent,ram_total,gpu_utilization,gpu_memused,gpu_memusedPercent,gpu_temp,nic_address,nic_io,nic_linkspeed,nic_mtu,nic_isup"
	#request = "cpu,cpu_all,ram_percent,ram_total,gpu_utilization"
	packets.append(id)
	# outQueue.put makes CPU utilization on all cores rise to 25% if start.py is run in VS code. In terminal this does not happen. WTF?
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
						data = read[1][3][13:].decode("utf-8").split("|")
				except Exception as e:
					continue
				cpu = data[0]
				cpu_all = data[1][1:-1].split(", ")
				ram_percent = data[2]
				ram_total = data[3]
				gpu_utilization = data[4]
				gpu_memused = data[5]
				gpu_memusedPercent = data[6]
				gpu_temp = data[7]
				nic_address = data[8]
				nic_io = data[9]
				nic_linkspeed = data[10]
				nic_mtu = data[11]
				nic_isup = data[12]
				addDatapoint("cpu", cpu)
				addDatapoint("gpu", gpu_utilization)
				addDatapoint("ram", ram_percent)
				addDatapoint("gpu_temp", gpu_temp)
				#addDatapoint("cpu_temp", cpu_temp) # todo add cpu_temp to hardwareinfo
				addDatapoint("nic_io", nic_io)
#				datapoints = {"cpu": [], "gpu": [], "ram": [], "nic": [], "cpu_temp": [], "gpu_temp": [], "nic_io": []}

			#---> ['conmanager', ('recvdata', 'ifd', 'intermetry', b"hardwareinfo:b'd\\xa3(\\xf3\\xb7\\x85*\\x1a':50.0|[54.5, 44.4, 55.6, 54.5, 50.0, 50.0, 55.6, 45.5, 50.0, 70.0, 60.0, 58.3, 45.5, 44.4, 33.3, 36.4]|34.9|16719659008|12.0|519.0|6.33544921875|49.0|lo=127.0.0.1,enp5s0=192.168.2.166,ztrf2vegnr=192.168.192.101,ztr2qy64cl=10.147.20.101,anbox0=192.168.250.1|lo=1184531/1184531,enp5s0=58362229/3353709404,enp6s0=0/0,ztrf2vegnr=15511/190354,ztr2qy64cl=15478/500,anbox0=0/0|lo=0,enp5s0=1000,enp6s0=0,ztrf2vegnr=10,ztr2qy64cl=10,anbox0=65535|lo=65536,enp5s0=1500,enp6s0=1500,ztrf2vegnr=2800,ztr2qy64cl=2800,anbox0=1500|lo=True,enp5s0=True,enp6s0=False,ztrf2vegnr=True,ztr2qy64cl=True,anbox0=False|")]
			print(read)
	print("debug@requestalldata: exit. Time taken: {}".format(time.time() - time1))

def makeGraph(pData, pHeight):
	width = len(pData)
	if width == 0:
		return False
	dividers=["▏", "▔", "▕", "▁"]
	nth = 100 / pHeight
	returnString = "{}\n".format(dividers[3] * (width + 2))
	for i in range(pHeight):
		returnString += dividers[0]
		for j in pData:
			#temp = 50 - 10 * (10 - 9 - 1)
			temp = float(j) - nth * (pHeight - i - 1)
			if temp > nth:
				returnString += usageramps[7]
			elif temp >= 0:
				print("test:")
				print(temp)
				print(nth)
				print(int(temp / (nth / 7)))
				returnString += usageramps[int(temp / (nth / 7))]
			else:
				returnString += " "
		returnString += "{}\n".format(dividers[2])
	returnString += dividers[1] * (width + 2)
	return returnString


def cpuPercent(pVar):
	global cpu
	try: # Make sure variable is initialized. Otherwise expect uncaught exception.
		cpu
	except:
		return False
	pVar.set("{}%".format(cpu))

def cpuPercentGraph(pVar):
	global datapoints
	try: # Make sure variable is initialized. Otherwise expect uncaught exception.
		datapoints["cpu"]
	except:
		return False
	graph = makeGraph(datapoints["cpu"][-15:], 4)
	pVar.set(graph)

def cpuAll(pVar):
	global cpu_all
	try:
		cpu_all
	except:
		return False
#	print("debug@cpupercent: WIP")
	ramps = ""
	for n in cpu_all:
		n = float(n)
		ramps = "{}{}".format(ramps, usageramps[int(n / 12.5)])
	
	pVar.set(ramps)

def gpuPercent(pVar):
	global gpu_utilization
	try:
		gpu_utilization
	except:
		return False
	setString = "{:.1f}%".format(float(gpu_utilization))
	if len(setString) < 5:
		setString = " {}".format(setString)
	pVar.set(setString)

def gpuMemused(pVar):
	global gpu_memused, gpu_memusedPercent
	try:
		gpu_memused
		gpu_memusedPercent
	except:
		return False
	pVar.set("Mem: {:.1f}MB = {:.1f}%".format(float(gpu_memused), float(gpu_memusedPercent)))

def gpuTemp(pVar):
	global gpu_temp
	try:
		gpu_temp
	except:
		return False
	pVar.set("{}°C".format(gpu_temp))

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
	global ram_percent
	try:
		ram_percent
	except:
		return False
	pVar.set("{:.1f}%".format(float(ram_percent)))

def ramPercentGraph(pVar):
	global datapoints
	try: # Make sure variable is initialized. Otherwise expect uncaught exception.
		datapoints["gpu"]
	except:
		return False
	graph = makeGraph(datapoints["ram"][-15:], 4)
	pVar.set(graph)

def nic(pVar):
	print("debug@cpupercent: NIY")

def tcpu(pVar):
	print("debug@cpupercent: NIY")

def tgpu(pVar):
	print("debug@cpupercent: NIY")

def tsys(pVar):
	print("debug@cpupercent: NIY")


