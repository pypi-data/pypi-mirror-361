
import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseButton

class xyz_mouse:

    def __init__(self, plt, ax, on_click_cb, on_move_cb):
        self.plt = plt
        self.ax = ax
        self.on_click_cb = on_click_cb
        self.on_move_cb = on_move_cb
        self.in_axes_range_prev = False
        self.plt.connect('motion_notify_event', self.on_move)
    
    def on_move(self, event):
        global in_axes_range_prev
        if event.inaxes:
            s = self.ax.format_coord(event.xdata, event.ydata)
            p = self._get_pane_coords(s)
            in_axes_range_now = self._in_axes_range(p)
            self.movedto_xyz = p
            self.on_move_cb(p)
            if(not (in_axes_range_now == self.in_axes_range_prev)):
                if in_axes_range_now:
                    self.ax.mouse_init(rotate_btn=0)
                    self.plt.connect('button_press_event', self.on_click)
                else:
                    self.plt.disconnect(self.on_click)
                    self.ax.mouse_init(rotate_btn=1)
                    event.button = None
                self.in_axes_range_prev = in_axes_range_now
     
    def on_click(self, event):
        if event.button is MouseButton.LEFT:
            s = self.ax.format_coord(event.xdata, event.ydata)
            p = self._get_pane_coords(s)
            if(self._in_axes_range(p)):
                self.on_click_cb(p)
            
    def _get_pane_coords(self, s):
        # gets x,y,z of mouse position from s=ax.format_coord(event.xdata, event.ydata)
        s=s.split(",")
        if('elevation' in s[0]):
            return None
        xyz=[0,0,0]
        for valstr in s:
            valstr=valstr.replace(' pane','')
            ordinate = valstr.split("=")[0].strip()
            i = ['x','y','z'].index(ordinate)
            xyz[i]=float(valstr.split("=")[1].replace('−','-'))
        return xyz

    def _in_axes_range(self, p):
        # determines if x,y and z are all in the axis ranges
        if p == None:
            return False
        x_in = self.ax.get_xlim()[0] <= p[0] <= self.ax.get_xlim()[1]
        y_in = self.ax.get_ylim()[0] <= p[1] <= self.ax.get_ylim()[1]
        z_in = self.ax.get_zlim()[0] <= p[2] <= self.ax.get_zlim()[1]
        return (x_in and y_in and z_in)


class xyz_lines:
    def __init__(self, plt, ax):
        self.plt = plt
        self.ax = ax
        self.current_line_ends = [None, None]
        self.current_line_start = None
        self.lines_collection = []

    def add_line_end(self, xyz):
        if (self.current_line_start):
            line = [self.current_line_start, xyz]
            self.ax.plot([line[0][0],line[1][0]],[line[0][1],line[1][1]],[line[0][2],line[1][2]])
            self.lines_collection.append(line)
            self.current_line_start = None
        else:
            self.current_line_start = xyz
        
    
