# ModularKraken
## What is ModularKraken? (Formerly called pyMoShP or DiShSOAP)

ModularKraken is a networking framework that allows you to skip **as many steps** as possible when implementing communication between devices.

This allows you to focus on other things like the functions you actually want to implement.
Meanwhile you get MANY upsides like being able to add devices, modules, etc. and configuring them in close to no-time and with as close of an experience to "copy, paste and hit the ground ~~running~~ coding" as possible!

## How does it work?

Everything works as modules.
The core module is the most important one and is included in start.py for simplicity.

So if you run start.py what happens is:
1. All modules are individually loaded based on config.ini entry
2. Their respective \_\_init\_\_ function gets called.
3. Queues (for communication between module and core) are passed to the module.
4. The module's run function is called and executed in its own thread.

The module now runs in its own thread, free to complete its tasks.

Some modules that come pre-packaged for convenience are:
* intermetry: supplies system data like CPU, RAM, and GPU utilization, as well as temperature.
* audiocontrol: (WIP) can be used to retrieve volume, mute, and control audio.
* conmanager: establishes connections between devices and exposes functionality for sending to and receiving data from said devices.

## How does communication look like?
Before I actually get more technical, let's visualize some scenarios.

	1. Module A requests something from module B. (Both on the same device.)
		A ---> core ---> B
		B processes the request and sends an answer back to A.
		A <--- core <--- B

	2. Module A requests something from module B. (Both are on **separate** devices.)
		The () represent the boundaries of the individual devices.
		(A ---> core ---> conmanager) ---> (conmanager ---> core ---> B)
		B processes the request and sends an answer back to A.
		(A <--- core <--- conmanager) <--- (conmanager <--- core <--- B)

Now that we have visualized those two scenarios, let me repeat them, but with actual example packet contents.

	1. A sends a request to B. (Both on same device.)
		A ---> core: ("intermetry", "you alive?")
		core ---> B: ("mymodule", "you alive?")
		
		B ---> core: ("intermetry", "yes.")
		core ---> A: ("mymodule", "yes.")
	2. A sends a request to B. (Both on different devices. DeviceA and DeviceB)
		A ---> core: ("conmanager", ("senddata", "DeviceB", "B", b"Are you alive?"))
		core ---> conmanager: ("A", ("senddata", "DeviceB", "B", b"Are you alive?"))
		
		conmanager ---> conmanager: ENCRYPTED
		
		conmanager ---> core: ("B", ("recvdata", "DeviceA", "A", b"Are you alive?"))
		core ---> B: ("conmanager", ("recvdata", "DeviceA", "A", b"Are you alive?"))

## How do I create my own modules?
You can find well-documented (todo) templates in the (todo) hello-world modules.
 