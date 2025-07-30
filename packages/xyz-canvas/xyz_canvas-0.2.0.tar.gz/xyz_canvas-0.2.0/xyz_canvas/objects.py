from xyz_canvas.gui import xyz_mouse

# Base geometry class
class XyzObject:
    def draw(self, ax):
        raise NotImplementedError

    def get_lines(self):
        raise NotImplementedError

    def describe(self):
        raise NotImplementedError

    def to_dict(self):
        return {
            "type": self.__class__.__name__,
            "lines": self.get_lines()
        }

# Geometry primitives
class Line(XyzObject):
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def draw(self, ax):
        x = [self.start[0], self.end[0]]
        y = [self.start[1], self.end[1]]
        z = [self.start[2], self.end[2]]
        ax.plot(x, y, z, color='blue')

    def get_lines(self):
        return [(self.start, self.end)]

    def describe(self):
        return f"Line from {self.start} to {self.end}"

class Rectangle(XyzObject):
    def __init__(self, vertices):
        self.vertices = vertices

    def draw(self, ax):
        for i in range(4):
            s = self.vertices[i]
            e = self.vertices[(i+1)%4]
            ax.plot([s[0], e[0]], [s[1], e[1]], [s[2], e[2]], color='green')

    def get_lines(self):
        return [
            (self.vertices[i], self.vertices[(i+1)%4])
            for i in range(4)
        ]

    def describe(self):
        return f"Rectangle with vertices: {self.vertices}"

    def to_dict(self):
        return {
            "type": "Rectangle",
            "vertices": self.vertices,
            "lines": self.get_lines()
        }

# Main object creation controller
class XyzCreateObject:
    def __init__(self, plt, ax, add_cb, mode='line'):
        self.plt = plt
        self.ax = ax
        self.add_cb = add_cb
        self.mode = mode
        self.tools = {
            'line': self.XyzLines(self.object_created),
            'rectangle': self.XyzRectangles(self.object_created),
        }
        self.current_tool = self.tools[mode]
        self.mouse = xyz_mouse(plt, ax, self.mouse_clicked, self.mouse_movedto)

    def mouse_clicked(self, xyz):
        self.current_tool.add_point(xyz)

    def mouse_movedto(self, xyz):
        pass  # Optional preview feature

    def object_created(self, obj):
        self.add_cb(obj)
        obj.draw(self.ax)
        self.plt.draw()

    def set_mode(self, new_mode):
        self.mode = new_mode
        self.current_tool = self.tools[new_mode]

    # Tool for creating a line from 2 points
    class XyzLines:
        def __init__(self, add_cb):
            self.start = None
            self.add_cb = add_cb

        def add_point(self, xyz):
            if self.start is None:
                self.start = xyz
            else:
                line = Line(self.start, xyz)
                self.add_cb(line)
                self.start = None

    # Tool for creating a rectangle from 2 diagonal corners
    class XyzRectangles:
        def __init__(self, add_cb):
            self.first_corner = None
            self.add_cb = add_cb

        def add_point(self, xyz):
            if self.first_corner is None:
                self.first_corner = xyz
            else:
                x1, y1, z1 = self.first_corner
                x2, y2, _ = xyz
                vertices = [
                    (x1, y1, z1),
                    (x2, y1, z1),
                    (x2, y2, z1),
                    (x1, y2, z1),
                ]
                rect = Rectangle(vertices)
                self.add_cb(rect)
                self.first_corner = None
