import logging


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

    def save_azimuth(self, file):
        pass

    def set_azimuth_from_config(self, config):
        pass


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
