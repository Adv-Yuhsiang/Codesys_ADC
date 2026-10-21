"""Python interface for Advantech Data Connect (ADC), Python 3.7+."""

from ._version import __version__
from .ADCAPI import ADCAPI
from .ADCDef import *
from .ADCDef import __all__ as _constants
from .ADCType import *
from .ADCType import __all__ as _types

__all__ = ["ADCAPI", "__version__", *_constants, *_types]
