try: # python 3
    import tkinter.simpledialog as tkSimpleDialog
except:  # python 2
    import tkSimpleDialog
try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

####################################################################
# AzimuthWheelDialog
####################################################################
class GridDialog(tkSimpleDialog.Dialog):

    def __init__(self, parent, title=None, center=(0,0), radius=0, spacing=15):

        tk.Toplevel.__init__(self, parent)
        self.transient(parent)

        if title:
            self.title(title)

        self.parent = parent
        self.center = center
        self.radius = radius
        self.spoke_spacing = spacing
        self.result = None

        self.buttonbox()
        self.grab_set()
        body = tk.Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))

        self.initial_focus.focus_set()
        self.wait_window(self)

    def body(self, master):

        tk.Label(master, text="X:").grid(row=0)
        tk.Label(master, text="Y:").grid(row=1)
        tk.Label(master, text="Radius:").grid(row=2)
        tk.Label(master, text="Spoke spacing:").grid(row=3)

        c1 = tk.StringVar()
        self.e1 = tk.Entry(master, textvariable=c1)
        c1.set(str(self.center[0]))

        c2 = tk.StringVar()
        self.e2 = tk.Entry(master, textvariable=c2)
        c2.set(str(self.center[1]))

        r = tk.StringVar()
        self.e3 = tk.Entry(master, textvariable=r)
        r.set(str(self.radius))

        ss = tk.StringVar()
        self.e4 = tk.Entry(master, textvariable=ss)
        ss.set(str(self.spoke_spacing))

        self.e1.grid(row=0, column=1)
        self.e2.grid(row=1, column=1)
        self.e3.grid(row=2, column=1)
        self.e4.grid(row=3, column=1)

        return self.e1

    def apply(self):

        X = self.e1.get()
        Y = self.e2.get()
        R = self.e3.get()
        S = self.e4.get()

        self.center = (int(X), int(Y))
        self.radius = int(R)
        self.spoke_spacing = int(S)
        self.result = True