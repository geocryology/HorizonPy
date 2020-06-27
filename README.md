# HorizonPy
Tools for generating and manipulating horizon lines and sky view factors

## Introduction
HorizonPy has a number of submodules:
### QuickHorizon
This module is used to digitize horizon points from horizon camera images (fish-eye photographs)
### ArcSky
This module is used to transform ArcGIS sky plots into horizon points.



### Requirements
HorizonPy is tested with Python 3.6, but should work with python 2.7 if you need.

We recommend you create a conda environment for horizonpy
```
conda create -n horizon python=3.6
conda activate horizon
pip install numpy
pip install Pillow
pip install Scipy
pip install matplotlib
pip install pandas
```

Install Shapely from https://www.lfd.uci.edu/~gohlke/pythonlibs/#shapely then install the wheel

## Installation
To install HorizonPy use setup.py
```
git clone https://github.com/geocryology/HorizonPy
cd HorizonPy
python setup.py install
```

If you plan to be developing the code, use `python setup.py develop` instead


