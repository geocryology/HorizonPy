try:
    import Tkinter as tk
    import tkMessageBox
except ImportError:
    import tkinter as tk
    import tkinter.messagebox as tkMessageBox

import numpy as np
import matplotlib as mpl
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from horizonpy.skyview import SVF_discretized, add_sky_plot, plot_rotated_points, svf_steyn_1980, rotate_horizon, project_horizon_to_equirectangular
from shapely.errors import TopologicalError
from horizonpy.quickhorizon.geometry import calculate_true_azimuth
####################################################################
# Skyview factor popup
####################################################################
#http://www-acc.kek.jp/kekb/control/Activity/Python/TkIntro/introduction/intro09.htm


class SkyViewFactorDialog(tk.Toplevel):
    def __init__(self, parent, horizon_points, field_azimuth):

        tk.Toplevel.__init__(self, parent.frame)
        self.transient(parent.frame)

        self.title("Sky View Calculator")
        self.parent = parent.frame

        self.pts_az = np.array([calculate_true_azimuth(x[3], field_azimuth) for x in horizon_points.get_dots()])
        self.pts_hor = np.array([x[2] for x in horizon_points.get_dots()])

        self.pts_az = np.append(self.pts_az, self.pts_az[0])
        self.pts_hor = np.append(self.pts_hor, self.pts_hor[0])

        self.surface_dip = 15
        self.surface_asp = 30
        self.createcanvas()

        body = tk.Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=10, pady=10)

        self.buttonbox()
        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.geometry("+%d+%d" % (parent.frame.winfo_rootx() + 150,
                                  parent.frame.winfo_rooty() + 150))

        self.initial_focus.focus_set()
        self.wait_window(self)

    def createcanvas(self):
        f = mpl.figure.Figure(figsize=(5,5), dpi=100)
        self.ax = add_sky_plot(f, 111)
        self.canvas = FigureCanvasTkAgg(f, self)
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.draw_unrotated()

    def draw_unrotated(self):
        x,y = project_horizon_to_equirectangular(self.pts_az, self.pts_hor)
        r = np.sqrt(x**2 + y**2)
        azimuth = np.mod(np.arctan2(x,y), 2 * np.pi)
        self.ax.plot(azimuth, r)
        self.canvas.draw()

    def redraw(self):

        if hasattr(self, 'rot'):
            self.rot.remove()
        self.apply()
        # self.ax.plot(np.arange(0,360,30), np.random.random(12))
        self.rot, = plot_rotated_points(self.pts_az, self.pts_hor, self.surface_asp, self.surface_dip, self.ax)

        self.canvas.draw()

    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons
        box = tk.Frame(self)

        w = tk.Button(box, text="Calculate", width=10, command=self.ok, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = tk.Button(box, text="Redraw", width=10, command=self.redraw)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = tk.Button(box, text="Exit", width=10, command=self.cancel)
        w.pack(side=tk.LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)
        box.pack()

    # standard button semantics
    def ok(self, event=None):
        if self.apply():
            # F_sky = SVF_discretized(self.pts_az, self.pts_hor, self.surface_asp, self.surface_dip, 1)
            self.redraw()
            rotated_horizon = rotate_horizon(self.pts_az, self.pts_hor, self.surface_asp, self.surface_dip)
            try:
                F_sky = svf_steyn_1980(rotated_horizon[0], rotated_horizon[1], 72)
            except TopologicalError as e:
                tkMessageBox.showerror("Error!", "The horizon geometry or rotation angle has caused a topological error."
                                        "Try simplifying the geometry, or using a smaller rotation")
            else:
                tkMessageBox.showinfo(title="SkyView",
                message="Sky view factor = {}".format(F_sky))
        else:
            return

    def cancel(self, event=None):
        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()

    def body(self, master):
        tk.Label(master, text="Surface aspect").grid(row=0)
        tk.Label(master, text="Surface dip").grid(row=1)

        c1 = tk.StringVar()
        self.e1 = tk.Entry(master, textvariable=c1)
        c1.set(str(self.surface_asp))

        c2 = tk.StringVar()
        self.e2 = tk.Entry(master, textvariable=c2)
        c2.set(str(self.surface_dip))

        self.e1.grid(row=0, column=1)
        self.e2.grid(row=1, column=1)

        return self.e1

    def apply(self):
        try:
            AZ = float(self.e1.get())
            DIP = float(self.e2.get())

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