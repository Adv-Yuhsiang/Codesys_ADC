"""Native ADC.h structures and cdecl callback types (no forced packing)."""

import ctypes as C

ADC_SYMBOL_NAME_MAX_LENGTH = 256
ADC_SYMBOL_TYPE_MAX_LENGTH = 256


class ADC_SYMBOL_INFO(C.Structure):
    _fields_ = [
        ("szName", C.c_char * ADC_SYMBOL_NAME_MAX_LENGTH),
        ("szType", C.c_char * ADC_SYMBOL_TYPE_MAX_LENGTH),
        ("ulSize", C.c_ulong),
    ]


OnConnectCompletedEvent = C.CFUNCTYPE(None, C.c_long, C.c_char_p, C.c_void_p)
OnDisconnectCompletedEvent = C.CFUNCTYPE(None, C.c_long, C.c_char_p, C.c_void_p)
OnSymdataReadCompletedEvent = C.CFUNCTYPE(
    None, C.c_long, C.c_char_p, C.c_int, C.c_void_p
)
OnMemdataReadCompletedEvent = C.CFUNCTYPE(
    None, C.c_long, C.c_char_p, C.c_int, C.c_void_p
)
OnSymdataWriteCompletedEvent = C.CFUNCTYPE(None, C.c_long, C.c_void_p)
OnMemdataWriteCompletedEvent = C.CFUNCTYPE(None, C.c_long, C.c_void_p)

__all__ = [
    "ADC_SYMBOL_INFO", "ADC_SYMBOL_NAME_MAX_LENGTH", "ADC_SYMBOL_TYPE_MAX_LENGTH",
    "OnConnectCompletedEvent", "OnDisconnectCompletedEvent",
    "OnSymdataReadCompletedEvent", "OnMemdataReadCompletedEvent",
    "OnSymdataWriteCompletedEvent", "OnMemdataWriteCompletedEvent",
]
