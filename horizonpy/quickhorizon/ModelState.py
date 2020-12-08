class ModelState:

    MIN_ZOOM = 0
    MAX_ZOOM = 100

    def __init__(self):
        self._contrast_value = 1
        self._brightness_value = 1

    @property
    def contrast_value(self):
        return self._contrast_value

    @property
    def _brightness_value(self):
        return self._contrast_value

