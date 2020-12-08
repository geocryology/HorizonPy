import logging


class ModelState:

    DEFAULT_ZOOM = 0
    MIN_ZOOM = 0
    MAX_ZOOM = 10

    def __init__(self):
        self._contrast_value = 1
        self._brightness_value = 1
        self._zoom_level = self.DEFAULT_ZOOM
        self.build_zoom_levels()

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