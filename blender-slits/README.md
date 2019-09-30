# Simulator of slits with beam usign Blender

## How to play manually with slits?

In order to understand the system, I encourage you to execute:

```console
$ blenderplayer slits_keyboard_only.blend
```

Now you can use arrows (up/down/left/right) to open horizontal and vertical
gaps with the <SHIFT> modifier you will inverse the movement of each blade:
UP arrow will move TOP blade UP, and <SHIFT>+<UP> will move TOP blade DOWN
DOWN arrow will move BOTTOM blade DOWN, and <SHIFT>+<DOWN> will move BOTTOM blade UP
and the same for left and right. You can exit with Q or <Ctrl>+C

## TCP socket server

The TCP socket server runs a blenderplayer with a scene that contains 4 motors and one
detector. The process listens on two sockets. The first (port 9999) understands motion
control ASCII commands and the second (port 9998) understands detector control ASCII
commands.

### Installation

You need to have blender + blenderplayer installed.

You must install blender socket server in the same python environment that blender
uses (ex: if you installed blender system wide, it uses the installed system python3).

To install blender slits socket server, from within the proper python environment,
simply type:

```console
pip install .
```

### How to run a TCP socket server?

Run in two terminals:

```console
$ blender-slits-server
```

```console
 $ python client.py
```

### Test with a simple client

You can use `nc` linux tool:

```console
$ nc 0 9999
?pos top
pos top 20
?move top 10
Ready
```

(replace *0* with hostname if you are running the client on a different machine)

**Pro tip**: install `rlwrap` command line tool and run `rlwrap nc 0 9999`.
This will enpower `nc` with readline capabilites like history and command completion ;-)

The same from python:

```python
>>> import socket
>>> sock = socket.create_connection(('0', 9999))
>>> sock.sendall(b'?pos top\n')
>>> print(sock.recv(1024))
'pos top 10.0\n'
```

### Communication protocol

Communicates via TCP/UP socket on ports:

* 9999 (motion control) and
* 9998 (detector control)

Communication protocol is ASCII based on request-reply semantics.

Commands must end with newline character (ASCII code 10).
Replies always end with newline (ASCII code 10). New line is omitted in the
description below for better understanding only.

Commands that were accepted reply with:
`Ready\n`

Commands that are not understood or which result in error reply with:
`ERROR: <description>\n`

#### Motion

Motor axes are referenced by the following identifiers:
* top - top blade
* bot - bottom blade
* left - left blade
* right - right blade

Query commands:

* Query position of a single axis:

  request: `?pos <axis id>`

  answer: `pos <axis id> <position>`

  example: `?pos top` -> `pos top 20.3`

* Query positions of multiple axes

  request: `?positions`

  answer: `<top pos> <bot pos> <left pos> <right pos>`

* Query state of a single axis:

  request: `?state <axis id>`

  answer: `state <axis id> <state>`

  (state can by either ON or MOVING)

* Query states of multiple axes

  request: `?states`

  answer: `<top state> <bot state> <left state> <right state>`

* Query velocity of a single axis:

  request: `?vel <axis id>`

  answer: `vel <axis id> <velocity>`

* Query acceleration of a single axis:

  request: `?acc <axis id>`

  answer: `acc <axis id> <acceleration>`

* Query deceleration of a single axis:

  request: `?dec <axis id>`

  answer: `dec <axis id> <deceleration>`

Commands:

* Move a single axis to an absolute position

  request: `<axis id> <position>`

  answer: `Ready`

* Move multiple axes to absolute positions

  request: `move <axis id> <position> <axis id> <position> ...`

  answer: `Ready`

* Abort any motion

  request: `abort`

  answer `Ready`

* Set velocity of a single axis:

  request: `vel <axis id> <velocity>`

  answer: `Ready`

* Set acceleration of a single axis:

  request: `acc <axis id> <acceleration>`

  answer: `Ready`

* Set deceleration of a single axis:

  request: `dec <axis id> <deceleration>`

  answer: `Ready`

#### Detector

Query commands:

* Query detector exposure time:

  request: `?acq_exposure_time`

  answer: `acq_exposure_time <time in seconds>

  example: `?acq_exposure_time` -> `acq_exposure_time 1.0`

* Query detector saving directory:

  request: `?acq_saving_directory`

  answer: `acq_saving_directory <absolute path or empty string if no saving>`

  example: `?acq_saving_directory` -> `acq_saving_directory /tmp/sardana`

* Query detector image file name pattern (recognizes one variable: image_nb):

  request: `?acq_image_name`

  answer: `acq_image_name <image file name pattern>`

  example: `?acq_image_name' -> acq_image_name image-{image_nb:03d}.h5`

* Query detector status (possible values: 'Ready', 'Acquiring', 'Readout', 'Saving')

  request: `?acq_status`

  answer: `acq_status <detector status>`

  example: `?acq_status` -> `acq_status Ready`

* Query detector last recorded image file name (returns absolute path)

  request: `?acq_last_image_file_name`

  answer: `acq_last_image_file_name <detector last image file name>`

  example: `?acq_last_image_file_name` -> `acq_last_image_file_name /tmp/sardana/image-004.h5`

* Query detector last recorded image data

  request: `?acq_last_image`

  answer: binary data. First 8 characters are ASCII representing size of binary
  data that follows. The next bytes are a python pickle dump of either a numpy array representing the 2D data or None if no image has ever been acquired.

Commands:

* Set detector exposure time:

  request: `acq_exposure_time <time in seconds>`

  answer: `Ready`

* Set detector saving directory:

  request: `acq_saving_directory <absolute path or empty string if no saving>

  answer: `Ready`

* Set detector image file name pattern (recognizes one variable: image_nb):

  request: `acq_image_name <image file name pattern>`

  answer: `Ready`

* Prepare detector for acquisition (must be called before each `acq_start`)

  request: `acq_prepare`

  answer: `Ready`

* Start detector acquisition

  request: `acq_start`

  answer: `Ready`

* Stop detector acquisition

  request: `acq_stop`

  answer: `Ready`

## Notes

LIGHT IDEAS FROM: http://www.tutorialsforblender3d.com/GameDoc/Shadows/Shadows_3.html
