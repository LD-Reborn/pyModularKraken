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

    <html>
        <head>
            <x>0</x>
            <y>0</y>
            <width>1024</width>
            <height>600</height>
            <title>hwdisplay</title>
            <controller>hexa</controller>
            <target>ifd</target>
            <bg>#000000</bg>
            <fg>#ffffff</fg>
            <font>("Arial", 25)</font>
        </head>
        <body>
            <pagecontroller default="info" x="0" y="0" width="100" height="600">
                <page name="info">Info</page>
                <page name="audio">Audio</page>
                <page name="desktop">Desktop</page>
                <page name="hid">HID</page>
                <page name="obs">OBS</page>
            </pagecontroller>
            
            <image page="info" x="250" y="60" image="assets/hexa.png"/>
            <label page="info" x="250" y="50" color="#FF0000" bg="#00FF00" text="CPU"/>
            <variable page="info" name="cpupercent" function="cpupercent" every="0.1"/>
            <label page="info" x="250" y="80" variable="cpupercent"/>
            
            <image page="info" x="450" y="60" image="assets/hexa.png"/>
            <label page="info" x="450" y="50" text="GPU"/>
            <variable page="info" name="gpupercent" function="gpupercent" every="0.5"/>
            <label page="info" x="450" y="80" variable="gpupercent"/>

            <image page="info" x="650" y="60" image="assets/hexa.png"/>
            <label page="info" x="650" y="50" text="RAM"/>
            <variable page="info" name="rampercent" function="rampercent" every="0.5"/>
            <label page="info" x="650" y="80" variable="rampercent"/>

            <image page="info" x="850" y="60" image="assets/hexa.png" onclick="hexa.nicswitch"/>
            <label page="info" x="850" y="50" text="NIC"/>
            <variable page="info" name="nic" function="nic" every="0.5"/>
            <label page="info" x="850" y="80" variable="nic"/>

            <image page="info" x="350" y="260" image="assets/hexa.png"/>
            <label page="info" x="350" y="250" text="TEMP_CPU"/>
            <variable page="info" name="tcpu" function="tcpu" every="0.5"/>
            <label page="info" x="350" y="280" variable="tcpu"/>
            
            <image page="info" x="550" y="260" image="assets/hexa.png"/>
            <label page="info" x="550" y="250" text="TEMP_GPU"/>
            <variable page="info" name="tgpu" function="tgpu" every="0.5"/>
            <label page="info" x="550" y="280" variable="tgpu"/>

            <image page="info" x="750" y="260" image="assets/hexa.png"/>
            <label page="info" x="750" y="250" text="TEMP_SYS"/>
            <variable page="info" name="tsys" function="tsys" every="0.5"/>
            <label page="info" x="750" y="280" variable="tsys"/>

            <label page="audio" text="Nothing to see here in the audio page" x="250" y="50"/>
            <label page="desktop" text="Nothing to see here in the desktop page" x="250" y="50"/>
            <label page="hid" text="Nothing to see here in the HID page" x="250" y="50"/>
            <label page="obs" text="Nothing to see here in the OBS page" x="250" y="50"/>

        </body>

    </html>