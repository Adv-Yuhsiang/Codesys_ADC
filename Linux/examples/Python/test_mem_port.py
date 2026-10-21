from __future__ import annotations

from pathlib import Path

from adc_api import ADC_MEM_CONNECTED, check, load_library
from config import DEFAULT_LIBRARY
from test_common import CONNECTION, initialized, new_connection

DEFAULT_MODBUS_PORT = 503
ALTERNATE_TEST_PORT = 1503


def test_mem_port(dll):
    polling_started = False
    sync_connected = False

    with initialized(dll):
        new_connection(dll)
        try:
            check("ADC_SetMemConnectPort before connection",
                  dll.ADC_SetMemConnectPort(CONNECTION, DEFAULT_MODBUS_PORT))
            check("ADC_SetMemConnectPort port zero",
                  dll.ADC_SetMemConnectPort(CONNECTION, 0), accepted=(1002,))

            check("ADC_ConnectSync", dll.ADC_ConnectSync(CONNECTION))
            sync_connected = True
            check("ADC_SetMemConnectPort during synchronous connection",
                  dll.ADC_SetMemConnectPort(CONNECTION, ALTERNATE_TEST_PORT),
                  accepted=(ADC_MEM_CONNECTED,))
            check("ADC_DisconnectSync", dll.ADC_DisconnectSync(CONNECTION))
            sync_connected = False

            check("ADC_SetMemConnectPort after synchronous disconnect",
                  dll.ADC_SetMemConnectPort(CONNECTION, DEFAULT_MODBUS_PORT))

            check("ADC_StartDataPolling", dll.ADC_StartDataPolling())
            polling_started = True
            check("ADC_SetMemConnectPort during polling",
                  dll.ADC_SetMemConnectPort(CONNECTION, ALTERNATE_TEST_PORT),
                  accepted=(ADC_MEM_CONNECTED,))
            check("ADC_StopDataPolling", dll.ADC_StopDataPolling())
            polling_started = False

            check("ADC_SetMemConnectPort after polling stopped",
                  dll.ADC_SetMemConnectPort(CONNECTION, DEFAULT_MODBUS_PORT))
            print("PASS Memory connection port lifecycle protection")
        finally:
            if polling_started:
                dll.ADC_StopDataPolling()
            if sync_connected:
                dll.ADC_DisconnectSync(CONNECTION)


def main():
    dll, loader_handles = load_library(Path(DEFAULT_LIBRARY))
    try:
        test_mem_port(dll)
    finally:
        loader_handles.clear()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
