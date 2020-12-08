import logging
import configparser
from PIL import Image, ImageTk
import numpy as np


class ImageState:

    DEFAULT_ZOOM = 0
    MIN_ZOOM = 0
    MAX_ZOOM = 5
    DEFAULT_VIEWPORT = (0,0)
    DEFAULT_IMAGE_AZIMUTH = -1

    def __init__(self):
        self._contrast_value = 1
        self._brightness_value = 1
        self._zoom_level = self.DEFAULT_ZOOM
        self.build_zoom_levels()
        self._show_grid = False
        self.viewport = self.DEFAULT_VIEWPORT  # Used for zoom and pan
        
        self.image_azimuth_coords = (0,0)
        self.reset_image_azimuth()
        self.anchor = (-999, -999)  # Azimuth anchor
        self.radius = 0
        self.field_azimuth = -1
        self.grid_set = False
        
        self.raw_image = None
        self.zoomed_image = None


    @property
    def contrast_value(self):
        return self._contrast_value

    @contrast_value.setter
    def contrast_value(self, value):
        old = self._contrast_value
        self._contrast_value = value
        logging.info('Image contrast changed from {:.2f} to {:.2f}'.format(
                     old, self._contrast_value))

    @property
    def brightness_value(self):
        return self._brightness_value

    @brightness_value.setter
    def brightness_value(self, value):
        old = self._brightness_value
        self._brightness_value = value
        logging.info('Image brightness changed from {:.2f} to {:.2f}'.format(
                     old, self._brightness_value))
    
    @property
    def zoom_level(self):
        return self._zoom_level

    @zoom_level.setter
    def zoom_level(self, value):
        if not value >= self.MIN_ZOOM:
            raise ValueError("Attempted to set too small zoom value")
            
        if not value <= self.MAX_ZOOM:
            raise ValueError("Attempted to set too large zoom value")
        
        self._zoom_level = value
        logging.info("zoom level is {}".format(self._zoom_level))

    def reset_zoom(self):
        self._zoom_level = self.DEFAULT_ZOOM
        self.viewport = self.DEFAULT_VIEWPORT

    def build_zoom_levels(self):
        self.mux = {0: 1.0}
        for n in range(1, self.MAX_ZOOM + 1, 1):
            self.mux[n] = round(self.mux[n - 1] * 1.5, 5)

        for n in range(-1, self.MIN_ZOOM - 1, -1):
            self.mux[n] = round(self.mux[n + 1] * 1.5, 5)

    @property
    def zoomcoefficient(self):
        return self.mux[self.zoom_level]

    @zoomcoefficient.setter
    def zoomcoefficient(self):
        raise RuntimeError("You can't set this property")

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

    def update_viewport(self, new_x, new_y, old_x, old_y):
        if not all((old_x, old_y)):
            return
        view_x = self.viewport[0] - (new_x - old_x)
        view_y = self.viewport[1] - (new_y - old_y)
        self.viewport = (view_x, view_y)

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
    
    def set_grid_from_lens(self, center, radius, spoke_spacing):
        if self.raw_image:
            self.spoke_spacing = spoke_spacing
            self.image_center = center
            self.radius = radius
            self.grid_set = True
            self.turn_on_grid()

    def to_raw(self, p):
        x, y = p
        # Translate the x,y coordinate from window to raw image coordinate
        (vx, vy) = self.viewport
        raw_x = int((x + vx) / self.zoomcoefficient)
        raw_y = int((y + vy) / self.zoomcoefficient)
        
        return (raw_x, raw_y)

    def to_window(self, p):
        x, y = p
        # Translate the x,y coordinate from raw image coordinate to window coordinate
        (vx, vy) = self.viewport
        window_x = int(x * self.zoomcoefficient) - vx
        window_y = int(y * self.zoomcoefficient) - vy
        
        return (window_x, window_y)
    
    def scale_image(self):
        # Resize image
        raw_x, raw_y = self.raw_image.size
        new_w = int(raw_x * self.zoomcoefficient)
        new_h = int(raw_y * self.zoomcoefficient)

        self.zoomed_image = self.raw_image.resize((new_w, new_h),
                                                  Image.ANTIALIAS)

    def load_image(self, image_file):
        self.imageFile = image_file
        self.raw_image = Image.open(image_file)
        self.orig_img = Image.open(image_file)
        (width, height) = self.raw_image.size
        self.reset_image_azimuth()

        # Image larger than 1000 pixels, resize to 800 x 600
        if (width > 1000) or (height > 1000):
            self.orig_img.thumbnail((800, 600), Image.ANTIALIAS)
            self.raw_image.thumbnail((800, 600), Image.ANTIALIAS)
            (width, height) = self.raw_image.size
            logging.info("Resizing image to {} x {}".format(width, height))

        self.zoomed_image = self.raw_image

        # Save reference to image object so it can be displayed
        self.p_img = ImageTk.PhotoImage(self.raw_image)

        # Find center of image and radius
        self.image_center = (int(width / 2), int(height / 2))
        self.radius = int(np.sqrt(self.image_center[0] ** 2 + self.image_center[1] ** 2))
        self.spoke_spacing = 15

        logging.info("Loaded image {}".format(self.imageFile))


class EventState:

    NOEVENT = (None, None)

    def __init__(self):
        self.reset_event()

    def store_event(self, x, y):
        self.old_event = (x, y)

    def reset_event(self):
        self.old_event = self.NOEVENT

    def reset_buttons(self):
        self.button_1 = "up"
        self.button_2 = "up"
        self.button_3 = "up"
        self.tool = "move"
