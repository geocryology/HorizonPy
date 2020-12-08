from functools import wraps
import logging

try:  # python 3
    import tkinter.messagebox as tkMessageBox
    izip = zip
except:  # python 2
    import tkMessageBox


def require_horizon_points(func):
    @wraps(func)
    def wrapper(self, *args, **kw):
        if not self.points.any_defined():
            tkMessageBox.showerror("Error!", "No horizon points have been specified.")
            logging.info("Attempted to call function {} without horizon points".format(func))
        else:
            func(self, *args, **kw)
    return wrapper


def require_field_azimuth(func):
    @wraps(func)
    def wrapper(self, *args, **kw):
        if self.field_azimuth == -1:
            tkMessageBox.showerror("Error!", "Field azimuth has not yet been defined.")
            logging.info("Attempted to call function {} without field azimuth".format(func))
        else:
            func(self, *args, **kw)
    return wrapper


def require_image_azimuth(func):
    @wraps(func)
    def wrapper(self, *args, **kw):
        if self.image_state.image_azimuth == -1:
            tkMessageBox.showerror("Error!", "Image azimuth has not yet been defined.")
            logging.info("Attempted to call function {} without image azimuth".format(func))
        else:
            func(self, *args, **kw)
    return wrapper


def require_image_file(func):
    @wraps(func)
    def wrapper(self, *args, **kw):
        if not self.imageFile:
            tkMessageBox.showerror("Error!", "Load an image first (File > Open Image).")
            logging.info("Attempted to call function {} without a horizon image".format(func))
        else:
            func(self, *args, **kw)
    return wrapper


def require_grid(func):
    @wraps(func)
    def wrapper(self, *args, **kw):
        if not self.grid_set:
            tkMessageBox.showerror("Error!", "No grid parameters have been set! Please define azimuth grid first")
            logging.info("Attempted to call function {} without a horizon grid".format(func))
        else:
            func(self, *args, **kw)
    return wrapper