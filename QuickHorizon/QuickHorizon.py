try:
    from Tkinter import *
except ImportError:
    from tkinter import *

from PIL import Image, ImageTk
import sys
import os
import math
import csv
import tkFileDialog
import tkMessageBox
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import tkSimpleDialog

import logging

####################################################################
# AzimuthWheelDialog
####################################################################
class GridDialog(tkSimpleDialog.Dialog):

    def __init__(self,parent,title=None,center=(0,0),radius=0):

        Toplevel.__init__(self, parent)
        self.transient(parent)

        if title:
            self.title(title)

        self.parent = parent
        self.center = center
        self.radius = radius

        self.result = None

        body = Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)

        self.buttonbox()

        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))

        self.initial_focus.focus_set()
        self.wait_window(self)

    def body(self, master):

        Label(master, text="X:").grid(row=0)
        Label(master, text="Y:").grid(row=1)
        Label(master, text="Radius:").grid(row=2)

        c1 = StringVar()
        self.e1 = Entry(master, textvariable=c1)
        c1.set(str(self.center[0]))

        c2 = StringVar()
        self.e2 = Entry(master, textvariable=c2)
        c2.set(str(self.center[1]))

        r = StringVar()
        self.e3 = Entry(master, textvariable=r)
        r.set(str(self.radius))

        self.e1.grid(row=0, column=1)
        self.e2.grid(row=1, column=1)
        self.e3.grid(row=2, column=1)

        return self.e1    

    def apply(self):

        X = self.e1.get()
        Y = self.e2.get()
        R = self.e3.get()

        self.center = (int(X), int(Y))
        self.radius = int(R)
        self.result = True

####################################################################
# FieldAzimuth Dialog (green line)
####################################################################
class AzimuthDialog(tkSimpleDialog.Dialog):

    def __init__(self,parent,title=None,center=(0,0),azimuth=-1):

        Toplevel.__init__(self, parent)
        self.transient(parent)

        if title:
            self.title(title)

        self.parent = parent
        self.center = center
        self.azimuth = azimuth

        self.result = None

        body = Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)

        self.buttonbox()

        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))

        self.initial_focus.focus_set()
        self.wait_window(self)

    def body(self, master):

        Label(master, text="Grid Center X:").grid(row=0)
        Label(master, text="Grid Center Y:").grid(row=1)
        Label(master, text="Field Azimuth:").grid(row=2)

        c1 = StringVar()
        self.e1 = Entry(master, textvariable=c1, state=DISABLED)
        c1.set(str(self.center[0]))

        c2 = StringVar()
        self.e2 = Entry(master, textvariable=c2, state=DISABLED)
        c2.set(str(self.center[1]))

        r = StringVar()
        self.e3 = Entry(master, textvariable=r)
        r.set(str(self.azimuth))

        self.e1.grid(row=0, column=1)
        self.e2.grid(row=1, column=1)
        self.e3.grid(row=2, column=1)

        return self.e1    

    def apply(self):

        X = self.e1.get()
        Y = self.e2.get()
        A = self.e3.get()

        self.center = (int(X), int(Y))
        self.azimuth = int(A)
        self.result = True


