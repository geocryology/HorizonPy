from setuptools import setup


version = open('horizonpy/VERSION').read().strip()

setup(name='horizonpy',
      version=version,
      description='Calculating sky view factors',
      url='http://github.com/geocryology/horizonpy',
      author='Nick Brown',
      packages=['horizonpy', 'horizonpy/quickhorizon'],
      package_data={'horizonpy': ['SampleHorizonImages']},
      entry_points={
            'console_scripts': ['quickhorizon = horizonpy.quickhorizon.main:main',
                                'arcsky = horizonpy.arcsky:main']
      },
      install_requires=['numpy',
                        'pandas',
                        ],
      extras_require={
            "gui": ['Pillow', 'matplotlib', 'scipy', "shapely"],
            "full": ['Pillow','matplotlib','scipy',"gdal", "shapely"]
                        })
