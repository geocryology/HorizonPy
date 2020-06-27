from horizonpy.quickhorizon.LoadImageApp import LoadImageApp
import logging
import sys
import pkg_resources
from os import path

try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

if __name__ == '__main__':
    root = tk.Tk()
    root.title("QuickHorizon")
    icon = pkg_resources.resource_filename("horizonpy", path.join("quickhorizon", "assets", "QH.ico"))
    root.iconbitmap(icon)

    image_file = None

    logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

    if len(sys.argv) > 1:
        if os.path.isfile(sys.argv[1]):
            image_file = sys.argv[1]

        else:
            exit_string = "Image File " + sys.argv[1] + " doesn't exist!"
            sys.exit(exit_string)


    App = LoadImageApp(root,image_file)

    root.mainloop()
