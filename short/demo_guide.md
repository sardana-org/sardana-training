---
title: Introduction to Sardana
tags: Talk
description: View the slide with "Slide Mode".
---

# Introduction to Sardana

<!-- Put the link to this slide here so people can follow -->
slide: https://hackmd.io/@reszelaz/Bk-p3tZBF

Tango Workshop @ ICALEPCS 2021
by Zbigniew Reszela from ALBA Synchrotron

---

<!-- .slide: data-background="https://raw.githubusercontent.com/sardana-org/sardana-training/master/short/res/what_is_sardana_suite.png" -->

---

## [Installation](https://sardana-controls.org/users/getting_started/installing.html)

```console

$ conda create -n sardana-icalepcs2021 -y -c conda-forge python=3.9 sardana
$ conda activate sardana-icalepcs2021
# extra dependencies + tango-test
$ conda install -y -c conda-forge h5py matplotlib taurus_pyqtgraph tango-test
```

---

## Creating sar_demo environment

----

In first terminal start the Sardana server:

```console
$ Sardana demo1 --log-level=debug
```

----

In second terminal start the Spock client:

```console
$ spock
```

----

Execute `lsdef` to list all macros with short description:

```console
Door_demo1_1 [X]: lsdef
```

Execute `lsa` to list all elements (no elements so far):

```console
Door_demo1_1 [X]: lsa
```

----

Execute `sar_demo` macro to create simulated elements:

```console
Door_demo1_1 [X]: sar_demo
```

----

Execute `lsa` macro again. Simulated elements are already defined.

```console
Door_demo1_1 [X]: lsa
```

---

## Simulated motion

----

Start taurus form and taurus trend:

```console
$ taurus form mot01
```

```console
$ taurus trend -r 100 mot01/position
```

----

In Spock execute `umv` macro on a motor:

```console
Door_demo1_1 [X]: umv mot01 100
```

Then, in taurus form execute relative move by 100 units in negative direction.

----

In Spock change motor's velocity:

```console
Door_demo1_1 [X]: mot01.velocity=10
```

Then, repeat the previous `umv` macro execution:

```console
Door_demo1_1 [X]: umv mot01 100
```

---

## Simulated acquisition

----

In Spock execute `ct` macro on a counter/timer:

```console
Door_demo1_1 [X]: ct 1 ct01
```

----

In Spock execute `ct` macro on a 1D experimental channel (after prior configuring its timer):

```console
Door_demo1_1 [X]: oned01.timer = "__self"
```

```console
Door_demo1_1 [X]: ct 1 oned01
```

----

In Spock execute `ct` macro on a 2D experimental channel (after prior configuring its timer):

```console
Door_demo1_1 [X]: twod01.timer = "__self"
```

```console
Door_demo1_1 [X]: ct 1 twod01
```

----

Start taurus form with those experimental channels:

```console
$ taurus form ct01 oned01 twod01
```

And repeat those acquisitions.

---

## Taurus GUI

----

### Create a Taurus GUI using wizard

Create a new GUI with taurus newgui:

```console
taurus newgui
```

----

<!-- .slide: style="font-size: 24px;" -->

Follow the wizard of taurus newgui:
- Choose the project directory (e.g: \<your home\>/demogui)
- Choose GUI name (e.g: demogui)
- Add synoptic (optional): sardana-training/short/res/demoBL.jdw
- Enable Sardana communication (optional) select: MacroServer - MacroServer/demo1/1 and Door - Door/demo1/1
- Generate panels from Sardana Pool (optional): choose yes
- We will skip some steps: custom logo, extra panels, Monitor list

----

### Taurus GUI installation and lauch

Install the freshly created GUI:

```console
pip install <your home>/demogui
```

Launch your GUI:
```console
demogui
```

Enable JSONRecorder pop-up.

---

## Taurus GUI - interaction with *instruments*

----

<!-- .slide: style="font-size: 24px;" -->

Reorder the widgets for "interaction with instruments":
- Go to Panels -> hide all panels
- Click on the "demoBL" button in the toolbar to show the synoptic panel
- Click on the "mirror" instrument in the synoptic (the area below "DCM"). This should show the "/mirror" panel
- Move the "mirror" panel above the synoptic
- Click on the slits in the synoptics (labelled "diagnostics" in the synoptic). This should show the "/slits" panel. Move it to a tab together with "/mirror"
- Click on the monitor in the synoptics (labelled "FSM4" in the synoptic). This should show the "/monitor" panel. Move it to a tab together with "/mirror" and "/slits"
- Show the 2-ways communication between panels and synoptics
    - Click on the active areas of the synoptics and show that the corresponding panels are shown
    - Select the panels and see that the synoptic highlights the corresponding area
- Save as Instruments perspective

---

## Taurus GUI - interaction with Tango

----

<!-- .slide: style="font-size: 24px;" -->

- Go to Panels -> hide all panels
- Create a Tango DB tree panel:
    - Use New Panel button
        - Select TaurusDBTreeWidget and use name db
        - Click on "Advanced Settings" and set tango://\<your Tango DB host\>:10000 as model and click on finish
- Create a Plot panel:
    - Use New Panel button
        - Select TaurusPlot and use name plot and click on finish
- Create a Form panel:
    - Use New Panel button
        - Select TaurusForm and use name form and click on finish
