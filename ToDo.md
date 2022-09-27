conmanager:


    -Packet indexing and improve error message texts like "No socket connected towards destination"
        ---> action type "senddata" for unindexed packets. Example use: 1-way packets.
        ---> action type "senddataI" for indexed packets. Index is transmitted too.
            ---> How about a .respond() function for packets? No need for the user to deal with
                orig_device, orig_module, as well as packet index. Much simpler.
    
    -Also accept strings, numbers, etc. as to-be-sent payload. Currently only bytestrings (i.e. b'something like this') are accepted.
        Anything else results in a crash as of now. Crash = bad

    -"Errno 98 address already in use" error. Happens sometimes when you restart start.py.

    #-Connection to self. Or at least if target_device == own_name then just internally forward it to the respective #queue.
    # Isaias: Implemented internal forwarding.

    #-"standardport" add config.ini setting to change port.
    #   Isaias: Implemented!

    #-Store private and public keys in separate files in a sub folder. (e.g. keys/bob.pub, keys/bob.priv)
    #    Isaias: Done.
    
    -Implement action "getDeviceName". It should return the current device's name

    #-Signing messages is of highest priority before we make our repo public!
    #    A malicious attacker could use person A's public key to send person B a packet in person A's name.
    #    E.g.:
    #        Eve: "Hi. I'm totally bob. I want you to do [harmful thing]" ---alice.publickey---> alice
    #    The worst case scenario would be an attacker being able to
    #    do remote code execution and taking over the entire network.
    #    And that would be no bueno! Hence highest priority before going public!
    #
    #    Isaias: Imports for signing and hashing added. Look into conmanager.py imports for details.
    #        Update: Implemented!
    
    #-Bug: Once in a while a packet will come in, but be entirely nonesense.
    #    Isaias: Applied solution: Packet seemed fragmented. Implemented check for fragmentation.
    #        Long-term testing seems necessary. But as of now, not reproducable in 15 minute runs.
    #        Fragmentation filter gets hit though. So I consider it fixed.
        
    
    #-RSA 1024 bit ---> 4096 bit.
    #    Isaias:
    #    Implemented and works.



intermetry:
    
	-Find more system info points a user may want to monitor and add them into hardwareinfo.py

audiocontrol:
    
	-create prototype implementing pulseaudio. ---> Isaias

hwdisplay:
    
	#-Communication between controller and core ---> Isaias
    #   Isaias: For now implemented with hwdisplay as a proxy between core and controller.
    #       Packets are forwarded based on packetID.
    #       Once core gets a function to register modules and hand over queues, I will change it.

    -Communication between controller and core: register controllers as own modules and hand over communication queues!

    -Functioning prototype ---> Isaias

core:
    
	#-Implement ability to include modules where folder name and module name don't match.
    #    E.g.: hwdisplay\hwdisplay, hwdisplay\hexa, hwdisplay\simpletext, ...
    #implemented! ~ Isaias
    
    -Implement function to add modules. (Set name, generate queue pair, and forward to requesting module)


Github / general:
    
	-Create tutorials and copy-paste friendly example sections.
    #-Add a GPLv2 or GPLv3 license?
    #   Isaias: Implemented GPLv3!
    -Clean up top folder. Remove deprecated modules and folders like intermetrymaster and "signing test DELME"
    -Add separate repos for different modules?
        -E.g.: move hwdisplay, audiocontrol, DEcontrol, and OBScontrol into repository "modularkraken_hwdisplay"
        -Then add example modules (possibly with gui, but most important of all: easy to understand) and private keys for testing purposes.
            Also make a video on YouTube. (Leave it private for as long as the repository is private too.)
	-add example-modules. E.g. "hello-world bob" and "hello-world alice"
		-Supposed to be well-documented and easy to copy-&paste.
    

To-be-implemented future modules:
    
	-DEcontrol:
        Control aspects of the current desktop environment. E.g.:
            -Focus / Minimize / unminimize / close / maximize / move / resize windows
            -Move windows between monitors and workspaces
            -gTile integration for resizing / tiling?
    -HIDcontrol:
        Control the system's Human Interface Devices. E.g.:
            -xinput create and utilize master and slave devices.
            -issue keyboard inputs
            -issue mouse movement, clicks, etc.
            -at some point add Windows compatibility, if Windows has multipointer capabilities
    -OBScontrol:
        Control OBS recording and streaming.
            -Start / stop:
                *stream
                *recording
                *virtual camera
            -Select scenes
            -Hide / unhide sources
            -Statistics like live/recording time, CPU utilization, FPS, bitrates, framedrops, etc.
    -Twitch:
        View Twitch chat, show (and record) statistics, maybe some light moderation? I.e. muting people, etc.?
