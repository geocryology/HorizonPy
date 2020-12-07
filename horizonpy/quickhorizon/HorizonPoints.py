import csv
import pandas as pd
import logging
import numpy as np
from scipy.interpolate import interp1d
from horizonpy.quickhorizon.geometry import calculate_true_azimuth, find_angle


class HorizonPoints:

    def __init__(self):
        self.dots = list()
    
    def import_horizon_csv(self, file):
        del self.dots[:]

        # start canvas with image file
        f = open(file, 'rt')
        try:
            reader = csv.reader(f)
            next(reader)  # skip header row

            for row in reader:
                raw = (int(row[0]), int(row[1]))
                overhang = float(row[2]) > 90
                self._define_new_dot(raw, overhanging=overhang)

        finally:
            f.close()

    def import_geotop_csv(): 
        raise NotImplementedError

    def import_data(self, data_type="horizon"):
        pass

    def __get_import_method(self, data_type):
        pass

    def export_to_geotop(self, f_name, delta): 
        """ Save the horizon points to a geotop CSV file 
        
        f_name : str
            file path

        delta : int
            Discretization interval for azimuth spline
        """
        az = np.array([x[4] for x in self.get_dots()])
        hor = np.array([x[2] for x in self.get_dots()])
 
        hor[hor >= 90] = 90

        az = az[np.argsort(az)]
        hor = hor[np.argsort(az)]  # sorting to order by azimuth

        # Create spline equation to obtain hor(az) for any azimuth
        # add endpoints on either side of sequence so interpolation is good
        x = np.concatenate((az[-2:] - 360, az, az[:2] + 360))
        y = np.concatenate((hor[-2:], hor, hor[:2]))
        f_hor = interp1d(x, y, kind='linear')

        # Interpolate horizon at evenly spaced interval using spline
        phi = np.array(range(0, 360, delta))
        theta_h = f_hor(phi)

        df = zip(phi, ["{:.2f}".format(t) for t in theta_h])
        df = pd.DataFrame(df)
        df.columns = ('azimuth_deg', 'horizon_ele_deg')
        df.to_csv(f_name, index=False)

    def export_to_horizon_csv(self, f_name):
        """ Save the dots to CSV file 
        """                
        df = pd.DataFrame(self.get_dots())
        df.columns = ('X', 'Y', 'Horizon', 'Image Azimuth', 'True Azimuth')
        df.to_csv(f_name, index=False)

    def delete_all(self):
        del self.dots[:]

    def add_dot(self):
        pass

    def get_dots(self):
        return self.dots

    def print_dots(self):
        text = "X , Y = "

        rows = len(self.dots())
        for row in range(rows):
            i = self.dots[row]

            text = text + "(" + str(i[0]) + " , " + str(i[1]) + "), "

        return text

    def any_defined(self):
        if len(self.dots) > 0:
            return True
        else:
            return False

    def update_image_azimuth(self, image_azimuth):
        pass

    def del_point_with_coordinates(self, coords):
        """ Delete point with specified raw coordinates 
        
        coords: tuple
            Raw (x,y) coordiantes of horizon point
        """
        for dot in self.dots:
            if coords == tuple(dot[0:2]):
                self.dots.remove(dot)

    def update_field_azimuth(self, field_azimuth):
        self.dots = [x + [calculate_true_azimuth(x[3], field_azimuth)] for x in self.get_dots()]

