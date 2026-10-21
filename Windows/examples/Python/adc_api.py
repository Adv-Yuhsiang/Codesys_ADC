from __future__ import annotations

import ctypes
import os
import sys
from pathlib import Path

ADC_SUCCESS = 0
ADC_PLC_CONNECTED = 2001
ADC_PLC_SYMBOL_LOAD_FAILED = 2012
ADC_MEM_CONNECTED = 3001
ADC_SYMBOL_NAME_MAX_LENGTH = 256
ADC_SYMBOL_TYPE_MAX_LENGTH = 256


class ADC_SYMBOL_INFO(ctypes.Structure):
    _fields_ = [
        ("szName", ctypes.c_char * ADC_SYMBOL_NAME_MAX_LENGTH),
        ("szType", ctypes.c_char * ADC_SYMBOL_TYPE_MAX_LENGTH),
        ("ulSize", ctypes.c_ulong),
    ]

CONNECT_CB = ctypes.CFUNCTYPE(None, ctypes.c_long, ctypes.c_char_p, ctypes.c_void_p)
DISCONNECT_CB = ctypes.CFUNCTYPE(None, ctypes.c_long, ctypes.c_char_p, ctypes.c_void_p)
SECTOR_CB = ctypes.CFUNCTYPE(None, ctypes.c_long, ctypes.c_char_p, ctypes.c_int, ctypes.c_void_p)
WRITE_CB = ctypes.CFUNCTYPE(None, ctypes.c_long, ctypes.c_void_p)


def _bind(dll, name, args=()):
    function = getattr(dll, name)
    function.argtypes = list(args)
    function.restype = ctypes.c_long
    return function


def load_library(path: Path):
    resolved = path.resolve()
    if not resolved.is_file():
        raise FileNotFoundError(resolved)
    handles = []
    if sys.platform == "win32" and hasattr(os, "add_dll_directory"):
        if resolved.parent.is_dir():
            handles.append(os.add_dll_directory(str(resolved.parent)))
    dll = ctypes.CDLL(str(resolved))
    configure(dll)
    return dll, handles


def configure(dll):
    _bind(dll, "ADC_Initialize")
    _bind(dll, "ADC_Terminate")
    _bind(dll, "ADC_GetVersion")
    _bind(dll, "ADC_StartDataPolling")
    _bind(dll, "ADC_StopDataPolling")
    _bind(dll, "ADC_SetADCPriority", [ctypes.c_int])
    _bind(dll, "ADC_ReleaseADCResource")
    _bind(dll, "ADC_ShowConnection")
    _bind(dll, "ADC_NewDataConnect", [
        ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p,
        ctypes.c_int, ctypes.c_int, ctypes.c_int,
        ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p])
    _bind(dll, "ADC_SetMemConnectPort", [ctypes.c_char_p, ctypes.c_ushort])
    _bind(dll, "ADC_ConnectSync", [ctypes.c_char_p])
    _bind(dll, "ADC_DisconnectSync", [ctypes.c_char_p])
    _bind(dll, "ADC_NewSymdataSector", [ctypes.c_char_p, ctypes.c_char_p, SECTOR_CB])
    _bind(dll, "ADC_DelSymdataSector", [ctypes.c_char_p, ctypes.c_char_p])
    _bind(dll, "ADC_AddSymbolToSector", [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p])
    _bind(dll, "ADC_ReadSymbolValue", [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_int)])
    _bind(dll, "ADC_WriteSymbolValue", [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_void_p, WRITE_CB])
    _bind(dll, "ADC_ReadSymbolValueSync", [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_void_p, ctypes.c_ulong])
    _bind(dll, "ADC_WriteSymbolValueSync", [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_void_p, ctypes.c_ulong])
    _bind(dll, "ADC_GetSymbolList", [
        ctypes.c_char_p,
        ctypes.POINTER(ctypes.POINTER(ADC_SYMBOL_INFO)),
        ctypes.POINTER(ctypes.c_ulong)])
    _bind(dll, "ADC_NewMemdataSector", [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, SECTOR_CB])
    _bind(dll, "ADC_DelMemdataSector", [ctypes.c_char_p, ctypes.c_char_p])
    _bind(dll, "ADC_ReadSingleMemoryValue", [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_int)])
    _bind(dll, "ADC_ReadMultipleMemoryValue", [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_void_p, ctypes.POINTER(ctypes.c_int)])
    _bind(dll, "ADC_WriteSingleMemoryValue", [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_int), WRITE_CB])
    _bind(dll, "ADC_WriteMultipleMemoryValue", [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_void_p, ctypes.POINTER(ctypes.c_int), WRITE_CB])
    _bind(dll, "ADC_ReadMemoryValueSync", [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_void_p, ctypes.c_ulong])
    _bind(dll, "ADC_WriteMemoryValueSync", [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_void_p, ctypes.c_ulong])
    _bind(dll, "ADC_ReadSingleMemoryValue_Local", [ctypes.c_char_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_int)])
    _bind(dll, "ADC_ReadMultipleMemoryValue_Local", [ctypes.c_char_p, ctypes.c_int, ctypes.c_void_p, ctypes.POINTER(ctypes.c_int)])
    _bind(dll, "ADC_WriteSingleMemoryValue_Local", [ctypes.c_char_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_int)])
    _bind(dll, "ADC_WriteMultipleMemoryValue_Local", [ctypes.c_char_p, ctypes.c_int, ctypes.c_void_p, ctypes.POINTER(ctypes.c_int)])


def check(name: str, result: int, accepted=(ADC_SUCCESS,)):
    if result not in accepted:
        raise RuntimeError(f"{name} failed: {result}")


def free_symbol_list(symbol_list, library_path: Path):
    """Release the calloc buffer returned by ADC_GetSymbolList."""
    if not symbol_list:
        return
    if sys.platform == "win32":
        is_debug = any(part.lower() == "debug" for part in library_path.resolve().parts)
        runtime = ctypes.CDLL("ucrtbased.dll" if is_debug else "ucrtbase.dll")
    else:
        runtime = ctypes.CDLL(None)
    runtime.free.argtypes = [ctypes.c_void_p]
    runtime.free.restype = None
    runtime.free(ctypes.cast(symbol_list, ctypes.c_void_p))
