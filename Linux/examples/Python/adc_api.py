from __future__ import annotations

import ctypes
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
    dll = ctypes.CDLL(str(resolved))
    configure(dll)
    return dll, []


PUBLIC_APIS = ('ADC_SetMemConnectPort', 'ADC_ConnectSync', 'ADC_DisconnectSync', 'ADC_ReadSymbolValueSync', 'ADC_WriteSymbolValueSync', 'ADC_GetSymbolList', 'ADC_FreeSymbolList', 'ADC_ReadMemoryValueSync', 'ADC_WriteMemoryValueSync', 'ADC_Initialize', 'ADC_Terminate', 'ADC_GetVersion', 'ADC_StartDataPolling', 'ADC_StopDataPolling', 'ADC_SetADCPriority', 'ADC_ReleaseADCResource', 'ADC_NewDataConnect', 'ADC_NewSymdataSector', 'ADC_AddSymbolToSector', 'ADC_NewMemdataSector', 'ADC_ReadSymbolValue', 'ADC_WriteSymbolValue', 'ADC_ReadSingleMemoryValue', 'ADC_ReadMultipleMemoryValue', 'ADC_WriteSingleMemoryValue', 'ADC_WriteMultipleMemoryValue', 'ADC_ShowConnection', 'ADC_ReadSingleMemoryValue_Local', 'ADC_ReadMultipleMemoryValue_Local', 'ADC_WriteSingleMemoryValue_Local', 'ADC_WriteMultipleMemoryValue_Local')


# Exported for Windows-compatible tests; not declared in the public header.
REQUIRED_APIS = PUBLIC_APIS + ("ADC_DelSymdataSector", "ADC_DelMemdataSector")

def configure(dll):
    missing = [name for name in REQUIRED_APIS if not hasattr(dll, name)]
    if missing:
        raise RuntimeError("Library lacks required APIs; deploy the newly built Linux Library: " + ", ".join(missing))
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
    _bind(dll, "ADC_DelMemdataSector", [ctypes.c_char_p, ctypes.c_char_p])
    _bind(dll, "ADC_AddSymbolToSector", [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p])
    _bind(dll, "ADC_ReadSymbolValue", [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_int)])
    _bind(dll, "ADC_WriteSymbolValue", [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_void_p, WRITE_CB])
    _bind(dll, "ADC_ReadSymbolValueSync", [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_void_p, ctypes.c_ulong])
    _bind(dll, "ADC_WriteSymbolValueSync", [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_void_p, ctypes.c_ulong])
    _bind(dll, "ADC_GetSymbolList", [
        ctypes.c_char_p,
        ctypes.POINTER(ctypes.POINTER(ADC_SYMBOL_INFO)),
        ctypes.POINTER(ctypes.c_ulong)])
    dll.ADC_FreeSymbolList.argtypes = [ctypes.POINTER(ADC_SYMBOL_INFO)]
    dll.ADC_FreeSymbolList.restype = None
    _bind(dll, "ADC_NewMemdataSector", [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, SECTOR_CB])
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


def free_symbol_list(symbol_list, dll):
    """Return ownership to the native module that allocated the list."""
    dll.ADC_FreeSymbolList(symbol_list)

