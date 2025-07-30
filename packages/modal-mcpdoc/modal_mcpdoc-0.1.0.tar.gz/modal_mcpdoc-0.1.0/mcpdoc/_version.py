from importlib import metadata

try:
    __version__ = metadata.version("modal-mcpdoc")
except metadata.PackageNotFoundError:
    # Case where package metadata is not available.
    __version__ = "0.1.0"
