from horizonpy.arcsky import ArcSky

try:
    import Tkinter as tk
    import tkMessageBox
except ImportError:
    import tkinter as tk
    import tkinter.filedialog as tkFileDialog
    import tkinter.messagebox as tkMessageBox



####################################################################
# FieldAzimuth Dialog (green line)
####################################################################
class ArcSkyDialog(tk.Toplevel):
    def __init__(self, parent):

        tk.Toplevel.__init__(self, parent.frame)
        self.transient(parent.frame)

        self.title("Process ArcGIS horizon map")
        self.parent = parent


        body = tk.Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=10, pady=10)

        #self.buttonbox()
        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.geometry("+%d+%d" % (self.parent.frame.winfo_rootx() + 150,
                                  self.parent.frame.winfo_rooty() + 150))

        self.initial_focus.focus_set()
        self.wait_window(self)


    def body(self, master):
        l0 = tk.Label(master, text = "Input File")
        l1 = tk.Label(master, text = "Output File")
        l2 = tk.Label(master, text = "Pixel value for sky")

        # grid method to arrange labels in respective
        # rows and columns as specified
        l0.grid(row = 0, column = 0, sticky = tk.W, pady = 2)
        l1.grid(row = 1, column = 0, sticky = tk.W, pady = 2)
        l2.grid(row = 2, column = 0, sticky = tk.W, pady = 2)

        # entry widgets, used to take entry from user

        self.inputfilename = tk.StringVar()
        e0 = tk.Entry(master, textvariable=self.inputfilename)
        e0.configure(state='readonly')
        self.inputfilename.set(self.parent.imageFile)

        self.outputfilename = tk.StringVar()
        e1 = tk.Entry(master, textvariable=self.outputfilename)
        self.outputfilename.set('')

        self.skyid = tk.IntVar()
        e2 = tk.Entry(master, textvariable=self.skyid)
        self.skyid.set(1)


        # this will arrange entry widgets
        e0.grid(row = 0, column = 1, pady = 2, padx = 2,  columnspan = 4, sticky = tk.W + tk.E)
        e1.grid(row = 1, column = 1, pady = 2, padx = 2,  columnspan = 4, sticky = tk.W + tk.E)
        e2.grid(row = 2, column = 1, pady = 2)

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
        b0 = tk.Button(master, text = "Select Input File", command=self.open_inputfile)
        b0.grid(row = 0, column = 5, sticky = tk.E, padx=2, pady=2)

        b1 = tk.Button(master, text = "Select Output File", command=self.open_outputfile)
        b1.grid(row = 1, column = 5, sticky = tk.E, padx=2, pady=2)

        b2 = tk.Button(master, text = "Process", command=self.ok)
        b2.grid(row = 4, column = 0, sticky = tk.E, padx=2, pady=5)

        b3 = tk.Button(master, text = "Cancel", command=self.cancel)
        b3.grid(row = 4, column = 2, sticky = tk.E, padx=2, pady=5)
        # arranging button widgets




        #return self.e1

    def ok(self, event=None):
        if self.process():
           pass
        else:
            return

    def cancel(self, event=None):
        # put focus back to the parent window
        self.parent.frame.focus_set()
        self.destroy()

    def open_inputfile(self):
        file = tkFileDialog.askopenfilename()
        if file:
            self.inputfilename.set(file)
        else:
            return

    def open_outputfile(self):
        file = tkFileDialog.asksaveasfilename()
        if file:
            self.outputfilename.set(file)
        else:
            return

    def process(self):

        AS = ArcSky()
        AS.setSkyClassValue(self.skyid.get())
        AS.open_new_file(self.parent.imageFile)
        AS.write_horizon_file(self.outputfilename.get())

        return