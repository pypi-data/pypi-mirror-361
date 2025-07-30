# xyz_canvas
Interactive canvas for editing 3D geometry, using matplotlib.pyplot

This is a demo of xyz_canvas (pre-release, V0.2.0), a Python library to add, edit, and connect 3D wire-frame objects
using only Matplotlib. The idea is that this will be called by code that needs the 
user to define / edit these objects in 3D space.

Currently, only lines are supported but the plan is to include at least lines, rectangles, 
arcs (circles) and helices. Shape types are seleced via the buttons next to the geometry display.
The clear button is implemented, as is Exit & Close and List, but the others are placeholders.

To add a line, click two points within the axis space (note that no feedback is given for the first click).

The view may be rotated at any time by clicking and dragging just oustide the axis space.

Currently, endpoints / vertices are pinned to the 'closest' backplane (shaded & gridded).
Methods to move vertices into general 3D space by clicking and typing co-ordinates,
snapping to a 3D grid / other objects,  will be added soon.

## Installation
Install with pip:
```
pip install xyz_canvas
```

## Demo Screenshot
The file demo.py currently allows you to add lines to the canvas by clicking end points sequentially. The callback function then has access to the lines collection. At the moment, no markers precede line generation but that's my next step, as well as adding delete, move, attach, snap to grid, snap to object methods.

The XYZ co-ordinates all snap to the nearest backplane (XY, XZ, YZ) but I will add ways to put the lines into arbitrary locations.

![Capture](https://github.com/user-attachments/assets/80abeb00-da7e-44d8-9379-c7abef099912)
