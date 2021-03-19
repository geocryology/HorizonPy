try:  # python 2
    import Tkinter as tk
except ImportError:  # python 2
    import tkinter as tk
    import tkinter.messagebox as tkMessageBox

from horizonpy.quickhorizon.utils import plot_styles
import logging
from PIL import Image, ImageTk, ImageEnhance
from copy import copy
import numpy as np


class MainView:

    DEFAULT_ZOOM = 0
    MIN_ZOOM = 0
    MAX_ZOOM = 5
    DEFAULT_VIEWPORT = (0,0)

    def __init__(self, root):
        self.frame = tk.Frame(root, bg='black')
        self._zoom_level = self.DEFAULT_ZOOM
        self._old_zoom_level = None
        self.build_zoom_levels()
        self.viewport = self.DEFAULT_VIEWPORT  # Used for zoom and pan
        self.zoomed_image = None

        self._contrast_value = 1
        self._old_contrast_value = None
        self._brightness_value = 1
        self._old_brightness_value = None

        self.raw_image = None
        self.orig_image = None
        # Create canvas
        self.canvas = tk.Canvas(self.frame, width=800, height=600, bg='gray')
        self.canvas.focus_set()

        self.frame.pack(fill='both', expand=1)
        self.canvas.pack(fill='both', expand=1)

        self._show_grid = False

    @property
    def zoom_level(self):
        return self._zoom_level

    @zoom_level.setter
    def zoom_level(self, value):
        if not value >= self.MIN_ZOOM:
            raise ValueError("Attempted to set too small zoom value")

        if not value <= self.MAX_ZOOM:
            raise ValueError("Attempted to set too large zoom value")

        self._old_zoom_level = self._zoom_level
        self._zoom_level = value
        logging.info("zoom level is {}".format(self._zoom_level))

    def reset_zoom(self):
        self.zoom_level = self.DEFAULT_ZOOM
        self.viewport = self.DEFAULT_VIEWPORT
        self.scale_image()

    def build_zoom_levels(self):
        self.mux = {0: 1.0}
        for n in range(1, self.MAX_ZOOM + 1, 1):
            self.mux[n] = round(self.mux[n - 1] * 1.5, 5)

        for n in range(-1, self.MIN_ZOOM - 1, -1):
            self.mux[n] = round(self.mux[n + 1] * 1.5, 5)

    def update_viewport(self, new_x, new_y, old_x, old_y):
        if not all((old_x, old_y)):
            return
        view_x = self.viewport[0] - (new_x - old_x)
        view_y = self.viewport[1] - (new_y - old_y)
        self.viewport = (view_x, view_y)

    def zoom_in(self):
        self.zoom_level += 1
        self.scale_image()

    def zoom_out(self):
        self.zoom_level -= 1
        self.scale_image()

    def zoom_wheel(self, event):
        if self.raw_image:
            (x, y) = self.to_raw((event.x, event.y))

            if event.delta > 0:
                increment = 1
            elif event.delta < 0:
                increment = -1
            else:
                return

            try:
                self.zoom_level += increment
            except ValueError:
                logging.info('Zoom limit reached!')
                return

            self.scale_image()

            view_x = int(x * self.zoomcoefficient) - x
            view_y = int(y * self.zoomcoefficient) - y
            self.viewport = (view_x, view_y)

    def to_raw(self, p):
        x, y = p
        # Translate the x,y coordinate from window to raw image coordinate
        (vx, vy) = self.viewport
        raw_x = int((x + vx) / self.zoomcoefficient)
        raw_y = int((y + vy) / self.zoomcoefficient)

        return (raw_x, raw_y)

    @property
    def contrast_value(self):
        return self._contrast_value

    @contrast_value.setter
    def contrast_value(self, value):
        self._old_contrast_value = self._contrast_value
        self._contrast_value = value
        logging.info('Image contrast changed from {:.2f} to {:.2f}'.format(
                     self._old_contrast_value, self._contrast_value))

    @property
    def brightness_value(self):
        return self._brightness_value

    @brightness_value.setter
    def brightness_value(self, value):
        self.old_brightness_value = self._brightness_value
        self._brightness_value = value
        logging.info('Image brightness changed from {:.2f} to {:.2f}'.format(
                     self.old_brightness_value, self._brightness_value))

    def apply_enhancements(self):
        self.enh_image = self.apply_enhancement(self.zoomed_image,
                                                ImageEnhance.Contrast,
                                                self.contrast_value,
                                                self._old_contrast_value)

        self.enh_image = self.apply_enhancement(self.enh_image,
                                                ImageEnhance.Brightness,
                                                self.brightness_value,
                                                self._old_brightness_value)

    def apply_enhancement(self, image, enhancement, new_value, old_value):
        if image.mode == 'I':
            logging.info("Cannot apply enhancement to image")
            return image
        if new_value == old_value:
            return image
        else:
            return enhancement(image).enhance(new_value)

    def to_window(self, p):
        x, y = p
        # Translate the x,y coordinate from raw image coordinate to window coordinate
        (vx, vy) = self.viewport
        window_x = int(x * self.zoomcoefficient) - vx
        window_y = int(y * self.zoomcoefficient) - vy

        return (window_x, window_y)

    def scale_image(self):
        # Resize image
        if self._old_zoom_level == self.zoom_level:
            return

        raw_x, raw_y = self.raw_image.size
        new_w = int(raw_x * self.zoomcoefficient)
        new_h = int(raw_y * self.zoomcoefficient)

        self.scaled_image = self.raw_image.resize((new_w, new_h),
                                                  Image.ANTIALIAS)

        self._old_zoom_level = self.zoom_level

    def crop_image(self):
        # Display the region of the zoomed image starting at viewport and window size
        x, y = self.viewport
        w = self.frame.winfo_width()
        h = self.frame.winfo_height()

        self.zoomed_image = self.scaled_image.crop((x, y, x + w, y + h))

    @property
    def zoomcoefficient(self):
        return self.mux[self.zoom_level]

    @zoomcoefficient.setter
    def zoomcoefficient(self):
        raise RuntimeError("You can't set this property")

    def add_keybinding(self, key, action):
        self.canvas.bind(key, action)

    @staticmethod
    def create_canvas():
        pass

    def load_image(self, raw_image):
        # Change size of canvas to new width and height
        (width, height) = raw_image.size
        self.canvas.config(width=width, height=height)
        self.raw_image = raw_image
        self.orig_image = copy(raw_image)

    def draw_grid_data(self, grid_data):
        self.canvas.delete("grid")

        x, y, wR = grid_data['oval']
        self.canvas.create_oval(x, y, x + (2 * wR), y + (2 * wR),
                                outline="red", tag="grid")

        for s in grid_data['spokes']:
            wX, wY, pX, pY = s
            self.canvas.create_line(wX, wY, pX, pY, fill="red", tag="grid")

    def plot_grid_data(self, image_center, radius, spoke_spacing):
        (wX, wY) = self.to_window(image_center)
        wR = radius * self.zoomcoefficient

        x = wX - wR
        y = wY - wR
        oval = (x, y, wR)

        spokes = list()
        for n in range(0, 360, spoke_spacing):
            rX = image_center[0] + int(radius * np.cos(np.radians(n)))
            rY = image_center[1] + int(radius * np.sin(np.radians(n)))
            pX, pY = self.to_window((rX, rY))
            spokes.append((wX, wY, pX, pY))

        grid_data = {'oval': oval,
                     'spokes': spokes}

        self.grid_set = True
        self.turn_on_grid()
        self.draw_grid_data(grid_data)

    def draw_patch(self, plottable_points):
        points = plottable_points['points']
        self.canvas.delete("sky_polygon")
        if len(points) > 3:
            xy = [self.to_window((x,y)) for dot in points for (x,y) in [dot[:2]]]
            sky_polygon = self.canvas.create_polygon(*xy, fill="", outline='blue')
            self.canvas.itemconfig(sky_polygon, tags=("sky_polygon"))

    def draw_dots(self, plottable_points):
        for p in plottable_points['points']:
            x, y, overhang, uid = p
            x, y = self.to_window((x, y))
            if overhang:
                style = plot_styles['overhangingpoint']
                item = self.canvas.create_rectangle(x - 2, y - 2, x + 2, y + 2, **style)
            else:
                style = plot_styles['regularpoint']
                item = self.canvas.create_oval(x - 2, y - 2, x + 2, y + 2, **style)

            self.canvas.itemconfig(item, tags=("dot", f"id:{uid}"))

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

    def plot_azimuth_data(self, image_center, image_azimuth_coords):
        wX, wY = self.to_window(image_center)
        pX, pY = self.to_window(image_azimuth_coords)

        self.canvas.delete("azimuth")
        self.canvas.create_line(wX, wY, pX, pY, tag="azimuth",
                                fill="green", width=3)

    def turn_off_grid(self):
        self._show_grid = False
        self.canvas.delete("grid")
        self.canvas.delete("azimuth")

    def turn_on_grid(self):
        self._show_grid = True

    @property
    def show_grid(self):
        return self._show_grid

    @show_grid.setter
    def show_grid(self, value):
        if not isinstance(value, bool):
            raise ValueError("must be True or False")
        self._show_grid = value

    def render_image(self):
        self.scale_image()
        self.crop_image()
        self.apply_enhancements()
        self.p_img = ImageTk.PhotoImage(self.enh_image)
        self.canvas.create_image(0, 0, image=self.p_img, anchor="nw")

    def adjust_contrast(self, increment, *args):
        self.contrast_value += increment

    def increase_contrast(self, increment=0.1):
        self.adjust_contrast(increment)

    def decrease_contrast(self, increment=-0.1):
        self.adjust_contrast(increment)

    def adjust_brightness(self, increment, *args):
        self.brightness_value += increment

    def increase_brightness(self, increment=0.1):
        self.adjust_brightness(increment)

    def decrease_brightness(self, increment=-0.1):
        self.adjust_brightness(increment)

    def confirm(self, title, message):
        confirm = tkMessageBox.askokcancel(title, message)
        return confirm


class MainMenu:

    def __init__(self, root):
        self.menubar = tk.Menu(root)
        self.top_level_items = dict()

    def add_toplevel_menu(self, name):
        self.top_level_items[name] = tk.Menu(self.menubar, tearoff=0)

    def add_menu_command(self, label, command, parent):
        self.top_level_items[parent].add_command(label=label,
                                                 command=command)


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
            if isinstance(img_value, int):
                img_value_display = "({:03d})".format(img_value)
            else:
                img_value_display = "({:03d}, {:03d}, {:03d})".format(*img_value)
        else:
            img_value_display = "(---, ---, ---)"

        output += "Image value: {}".format(img_value_display).ljust(25)

        self.status.config(text=output)
