try: # python 3
    import tkinter.simpledialog as tkSimpleDialog
except:  # python 2
    import tkSimpleDialog
try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

from horizonpy.quickhorizon.LensCalibrations import lenses

####################################################################
# FieldAzimuth Dialog (green line)
####################################################################
class LensSelectionDialog(tkSimpleDialog.Dialog):

    def __init__(self,parent,azimuth=0):

        tk.Toplevel.__init__(self, parent.frame)

        self.transient(parent.frame)

        self.title("Field Azimuth")

        self.parent = parent
        self.lens = parent.lens


        body = tk.Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)

        self.buttonbox()

        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.initial_focus.focus_set()
        self.wait_window(self)

    def body(self, master):
        lens_selection = tk.StringVar()
        tk.Label(master, text="Select Lens").grid(row=0)
        w = tk.OptionMenu(master, lens_selection, "one", "two", "three")
        w.grid(row=2)


        return w

    def apply(self):
        pass