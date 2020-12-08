import logging


class ModelState:

    MIN_ZOOM = 0
    MAX_ZOOM = 100

    def __init__(self):
        self._contrast_value = 1
        self._brightness_value = 1

    @property
    def contrast_value(self):
        return self._contrast_value

    @contrast_value.setter
    def contrast_value(self, value):
        old = self._contrast_value
        self._contrast_value = value
        logging.info('Image contrast changed from {:.2f} to {:.2f})'.format(
                     old, self._contrast_value))

    @property
    def brightness_value(self):
        return self._contrast_value
