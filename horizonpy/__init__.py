import pkg_resources

try:
    fname = pkg_resources.resource_filename('horizonpy', "VERSION")
    __version__ = open('horizonpy/VERSION').read().strip()
except Exception:
    __version__ = "???"
