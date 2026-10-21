from __future__ import annotations

import ctypes
from contextlib import contextmanager
from config import (PLC_IP, PLC_USERNAME, PLC_PASSWORD, CONNECTION_NAME,
                    SCAN_INTERVAL_MS, CONNECT_TIMEOUT_MS, TRANSACTION_TIMEOUT_MS)
from adc_api import check

CONNECTION = CONNECTION_NAME.encode()


@contextmanager
def initialized(dll):
    check("ADC_Initialize", dll.ADC_Initialize())
    try:
        yield
    finally:
        dll.ADC_ReleaseADCResource()
        dll.ADC_Terminate()


def new_connection(dll, connect_cb=None, disconnect_cb=None):
    connect_pointer = ctypes.cast(connect_cb, ctypes.c_void_p) if connect_cb is not None else None
    disconnect_pointer = ctypes.cast(disconnect_cb, ctypes.c_void_p) if disconnect_cb is not None else None
    check("ADC_NewDataConnect", dll.ADC_NewDataConnect(
        CONNECTION, PLC_IP.encode(), PLC_USERNAME.encode(), PLC_PASSWORD.encode(),
        SCAN_INTERVAL_MS, CONNECT_TIMEOUT_MS, TRANSACTION_TIMEOUT_MS,
        connect_pointer, disconnect_pointer, None))


@contextmanager
def sync_connection(dll):
    with initialized(dll):
        new_connection(dll)
        check("ADC_ConnectSync", dll.ADC_ConnectSync(CONNECTION))
        try:
            yield
        finally:
            dll.ADC_DisconnectSync(CONNECTION)


def buffer_from(data: bytes):
    return ctypes.create_string_buffer(data, len(data))
