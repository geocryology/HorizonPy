from setuptools import setup

setup(name='horizonpy',
      version='0.1',
      description='Calculating sky view factors',
      url='http://github.com/geocryology/horizonpy',
      author='Nick Brown',
      packages=['horizonpy'], 
      install_requires=[
                        'numpy==1.13.3',
                        'matplotlib==2.2.5'])