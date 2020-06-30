try:
    import Tkinter as tk
    import tkFileDialog
except ImportError:
    import tkinter as tk
    import tkinter.filedialog as tkFileDialog
#from ..arcsky import ArcSky
####################################################################
# FieldAzimuth Dialog (green line)
####################################################################
class ArcSkyDialog(tk.Toplevel):
    def __init__(self, parent):

        tk.Toplevel.__init__(self, parent.frame)
        self.transient(parent.frame)

        self.title("Process ArcGIS horizon map")
        self.parent = parent.frame


        body = tk.Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=10, pady=10)

        #self.buttonbox()
        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.geometry("+%d+%d" % (parent.frame.winfo_rootx() + 150,
                                  parent.frame.winfo_rooty() + 150))

        self.initial_focus.focus_set()
        self.wait_window(self)


    def body(self, master):
        l1 = tk.Label(master, text = "Output File")
        l2 = tk.Label(master, text = "Pixel value for sky")

        # grid method to arrange labels in respective
        # rows and columns as specified
        l1.grid(row = 0, column = 0, sticky = tk.W, pady = 2)
        l2.grid(row = 1, column = 0, sticky = tk.W, pady = 2)

        # entry widgets, used to take entry from user
        self.filename = tk.StringVar()
        e1 = tk.Entry(master, textvariable=self.filename)
        self.filename.set('')

        self.skyid = tk.IntVar()
        e2 = tk.Entry(master, textvariable=self.skyid)
        self.skyid.set(1)


        # this will arrange entry widgets
        e1.grid(row = 0, column = 1, pady = 2)
        e2.grid(row = 1, column = 1, pady = 2)

        # checkbutton widget
        #c1 = tk.Checkbutton(master, text = "Preserve")
        #c1.grid(row = 2, column = 0, sticky = tk.W, columnspan = 2)

        # adding image (remember image should be PNG and not JPG)
        #img = tk.PhotoImage(file = r"C:\Users\Nick\Pictures\Snips\22.png")
        #img1 = img.subsample(2, 2)

        # setting image with the help of label
        #tk.Label(master, image = img1).grid(row = 0, column = 2,
        #    columnspan = 2, rowspan = 2, padx = 5, pady = 5)

        # button widget
        b1 = tk.Button(master, text = "Select File")
        b2 = tk.Button(master, text = "Process", command=self.ok)
        b3 = tk.Button(master, text = "Cancel", command=self.cancel)

        # arranging button widgets
        b1.grid(row = 0, column = 3, sticky = tk.E)
        b2.grid(row = 2, column = 0, sticky = tk.E)
        b3.grid(row = 2, column = 3, sticky = tk.E)

        #return self.e1

    def ok(self, event=None):
        if self.process():
           pass
        else:
            return

    def cancel(self, event=None):
        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()

    def open_file(self):
        file = tkFileDialog.askopenfilename()

        if not file:
            return

    def apply(self):
        try:
            sky_id = int(self.e1.get())
            output_file = self.e2.get()

            if not 0 <= AZ <= 360:
                tkMessageBox.showerror("Error!", "Azimuth value must be between 0 and 360")
                return False

            if not 0 <= DIP <= 180:
                tkMessageBox.showerror("Error!", "Dip value must be between 0 and 180")
                return False

            else:
                self.surface_dip = DIP
                self.surface_asp = AZ
                return True
        except:
            tkMessageBox.showerror("Error!", "Numeric values only, please")
            return False