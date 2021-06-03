import configparser
import threading
import os
import sys
import re

param = " ".join(sys.argv).lower()
split = re.compile("(a|o)nd").split(param)#param.split(" ")
print(split)
config = configparser.ConfigParser()
basepath = os.path.dirname(os.path.realpath(__file__)) + '/'
config.read(basepath + 'run.ini')

def runcommand():
	os.system(command)

print("!run.py")
#for word in split:
#	print(split)
#	for entry in config:
#		print(entry)
#		if re.search(entry['regex'], split):
#			print(split)

for word in split:
	print("word: {}".format(word))
	for i in range(1, len(config)):
		regex = config[str(i)]["regex"]
		command = config[str(i)]["command"]
		print(regex)
		print(command)
		if re.search(regex, word) != None:
			print("-found")
			print(regex)
			print(word)
			threading.Thread(target=runcommand).start()
			#os.system(command)

#os.system(sys.argv[1])