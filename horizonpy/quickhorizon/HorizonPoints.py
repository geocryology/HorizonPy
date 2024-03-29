import csv
import pandas as pd
import logging
import numpy as np
from scipy.interpolate import interp1d
from horizonpy.quickhorizon.geometry import calculate_true_azimuth, find_angle
from uuid import uuid1

class HorizonPoints:

    def __init__(self):
        self.dots = list()  # list of digitized dots.  Columns contain X, Y, Elevation, Az
        self.newdots = pd.DataFrame(columns=["raw_x", "raw_y", "elevation", "image_az", "true_az", "id"])

    def import_horizon_csv(self, file):
        self.delete_all()

        f = open(file, 'rt')
        try:
            reader = csv.reader(f)
            next(reader)  # skip header row

            for row in reader:
                uid = uuid1().hex
                raw = (int(row[0]), int(row[1]), float(row[2]), float(row[3]), float(row[4]), uid)
                self.dots.append(raw)  # self._define_new_dot(raw, overhanging=overhang)

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
        az = np.array([x[4] for x in self.get()])
        hor = np.array([x[2] for x in self.get()])

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
        df = pd.DataFrame(self.get())
        df.columns = ('X', 'Y', 'Horizon', 'Image Azimuth', 'True Azimuth')
        df.to_csv(f_name, index=False)

    def delete_all(self):
        del self.dots[:]

    def add_raw(self, raw_x, raw_y, img_ctr, grid_radius, image_azimuth_coords, lens, overhanging):
        uid = uuid1().hex
        azimuth = find_angle(img_ctr, image_azimuth_coords, (raw_x, raw_y))
        dx = raw_x - img_ctr[0]
        dy = raw_y - img_ctr[1]
        dot_radius = np.sqrt(np.power(dx, 2) + np.power(dy, 2))
        horizon = lens.horizon_from_radius(dot_radius, grid_radius)

        if overhanging:
            #  modify coordinates so that the point is 'overhanging'
            if horizon == 0:  # if horizon is exactly 0, make it a 90 deg point
                horizon = 90
            else:
                horizon = 180 - horizon
                azimuth = (180 + azimuth) % 360

        new_dot = (raw_x, raw_y, round(horizon, 5), round(azimuth, 5), round(azimuth, 5), uid)
        self.dots.append(new_dot)
        logging.info('Dot ({},{}) has Horizon Elevation = {:.1f}, Azimuth = {:.1f}'.format(
                     raw_x, raw_y, horizon, azimuth))

    def get(self):
        return self.dots

    def print_dots(self):
        text = "X , Y = "

        rows = len(self.dots)
        for row in range(rows):
            i = self.dots[row]

            text = text + "(" + str(i[0]) + " , " + str(i[1]) + "), "

        return text

    def any_defined(self):
        if len(self.dots) > 0:
            return True
        else:
            return False

    def del_point_with_id(self, id):
        for dot in self.dots:
            if id == dot[5]:
                self.dots.remove(dot)

    def update_image_azimuth(self, center, grid_radius, image_azimuth, image_azimuth_coords, lens):
        new_dots = []

        for dot in self.dots:
            uid = dot[5]
            azimuth = find_angle(center, image_azimuth_coords, (dot[0], dot[1]))

            dot_radius = np.sqrt(np.power(dot[0] - center[0], 2) + np.power(dot[1] - center[1], 2))
            horizon = lens.horizon_from_radius(dot_radius, grid_radius)

            if dot[2] == -998 or dot[2] > 90:
                if horizon == 0:  # if horizon is exactly 0, make it a 90 deg point
                    horizon = 90
                else:
                    horizon = 180 - horizon
                    azimuth = (180 + azimuth) % 360

            logging.info('Dot (%d,%d) has Horizon Elevation = %f, Azimuth = %f', dot[0], dot[1], horizon, azimuth)
            new_dot = (dot[0], dot[1], round(horizon, 5), round(azimuth, 5), round(azimuth, 5), uid)
            new_dots.append(new_dot)

        self.dots = new_dots

    def get_plottable_points(self):
        pts = [(x, y, z > 90, i) for p in self.dots for x,y,z,i in [(p[0:3] + (p[5],))]]
        return {'points': pts}

    def update_field_azimuth(self, field_azimuth):
        """ Recalculate true azimuth for all dots """
        self.dots = [x[0:3] + (calculate_true_azimuth(x[3], field_azimuth), x[4])  for x in self.get()]


class HorizonPoint:

    def __init__(self):
        self.uid = uuid1().hex

    @classmethod
    def from_raw(cls, raw_x, raw_y):
        Point = cls()
        Point.raw_x = raw_x
        Point.raw_y = raw_y
        return Point

