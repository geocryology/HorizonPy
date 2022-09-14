try:  # python 2
    import Tkinter as tk
    import tkFileDialog
    import tkMessageBox
    from itertools import izip
except ImportError:  # python 2

    import tkinter as tk
    import tkinter.filedialog as tkFileDialog
    import tkinter.messagebox as tkMessageBox
    izip = zip

import logging
import matplotlib as mpl
import numpy as np
import os

from PIL import ImageTk, ImageEnhance
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from horizonpy.quickhorizon.ArcSkyDialog import ArcSkyDialog
from horizonpy.quickhorizon.GridDialog import GridDialog
from horizonpy.quickhorizon.AzimuthDialog import AzimuthDialog
from horizonpy.quickhorizon.SkyViewFactorDialog import SkyViewFactorDialog
from horizonpy.quickhorizon.LensSelectionDialog import LensSelectionDialog
from horizonpy.quickhorizon.HorizonPoints import HorizonPoints
from horizonpy.quickhorizon.ImageState import ImageState, EventState
from horizonpy.quickhorizon.View import StatusBar
from horizonpy.quickhorizon.geometry import find_angle
from horizonpy import __version__ as _version
import horizonpy.quickhorizon.HorizonDecorators as hd
import horizonpy.quickhorizon.LensCalibrations as lens

####################################################################
# Main
####################################################################


