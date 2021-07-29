# HorizonPy
HorizonPy is a collection of tools for defining horizon lines and calculating sky view factors to support models requiring information about the surface energy balance. **QuickHorizon** is a GUI that allows you to delineate horizon lines from fish-eye photographs. You can also calculate sky view factors for surfaces at specific orientations, making it suitable for calculating energy balances in non-horizontal terrain. **ArcSky** can transform an ArcGIS sky plot into textfiles of horizon elevations and azimuths, which can then be used to calculate sky view factors. Both ArcSky and the sky view factor calculations are accessible within the GUI and as standalone python modules.  


### Requirements
HorizonPy is tested with Python 3. We recommend using python 3.8. 

We recommend you create a conda environment for horizonpy
```
conda create -n horizon python=3.8
conda activate horizon
pip install -r requirements.txt
```

Download Shapely. If you're on windows you'll need to download the pre-built wheel file from https://www.lfd.uci.edu/~gohlke/pythonlibs/#shapely then install it using pip.  Make sure to download the right file, they are named according to the version of python and your system architecture (python 3.8 on 64-bit windows would be cp38-cp38m-win_amd64.whl)

`pip install <path to wheel file>`

## Installation
To install HorizonPy use setup.py
```
git clone https://github.com/geocryology/HorizonPy
cd HorizonPy
python setup.py install
```

If you plan to be developing the code, use `python setup.py develop` instead


