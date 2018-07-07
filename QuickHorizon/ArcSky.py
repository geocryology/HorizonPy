import gdal
import ogr
import re 

from numpy import mean, arccos, degrees
from math import atan2, sqrt

class ArcSky(object):
    
    def __init__(self, raster_file):
        self.raster = raster_file
        self.raw_points = None
        self.centroid = None
        
    def polygonize(self, vector_file=None):
        '''convert raster file into file'''
        
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
        
        # close and write to file
        if result == 0:
            dst_ds = None
            self.vector_file = vector_file
            return True
        
        return False

    
    def extract_coordinates(self, sky_id=200):
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
        x0 = mean([extent[0], extent[1]])
        y0 = mean([extent[2], extent[3]])
        self.centroid = (x0, y0)
        
        # find feature with matching ID
        ID = {feature.GetField(0): feature.GetFID() for feature in layer}
        sky_poly = layer.GetFeature(ID[sky_id])
        
        # return coordinates of feature (sky)
        geom = sky_poly.GetGeometryRef()
        ring = geom.GetGeometryRef(0)
        n_pts = ring.GetPointCount()
        
        points = [ring.GetPoint(n) for n in range(0, n_pts)] #can probably do this in 1 step
        points =[(x,y) for (x,y,z) in points]
        
        self.raw_points = points
        
        # close points
        dataSource = None
        
        if self.raw_points and self.centroid:
            return True
            
        return False
    
    def getangle(self, r, Rmax):
        """returns a horizon angle given a distance fom the centroid"""
        theta_h = degrees(arccos(r / Rmax))
        
        return(theta_h)
        
    def get_horizon(self):
        if not self.centroid and self.raw_points:
            if not self.extract_coordinates():
                exit(1)
        
        Rmax = self.centroid[0]
        x0   = self.centroid[0]
        y0   = self.centroid[1]
        
        phi = [atan2(y - y0, x - x0) for (x, y) in self.raw_points]
        R = [sqrt( (y - y0) ** 2 + (x - x0) ** 2) for (x, y) in self.raw_points]
        theta_h = [self.getangle(r, Rmax) for r in R]
        
        return(zip(phi, theta_h))
        
def polygonize(raster_file, vector_file=None):
    '''convert raster file into file'''
    
    # Open raster file
    rast = gdal.Open(raster_file)
    srcband = rast.GetRasterBand(1)
    
    # rename raster filename if no vector filename provided
    if vector_file is None:
        vector_file = re.sub("\\.[^.]*$", ".shp", raster_file)

    # create vector shapefile
    drv = ogr.GetDriverByName("ESRI Shapefile")
    dst_ds = drv.CreateDataSource(vector_file)
    
    dst_layer = dst_ds.CreateLayer(re.sub("\\.shp$", "", vector_file), srs = None)
    
    newField = ogr.FieldDefn('view', ogr.OFTInteger)
    dst_layer.CreateField(newField)
    
    result = gdal.Polygonize(srcband, None, dst_layer, 0, [], callback=None)
    
    # close and write to file
    if result == 0:
        dst_ds = None
        return True
    
    return False
   


def get_horizon_lines(horizon_polygons, sky_id=200):
    '''
    
    '''
    
    # open file
    driver = ogr.GetDriverByName("ESRI Shapefile")
    dataSource = driver.Open(horizon_polygons, 0)
    layer = dataSource.GetLayer() 
    
    # get centroid
    extent = layer.GetExtent()  
    x0 = mean([extent[0], extent[1]])
    y0 = mean([extent[2], extent[3]])
    
    # find feature with matching ID
    ID = {feature.GetField(0): feature.GetFID() for feature in layer}
    sky_poly = layer.GetFeature(ID[sky_id])
    
    # return coordinates of feature (sky)
    geom = sky_poly.GetGeometryRef()
    ring = geom.GetGeometryRef(0)
    n_pts = ring.GetPointCount()
    
    points = [ring.GetPoint(n) for n in range(0, n_pts)] #can probably do this in 1 step
    points =[(x,y) for (x,y,z) in points]

    return(points)


gdal.Open()
ogr.r
sky_id=200
driver = ogr.GetDriverByName("ESRI Shapefile")
dataSource = driver.Open("C:/NB/viewout.shp", 0)
layer = dataSource.GetLayer() 

# get centroid
extent = layer.GetExtent()  
x0 = mean([extent[0], extent[1]])
y0 = mean([extent[2], extent[3]])

# find feature with matching ID
ID = {feature.GetField(0): feature.GetFID() for feature in layer}
sky_poly = layer.GetFeature(ID[sky_id])

# return coordinates of feature (sky)
geom = sky_poly.GetGeometryRef()
ring = geom.GetGeometryRef(0)
n_pts = ring.GetPointCount()

points = [ring.GetPoint(n) for n in range(0, n_pts)] #can probably do this in 1 step
points =[(x,y) for (x,y,z) in points]

xp = [x for (x,y) in points]
yp = [y for (x,y) in points]

x = layer[2]
geom = x.geometry() 
