import configparser
import os
import time
import sys

config = configparser.ConfigParser()
basepath = os.path.dirname(os.path.realpath(__file__)) + '/'
config.read(basepath + 'statistics.ini')
config['statistics']['calls'] = str(int(config['statistics']['calls']) + 1)

config.add_section(config['statistics']['calls'])
config[config['statistics']['calls']]["time"] = time.asctime(time.localtime(time.time()))
config[config['statistics']['calls']]["text"] = sys.argv[1]
with open(basepath + 'statistics.ini', "w") as save:
	config.write(save)