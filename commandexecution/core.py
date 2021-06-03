#from xml.dom.minidom import parse
from multiprocessing import Process
from datetime import datetime
import xml.dom.minidom
import configparser
#import threading
import string
import time
import os
import re

config = configparser.ConfigParser()
basepath = os.path.dirname(os.path.realpath(__file__)) + '/'
config.read(basepath + 'config.ini')
var = config['base']['var']
name = config['base']['name']
callsign  = config['base']['callsign']
commandfile = basepath + config['base']['commandfile']
ownername  = config['base']['ownername']
scriptpath = basepath + config['base']['scriptpath'] + '/'
speechtimeout = config['base']['speechtimeout']

dateLastInput = None
text = ""

DOMTree = xml.dom.minidom.parse(commandfile)
collection = DOMTree.documentElement

#elements = collection.getElementsByTagName("sub")

pointer = collection

#for element in elements:
#	print("int: %s" % element.getAttribute("int"))
#	text = element.getElementsByTagName('text')
#	for temp in text:
#		print("text: %s" % temp.childNodes[0].data)
#	if element.hasAttribute("alias"):
#		alias = element.getElementsByTagName('alias')[0]
#		print("alias: %s" % alias.childNodes[0].data)
	#rating = movie.getElementsByTagName('rating')[0]
	#print "Rating: %s" % rating.childNodes[0].data
	#description = movie.getElementsByTagName('description')[0]
	#print "Description: %s" % description.childNodes[0].data

def input(pText):
	if pText == "": return 1
	global pointer
	global text
	text = pText
	print("-{}".format(pText))
	#elements = pointer.getElementsByTagName("sub")
	#child = pointer.firstChild
	#while child != None:
	#	print("int: {}".format(child))
	#	child = pointer.nextSibling
	
	for node in pointer.childNodes:
		#print(node)
		if node.nodeName != "#text":
			res = searchValue(node, "text", pText)
			if res != None:
				pointer = node
				
				jmpnode = searchNode(node, "jumpto")
				
				commandnode = searchNode(node, "command")
				if commandnode != None:
					command = commandnode.firstChild.data.strip()
					#executeCommand(command)
					p = Process(target = executeCommand, args = (command,))
					p.start()
					if commandnode.attributes.length >= 1 and commandnode.attributes.item(0).name == "nobreak":
						#print("nobreak!")
						return input(pText[res[1].end():].strip())
					else:
						#print("break!")
						resetPointer()
						return
				
				if jmpnode != None:
					print("!jmpnode")
					tags = collection.getElementsByTagName("jumplabel")
					for label in tags:
						if label.firstChild.data.strip() == jmpnode.firstChild.data.strip():
							pointer = label.parentNode
				
				return input(pText[res[1].end():].strip())
				
					#print(tags)
	print("No sub for '{}'".format(pText))
	return 0
	#for element in elements:
	#	print("int {}".format(element.getAttribute("int")))
	#	textnodes = element.getElementsByTagName("text")
	#	for textnode in textnodes:
	#		for child in textnode.childNodes:
	#			print("text {}".format(textnode.childNodes[0].data))



def searchNode(pNode, pName):
	for child in pNode.childNodes:
		if child.nodeName == pName:
				return child

def searchValue(pNode, pName, pValue):
	for child in pNode.childNodes:
		if child.nodeName == pName:
			text = child.childNodes[0].data
			text = parse(text)
			#print(text)
			search = re.search(text.lower(), pValue.lower())
			if search != None:
				#print("found!")
				#print(text)
				#print(pValue)
				return child, search
			#else:
				#print("not found!")
				#print(text)
				#print(pValue)

def executeCommand(pStr):
	global scriptpath
	str = parse(pStr)
	scriptpath = parse(scriptpath)
	#print(str)
	#print(re.search("py", str))
	if re.search("py", str) != None:
		pre = "python3 "
	else:
		pre = ""
	#print(pre + scriptpath + str)
	#subprocess.run(pre + scriptpath + str)
	os.system(pre + scriptpath + str)
	
def resetPointer():
	global pointer, dateLastInput
	pointer = collection
	dateLastInput = None

def parse(pText):
	temp = re.search(var, pText) != None
	try:
		while temp:
			search = re.search(var, pText)
			varname = pText[search.start() + 1 : search.end() - 1]
			pText = pText.replace(pText[search.start() : search.end()], readVar(varname))
			temp = re.search(var, pText) != None
	except:
		print("! Malformed! '{}'".format(pText))
	return pText

def readVar(pVarname):
	try:
		return parse(eval(pVarname))
	except:
		return Exception

input("Hey Felix.")
input("öffne mousepad")
print("! Done!")
