try: # python 3
    import tkinter.simpledialog as tkSimpleDialog
except ImportError:  # python 2
    import tkSimpleDialog
try:
    import Tkinter as tk
    import tkMessageBox
except ImportError:
    import tkinter as tk
    import tkinter.messagebox as tkMessageBox
####################################################################
# FieldAzimuth Dialog (green line)
####################################################################
class AzimuthDialog(tkSimpleDialog.Dialog):

    def __init__(self,parent,azimuth=0):

        tk.Toplevel.__init__(self, parent)
        self.transient(parent)

        self.title("Field Azimuth")

        self.parent = parent
        self.azimuth = azimuth

        self.result = None

        body = tk.Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)

        self.buttonbox()

        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.geometry("+%d+%d" % (parent.winfo_rootx() + 50,
                                  parent.winfo_rooty() + 50))

        self.initial_focus.focus_set()
        self.wait_window(self)

    def body(self, master):

        tk.Label(master, text="Field Azimuth").grid(row=0)
        tk.Label(master, text="Enter field azimuth \n AZIMUTH VALUES MUST BE CORRECTED \n WITH RESPECT TO MAGNETIC DECLINATION!!!").grid(row=2)

        c1 = tk.StringVar()
        self.e1 = tk.Entry(master, textvariable=c1)
        c1.set(str(self.azimuth))

        self.e1.grid(row=0, column=1)

        return self.e1

    def apply(self):
        try:
            X = float(self.e1.get())
            if not 0 <= X <= 360:
                tkMessageBox.showerror("Error!", "Azimuth value must be between 0 and 360")
                self.result = False
            else:
                self.azimuth = X
                self.result = True
        except:
            tkMessageBox.showerror("Error!", "Numeric values only, please")
            self.result = False