"""Direct ctypes bindings for ADC.h, following AcmP's class-level API style.

Importing this module loads the fixed native library and binds its exports.
Keep callbacks and asynchronous buffers alive until native work has stopped.
"""

from ctypes import CDLL, POINTER, c_char_p, c_int, c_long, c_ulong, c_ushort, c_void_p, sizeof
import os
from pathlib import Path
import sys

from .ADCType import (
    ADC_SYMBOL_INFO, OnConnectCompletedEvent, OnDisconnectCompletedEvent,
    OnSymdataReadCompletedEvent, OnMemdataReadCompletedEvent,
    OnSymdataWriteCompletedEvent, OnMemdataWriteCompletedEvent,
)

__all__ = ["ADCAPI"]

# Fixed paths. Keep the Windows dependency search directory alive with the module.
_dll_directory = None
_ARCH = "x64" if sizeof(c_void_p) == 8 else "x86"
if sys.platform == "win32":
    LIBRARY_PATH = str(Path(__file__).resolve().parent / "library" / _ARCH / "AdvHandler.dll")
    if hasattr(os, "add_dll_directory"):
        _dll_directory = os.add_dll_directory(str(Path(LIBRARY_PATH).parent))
elif sys.platform.startswith("linux"):
    LIBRARY_PATH = f"/usr/lib/libADCLibrary-{_ARCH}.so"
else:
    raise OSError("ADC supports Windows and Linux only")

lib = CDLL(LIBRARY_PATH)  # ADC exports and callbacks use cdecl.


def _bind(name, argtypes=None, restype=c_long):
    try:
        function = getattr(lib, name)
    except AttributeError:
        def missing(*args, **kwargs):
            raise NotImplementedError(f"{name} is not exported by the loaded ADC library")
        # Keep the same call signature through ADCAPI and ADCAPI().
        return staticmethod(missing)
    if argtypes is not None:
        function.argtypes = argtypes
    function.restype = restype
    return function


class ADCAPI:
    """Call ADCAPI.ADC_Initialize(), etc.; native state is process-global."""

    # General
    ADC_Initialize = _bind("ADC_Initialize", [])
    ADC_Terminate = _bind("ADC_Terminate", [])
    ADC_GetVersion = _bind("ADC_GetVersion", [])
    ADC_StartDataPolling = _bind("ADC_StartDataPolling", [])
    ADC_StopDataPolling = _bind("ADC_StopDataPolling", [])
    ADC_SetADCPriority = _bind("ADC_SetADCPriority", [c_int])
    ADC_ReleaseADCResource = _bind("ADC_ReleaseADCResource", [])
    # Connections
    ADC_NewDataConnect = _bind("ADC_NewDataConnect", [
        c_char_p, c_char_p, c_char_p, c_char_p,
        c_int, c_int, c_int,
        OnConnectCompletedEvent, OnDisconnectCompletedEvent, c_void_p,
    ])
    ADC_SetMemConnectPort = _bind("ADC_SetMemConnectPort", [c_char_p, c_ushort])
    ADC_ConnectSync = _bind("ADC_ConnectSync", [c_char_p])
    ADC_DisconnectSync = _bind("ADC_DisconnectSync", [c_char_p])
    # Polling sectors
    ADC_NewSymdataSector = _bind("ADC_NewSymdataSector", [
        c_char_p, c_char_p, OnSymdataReadCompletedEvent,
    ])
    ADC_AddSymbolToSector = _bind("ADC_AddSymbolToSector", [
        c_char_p, c_char_p, c_char_p,
    ])
    ADC_NewMemdataSector = _bind("ADC_NewMemdataSector", [
        c_char_p, c_char_p, c_char_p, c_int, OnMemdataReadCompletedEvent,
    ])
    # Symbols
    ADC_ReadSymbolValue = _bind("ADC_ReadSymbolValue", [
        c_char_p, c_char_p, c_void_p, POINTER(c_int),
    ])
    ADC_WriteSymbolValue = _bind("ADC_WriteSymbolValue", [
        c_char_p, c_char_p, c_void_p, OnSymdataWriteCompletedEvent,
    ])
    ADC_ReadSymbolValueSync = _bind("ADC_ReadSymbolValueSync", [
        c_char_p, c_char_p, c_void_p, c_ulong,
    ])
    ADC_WriteSymbolValueSync = _bind("ADC_WriteSymbolValueSync", [
        c_char_p, c_char_p, c_void_p, c_ulong,
    ])
    ADC_GetSymbolList = _bind("ADC_GetSymbolList", [
        c_char_p, POINTER(POINTER(ADC_SYMBOL_INFO)), POINTER(c_ulong),
    ])
    ADC_FreeSymbolList = _bind("ADC_FreeSymbolList", [POINTER(ADC_SYMBOL_INFO)], None)
    # Remote memory
    ADC_ReadMemoryValueSync = _bind("ADC_ReadMemoryValueSync", [
        c_char_p, c_char_p, c_void_p, c_ulong,
    ])
    ADC_WriteMemoryValueSync = _bind("ADC_WriteMemoryValueSync", [
        c_char_p, c_char_p, c_void_p, c_ulong,
    ])
    ADC_ReadSingleMemoryValue = _bind("ADC_ReadSingleMemoryValue", [
        c_char_p, c_char_p, c_void_p, POINTER(c_int),
    ])
    ADC_ReadMultipleMemoryValue = _bind("ADC_ReadMultipleMemoryValue", [
        c_char_p, c_char_p, c_int, c_void_p, POINTER(c_int),
    ])
    ADC_WriteSingleMemoryValue = _bind("ADC_WriteSingleMemoryValue", [
        c_char_p, c_char_p, c_void_p, POINTER(c_int), OnMemdataWriteCompletedEvent,
    ])
    ADC_WriteMultipleMemoryValue = _bind("ADC_WriteMultipleMemoryValue", [
        c_char_p, c_char_p, c_int, c_void_p, POINTER(c_int), OnMemdataWriteCompletedEvent,
    ])
    ADC_ShowConnection = _bind("ADC_ShowConnection", [])
    # Local memory
    ADC_ReadSingleMemoryValue_Local = _bind("ADC_ReadSingleMemoryValue_Local", [
        c_char_p, c_void_p, POINTER(c_int),
    ])
    ADC_ReadMultipleMemoryValue_Local = _bind("ADC_ReadMultipleMemoryValue_Local", [
        c_char_p, c_int, c_void_p, POINTER(c_int),
    ])
    ADC_WriteSingleMemoryValue_Local = _bind("ADC_WriteSingleMemoryValue_Local", [
        c_char_p, c_void_p, POINTER(c_int),
    ])
    ADC_WriteMultipleMemoryValue_Local = _bind("ADC_WriteMultipleMemoryValue_Local", [
        c_char_p, c_int, c_void_p, POINTER(c_int),
    ])
