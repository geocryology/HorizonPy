import logging
import pkg_resources

from os import path


from horizonpy.quickhorizon.LoadImageApp import LoadImageApp

try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

if __name__ == '__main__':
    root = tk.Tk()
    root.title("QuickHorizon")
    icon = pkg_resources.resource_filename("horizonpy", path.join("quickhorizon", "assets", "QH.ico"))
    root.iconbitmap(icon)

    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

    App = LoadImageApp(root)

    root.mainloop()
