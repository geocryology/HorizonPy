try:  # python 2
    import Tkinter as tk
except ImportError:  # python 2
    import tkinter as tk

from horizonpy.quickhorizon.utils import plot_styles


class StatusBar:

    def __init__(self, root):
        self.status = tk.Label(root, text="X,Y", bd=1, relief=tk.SUNKEN, 
                               anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    def display(self, cursor_loc, image_azimuth, field_azimuth, img_value):
        output = "Cursor = {}".format(str(cursor_loc)).ljust(25)

        if 0 <= image_azimuth <= 360:
            output += "Image Azimuth = {:.1f}".format(360 - image_azimuth).ljust(25)

        if 0 <= field_azimuth <= 360:
            output += "Field Azimuth = {:.1f}".format(field_azimuth).ljust(25)

        if img_value:
            img_value_display = "({:03d}, {:03d}, {:03d})".format(*img_value) 
        else:
            img_value_display = "(---, ---, ---)"

        output += "Image value: {}".format(img_value_display).ljust(25)

        self.status.config(text=output)


class MainView:

    def __init__(self, root):
        self.frame = tk.Frame(root, bg='black')
        
        # Create canvas
        self.canvas = tk.Canvas(self.frame, width=800, height=600, bg='gray')
        self.canvas.focus_set()
        
        self.frame.pack(fill='both', expand=1)
        self.canvas.pack(fill='both', expand=1)

    def add_keybinding(self, key, action):
        self.canvas.bind(key, action)

    @staticmethod
    def create_canvas():
        pass

    def draw_image(self, image):
        self.canvas.create_image(0, 0, image=image, anchor="nw")

    def plot_grid_data(self, grid_data):
        self.canvas.delete("grid")

        x, y, wR = grid_data['oval']
        self.canvas.create_oval(x, y, x + (2 * wR), y + (2 * wR),
                           outline="red", tag="grid")

        for s in grid_data['spokes']:
            wX, wY, pX, pY = s
            self.canvas.create_line(wX, wY, pX, pY, fill="red", tag="grid")

    @staticmethod
    def draw_patch(canvas, plottable_points):
        points = plottable_points['points']
        canvas.delete("sky_polygon")
        if len(points) > 3:
            xy = [i for dot in points for i in dot[:2]]
            sky_polygon = canvas.create_polygon(*xy, fill="", outline='blue')
            canvas.itemconfig(sky_polygon, tags=("sky_polygon"))

    @staticmethod
    def draw_dots(canvas, plottable_points):
        for p in plottable_points['points']:
            x, y, overhang, uid = p
            if overhang:
                style = plot_styles['overhangingpoint']
                item = canvas.create_rectangle(x - 2, y - 2, x + 2, y + 2, **style)
            else:
                style = plot_styles['regularpoint']
                item = canvas.create_oval(x - 2, y - 2, x + 2, y + 2, **style)
                                                    
            canvas.itemconfig(item, tags=("dot", f"id:{uid}"))

    @staticmethod
    def draw_selection_rectangle(event, select_x, select_y):
        rect = event.widget.find_withtag("selection_rectangle")
        if rect:
            event.widget.delete(rect)
        event.widget.create_rectangle(select_x, select_y,
                                      event.x, event.y, fill="",
                                      dash=(4, 2),
                                      tag="selection_rectangle")

    def delete_all_overlays(self):
        self.canvas.delete("all")

    @staticmethod
    def plot_azimuth_data(canvas, azimuth_data):
        wX, wY, pX, pY = azimuth_data
        canvas.delete("azimuth")
        canvas.create_line(wX, wY, pX, pY, tag="azimuth",
                           fill="green", width=3)

    def turn_off_grid(self):
        self.canvas.delete("grid")
        self.canvas.delete("azimuth")


class MainMenu:
    
    def __init__(self, root):
        self.menubar = tk.Menu(root)
        self.top_level_items = dict()
    
    def add_toplevel_menu(self, name):
        self.top_level_items[name] = tk.Menu(self.menubar, tearoff=0)

    def add_menu_command(self, label, command, parent):
        self.top_level_items[parent].add_command(label=label, 
                                                 command=command)

    


    