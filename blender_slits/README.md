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


## How to run a TCP socket server? 

Run in tow terminals:

```console
$ blenderplayer slits.blend
```

```console
 $ python client.py
```

## Communication protocol

Communicates via TCP/UP socket on port: 9999.

Motor axes are referenced by the following identifiers:
* top - top blade
* bot - bottom blade
* left - left blade
* right - right blade

Query commands:

* Query position of a single axis:
  request: ?pos <axis id>
  answer: pos <axis id> <position>
  example: ?pos top' -> pos top 20.3

* Query positions of multiple axes
  request: ?positions
  answer: <top pos> <bot pos> <left pos> <right pos>

* Query state of a single axis:
  request: ?state <axis id>
  answer: state <axis id> <state>
          <state> can by either ON or MOVING

* Query states of multiple axes
  request: ?states
  answer: <top state> <bot state> <left state> <right state>

* Query velocity of a single axis:
  request: ?vel <axis id>
  answer: vel <axis id> <velocity>

* Query acceleration of a single axis:
  request: ?acc <axis id>
  answer: acc <axis id> <acceleration>

* Query deceleration of a single axis:
  request: ?dec <axis id>
  answer: dec <axis id> <deceleration>

Commands:

* Move a single axis to an absolute position
  request: <axis id> <position>
  answer: Ready

* Move multiple axes to absolute positions
  request: move <axis id> <position> <axis id> <position> ...
  answer: Ready

* Abort any motion
  request: abort
  answer Ready

* Set velocity of a single axis:
  request: vel <axis id> <velocity>
  answer: Ready

* Set acceleration of a single axis:
  request: acc <axis id> <acceleration>
  answer: Ready

* Set deceleration of a single axis:
  request: dec <axis id> <deceleration>
  answer: Ready

## Notes

LIGHT IDEAS FROM: http://www.tutorialsforblender3d.com/GameDoc/Shadows/Shadows_3.html
