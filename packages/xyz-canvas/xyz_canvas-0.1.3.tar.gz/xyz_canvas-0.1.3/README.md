# xyz_canvas
Interactive canvas for editing 3D geometry, using matplotlib.pyplot

Current classes:
In xyz_canvas.gui:
- xyz_mouse: uses specified callbacks on mouse (left) click and on mouse move to return 3D co-ordinates
- xyz_lines: adds lines to a collection of lines with sequentially specified end points

I'm thinking of adding
xyz_canvas.transforms
- rotatations
- translations
- sheers
  etc
xyz_canvas.utils
 ....

## Installation
Install with pip:
```
pip install xyz_canvas
```

## Demo Screenshot
The file demo.py currently allows you to add lines to the canvas by clicking end points sequentially. The callback function then has access to the lines collection. At the moment, no markers precede line generation but that's my next step, as well as adding delete, move, attach, snap to grid, snap to object methods.

The XYZ co-ordinates all snap to the nearest backplane (XY, XZ, YZ) but I will add ways to put the lines into arbitrary locations.

![Capture](https://github.com/user-attachments/assets/80abeb00-da7e-44d8-9379-c7abef099912)
