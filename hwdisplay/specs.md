# specifications

## formatting
GUI files are only accepted in XML format.


## Useful Tags
`<head>`:
    Place general configuration about your GUI. Things like position, size, controller script, colors and font.

`<body>`:
    This is where you place all of your elements.

`<pagecontroller>`:
    A page controller / selector is a type of list dedicated to house `<page>` elements, which - when clicked - select a page.

`<page>`:
    Define a page. Give it a name, make it the default page, give it some custom properties. See examples for more.

`<variable>`:
    Define a variable. Give it a name and specify a `function` to be executed `every` interval.

`<label>`:
    Label element. Can contain static text or reference a `variable`. Supports `onclick`.

`<image>`:
    Image element. Insert an image to be shown. Supports `onclick`.




## example xml
example hexa.xml:

    <head>
        <x>0</x>
        <y>0</y>
        <width>1024</width>
        <height>600</height>
        <controller>hexa.py</controller>
        <target>ifd</target>
        <bg>#000000</bg>
        <fg>#ffffff</fg>
        <font>("Arial", 25)</font>
    </head>
    
    <body>
        <pagecontroller x=0 y=0 width=100 height=600>
            <page default>Info</page>
            <page>Audio</page>
            <page>Desktop</page>
            <page>HID</page>
            <page>OBS</page>
        </pagecontroller>
        <label page="Info" x=250 y=50 text="CPU"/>
        <image page="Info" x=250 y=60 image="assets/hexa.png">
        <variable page="Info" name="cpupercent" function="hexa.cpupercent" every="0.5">
        <label page="Info" x=250 y=80 variable="cpupercent"/>
        
        <label page="Info" x=450 y=50 text="GPU"/>
        <image page="Info" x=450 y=60 image="assets/hexa.png">
        <variable page="Info" name="gpupercent" function="hexa.gpupercent" every="0.5">
        <label page="Info" x=450 y=80 variable="gpupercent"/>

        <label page="Info" x=650 y=50 text="RAM"/>
        <image page="Info" x=650 y=60 image="assets/hexa.png">
        <variable page="Info" name="rampercent" function="hexa.rampercent" every="0.5">
        <label page="Info" x=650 y=80 variable="rampercent"/>

        <label page="Info" x=850 y=50 text="NIC"/>
        <image page="Info" x=850 y=60 image="assets/hexa.png" onclick="hexa.nicswitch">
        <variable page="Info" name="nic" function="hexa.nic" every="0.5">
        <label page="Info" x=850 y=80 variable="nic"/>

        <label page="Info" x=350 y=250 text="TEMP_CPU"/>
        <image page="Info" x=350 y=260 image="assets/hexa.png">
        <variable page="Info" name="tcpu" function="hexa.tcpu" every="0.5">
        <label page="Info" x=350 y=280 variable="tcpu"/>
        
        <label page="Info" x=550 y=250 text="TEMP_GPU"/>
        <image page="Info" x=550 y=260 image="assets/hexa.png">
        <variable page="Info" name="tgpu" function="hexa.tgpu" every="0.5">
        <label page="Info" x=550 y=280 variable="tgpu"/>

        <label page="Info" x=750 y=250 text="TEMP_SYS"/>
        <image page="Info" x=750 y=260 image="assets/hexa.png">
        <variable page="Info" name="tsys" function="hexa.tsys" every="0.5">
        <label page="Info" x=750 y=280 variable="tsys"/>

        <label page="Audio" text="Nothing to see here in the audio page" x=250, y=50/>
        <label page="Desktop" text="Nothing to see here in the desktop page" x=250, y=50/>
        <label page="HID" text="Nothing to see here in the HID page" x=250, y=50/>
        <label page="OBS" text="Nothing to see here in the OBS page" x=250, y=50/>

    </body>