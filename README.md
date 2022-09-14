# HorizonPy
Tools for generating and manipulating horizon lines and sky view factors

## Introduction
HorizonPy has a number of submodules:
### QuickHorizon
This module is used to digitize horizon points from horizon camera images (fish-eye photographs)
### ArcSky
This module is used to transform ArcGIS sky plots into horizon points.


## Installation
HorizonPy is tested with Python 3. We recommend using python 3.8. 

We recommend you create a conda environment for horizonpy
```
conda create -n horizon python=3.8
conda activate horizon
```

To install HorizonPy use setup.py
```
git clone https://github.com/geocryology/HorizonPy
cd HorizonPy
pip install .[gui]
```

This installs all necessary sub-modules for using the GUI. For a basic installation with fewer dependencies use `pip install .`

If you plan to be editing the code, use `pip install -e .[gui]` instead

### Special Requirements

#### Shapely.
 If you're on windows you may need to install Shapely the hard way: download the pre-built wheel file from https://www.lfd.uci.edu/~gohlke/pythonlibs/#shapely then install it using pip.  Make sure to download the right file, they are named according to the version of python and your system architecture (python 3.8 on 64-bit windows would be cp38-cp38m-win_amd64.whl)
 
 `pip install <path to wheel file>`


#### gdal
If you're using windows, you'll almost certainly need to install `gdal` the hard way. Follow the instructions above but with gdal instead of Shapely. This library is needed for the arcsky module.


