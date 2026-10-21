from __future__ import annotations

import ctypes
import threading
from pathlib import Path

from adc_api import SECTOR_CB, check, load_library
from config import CALLBACK_TIMEOUT_SECONDS, DEFAULT_LIBRARY
from test_common import CONNECTION, initialized, new_connection
from test_data import CASES


def test_mixed_plc(dll):
    case = CASES[0]
    sector = b"MixedPLCConnection"
    sector_event = threading.Event()
    sector_result = ctypes.c_long(0)
    polling_started = False
    sync_connected = False
    sector_created = False

    @SECTOR_CB
    def on_sector(result, _name, _total, _param):
        sector_result.value = result
        sector_event.set()

    with initialized(dll):
        new_connection(dll)
        try:
            check("ADC_ConnectSync", dll.ADC_ConnectSync(CONNECTION))
            sync_connected = True
            check("ADC_NewSymdataSector", dll.ADC_NewSymdataSector(
                CONNECTION, sector, on_sector))
            sector_created = True
            check("ADC_AddSymbolToSector", dll.ADC_AddSymbolToSector(
                CONNECTION, sector, case.symbol.encode()))

            check("ADC_StartDataPolling", dll.ADC_StartDataPolling())
            polling_started = True
            if not sector_event.wait(CALLBACK_TIMEOUT_SECONDS):
                raise RuntimeError("mixed PLC sector callback timeout")
            check("mixed PLC sector callback", sector_result.value)

            check("ADC_DisconnectSync", dll.ADC_DisconnectSync(CONNECTION))
            sync_connected = False
            sector_event.clear()
            if not sector_event.wait(CALLBACK_TIMEOUT_SECONDS):
                raise RuntimeError("polling stopped after ADC_DisconnectSync")
            check("post-disconnect sector callback", sector_result.value)
            print("PASS polling continued after ADC_DisconnectSync")

            check("ADC_ConnectSync while polling", dll.ADC_ConnectSync(CONNECTION))
            sync_connected = True
            check("ADC_StopDataPolling", dll.ADC_StopDataPolling())
            polling_started = False

            output = ctypes.create_string_buffer(case.size)
            check("ADC_ReadSymbolValueSync after polling stopped",
                  dll.ADC_ReadSymbolValueSync(
                      CONNECTION, case.symbol.encode(), output, case.size))
            print("PASS synchronous access continued after ADC_StopDataPolling")
        finally:
            if polling_started:
                dll.ADC_StopDataPolling()
            if sector_created:
                dll.ADC_DelSymdataSector(CONNECTION, sector)
            if sync_connected:
                dll.ADC_DisconnectSync(CONNECTION)


def main():
    dll, loader_handles = load_library(Path(DEFAULT_LIBRARY))
    try:
        test_mixed_plc(dll)
    finally:
        loader_handles.clear()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
