try:  # python 2
    import Tkinter as tk
except ImportError:  # python 2
    import tkinter as tk


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