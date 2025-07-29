import importlib.metadata

PACKAGE_NAME = "ctfatsegment"

try:
    __version__ = importlib.metadata.version(PACKAGE_NAME)
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0"  # Fallback for development mode


__all__ = [
    "__version__"
]
