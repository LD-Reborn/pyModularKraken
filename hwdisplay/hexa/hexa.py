import time
import psutil
import netifaces
import math
import pulsectl
#dependency ---> pip3 import gputil
import GPUtil
import random

usageramps=("▁", "▂", "▃", "▄", "▅", "▆", "▇", "█", "█") #<--- Duplicate at the end to prevent tuple index out of range error, while keeping maths simple / reducing number of instructions 

def initController(pInQueue, pOutQueue, pDisplay, pTarget):
	global inQueue, outQueue, display, target, packets
	inQueue = pInQueue
	outQueue = pOutQueue
	display = pDisplay
	target = pTarget
	packets = []

def requestalldata(pVar):
	global inQueue, outQueue, display, target, packets
	#read = {dstModule: "destination module", dstDevice: "destination device", data: "data"}
	id = random.randbytes(8)
	#Currently implemented:
	#	"cpu" "cpu_all" "cpu_numcores"
	#	"ram_percent" "ram_total" "ram_used"
	#	"gpu_name" "gpu_temp" "gpu_utilization" "gpu_memused" "gpu_memtotal" "gpu_memusedPercent"
    #	"nic_address" "nic_io" "nic_linkspeed" "nic_mtu" "nic_isup"
	request = "cpu,cpu_all,ram_percent,ram_total,gpu_utilization,gpu_memused,gpu_memusedPercent,gpu_temp,nic_address,nic_io,nic_linkspeed,nic_mtu,nic_isup"
	packets.append(id)
	outQueue.put({"dstModule": "intermetry", "dstDevice": target, "data": "hardwareinfo:{}:{}".format(id, request)})
	if not inQueue.empty():
		read = inQueue.read()
		if len(packets) > 0:
			#try:
			#	packets.index()
			print(read)
def cpupercent(pVar):
	print("debug@cpupercent: WIP")
#	ramps = ""
#	for n in psutil.cpu_percent(percpu=True):
#		ramps = "{}{}".format(ramps, usageramps[int(n / 12.5)])
#	
#	pVar.set(ramps)

def gpupercent(pVar):
	print("debug@cpupercent: WIP")
	pVar.set("GPU: {}".format(random.random()))

def rampercent(pVar):
	print("debug@cpupercent: NIY")

def nic(pVar):
	print("debug@cpupercent: NIY")

def tcpu(pVar):
	print("debug@cpupercent: NIY")

def tgpu(pVar):
	print("debug@cpupercent: NIY")

def tsys(pVar):
	print("debug@cpupercent: NIY")


