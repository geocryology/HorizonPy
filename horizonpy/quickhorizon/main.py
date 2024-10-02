import logging
import pkg_resources
import argparse

from os import path


from horizonpy.quickhorizon.LoadImageApp import LoadImageApp

try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk


def main():
    parser = argparse.ArgumentParser(
                    prog='Quickhorizon',
                    description='Digitize horizon lines',
                    epilog='Type "quickhorizon" at the command line to launch the app')
    parser.add_argument("--debug", help="turn debug logging on", action='store_true')
    args = parser.parse_known_args()[0]

    root = tk.Tk()
    root.title("QuickHorizon")
    icon = pkg_resources.resource_filename("horizonpy", path.join("quickhorizon", "assets", "QH.ico"))
    root.iconbitmap(icon)

    if args.debug:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO

    logging.basicConfig(level=loglevel,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

    App = LoadImageApp(root)

    root.mainloop()


if __name__ == '__main__':
    main()
