# iLaplace/__init__.py

from .solver import invert_laplace
from mpmath import mp

__version__ = "0.1.0"

mp.dps = 25

__all__ = ["invert_laplace"]