- Make sure that the "db" and "form" and "plot" panels are all simultaneously visible
- Add a new element to the "form" form panel:
    - Navigate in the db panel to sys/tg_test/1/ampli, and drag and drop it into "form".
    - Navigate in the db panel to sys/tg_test/1/boolean_scalar, and drag and drop it into "form"
    - Navigate in the db panel to sys/tg_test/1/wave, and drag and drop it into "plot"
- Save as Tango perspective

---

## Generic Scan Framework

- In Spock configure data storage:
```console
Door_demo1_1 [X]: newfile /tmp/icalepcs2021.h5
```
- In Spock run a scan:
```console
Door_demo1_1 [X]: dscan mot01 -5 5 10 0.1 
```
- Run the same scan in Taurus GUI:
    - Configure scan plotting for ct01:
        - In expconf change Plot Type: Spectrum and Plot Axis: \<mov\>
    - Execute dscan macro in the Sequencer panel:
        - Add dscan macro
        - Configure its parameters
        - Press the Play button
- You can add more macros to the sequence

---

## Developing custom macros

- Create new macro called `hello_world` module called `icalepcs2021` using `edmac`:
```console
Door_demo1_1 [X]: edmac hello_world icalepcs2021
```
- In the macro code use `self.input()`` to obtain a name from the users:

```python
from sardana.macroserver.macro import imacro

@imacro()
def hello_world(self):
    """Macro hello_world"""
    name = self.input("What's your name?")
    self.output("Hello {}".format(name))
```

---

## Developing custom controllers

----

Prepare Blender Slits:

```console
$ xhost +local:
$ docker run -it --name=blender-slits-server -p 9999:9999 -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix blender-slits-server
```
----

Add BlenderBladesMotorController to the Pool:
- Set PoolPath property:
```console
Door_demo1_1 [X]: Pool_demo1_1.put_property({"PoolPath": "<path to your sardana-training clone>/controllers/"})
```
- Restart the Sardana server

----

Create an instance of the controller (in Spock):
```console
Door_demo1_1 [X]: defctrl BlenderBladesMotorController bleblactrl
```

----

Create blades motors:
```console
Door_demo1_1 [X]: defelem top bleblactrl 1
Door_demo1_1 [X]: defelem bottom bleblactrl 2
Door_demo1_1 [X]: defelem left bleblactrl 3
Door_demo1_1 [X]: defelem right bleblactrl 4
```
Ask for motor positions (in Spock):
```console
Door_demo1_1 [X]: wm top bottom left right
```
----

Determine direction with relative move and adjust sign (in Spock, line by line):
```console
Door_demo1_1 [X]: bottom.sign = -1
Door_demo1_1 [X]: left.sign = -1
```
----

Fully close slits (optional) and change offset by using the set_user_pos macro (in Spock, line by line):
```console
Door_demo1_1 [X]: set_user_pos top 0
Door_demo1_1 [X]: set_user_pos bottom 0
Door_demo1_1 [X]: set_user_pos left 0
Door_demo1_1 [X]: set_user_pos right 0
```

----

Open and close gap by moving physical motors (in Spock, line by line)
```console
Door_demo1_1 [X]: mv top 5 bottom 5 left 5 right 5
Door_demo1_1 [X]: mv top 0 bottom 0 left 0 right 0
```

----

Instantiate vertical slits controller (in Spock):
```console
Door_demo1_1 [X]: defctrl Slit vertctrl sl2t=top sl2b=bottom Gap=gapvert Offset=offsetvert
```

----

Instantiate horizontal slits controller:
```console
Door_demo1_1 [X]: defctrl Slit horctrl sl2t=right sl2b=left Gap=gaphor Offset=offsethor
```

----
Open the gaps: 
```console
Door_demo1_1 [X]: mv gapvert 10 gaphor 10
```

Make a scan of offset:
```console
Door_demo1_1 [X]: dscan offsetvert -10 10 10 0.1
```
----

Or using a macro:

```python
from sardana.macroserver.macro import macro

@macro()
def create_blender_slits(self):
    """Macro create_blender_slits"""
    self.output("Running create_blender_slits...")
    self.defctrl("BlenderBladesMotorController", "bleblactrl")
    self.defelem("top", "bleblactrl", 1)
    self.defelem("bottom", "bleblactrl", 2)
    self.defelem("left", "bleblactrl", 3)
    self.defelem("right", "bleblactrl", 4)
    self.getMotor("bottom").write_attribute("sign", -1)
    self.getMotor("left").write_attribute("sign", -1)
    self.set_user_pos("top", 0)
    self.set_user_pos("bottom", 0)
    self.set_user_pos("left", 0)
    self.set_user_pos("right", 0)
    self.mv("top", 5, "bottom", 5, "left", 5, "right", 5)
    self.mv("top", 0, "bottom", 0, "left", 0, "right", 0)
    self.defctrl("Slit", "vertctrl", "sl2t=top", "sl2b=bottom", "Gap=gapvert", "Offset=offsetvert")
    self.defctrl("Slit", "horctrl", "sl2t=right", "sl2b=left", "Gap=gaphor", "Offset=offsethor")
    self.mv("gapvert", 10, "gaphor", 10)
```
---


## Thank you!

