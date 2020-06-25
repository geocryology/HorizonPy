################################################################
#                                                             ##
# Example 1: Converting ArcGIS solar radiation graphics to    ##
#              horizon coordinate points                      ##
################################################################

####
# 0. Import packages
####

from horizonpy import arcsky
from os        import path

#####
# 1. Set path to Example 1 directory /Horizonpy/Examples/Example_1
#####

EXDIR = r"E:\Users\Nick\Documents\src\HorizonPy\Examples\Example 1"
in_file  = path.join(EXDIR, "ArcGIS_Skymap.tif")
out_file = path.join(EXDIR, "horizon_pts.txt")


#####
# 2. Converting raster image to coordinate points for horizon
#####
# create ArcSky object
AS = ArcSky.ArcSky()

# Set the classified pixel value of the sky 
AS.setSkyClassValue(200)

# Open raster file
AS.open_new_file(in_file)

# convert to points
AS.write_horizon_file(out_file)