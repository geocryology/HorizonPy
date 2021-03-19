try:  # python 3
    import tkinter.simpledialog as tkSimpleDialog
except ImportError:  # python 2
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

    def __init__(self, parent, default):

        tk.Toplevel.__init__(self, parent)

        self.transient(parent)

        self.title("Lens selection")
        self.default = lenses[default]
        self.parent = parent
        self.lens = None

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

    def change_infobox(self, *args):
        self.infobox.config(state='normal')
        self.infobox.delete(1.0, "end")
        self.infobox.insert("end", lenses[self.lens_var.get()].INFO)
        self.infobox.config(state='disabled')

    def body(self, master):

        self.infobox = tk.Text(master, height=5, width=35)
        self.infobox.insert("end", self.default.INFO)
        self.infobox.grid(row=3, rowspan=3, columnspan=2)
        self.infobox.config(state='disabled')

        self.lens_var = tk.StringVar()
        self.lens_var.set(self.default.NAME)

        self.lens_var.trace("w", self.change_infobox)

        tk.Label(master, text="Select Lens").grid(row=0)
        lens_selected = tk.OptionMenu(master, self.lens_var, *list(lenses.keys()))
        lens_selected.grid(row=2, columnspan=4)

        return lens_selected

    def apply(self):
        self.lens = lenses[self.lens_var.get()]
