__version__ = "0.1.0"

from typing import Iterable

from .core import greet

__path__: Iterable[str] = __import__(name="pkgutil").extend_path(
    __path__,
    __name__,
)
