# pyModularKraken
## What is pyModularKraken? (Formerly called pyMoShP or DiShSOAP)

pyModularKraken is a networking framework that allows you to skip **as many steps** as possible when implementing communication between devices.

This allows you to focus on other things like the functions you actually want to implement.
Meanwhile you get MANY upsides like being able to add devices, modules, etc. and configuring them in close to no-time and with as close of an experience to "copy, paste and hit the ground ~~running~~ coding" as possible!

## How does this magic work?
This project is not a single blob of spaghetti code. It is rather 🌠 a few smaller blobs of spaghetti code 🌠 working together as modules.
Each module has its own tasks / purposes and they all work independently in different threads.

Let me give you a brief explanation to some of the base modules:
	intermetry: can supply you with system data like CPU, RAM, and GPU utilization, as well as temperature.
	conmanager: establishes connections between devices and exposes functionality for sending to and receiving data from said devices.
	core: is the middle man that passes requests between modules, thus allowing for them to communicate with each other.

## How does communication look like?
Before I actually get more technical, let's go through the possible scenarios.

	1. Module A requests something from module B. (Both on the same device.)
		A ---> core ---> B
		B processes the request and sends an answer back to A.
		A <--- core <--- B

	2. Module A requests something from module B. (Both are on <b>separate</b> devices.)
		The () represent the boundaries of the individual devices.
		(A ---> core ---> conmanager) ---> (conmanager ---> core ---> B)
		B processes the request and sends an answer back to A.
		(A <--- core <--- conmanager) <--- (conmanager <--- core <--- B)

Now that we have visualized those two scenarios, let me repeat them, but with actual packet contents.
First of all, let's give the modules and devices more realistic names.
	Module A    is now    mymodule
	Module B    is now    intermetry
	
	Device 1    is now    Bob
	Device 2    is now    Alice

	1. mymodule requests some info about CPU and RAM from intermetry. (Both on same device.)
		mymodule ---> core: ("intermetry", "hardwareinfo:1:cpu,cpu_all,ram_percent,ram_total,ram_used")
		core ---> intermetry: ("mymodule", "hardwareinfo:1:cpu,cpu_all,ram_percent,ram_total,ram_used")
		
