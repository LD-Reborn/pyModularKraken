from cmath import pi
from sys import displayhook
import time
import psutil
import netifaces
import math
import pulsectl
#dependency ---> pip3 import gputil
import GPUtil
import random

usageramps=("▁", "▂", "▃", "▄", "▅", "▆", "▇", "█", "█") #<--- Duplicate at the end to prevent tuple index out of range error, while keeping maths simple / reducing number of instructions 

def initController(pInQueue, pOutQueue, pDisplay):
	global inQueue, outQueue, display
	inQueue = pInQueue
	outQueue = pOutQueue
	display = pDisplay

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


