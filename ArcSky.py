import gdal
import ogr
import re 
import os

import numpy as np
from math import atan2, sqrt
from pandas import DataFrame
from scipy.interpolate import interp1d

class ArcSky(object):
    """ 
    Class to convert arcsky horizon maps from raster files into (azimuth, horizon)
    pairs and write values to a csv.
    """   
    SKY_CLASS_VALUE = 1 # default is: 1 = sky, -1 = ground, -3 = nodata
    
    def __init__(self, raster_file=None):
        self.raster = raster_file
        self.raw_points = None
        self.centroid = None
        self.vector_file = None
        if self.raster is not None:
            self.open_new_file(self.raster)
    
    def setSkyClassValue(self, value):
        """ set the value for the sky region in the input raster """
        self.SKY_CLASS_VALUE = value
        
    def __clean_shapefile(self):
        if not self.vector:
            return
        clean = [self.vector]
        clean.append(re.sub("shp$", "shx", self.vector))
        clean.append(re.sub("shp$", "dbf", self.vector))

        for tmpfile in clean:
            if os.path.isfile(tmpfile):
                os.remove(tmpfile)
        
        
    def polygonize(self, vector_file=None):
        """ convert raster file to shapefile """
        
        # Open raster file
        rast = gdal.Open(self.raster)
        srcband = rast.GetRasterBand(1)
        
        # rename raster filename if no vector filename provided
        if vector_file is None:
            vector_file = re.sub("\\.[^.]*$", ".shp", self.raster)
    
        # create vector shapefile
        drv = ogr.GetDriverByName("ESRI Shapefile")
        dst_ds = drv.CreateDataSource(vector_file)
        
        dst_layer = dst_ds.CreateLayer(re.sub("\\.shp$", "", vector_file), srs = None)
        
        newField = ogr.FieldDefn('view', ogr.OFTInteger)
        dst_layer.CreateField(newField)
        
        result = gdal.Polygonize(srcband, None, dst_layer, 0, [], callback=None)
        
        # store shapefile info so it can be cleaned later
        self.vector = vector_file
       
        # close and write to file
        if result == 0:
            dst_ds = None
            self.vector_file = vector_file
            return True
        
        return False
    
    def open_new_file(self, file):
        self.raster = file
        P = self.polygonize()
        E = self.extract_coordinates()
        C = self.calculate_horizon()
        
        self.__clean_shapefile()
        
        if (P and E and C):
            return True
        
        return False
        
    def extract_coordinates(self):
        '''
        get centroid and horizon coordinates from raster by polygonizing
        '''
        # reset coordinates
        self.centroid   = None
        self.raw_points = None

        if not self.vector_file:
            if not self.polygonize():
                exit(1)

        # open file
        driver = ogr.GetDriverByName("ESRI Shapefile")
        dataSource = driver.Open(self.vector_file, 0)
        layer = dataSource.GetLayer() 
        
        # get centroid
        extent = layer.GetExtent()  
        x0 = np.mean([extent[0], extent[1]])
        y0 = np.mean([extent[2], extent[3]])
        self.centroid = (x0, y0)
        
        # find feature with matching Sky ID
        ID = {feature.GetField(0): feature.GetFID() for feature in layer}
        sky_poly = layer.GetFeature(ID[self.SKY_CLASS_VALUE])
        
        # return coordinates of feature (sky)
        geom = sky_poly.GetGeometryRef()
        ring = geom.GetGeometryRef(0)
        n_pts = ring.GetPointCount()
        
        # get points from data structure
        points = [ring.GetPoint(n) for n in range(0, n_pts)] 
        points =[(x,y) for (x,y,z) in points]
        
        self.raw_points = points
        
        # close points
        dataSource = None
        
        if self.raw_points and self.centroid:
            return True
            
        return False
    
    def points(self):
        """ method for accessing raw_points """
        if not self.raw_points:
            self.extract_coordinates()
       
        return(DataFrame(self.raw_points))
        
    def get_angle(self, r, Rmax):
        """returns a horizon angle given a distance fom the centroid"""
        # According to ESRI, R = (N/2) * (zenith / 90)
        # here,  N = (2 * Rmax) and (phi = 90 - zenith)
        
        theta_h = 90 * (1 - r / Rmax)
        
        return(theta_h)
        
    def calculate_horizon(self):
        """ calculate horizon coordinates from raster (x,y) horizon outline  """ 
        if not (self.centroid and self.raw_points):
            if not self.extract_coordinates():
                exit(1)
        
        # get coordinate values
        Rmax = self.centroid[0] # equal to N/2 because centroid is halfway to other side 
        x0   = self.centroid[0]
        y0   = self.centroid[1]
        
        # calculate azimuth angles
        phi = [np.degrees(atan2(y - y0, x - x0)) for (x, y) in self.raw_points]
        phi = [x % 360 for x in phi]
        
        # calculate horizon angle from skyview radius
        R = [sqrt( (y - y0) ** 2 + (x - x0) ** 2) for (x, y) in self.raw_points]
        theta_h = [self.get_angle(r, Rmax) for r in R]
        
        # save as dataframe
        self.horizon = DataFrame(list(zip(phi, theta_h)))
        
        return True
    
    def interpolate_horizon(self, delta_phi):
        """ interpolate horizon to evenly-stepped azimuth values"""
        if not any(self.horizon):
            print('no horizon data')
            return
            
        # sort horizon coordinates by azimuth angle
        azi = self.horizon[0][np.argsort(self.horizon[0])]
        hor = self.horizon[1][np.argsort(self.horizon[0])]
        
        # add endpoints on either side of sequence so interpolation is good  
        x = np.concatenate((azi[-2: ] - 360, azi, azi[: 2] + 360)) 
        y = np.concatenate((hor[-2: ], hor, hor[: 2]))
        
        # create evenly spaced horizon points using interpolation
        f_hor = interp1d(x, y, kind = 'linear')  
        phi = np.array(range(0, 360, delta_phi))
        theta_h = f_hor(phi)

        return(DataFrame(list(zip(phi, theta_h)), columns=['azimuth_deg', 'horizon_ele_deg']))

    def write_horizon_file(self, output_file, delta_phi=2):
        """ write interpolated horizon data to a geotop horizon file """
        
        if not any(self.horizon):
            print('no horizon data')
            return
        
        hr_intrp = self.interpolate_horizon(delta_phi)
        hr_intrp = np.round(hr_intrp, 1)
        hr_intrp.to_csv(output_file, index = False)
        print("Horizon written to {}".format(output_file))

        
# Command-line utility 
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Convert ArcGIS skyview raster to csv of horizon points",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--sky',  type=str, help="Path to ArcSky raster")
    parser.add_argument('--out', type=str, default=None, help="Path to output csv with file extension")
    parser.add_argument('--id', default=1, type=int, help="Value of sky patch in skyview raster.  ArcGIS default is: 1 = sky, -1 = ground, -3 = nodata")
    
    args = parser.parse_args()
    out_file = args.out
    in_file = args.sky

    if out_file is None:
        out_file = re.sub("\\..*$", ".csv", in_file)
    
    AS = ArcSky()
    AS.setSkyClassValue(args.id)
    AS.open_new_file(in_file)
    AS.write_horizon_file(out_file)