class LoadImageApp(tk.Toplevel):

    def __init__(self, root, image_file=None):
        self.parent = root
        self.frame = tk.Frame(root, bg='black')
        self.lens = lens.SunexLens
        self.image_state = ImageState()
        self.event_state = EventState()
        self.points = HorizonPoints()
        self.image_state.imageFile = image_file  # TODO: remove?
        self.tool = "move"

        # File associations
        self.file_opt = options = {}
        options['defaultextension'] = '.gif'
        options['filetypes'] = [('all files', '.*'),
                                ('ppm files', '.ppm'),
                                ('pgm files', '.pgm'),
                                ('gif files', '.gif'),
                                ('jpg files', '.jpg'),
                                ('jpeg files', '.jpeg')]
        options['initialdir'] = '.'

        # Importing csv file
        self.csv_opt = csv_options = {}
        csv_options['defaultextension'] = '.hpt.csv'
        csv_options['filetypes'] = [('all files', '.*'),
                                    ('horizon csv files', '.hpt.csv')]

        csv_options['initialdir'] = "."

        # Importing azimuth files
        self.azm_opt = azm_options = {}
        azm_options['defaultextension'] = '.azm.ini'
        azm_options['filetypes'] = [('all files', '.*'),
                                    ("Azimuth files", ".azm.ini")]
        azm_options['initialdir'] = "."

        # Create canvas
        self.canvas = tk.Canvas(self.frame, width=800, height=600, bg='gray')
        self.canvas.focus_set()

        # Create the image on canvas
        if image_file:
            self.init_canvas(self.canvas, image_file)

        self.frame.pack(fill='both', expand=1)
        self.canvas.pack(fill='both', expand=1)

        # Menu items
        menubar = tk.Menu(root)

        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open Image", command=self.open_file)
        exportmenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_cascade(label="Export", menu=exportmenu)
        exportmenu.add_command(label="Export CSV", command=self.save_csv)
        exportmenu.add_command(label="Export GEOtop horizon file",
                               command=self.save_geotop_hrzn)
        exportmenu.add_command(label="Export Azimuth grid",
                               command=self.save_azimuth)
        filemenu.add_command(label="Import CSV", command=self.open_csv)
        filemenu.add_command(label="Import Azimuth", command=self.load_azimuth)
        filemenu.add_command(label="Exit", command=self.exit_app)
        menubar.add_cascade(label="File", menu=filemenu)

        toolsmenu = tk.Menu(menubar, tearoff=0)

        toolsmenu.add_command(label="Pan (Move)", command=self.move)
        toolsmenu.add_command(label="Draw Horizon Points", command=self.dot)
        toolsmenu.add_command(label="Delete Selection", command=self.select)
        toolsmenu.add_command(label="Delete All Points", command=self.delete_all)
        toolsmenu.add_command(label="Plot Horizon", command=self.plothorizon)
        toolsmenu.add_command(label="Compute SVF", command=self.svf)
        toolsmenu.add_command(label="Process ArcGIS file", command=self.arcsky)

        menubar.add_cascade(label="Tools", menu=toolsmenu)

        gridmenu = tk.Menu(menubar, tearoff=0)
        drawgridmenu = tk.Menu(menubar, tearoff=0)
        gridmenu.add_cascade(label="Draw Azimuth Grid", menu=drawgridmenu)
        drawgridmenu.add_command(label="Sunex 5.6mm Fisheye",
                                 command=lambda: self.create_grid_based_on_lens((397, 268), 251, 15))
        drawgridmenu.add_command(label="Custom Grid...", command=self.show_grid)

        gridmenu.add_command(label="Define Image Azimuth",
                             command=self.define_azimuth)
        gridmenu.add_command(label="Enter Field Azimuth",
                             command=self.define_field_azimuth)
        gridmenu.add_command(label="Select Lens Calibration",
                             command=self.select_lens)
        menubar.add_cascade(label="Azimuth", menu=gridmenu)

        viewmenu = tk.Menu(menubar, tearoff=0)
        viewmenu.add_command(label="Toggle Overlays (t)",
                             command=self.toggle_grid)
        viewmenu.add_command(label="Zoom In", command=self.zoom_in)
        viewmenu.add_command(label="Zoom Out", command=self.zoom_out)
        viewmenu.add_command(label="Reset Zoom", command=self.zoom_original)
        menubar.add_cascade(label="View", menu=viewmenu)

        imagemenu = tk.Menu(menubar, tearoff=0)

        imagemenu.add_command(label="Increase Contrast  <o>",
                              command=self.increase_contrast)
        imagemenu.add_command(label="Decrease Contrast <p>",
                              command=self.decrease_contrast)
        imagemenu.add_command(label="Increase Brightness <q>",
                              command=self.increase_brightness)
        imagemenu.add_command(label="Decrease Brightness <w>",
                              command=self.decrease_brightness)
        menubar.add_cascade(label="Image", menu=imagemenu)

        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="Show Point Coordinates",
                             command=self.show_dots)
        helpmenu.add_command(label="About QuickHorizon", command=self.about)

        menubar.add_cascade(label="Help", menu=helpmenu)

        # Attach menu bar to interface
        root.config(menu=menubar)

        # Show status bar
        self.status_bar = StatusBar(root)

        # Events
        self.canvas.bind("<MouseWheel>", self.zoom_wheel)
        self.canvas.bind("<Motion>", self.motion)
        self.canvas.bind("<ButtonPress-1>", self.b1down)
        self.canvas.bind("<ButtonRelease-1>", self.b1up)
        self.canvas.bind("<ButtonPress-2>", self.b2down)
        self.canvas.bind("<ButtonRelease-2>", self.b2up)
        self.canvas.bind("<ButtonPress-3>", self.b3down)
        self.canvas.bind("<ButtonRelease-3>", self.b3up)
        self.canvas.bind("<Configure>", self.resize_window)
        self.canvas.bind("1", self.zoom_in)
        self.canvas.bind("2", self.zoom_out)
        self.canvas.bind("p", self.increase_contrast)
        self.canvas.bind("o", self.decrease_contrast)
        self.canvas.bind("w", self.increase_brightness)
        self.canvas.bind("q", self.decrease_brightness)
        self.canvas.bind("t", self.toggle_grid)

    def set_file_locations(self, image_dir):
        name = os.path.splitext(os.path.basename(self.image_state.imageFile))[0]

        self.file_opt['initialdir'] = image_dir

        self.csv_opt['initialdir'] = image_dir
        self.csv_opt['initialfile'] = name + self.csv_opt['defaultextension']

        self.azm_opt['initialdir'] = image_dir
        self.azm_opt['initialfile'] = name + self.azm_opt['defaultextension']

    ####################################################################
    # Canvas and Image File
    ####################################################################
    def init_canvas(self, canvas, image_file):

        # Reset when a new image opened
        self.event_state.reset_buttons()
        self.image_state.grid_set = False

        self.points.delete_all()

        if image_file:
            self.load_image(canvas, image_file)

        default_azm = os.path.join(self.azm_opt['initialdir'], self.azm_opt['initialfile'])
        if os.path.isfile(default_azm):
            logging.info('Azimuth data found: {}'.format(default_azm))
            self.load_azimuth(default_azm)

        else:
            logging.info('No azimuth file found')

        default_pts = os.path.join(self.csv_opt['initialdir'], self.csv_opt['initialfile'])
        if os.path.isfile(default_pts):
            logging.info('Horizon points file found {}'.format(default_pts))
            self.open_csv(default_pts)
        else:
            logging.info('No horizon points file found')

    def reload_image(self):
        # Create objects to adjust brightness and contrast

        self.image_state.raw_image = self.apply_enhancement(self.image_state.orig_img,
                                                ImageEnhance.Contrast,
                                                self.image_state.contrast_value)

        self.image_state.raw_image = self.apply_enhancement(self.image_state.raw_image,
                                                ImageEnhance.Brightness,
                                                self.image_state.brightness_value)

        self.image_state.p_img = ImageTk.PhotoImage(self.image_state.raw_image)
        self.canvas.create_image(0, 0, image=self.image_state.p_img, anchor="nw")
        self.zoom_current()

    @hd.require_image_file
    def adjust_contrast(self, increment, *args):
        self.image_state.contrast_value += increment
        self.reload_image()

    def increase_contrast(self, event=None, increment=0.1):
        self.adjust_contrast(increment)

    def decrease_contrast(self, event=None, increment=-0.1):
        self.adjust_contrast(increment)

    @hd.require_image_file
    def adjust_brightness(self, increment, *args):
        self.image_state.brightness_value += increment
        self.reload_image()

    def increase_brightness(self, event=None, increment=0.1):
        self.adjust_brightness(increment)

    def decrease_brightness(self, event=None, increment=-0.1):
        self.adjust_brightness(increment)

    def apply_enhancement(self, image, enhancement, increment):
        if image.mode == 'I':
            logging.info("Cannot apply enhancement to image")
            return image
        else:
            return enhancement(image).enhance(increment)

    def load_image(self, canvas, image_file):
        self.image_state.load_image(image_file)

        image_dir = os.path.dirname(image_file)
        self.set_file_locations(image_dir)

        # Change size of canvas to new width and height
        (width, height) = self.image_state.raw_image.size
        canvas.config(width=width, height=height)

        # Remove all canvas items
        canvas.delete("all")
        canvas.create_image(0, 0, image=self.image_state.p_img, anchor="nw")

    def draw_dots(self, canvas, horizon_points):
        for dot in horizon_points.get():

            (x, y) = self.image_state.to_window((dot[0], dot[1]))

            if dot[2] >= 90:  # if horizon is greater than 90, overhanging pt
                item = canvas.create_rectangle(x - 2, y - 2,
                                                  x + 2, y + 2,
                                                  fill="yellow")
            elif 0 <= dot[2] < 90:
                item = canvas.create_oval(x - 2, y - 2,
                                             x + 2, y + 2,
                                             fill="blue", outline='pink')
            else:
                item = canvas.create_oval(x - 2, y - 2,
                                             x + 2, y + 2, fill="white")

            canvas.itemconfig(item, tags=("dot", str(dot[0]), str(dot[1])))

            self.draw_patch(canvas)

    def draw_patch(self, canvas):
        self.canvas.delete("sky_polygon")
        if len(self.points.get()) > 3:
            scaled = [self.image_state.to_window((dot[0], dot[1])) for dot in self.points.get()]
            xy = [i for dot in scaled for i in dot[:2]]
            sky_polygon = canvas.create_polygon(*xy, fill="", outline='blue')
            canvas.itemconfig(sky_polygon, tags=("sky_polygon"))

    def draw_grid(self, canvas):
        grid_data = self.image_state.get_plottable_grid()
        self.plot_grid_data(canvas, grid_data)

    def plot_grid_data(self, canvas, grid_data):
        canvas.delete("grid")

        x, y, wR = grid_data['oval']
        canvas.create_oval(x, y, x + (2 * wR), y + (2 * wR),
                           outline="red", tag="grid")

        for s in grid_data['spokes']:
            wX, wY, pX, pY = s
            canvas.create_line(wX, wY, pX, pY, fill="red", tag="grid")

    def set_azimuth(self, anchor):
        self.image_state.update_azimuth(anchor)

    def plot_azimuth_data(self, canvas, azimuth_data):
        wX, wY, pX, pY = azimuth_data
        canvas.delete("azimuth")
        canvas.create_line(wX, wY, pX, pY, tag="azimuth",
                           fill="green", width=3)

    def draw_azimuth(self, canvas):
        azimuth_data = self.image_state.get_plottable_azimuth()
        self.plot_azimuth_data(canvas, azimuth_data)

    def display_region(self, canvas):
        canvas.delete("all")

        # Display the region of the zoomed image starting at viewport and window size
        x, y = self.image_state.viewport
        w = self.frame.winfo_width()
        h = self.frame.winfo_height()

        tmp = self.image_state.zoomed_image.crop((x, y, x + w, y + h))

        self.image_state.p_img = ImageTk.PhotoImage(tmp)
        canvas.config(bg="gray50")
        canvas.create_image(0, 0, image=self.image_state.p_img, anchor="nw")

        # Draw  saved dots
        if self.points.any_defined():
            self.draw_dots(canvas, self.points)

        if self.image_state.show_grid:
            self.draw_grid(canvas)

            if 0 <= self.image_state.image_azimuth <= 360:
                self.draw_azimuth(canvas)

    ########################################################
    # Menu options
    ########################################################

    def open_file(self):
        file = tkFileDialog.askopenfilename(**self.file_opt)

        if not file:
            return

        # Initialize the canvas with an image file
        self.init_canvas(self.canvas, file)

    @hd.require_image_azimuth
    @hd.require_grid
    def open_csv(self, file=None):
        # Open a CSV file with previous XY coordinates

        if not file:
            file = tkFileDialog.askopenfilename(**self.csv_opt)

        if file:
            self.points.import_horizon_csv(file)
            self.draw_dots(self.canvas, self.points)
        else:
            logging.info('No file selected')

    @hd.require_image_azimuth
    @hd.require_grid
    def open_geotop(self, file=None):
        # Open a CSV file with previous XY coordinates

        if not file:
            file = tkFileDialog.askopenfilename(**self.csv_opt)

        if file:
            self.points.import_geotop_csv(file)
            self.draw_dots(self.canvas, self.points)

        else:
            logging.info('No file selected')

    @hd.require_field_azimuth
    @hd.require_horizon_points
    def save_csv(self):
        # Save the dots to CSV file
        self.points.update_field_azimuth(self.image_state.field_azimuth)

        try:
            f_name = tkFileDialog.asksaveasfilename(**self.csv_opt)
            if f_name:
                self.points.export_to_horizon_csv(f_name)

        except PermissionError as e:
            tkMessageBox.showerror("Error!",
                                   "Could not access file. Maybe it is already open?")
            logging.error(e)

    @hd.require_field_azimuth
    @hd.require_horizon_points
    def save_geotop_hrzn(self):
        # Save the horizon points to CSV file

        if not tkMessageBox.askokcancel("Warning!",
                                        "Horizon angles greater than 90 degrees are not "
                                        "compatible with geotop horizon files. They will be reduced "
                                        "to 90 degrees. Click OK to continue or Cancel to abort"):
            return

        self.points.update_field_azimuth(self.image_state.field_azimuth)

        try:
            f_name = tkFileDialog.asksaveasfilename(defaultextension=".txt")

            if f_name:
                self.points.export_to_geotop(f_name, delta=3)

        except PermissionError as e:
            tkMessageBox.showerror("Error!", "Could not access file.  Maybe it is already open?")
            logging.error(e)

    @hd.require_field_azimuth
    @hd.require_image_azimuth
    def save_azimuth(self):
        f_name = tkFileDialog.asksaveasfilename(**self.azm_opt)

        if f_name:
            self.image_state.save_azimuth_config(f_name)

    def load_azimuth(self, f_name=None):
        if not f_name:
            f_name = tkFileDialog.askopenfilename(**self.azm_opt)
        if f_name:
            self.image_state.load_azimuth_config(f_name)
            self.draw_grid(self.canvas)
            self.image_state.grid_set = True
            self.draw_azimuth(self.canvas)
            self.image_state.turn_on_grid()

    def exit_app(self):
        self.parent.destroy()

    def move(self):
        self.tool = "move"

    def select(self):
        self.tool = "select"

    def show_dots(self):
        tkMessageBox.showinfo("Dot Info", self.points.print_dots())

    def about(self):
        tkMessageBox.showinfo("About QuickHorizon",
                              (f"Version: {_version}\n"
                               "\nContributors:\n"
                               "Nick Brown (nick.brown@carleton.ca)\n"
                               "Stephan Gruber (stephan.gruber@carleton.ca)\n"
                               "Mark Empey\n"
                               "\nMore information:\n"
                               "github.com/geocryology/horizonpy")
                              )

    def delete_all(self):
        selection = self.canvas.find_withtag("dot")
        self.delete_dots(selection)

    def show_grid(self):
        # Get x,y coords and radius for of wheel
        if self.image_state.raw_image:

            d = GridDialog(self.parent, title="Wheel Preferences",
                           center=self.image_state.image_center, radius=self.image_state.radius,
                           spacing=self.image_state.spoke_spacing)

            self.canvas.focus_set()

            if d.result:
                logging.info("Set grid properties")
                self.image_state.image_center = d.center
                self.image_state.radius = d.radius
                self.image_state.spoke_spacing = d.spoke_spacing
                if not self.image_state.show_grid:
                    self.image_state.show_grid = d.result

                if self.image_state.show_grid:
                    self.draw_grid(self.canvas)
                    self.image_state.grid_set = True

    def create_grid_based_on_lens(self, center, radius, spoke_spacing):
        self.image_state.set_grid_from_lens(center, radius, spoke_spacing)
        self.draw_grid(self.canvas)

    def toggle_grid(self, *args):
        if not self.image_state.raw_image:
            return

        if self.image_state.show_grid:
            self.image_state.turn_off_grid()
            self.canvas.delete("grid")
            self.canvas.delete("azimuth")
        else:
            if self.canvas and self.image_state.image_center and self.image_state.radius:
                self.image_state.turn_on_grid()
                self.draw_grid(self.canvas)

                if self.image_state.anchor[0] != -999:
                    self.draw_azimuth(self.canvas)
            else:
                tkMessageBox.showerror("Error!",
                                       "No overlay parameters have been set!")

    @hd.require_image_file
    @hd.require_grid
    def define_azimuth(self):
        self.tool = "azimuth"

    @hd.require_image_file
    @hd.require_image_azimuth
    def define_field_azimuth(self):
        if self.warn_dots:
            d = AzimuthDialog(self.parent, azimuth=self.image_state.field_azimuth)
            self.canvas.focus_set()
            if d:
                self.image_state.field_azimuth = d.azimuth

    def warn_dots(self):
        if self.points.any_defined():
            dialog = tkMessageBox.askokcancel("Warning!",
                                              """Are you sure you want to
                                              change this parameter? calculated
                                              azimuth values will be affected.
                                              Click OK to continue.""")
            return(dialog)

        else:
            return(True)

    @hd.require_image_file
    @hd.require_image_azimuth
    def dot(self):
        self.tool = "dot"

    @hd.require_image_file
    def zoom_in(self, *args):
        try:
            self.image_state.zoom_level += 1
            self.image_state.scale_image()
            self.display_region(self.canvas)

        except ValueError:
            logging.info("Max zoom reached!")

    @hd.require_image_file
    def zoom_out(self, *args):
        try:
            self.image_state.zoom_level -= 1
            self.image_state.scale_image()
            self.display_region(self.canvas)

        except ValueError:
            logging.info("Min zoom reached!")

    @hd.require_image_file
    def zoom_original(self):
        self.image_state.reset_zoom()
        self.image_state.scale_image()
        self.display_region(self.canvas)

    @hd.require_image_file
    def zoom_current(self, *args):
        self.image_state.scale_image()
        self.display_region(self.canvas)

    #######################################################
    # Mouse options
    #######################################################

    def store_xy_selection(self, event):
        self.select_X, self.select_Y = event.x, event.y

    def zoom_wheel(self, event):

        if self.image_state.raw_image:
            (x, y) = self.image_state.to_raw((event.x, event.y))

            if event.delta > 0:
                increment = 1
            elif event.delta < 0:
                increment = -1
            else:
                return

            try:
                self.image_state.zoom_level += increment
            except ValueError:
                logging.info('Zoom limit reached!')
                return

            self.image_state.scale_image()

            view_x = int(x * self.image_state.zoomcoefficient) - x
            view_y = int(y * self.image_state.zoomcoefficient) - y
            self.image_state.viewport = (view_x, view_y)
            self.display_region(self.canvas)

    def b1down(self, event):
        logging.debug('b1down() at ({},{})'.format(event.x, event.y))
        self.store_xy_selection(event)
        self.event_state.button_1 = "down"

        if self.image_state.raw_image:
            if self.tool == "dot":
                raw = self.image_state.to_raw((event.x, event.y))
                self._define_new_dot(raw, overhanging=False)
                self.draw_dots(self.canvas, self.points)

            else:
                if self.tool == "azimuth":
                    self.draw_grid(self.canvas)

                    self.image_state.set_anchor(event)
                    self.draw_azimuth(self.canvas)

    def select_dots_from_rectangle(self, event):
        items = event.widget.find_enclosed(self.select_X, self.select_Y,
                                           event.x, event.y)

        rect = event.widget.find_withtag("selection_rectangle")
        if rect:
            event.widget.delete(rect)

        selected = [x for x in items if event.widget.gettags(x)[0] == 'dot']
        return selected

    def b1up(self, event):
        self.event_state.button_1 = "up"
        logging.debug('b1up()-> tool = %s at (%d, %d)',
                      self.tool, event.x, event.y)
        if not self.image_state.raw_image:
            return

        self.event_state.reset_event()

        if self.tool == "select":
            selected_dots = self.select_dots_from_rectangle(event)
            self.delete_dots(selected_dots)

        elif self.tool == "azimuth":
            self.points.update_image_azimuth(self.image_state.image_center,
                                             self.image_state.radius,
                                             self.image_state.image_azimuth,
                                             self.image_state.image_azimuth_coords,
                                             self.lens)

            self.draw_dots(self.canvas, self.points)
            if self.image_state.field_azimuth == -1:
                self.define_field_azimuth()

    def delete_dots(self, selected_dots):
        to_delete = {}
        for i in selected_dots:
            self.canvas.itemconfig(i, fill="red", outline="red")

            tags = self.canvas.gettags(i)
            to_delete[i] = (int(tags[1]), int(tags[2]))

            logging.debug('Selected Item-> %d with tags %s, %s, %s', i,
                          tags[0], tags[1], tags[2])

        if to_delete:
            confirm = tkMessageBox.askokcancel("Confirm deletion?", "Press OK to delete selected dot(s)!")

            if confirm:
                for i, coords in to_delete.items():
                    self.points.del_point_with_coordinates(coords)
                    logging.debug('Removing dot %d with coords: %d, %d', i,
                                  coords[0], coords[1])
                    self.canvas.delete(i)

            else:
                logging.info('Dot deletion cancelled!')

        self.display_region(self.canvas)

    def b2down(self, event):
        self.event_state.button_2 = "down"

    def b2up(self, event):
        self.event_state.button_2 = "up"
        self.event_state.reset_event()

    def b3down(self, event):
        logging.debug('b3down() at ({},{})'.format(event.x, event.y))

        if self.image_state.raw_image:
            if self.tool == "dot":
                raw = self.image_state.to_raw((event.x, event.y))
                self._define_new_dot(raw, overhanging=True)
                self.draw_dots(self.canvas, self.points)

    def _define_new_dot(self, raw, overhanging=False):
        self.points.add_raw(raw[0], raw[1], self.image_state.image_center, self.image_state.radius,
                            self.image_state.image_azimuth_coords,
                            self.lens, overhanging)

    def b3up(self, event):
        pass

    def pan(self, event):
        xold, yold = self.event_state.old_event
        self.image_state.update_viewport(event.x, event.y,
                                         xold, yold)
        self.display_region(self.canvas)

    # Handles mouse
    def motion(self, event):

        # Button 2 pans no matter what
        if self.image_state.raw_image and self.event_state.button_2 == "down":
            self.pan(event)

        # Conditional on button 1 depressed
        if self.image_state.raw_image and self.event_state.button_1 == "down":
            if self.tool == "move":     # Panning
                self.pan(event)

            elif self.tool == "select":
                self.update_selection_rectangle(event)

        self.event_state.store_event(event.x, event.y)
        self.update_status_bar(event)

    def update_selection_rectangle(self, event):
        rect = event.widget.find_withtag("selection_rectangle")
        if rect:
            event.widget.delete(rect)
        event.widget.create_rectangle(self.select_X, self.select_Y,
                                      event.x, event.y, fill="",
                                      dash=(4, 2),
                                      tag="selection_rectangle")

    def update_status_bar(self, event):
        cursor_loc = self.image_state.to_raw((event.x, event.y))

        try:
            img_value = self.image_state.raw_image.getpixel(cursor_loc)
        except (IndexError, AttributeError):
            img_value = None

        self.status_bar.display(cursor_loc, self.image_state.image_azimuth, self.image_state.field_azimuth, img_value)

    def resize_window(self, event):
        if self.image_state.zoomed_image:
            self.display_region(self.canvas)

    def find_horizon(self, dot_radius, grid_radius):
        horizon = self.lens.horizon_from_radius(dot_radius, grid_radius)
        return horizon

    @hd.require_horizon_points
    @hd.require_image_azimuth
    def plothorizon(self, show=True):
        fig, ax = mpl.pyplot.subplots(1, 1, sharex=True)
        plot_dots = self.points.get()
        plot_dots.sort(key=lambda x: x[3])  # sort dots using image azimuth
        image_azim = [x[3] for x in plot_dots]
        image_azim.insert(0, (image_azim[-1] - 360))
        image_azim.append(image_azim[1] + 360)
        horiz = [x[2] for x in plot_dots]
        horiz.insert(0, horiz[-1])
        horiz.append(horiz[1])
        plot_dots.sort(key=lambda x: (x[3] + 180) % 360)
        ia_over = [(x[3] + 180) % 360 for x in plot_dots]
        ia_over.insert(0, (ia_over[-1] - 360))
        ia_over.append(ia_over[1] + 360)
        h_over = [180 - x[2] for x in plot_dots]
        h_over.insert(0, h_over[-1])
        h_over.append(h_over[1])
        ax.set_xlabel('Image Azimuth')
        ax.set_ylabel('Horizon Angle')
        ax.set_facecolor('blue')
        ax.set_xlim((0, 360))
        ax.set_ylim((0, 90))
        horiz = np.array(horiz)
        image_azim = np.array(image_azim)
        h_over = np.array(h_over)
        ia_over = np.array(ia_over)
        ax.plot(image_azim, horiz, 'ko')
        ax.fill_between(image_azim, np.zeros(len(horiz)), np.minimum(horiz, 90), color='brown')
        if any(h_over > 90):
            ax.fill_between(ia_over, h_over, np.zeros(len(horiz)) + 180, where=h_over < 90, color='brown')
        if show:
            mpl.pyplot.show()
        return(fig)

    @hd.require_horizon_points
    @hd.require_image_azimuth
    def popupimage(self):
        self.root2 = tk.Tk()
        fig = self.plothorizon(show=False)
        canvas2 = FigureCanvasTkAgg(fig, master=self.root2)
        canvas2.show()
        canvas2.get_tk_widget().pack(side="top", fill="both", expand=1.0)
        canvas2.draw()

    @hd.require_horizon_points
    def svf(self):
        SkyViewFactorDialog(self, self.points, self.image_state.field_azimuth)

    def arcsky(self):
        _ = ArcSkyDialog(self)

    def select_lens(self):
        lens_selection = LensSelectionDialog(self.parent, default=self.lens.NAME)
        if lens_selection.lens:
            self.lens = lens_selection.lens
            logging.info("Set lens calibration to {}".format(self.lens.NAME))

        if self.image_state.imageFile:
            self.points.update_image_azimuth(self.image_state.image_center,
                                             self.image_state.radius,
                                             self.image_state.image_azimuth,
                                             self.image_state.image_azimuth_coords,
                                             self.lens)
