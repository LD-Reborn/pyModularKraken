# ModularKraken
## What is ModularKraken? (Formerly called pyMoShP or DiShSOAP)

ModularKraken is a networking framework that allows you to skip **as many steps** as possible when implementing communication between devices.

This allows you to focus on other things like the functions you actually want to implement.
Meanwhile you get MANY upsides like being able to add devices, modules, etc. and configuring them in close to no-time and with as close of an experience to "copy, paste and hit the ground ~~running~~ coding" as possible!

## How does it work?

Everything works as modules.
The core module is the most important one and is included in start.py for simplicity.

So if you run start.py what happens is:
1. All modules are loaded based on config.ini entry
2. Their respective \_\_init\_\_ function gets called.
3. Communication queues (between module and core) are passed to the module by calling initcore.
4. The run function is called and executed in its own thread.

The module now runs in its own thread, free to complete its tasks.

Some modules that come pre-packaged for convenience are:
*intermetry: supplies system data like CPU, RAM, and GPU utilization, as well as temperature.
*audiocontrol: (WIP) can be used to retrieve volume, mute, and control audio.
*conmanager: establishes connections between devices and exposes functionality for sending to and receiving data from said devices.

## How does communication look like?
Before I actually get more technical, let's visualize some scenarios.

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
	Module A    is now    ping
	Module B    is now    pong
	
	Device 1    is now    Bob
	Device 2    is now    Alice

	1. mymodule requests some info about CPU and RAM from intermetry. (Both on same device.)
		mymodule ---> core: ("intermetry", "hardwareinfo:1:cpu,cpu_all,ram_percent,ram_total,ram_used")
		core ---> intermetry: ("mymodule", "hardwareinfo:1:cpu,cpu_all,ram_percent,ram_total,ram_used")
		
