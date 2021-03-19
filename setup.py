from setuptools import setup

setup(name='horizonpy',
      version='0.1',
      description='Calculating sky view factors',
      url='http://github.com/geocryology/horizonpy',
      author='Nick Brown',
      packages=['horizonpy'], 
      install_requires=[
                        'numpy',
                        'matplotlib'
                        ],
      extras_require = {
                        "gdal": ["gdal"],
                        "shapely": ["shapely"]})