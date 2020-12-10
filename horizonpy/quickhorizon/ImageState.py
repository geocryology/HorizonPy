import logging
import configparser
from PIL import Image
import numpy as np
from horizonpy.quickhorizon.geometry import find_angle


class ImageState:

    DEFAULT_IMAGE_AZIMUTH = -1

    def __init__(self):  
        self._show_grid = False
        
        self.image_azimuth_coords = (0,0)
        self.reset_image_azimuth()
        self.anchor = (-999, -999)  # Azimuth anchor
        self.radius = 0
        self.field_azimuth = -1
        self.grid_set = False

        self.raw_image = None
    
    def turn_off_grid(self):
        self._show_grid = False

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

    def get_plottable_grid(self):
        return self.image_center, self.radius, self.spoke_spacing

    @property
    def image_azimuth(self):
        return self._image_azimuth
    
    @image_azimuth.setter
    def image_azimuth(self, value):
        if (0 <= value <= 360 or value == self.DEFAULT_IMAGE_AZIMUTH):
            self._image_azimuth = value
        else:
            raise ValueError("Invalid azimuth value")

    def reset_image_azimuth(self):
        self._image_azimuth = self.DEFAULT_IMAGE_AZIMUTH

    @property
    def image_azimuth_coords(self):
        return self._image_azimuth_coords

    @image_azimuth_coords.setter
    def image_azimuth_coords(self, coords):
        logging.info(f"set image azimuth reference point to {coords}")
        self._image_azimuth_coords = coords

    def get_plottable_azimuth(self):
        return self.image_center, self.image_azimuth_coords
        
    def update_azimuth(self, anchor):
        self.image_azimuth = find_angle(self.image_center, anchor, 
                                        (self.image_center[0] + self.radius, self.image_center[1]))
        
        # Draw the field azimuth in reference to the anchor point
        rX = self.image_center[0] + int(self.radius * np.cos(np.radians(self.image_azimuth)))
        rY = self.image_center[1] + int(self.radius * np.sin(np.radians(self.image_azimuth)))

        # Store field azimuth coordinates (end point)
        self.image_azimuth_coords = (rX, rY)
        
    def save_azimuth_config(self, f_name):
        C = configparser.ConfigParser()
        C.add_section("Azimuth")
        C.set("Azimuth", "grid_centre_x", str(self.image_center[0]))
        C.set("Azimuth", "grid_centre_y", str(self.image_center[1]))
        C.set("Azimuth", "anchor_x", str(self.anchor[0]))
        C.set("Azimuth", "anchor_y", str(self.anchor[1]))
        C.set("Azimuth", "grid_centre_y", str(self.image_center[1]))
        C.set("Azimuth", "radius", str(self.radius))
        C.set("Azimuth", "spokes", str(self.spoke_spacing))
        C.set("Azimuth", "image_azimuth", str(self.image_azimuth))
        C.set("Azimuth", "field_azimuth", str(self.field_azimuth))

        with open(f_name, 'w') as f_name:
            C.write(f_name)

    def load_azimuth_config(self, f_name):
        C = configparser.ConfigParser()
        C.read(f_name)
        self.spoke_spacing = C.getint("Azimuth", "spokes")
        self.image_center = (C.getint("Azimuth", "grid_centre_x"),
                             C.getint("Azimuth", "grid_centre_y"))
        self.radius = C.getint("Azimuth", "radius")
        self.anchor = (C.getint("Azimuth", "anchor_x"),
                       C.getint("Azimuth", "anchor_y"))
        self.radius = C.getint("Azimuth", "radius")
        self.field_azimuth = C.getfloat("Azimuth", "field_azimuth")
        self.image_azimuth = C.getfloat("Azimuth", "image_azimuth")
        self.update_azimuth(self.anchor)

    def set_anchor(self, raw_coords):
        self.anchor = raw_coords
        self.update_azimuth(self.anchor)

    def set_grid_from_lens(self, center, radius, spoke_spacing):
        if self.raw_image:
            self.spoke_spacing = spoke_spacing
            self.image_center = center
            self.radius = radius
            self.grid_set = True
            self.turn_on_grid()

    def load_image(self, image_file):
        self.grid_set = False 
        self.imageFile = image_file
        self.raw_image = Image.open(image_file)
        self.orig_image = Image.open(image_file)
        (width, height) = self.raw_image.size
        self.reset_image_azimuth()

        # Image larger than 1000 pixels, resize to 800 x 600
        if (width > 1000) or (height > 1000):
            self.orig_image.thumbnail((800, 600), Image.ANTIALIAS)
            self.raw_image.thumbnail((800, 600), Image.ANTIALIAS)
            (width, height) = self.raw_image.size
            logging.info("Resizing image to {} x {}".format(width, height))

        # Find center of image and radius
        self.image_center = (int(width / 2), int(height / 2))
        self.radius = int(np.sqrt(self.image_center[0] ** 2 + self.image_center[1] ** 2))
        self.spoke_spacing = 15

        logging.info("Loaded image {}".format(self.imageFile))

        return self.raw_image

class EventState:

    NOEVENT = (None, None)
    TOOL_OPTIONS = ["azimuth", "dot", "select", "move"]

    def __init__(self):
        self.tool = "move"
        self.reset_event()

    def store_event(self, x, y):
        self.old_event = (x, y)

    def store_select(self, event):
        self.select = (event.x, event.y)

    def reset_event(self):
        self.old_event = self.NOEVENT

    def reset_buttons(self):
        self.button_1 = "up"
        self.button_2 = "up"
        self.button_3 = "up"
        self.tool = "move"

    @property
    def tool(self):
        return self._tool
    
    @tool.setter
    def tool(self, value):
        if value in self.TOOL_OPTIONS:
            self._tool = value