####################################################################
# Main 
####################################################################
class LoadImageApp:

    #button_1 = "up"        
    tool = "move"          
    xold, yold = None, None
    viewport = (0,0)       # Used for zoom and pan
    zoomcycle = 0          
    MIN_ZOOM = -10
    MAX_ZOOM = 30
    raw_image = None       
    zoomed_image = None    
    showGrid = False
    field_azimuth = 0      # Define an angle of field azimuth from anchor (in degrees)
    field_azimuth_coords = (0,0)   # Store field Azimuth coordinates (end point)
    anchor = (0,0)         # Store the orange point coordinate


    # list of digitized dots.  Columns contain X, Y, Elevation, Az

    dots = []

    ####################################################################
    # Function: __init__
    ####################################################################
    def __init__(self,root,image_file):

        self.parent = root
        self.frame = Frame(root, bg='black')
        self.imageFile = image_file

        
        # zoom
        self.mux = {0 : 1.0}
        for n in range(1,self.MAX_ZOOM+1,1):
            self.mux[n] = round(self.mux[n-1] * 1.5, 5)

        for n in range(-1, self.MIN_ZOOM-1, -1):
            self.mux[n] = round(self.mux[n+1] * 1.5, 5)

        # Create canvas 
        self.canvas = Canvas(self.frame,width=800,height=600,bg='gray')

        # Create the image on canvas
        if image_file:
            self.init_canvas(self.canvas,image_file)

        self.frame.pack(fill='both', expand=1)
        self.canvas.pack(fill='both', expand=1)

        #file types 
        self.file_opt = options = {}
        options['defaultextension'] = '.gif'
        options['filetypes'] = [('all files', '.*'),
                                ('ppm files', '.ppm'),
                                ('pgm files', '.pgm'),
                                ('gif files', '.gif'),
                                ('jpg files', '.jpg'),
                                ('jpeg files', '.jpeg')]
        options['initialdir'] = '.'

        # Importing csv file 
        self.csv_opt = csv_options = {}
        csv_options['defaultextension'] = '.csv'
        csv_options['filetypes'] = [('all files', '.*'),
                                ('csv files', '.csv')]
        csv_options['initialdir'] = '.'

        # Menu items
        menubar = Menu(root)
        filemenu = Menu(menubar,tearoff=0)
        filemenu.add_command(label="Open Image", command=self.open_file)
        filemenu.add_command(label="Export CSV", command=self.save_csv)
        filemenu.add_command(label="Import CSV", command=self.open_csv)
        filemenu.add_command(label="Exit", command=self.exit_app)
        menubar.add_cascade(label="File", menu=filemenu)

        drawmenu = Menu(menubar,tearoff=0)
        drawmenu.add_command(label="Position", command=self.move)
        drawmenu.add_command(label="Digitize", command=self.dot)
        drawmenu.add_command(label="Delete", command=self.select)
        drawmenu.add_command(label="Delete All Points", command=self.delete_all)
        drawmenu.add_command(label="Plot Horizon", command=self.plothorizon)
        menubar.add_cascade(label="Tools", menu=drawmenu)
        

        gridmenu = Menu(menubar, tearoff=0)
        drawgridmenu = Menu(menubar, tearoff=0)
        gridmenu.add_cascade(label="Draw Azimuth Grid",menu=drawgridmenu)
        drawgridmenu.add_command(label="Sunex 5.6mm Fisheye", command=lambda: self.create_grid_based_on_lens((397,268), 251))
        drawgridmenu.add_command(label="Custom Grid", command=self.show_grid)
        gridmenu.add_command(label="Hide Azimuth Grid", command=self.hide_grid)
        gridmenu.add_command(label="Define Image Azimuth", command=self.define_azimuth)
        menubar.add_cascade(label="Azimuth",menu=gridmenu)

        zoommenu = Menu(menubar, tearoff=0)
        zoommenu.add_command(label="Zoom In", command=self.zoomin)
        zoommenu.add_command(label="Zoom Out", command=self.zoomout)
        zoommenu.add_command(label="Reset Zoom", command=self.zoomoriginal)
        menubar.add_cascade(label="Zoom",menu=zoommenu)
        
        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="Show Point Coordinates", command=self.show_dots)
        helpmenu.add_command(label="About QuickHorizon", command=self.about)

        helpmenu.add_command(label="new", command=self.popupimage)
        menubar.add_cascade(label="Help",menu=helpmenu)

        # Attach menu bar to interface
        root.config(menu=menubar)

        # Show XY coords in in bottom left 
        self.status = Label(root, text="X,Y", bd=1, relief=SUNKEN, anchor=W)
        self.status.pack(side=BOTTOM, fill=X)

        # Events 
        self.canvas.bind("<MouseWheel>", self.zoomer)
        self.canvas.bind("<Motion>", self.motion)
        self.canvas.bind("<ButtonPress-1>", self.b1down)
        self.canvas.bind("<ButtonRelease-1>", self.b1up)
        self.canvas.bind("<ButtonPress-2>", self.b2down)
        self.canvas.bind("<ButtonRelease-2>", self.b2up)
        self.canvas.bind("<ButtonPress-3>", self.b3down)
        self.canvas.bind("<ButtonRelease-3>", self.b3up)
        self.canvas.bind("<Configure>", self.resize_window)
        self.canvas.bind("a", self.zoomin)
        self.canvas.bind("<b>", self.zoomout)

    ####################################################################
    # Canvas and Image File
    ####################################################################
    def init_canvas(self, canvas, image_file):

        # Reset when a new image opened
        self.button_1 = "up"
        self.button_2 = "up"
        self.button_3 = "up"
        self.tool = "move"
        self.xold, self.yold = None, None
        self.viewport = (0,0)
        self.zoomcycle = 0
        self.showGrid = False

        del self.dots[:]

        if image_file:

            self.imageFile = image_file
            self.raw_image = Image.open(image_file)
            (width, height) = self.raw_image.size

            # Image larger than 1000 pixels, resize to 800 x 600
            if width > 1000 or height > 1000:
                self.raw_image.thumbnail((800,600),Image.ANTIALIAS)
                (width, height) = self.raw_image.size
                print "Resizing image to ", width, "x", height

            self.zoomed_image = self.raw_image

            # Save reference to the image object in order to show it
            self.p_img = ImageTk.PhotoImage(self.raw_image)

            # Change size of canvas to new width and height 
            canvas.config(width=width, height=height)

            # Remove all canvas items
            canvas.delete("all")
            canvas.create_image(0,0,image=self.p_img, anchor="nw")

            # Find center of image and radius
            self.center = (int(width/2), int(height/2))
            self.radius = int(math.sqrt(self.center[0] * self.center[0] + self.center[1] * self.center[1]))
            self.field_azimuth = -1

    def to_raw(self,(x,y)):

        # Translate the x,y coordinate from window to raw image coordinate
        (vx, vy) = self.viewport
        return (int((x + vx)/ self.mux[self.zoomcycle]),int((y + vy)/ self.mux[self.zoomcycle]))

    def to_window(self, (x,y)):
        
        # Translate the x,y coordinate from raw image coordinate to window coordinate
        (vx, vy) = self.viewport
        return (int(x * self.mux[self.zoomcycle]) - vx,int(y * self.mux[self.zoomcycle]) - vy)

    def drawDots(self, my_canvas):
        for dot in self.dots:
            
            (x,y) = self.to_window((dot[0], dot[1]))
            
            if dot[2] >= 90:  # if horizon is greater than 90, overhanging pt
                item = my_canvas.create_rectangle(x-2,y-2,x+2,y+2,fill="yellow")
            elif 0 <= dot[2] < 90:
                item = my_canvas.create_oval(x-2,y-2,x+2,y+2,fill="blue", outline='pink')
            else:
                item = my_canvas.create_oval(x-2,y-2,x+2,y+2,fill="white")
            
            my_canvas.itemconfig(item, tags=("dot", str(dot[0]), str(dot[1])))

    def drawGrid(self, my_canvas, center, radius):

        # Remove old grid before drawing new one
        my_canvas.delete("grid")

        (wX,wY) = self.to_window(center)
        wR = radius * self.mux[self.zoomcycle]

        x = wX - wR
        y = wY - wR

        my_canvas.create_oval(x,y,x+(2*wR),y+(2*wR),outline="red",tag="grid")

        # Draw spokes on Az wheel 
        for n in range(15,365,15):
            rX = center[0] + int(radius * math.cos(math.radians(n)))
            rY = center[1] + int(radius * math.sin(math.radians(n)))
            pX,pY = self.to_window((rX,rY))
            my_canvas.create_line(wX,wY,pX,pY,fill="red",tag="grid")

    def drawAzimuth(self, my_canvas, center, radius, azimuth, anchor):

        logging.debug('drawAzimuth() -> center = %d, %d, radius = %d, azimuth = %d, anchor = %d, %d', center[0], center[1], radius, azimuth, anchor[0], anchor[1])

        # Find the angle for the anchor point from a standard ciricle (1,0) 0 degrees
        anchor_angle = self.find_angle(center,(center[0]+radius, center[1]),anchor)
        adjusted_azimuth = (anchor_angle + azimuth) % 360
        #logging.debug('adjusted azimuth = %d, %d, %d', adjusted_azimuth, anchor_angle, azimuth)

        # Field Azimuth angle is in reference to the anchor point (in orange)
        my_canvas.delete("azimuth")

        old_anchor = my_canvas.find_withtag("anchor")
        if old_anchor:
            my_canvas.delete(old_anchor)

        ax, ay = self.to_window(anchor)

        my_canvas.create_oval(ax-2,ay-2,ax+2,ay+2,tag = "anchor", fill="orange")

        (wX,wY) = self.to_window(center)

        # Draw the field azimuth in reference to the anchor point
        rX = center[0] + int(radius * math.cos(math.radians(adjusted_azimuth)))
        rY = center[1] + int(radius * math.sin(math.radians(adjusted_azimuth)))

        # Store the field azimuth coordinates (end point) so that it can be used later to calculate dot azimuth
        self.field_azimuth_coords = (rX, rY)

        pX,pY = self.to_window((rX,rY))
        my_canvas.create_line(wX,wY,pX,pY, tag="azimuth", fill="green", width=3)


    def scale_image(self):

        # Resize image 
        raw_x, raw_y = self.raw_image.size
        new_w, new_h = int(raw_x * self.mux[self.zoomcycle]), int(raw_y * self.mux[self.zoomcycle])
        self.zoomed_image = self.raw_image.resize((new_w,new_h), Image.ANTIALIAS)

    def display_region(self, my_canvas):

        my_canvas.delete("all")

        # Display the region of the zoomed image starting at viewport and window size
        (x,y) = self.viewport
        w,h = self.frame.winfo_width(), self.frame.winfo_height()

        tmp = self.zoomed_image.crop((x,y,x+w,y+h))

        self.p_img = ImageTk.PhotoImage(tmp)
        my_canvas.config(bg="gray50")
        my_canvas.create_image(0,0,image=self.p_img, anchor="nw")

        # Draw  saved dots
        if self.dots:
            self.drawDots(my_canvas)

        if self.showGrid:
            self.drawGrid(my_canvas, self.center, self.radius)
            self.drawAzimuth(my_canvas, self.center, self.radius, self.field_azimuth, self.anchor)

    ########################################################
    # Menu options
    ########################################################

    def open_file(self):
        file = tkFileDialog.askopenfilename(**self.file_opt)

        if file:
            # Initialize the canvas with an image file
            self.init_canvas(self.canvas,file)

        else:
            logging.info('No file selected')

    def open_csv(self):

        # Open a CSV file with previous XY coordinates
        file = tkFileDialog.askopenfilename(**self.csv_opt)

        if file:

            # Delete  existing dots from canvas and data 
            self.canvas.delete("dot")
            del self.dots[:]

            # start canvas with image file
            f = open(file,'rt')
            try:
                reader = csv.reader(f)
                rownum = 0

                for row in reader:

                    
                    if rownum == 0:
                        header = row
                        
                    else:
                        self.dots.append((int(row[0]),int(row[1])))
                    rownum += 1
            finally:
                f.close()

            self.drawDots(self.canvas)
        else:
            logging.info('No file selected')

    def save_csv(self):

        # Save the dots to CSV file
        if self.dots:
            try:
                f_name = tkFileDialog.asksaveasfile(mode='wb', defaultextension=".csv")
                if f_name:
                    try:
                        writer = csv.writer(f_name)
                        writer.writerow(('X', 'Y', 'Horizon', 'Azimuth'))
                        for row in self.dots:
                            writer.writerow(row)
    
                    finally:
                        f_name.close()
            except:
                tkMessageBox.showerror("Error!", "Could not access file.  Maybe it is already open?")

        else:
            tkMessageBox.showerror("Error!", "No points to export!")

    def exit_app(self):
        sys.exit(0)

    def move(self):
        self.tool = "move"

    def select(self):
        self.tool = "select"

    def show_dots(self):
       tkMessageBox.showinfo("Dot Info", self.print_dots())
    
    def about(self):
        tkMessageBox.showinfo("About QuickHorizon", 
        """Contributors:\n
        Mark Empey
        Stephan Gruber (stephan.gruber@carleton.ca)
        Nick Brown
        
        """
        )
    
    def delete_all(self, confirm=True):
        delete = True
        if confirm:
            delete =tkMessageBox.askokcancel("Confirm deletion?","Press OK to delete all dots!") 
        if delete:
            self.canvas.delete("dot")
            self.dots = []

    def print_dots(self):

        text = "X , Y = "

        rows = len(self.dots)
        for row in xrange(rows):
            i = self.dots[row]

            text = text + "(" + str(i[0]) + " , " + str(i[1]) + "), "

        return text

    def show_grid(self):

        # Get x,y coords and radius for of wheel 
        if self.raw_image:

            d = GridDialog(self.parent, title="Wheel Preferences", center=self.center, radius=self.radius)

            print "D = ", d, self.showGrid, d.result

            if d:
                self.center = d.center
                self.radius = d.radius
                if not self.showGrid:
                    self.showGrid = d.result

                if self.showGrid:
                    self.drawGrid(self.canvas, d.center, d.radius)
   
    def create_grid_based_on_lens(self, center, radius):
        if self.raw_image:
            self.showGrid = True
            self.center = center
            self.radius = radius
            self.drawGrid(self.canvas, self.center, self.radius)

    def hide_grid(self):
        if self.raw_image:
            self.showGrid = False
            self.canvas.delete("grid")

    def define_azimuth(self):

        if self.raw_image and self.showGrid:
            self.tool = "azimuth"

    def dot(self):
        if self.raw_image:
            self.tool = "dot"

    def line(self):
        if self.raw_image:
            self.tool = "line"

    def zoomin(self):
        if self.raw_image:
            if self.zoomcycle < self.MAX_ZOOM:
                self.zoomcycle += 1
                self.scale_image()
                self.display_region(self.canvas)
            else:
                print "Max zoom reached!"

    def zoomout(self):
        if self.raw_image:
            if self.zoomcycle > self.MIN_ZOOM:
                self.zoomcycle -= 1
                self.scale_image()
                self.display_region(self.canvas)
            else:
                print "Min zoom reached!"
    
    def zoomoriginal(self):
        if self.raw_image:
            self.zoomcycle = 0
            self.scale_image()
            self.viewport = (0,0)
            self.display_region(self.canvas)

    #######################################################
    # Mouse options
    #######################################################

    def zoomer(self,event):
        
        if self.raw_image:
            (x,y) = self.to_raw((event.x,event.y))

            if (event.delta > 0 and self.zoomcycle < self.MAX_ZOOM):
                self.zoomcycle += 1
            elif (event.delta < 0 and self.zoomcycle > self.MIN_ZOOM):
                self.zoomcycle -= 1
            else:
                logging.info('Max/Min zoom reached!')
                return

            self.scale_image()

            self.viewport = (int(x * self.mux[self.zoomcycle]) - x, int(y * self.mux[self.zoomcycle]) - y)
            self.display_region(self.canvas)

    def b1down(self,event):

        logging.debug('b1down() at (%d,%d)', event.x, event.y)
        if self.raw_image:
            if self.tool is "dot":

                item = event.widget.create_oval(event.x-2,event.y-2,event.x+2,event.y+2,fill="blue",outline='pink' )

                
                raw = self.to_raw((event.x,event.y))
                event.widget.itemconfig(item, tags=("dot", str(raw[0]), str(raw[1])))

               
                if self.showGrid and self.field_azimuth >= 0 and self.field_azimuth <= 360:

                    rX = self.center[0] + int(self.radius * math.cos(math.radians(self.field_azimuth)))
                    rY = self.center[1] + int(self.radius * math.sin(math.radians(self.field_azimuth)))

                    azimuth = self.find_angle(self.center, self.field_azimuth_coords, (raw[0], raw[1]))

                   
                    dot_radius = math.sqrt(math.pow(raw[0]-self.center[0],2)+math.pow(raw[1]-self.center[1],2))
                    logging.debug('Dot (%d,%d) has radius %f', raw[0], raw[1], dot_radius)
                    horizon = self.find_horizon(dot_radius, self.radius)
                    logging.info('Dot (%d,%d) has Horizon Elevation = %f, Azimuth = %f', raw[0], raw[1], horizon, azimuth)
                    
                    new_dot = [raw[0], raw[1], round(horizon,5), round(azimuth,5)]
                    self.dots.append(new_dot)

                else:
                    self.dots.append(raw + (-999,-999))

            else:   

                self.select_X, self.select_Y = event.x, event.y
                self.button_1 = "down"       
                                             

                if self.showGrid and self.tool is "azimuth":

                    old_anchor = event.widget.find_withtag("anchor")
                    if old_anchor:
                        event.widget.delete(old_anchor)

                    item = event.widget.create_oval(event.x-2,event.y-2,event.x+2,event.y+2,fill="orange")

                    # save the anchor 
                    self.anchor = self.to_raw((event.x,event.y))
                    event.widget.itemconfig(item, tags=("anchor"))

                    logging.debug('Button down, drawing azimuth line with 0 degree')
                    self.drawAzimuth(self.canvas, self.center, self.radius, 0, self.anchor)

    def b1up(self,event):

        logging.debug('b1up()-> tool = %s at (%d, %d)', self.tool, event.x, event.y)
        if not self.raw_image:
            return

        self.button_1 = "up"
        self.xold = None           
        self.yold = None

        
        if self.tool is "select":
            items = event.widget.find_enclosed(self.select_X, self.select_Y, event.x, event.y)

            
            rect = event.widget.find_withtag("selection_rectangle")
            if rect:
                event.widget.delete(rect)
            
            selected = [x for x in items if event.widget.gettags(x)[0] == 'dot']
            
            to_delete = {}
            for i in selected:
                
                # Change the color of the selected dots 
                event.widget.itemconfig(i,fill="red")
                
                tags = event.widget.gettags(i)
                
                to_delete[i] = (int(tags[1]),int(tags[2])) 
                                     
                logging.debug('Selected Item-> %d with tags %s, %s, %s', i, tags[0], tags[1], tags[2])
                

            if to_delete:
                confirm = tkMessageBox.askokcancel("Confirm deletion?","Press OK to delete selected dot(s)!")
    
                if confirm:
                    # Delete the selected dots on the canvas, and remove it from list
                    for i,coords in to_delete.items():
                        logging.debug('Removing dot %d with coords: %d, %d', i, coords[0], coords[1])
                        
                        for dot in self.dots:
                            if coords == tuple(dot[0:2]):
                                self.dots.remove(dot)
                                
                        event.widget.delete(i)

                else: 
                    logging.info('Dot deletion cancelled!')
                    self.drawDots(self.canvas)

        elif self.tool is "azimuth":
            self.azimuth_calculation(self.center, self.radius, self.field_azimuth_coords)
    def b2down(self,event):
        self.button_2 = "down"

    def b2up(self, event):
        self.button_2 = "up"
        self.xold = None           
        self.yold = None
        
    def b3down(self,event):

        logging.debug('b3down() at (%d,%d)', event.x, event.y)
        if self.raw_image:
            if self.tool is "dot":

                item = event.widget.create_rectangle(event.x-2,event.y-2,event.x+2,event.y+2,fill="yellow")
          
                raw = self.to_raw((event.x,event.y))
                event.widget.itemconfig(item, tags=("dot", str(raw[0]), str(raw[1])))

               
                if self.showGrid and self.field_azimuth >= 0 and self.field_azimuth <= 360:

                    rX = self.center[0] + int(self.radius * math.cos(math.radians(self.field_azimuth)))
                    rY = self.center[1] + int(self.radius * math.sin(math.radians(self.field_azimuth)))

                    azimuth = self.find_angle(self.center, self.field_azimuth_coords, (raw[0], raw[1]))

                   
                    dot_radius = math.sqrt(math.pow(raw[0]-self.center[0],2)+math.pow(raw[1]-self.center[1],2))
                    logging.debug('Dot (%d,%d) has radius %f', raw[0], raw[1], dot_radius)
                    horizon = self.find_horizon(dot_radius, self.radius)
                    logging.info('Dot (%d,%d) has Horizon Elevation = %f, Azimuth = %f', raw[0], raw[1], horizon, azimuth)
                    
                    #modify coordinates so that the point is 'overhanging'
                    azimuth = (azimuth + 180) % 360
                    horizon = 180 - horizon 
                    
                    if horizon == 180: # for "180-obstruction" points, make two: one on either side
                        twin_x = 2*self.center[0]-raw[0]
                        twin_y = 2*self.center[1]-raw[1]
                        twin_az  = self.find_angle(self.center, self.field_azimuth_coords, (twin_x, twin_y))
                        twin_dot = [twin_x, twin_y, 90, round((twin_az+180)%360,5)]
                        self.dots.append(twin_dot)
                        horizon = 90
                    new_dot = [raw[0], raw[1], round(horizon,5), round(azimuth,5)]
                    self.dots.append(new_dot)

                else:
                    self.dots.append(raw + (-998, -999))
                
                self.drawDots(self.canvas)
    
    def b3up(self,event):
        logging.debug('b3up()-> tool = %s at (%d, %d)', self.tool, event.x, event.y)
        pass
                        
    # Handles mouse 
    def motion(self,event):
        
        # Button 2 pans no matter what
        if self.raw_image and self.button_2 == "down":
            if self.xold is not None and self.yold is not None:
                self.viewport = (self.viewport[0] - (event.x - self.xold), self.viewport[1] - (event.y - self.yold))
                self.display_region(self.canvas)
            self.xold = event.x
            self.yold = event.y

        # Conditional on button 1 depressed
        if self.raw_image and self.button_1 == "down":
            if self.xold is not None and self.yold is not None:

                
                if self.tool is "line":
                    
                    event.widget.create_line(self.xold,self.yold,event.x,event.y,smooth=TRUE,fill="blue",width=5)

                elif self.tool is "azimuth":   # Defining Field Azimuth

                    
                    if self.showGrid:
                        
                        zoomed_center = self.to_window(self.center)
                        zoomed_anchor = self.to_window(self.anchor)

                        self.field_azimuth = self.find_angle(zoomed_center, zoomed_anchor, (event.x,event.y))
                        self.drawAzimuth(self.canvas, self.center, self.radius, self.field_azimuth, self.anchor)

                elif self.tool is "move":     # Panning
                    self.viewport = (self.viewport[0] - (event.x - self.xold), self.viewport[1] - (event.y - self.yold))
                    self.display_region(self.canvas)

                elif self.tool is "select":
                    # Draw a dotted rectangle to show the area selected
                    rect = event.widget.find_withtag("selection_rectangle")
                    if rect:
                        event.widget.delete(rect)
                    event.widget.create_rectangle(self.select_X,self.select_Y,event.x,event.y,fill="",dash=(4,2),tag="selection_rectangle")

            self.xold = event.x
            self.yold = event.y

        # update the status bar with x,y values, status bar always shows "RAW" coordinates
        (rX,rY) = self.to_raw((event.x,event.y))
        output = "Cursor = %d, %d" % (rX,rY)
        if self.field_azimuth:
            output += "      Field Azimuth = %d" %(360 - self.field_azimuth)
        self.status.config(text=output)

    def resize_window(self, event):
        if self.zoomed_image:
            self.display_region(self.canvas)

    def azimuth_calculation(self, center, radius, azimuth):
        new_dots = []

        for dot in self.dots:
            azimuth = self.find_angle(center, self.field_azimuth_coords, (dot[0], dot[1]))

            dot_radius = math.sqrt(math.pow(dot[0]-center[0],2)+math.pow(dot[1]-center[1],2))
            horizon = self.find_horizon(dot_radius, radius)
            if dot[2] == -998 or dot[2] > 90:
                horizon = 180 - horizon
                azimuth = (180 + azimuth) % 360
                if horizon == 180: # for these points, make two: one on either side
                    twin_x = 2*self.center[0]-raw[0]
                    twin_y = 2*self.center[1]-raw[1]
                    twin_az  = self.find_angle(self.center, self.field_azimuth_coords, (twin_x, twin_y))
                    twin_dot = [twin_x, twin_y, 90, round((twin_az+180)%360,5)]
                    new_dots.append(twin_dot)
                    horizon = 90
                        
            logging.info('Dot (%d,%d) has Horizon Elevation = %f, Azimuth = %f', dot[0], dot[1], horizon, azimuth)
            new_dot = [dot[0], dot[1], round(horizon,5), round(azimuth,5)]
            new_dots.append(new_dot)

        self.dots = new_dots
        self.drawDots(self.canvas)
    def find_angle(self, C, P2, P3):

        angle = math.atan2(P2[1]-C[1], P2[0]-C[0]) - math.atan2(P3[1]-C[1], P3[0]-C[0])
        angle_in_degree = math.degrees(angle)

        if angle_in_degree < 0:
            angle_in_degree += 360

        return angle_in_degree

    def find_horizon(self, dot_radius, grid_radius):
        
        # Enter total field of view of Sunex camera (based on lens/camera model)
        camera = 185   

        # Adjust horizon elevation using calibration polynomial
        elev = (camera/2) - ((dot_radius/grid_radius) * (camera/2))
        
        # Calculate Horizon Elevation
        elev = (-0.00003 * (elev * elev)) + (1.0317 * (elev)) - 2.4902
        return (max([elev,0]))
    

    def plothorizon(self, show=True):
        fig, ax = plt.subplots(1,1, sharex=True)
        plot_dots = self.dots
        plot_dots.sort(key=lambda x: x[3])  # sort dots using image azimuth
        image_azim = [x[3] for x in plot_dots]
        image_azim.insert(0,(image_azim[-1] - 360))
        image_azim.append(image_azim[1] + 360)
        horiz = [x[2] for x in plot_dots]
        horiz.insert(0,horiz[-1])
        horiz.append(horiz[1])
        plot_dots.sort(key=lambda x: (x[3]+180) % 360)
        ia_over = [(x[3]+180) % 360 for x in plot_dots]
        ia_over.insert(0,(ia_over[-1] - 360))
        ia_over.append(ia_over[1] + 360)
        h_over = [180-x[2] for x in plot_dots]
        h_over.insert(0,h_over[-1])
        h_over.append(h_over[1])
        h_over = [x if x!=90 else 0 for x in h_over ]
        ax.set_xlabel('Image Azimuth')
        ax.set_ylabel('Horizon Angle')
        ax.set_axis_bgcolor('blue')
        ax.set_xlim((0,360))
        ax.set_ylim((0,90))   
        horiz = np.array(horiz)
        image_azim = np.array(image_azim) 
        ax.plot(image_azim, horiz, 'ko')
        ax.fill_between(image_azim, np.zeros(len(horiz)), np.minimum(horiz,90), color='brown')
        ax.fill_between(ia_over, h_over,  np.zeros(len(horiz))+180, color='brown') #where=horiz >= 90,
        if show:
            plt.show()
        return(fig)
        
    def popupimage(self):
        self.root2 = Tk()
        fig = self.plothorizon(show=False)
        canvas2 = FigureCanvasTkAgg(fig, master=self.root2)     
        canvas2.show()
        canvas2.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1.0)      
        canvas2.draw()

# Main Program 

if __name__ == '__main__':
    root = Tk()
    root.title("QuickHorizon")
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
