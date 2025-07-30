"""
constellation: A Python enum for astronomical constellations with standard abbreviations

This package provides a comprehensive enum of all 88 modern constellations
recognized by the International Astronomical Union (IAU), along with their
standard 3-letter abbreviations.

Example usage:
    >>> from constellation import Constellation
    >>> print(Constellation.Andromeda.abbr)
    'And'
    >>> print(Constellation['And'])
    Constellation.Andromeda
"""

__version__ = "0.1.0"
__author__ = "gomeshun"

from .constellation import Constellation

__all__ = ['Constellation']
