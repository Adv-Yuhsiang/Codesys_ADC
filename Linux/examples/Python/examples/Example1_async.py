"""CPlusPlus/Example1: poll symbols and flag memory; write on value 1000."""

import ctypes as C
import time

if __package__:
    from ._common import Console, check, finish
else:
    from _common import Console, check, finish
from advantech_adc import (
    ADCAPI, ErrorCode, ThreadPriority, OnConnectCompletedEvent,
    OnDisconnectCompletedEvent, OnSymdataReadCompletedEvent,
    OnMemdataReadCompletedEvent, OnSymdataWriteCompletedEvent,
    OnMemdataWriteCompletedEvent,
)

# Edit the settings here to match your controller and example.project.
CONNECTION_NAME = b"CONN1"
PLC_IP = b"192.168.11.80"
USERNAME = b"root"
PASSWORD = b"1234"
SCAN_INTERVAL = 1000
CONNECT_TIMEOUT = 3000
TRANSACT_TIMEOUT = 1000
SYMBOL_SECTOR = b"SymSec"
SYMBOL_NAMES = (
    b"Application.PLC_PRG.sym1", b"Application.PLC_PRG.sym2", b"Application.PLC_PRG.sym3",
)
MEMORY_SECTOR = b"MemSec"
MEMORY_ADDRESS = b"%MW0"
MEMORY_COUNT = 10


def main():
    api = ADCAPI
    # Windows unsigned long is 32-bit; use a fixed-width PLC DWORD on Linux too.
    # Keep callback buffers alive for the entire polling session.
    symbol_value = C.c_uint32()
    memory_value = C.c_uint32()
    symbol_write_value = C.c_uint32(1100)
    memory_write_value = C.c_uint32(1200)
    memory_write_length = C.c_int(C.sizeof(memory_write_value))

    @OnConnectCompletedEvent
    def on_connect(result, name, user_data):
        print(f"Connect to '{name.decode(errors='replace')}' result = {result}")

    @OnDisconnectCompletedEvent
    def on_disconnect(result, name, user_data):
        print(f"Disconnect from '{name.decode(errors='replace')}' result = {result}")

    @OnSymdataReadCompletedEvent
    def on_symbol_read(result, sector, total, user_data):
        print(f"Read '{sector.decode(errors='replace')}' result = {result} count={total}")
        if result == ErrorCode.SUCCESS:
            symbol_value.value = 0
            length = C.c_int(C.sizeof(symbol_value))
            result = api.ADC_ReadSymbolValue(
                CONNECTION_NAME, SYMBOL_NAMES[2], C.byref(symbol_value), C.byref(length),
            )
            if result == ErrorCode.SUCCESS and symbol_value.value == 1000:
                result = api.ADC_WriteSymbolValue(
                    CONNECTION_NAME, SYMBOL_NAMES[2], C.byref(symbol_write_value),
                    OnSymdataWriteCompletedEvent(),
                )
                print(f"write symbol result = {result} size={C.sizeof(symbol_write_value)}")

    @OnMemdataReadCompletedEvent
    def on_memory_read(result, sector, total, user_data):
        print(f"Read '{sector.decode(errors='replace')}' result = {result} count={total}")
        if result == ErrorCode.SUCCESS:
            memory_value.value = 0
            length = C.c_int(C.sizeof(memory_value))
            result = api.ADC_ReadSingleMemoryValue(
                CONNECTION_NAME, MEMORY_ADDRESS, C.byref(memory_value), C.byref(length),
            )
            if result == ErrorCode.SUCCESS and memory_value.value == 1000:
                memory_write_length.value = C.sizeof(memory_write_value)
                result = api.ADC_WriteSingleMemoryValue(
                    CONNECTION_NAME, MEMORY_ADDRESS, C.byref(memory_write_value),
                    C.byref(memory_write_length), OnMemdataWriteCompletedEvent(),
                )
                print(f"write memory result = {result} size={memory_write_length.value}")

    result = api.ADC_Initialize()
    if result != ErrorCode.SUCCESS:
        print(f"Initialize failed, result = {result}")
        return 1
    polling = False
    try:
        check(api.ADC_NewDataConnect(
            CONNECTION_NAME, PLC_IP, USERNAME, PASSWORD, SCAN_INTERVAL,
            CONNECT_TIMEOUT, TRANSACT_TIMEOUT, on_connect, on_disconnect, None,
        ), "ADC_NewDataConnect")
        check(api.ADC_NewSymdataSector(CONNECTION_NAME, SYMBOL_SECTOR, on_symbol_read),
              "ADC_NewSymdataSector")
        for name in SYMBOL_NAMES:
            check(api.ADC_AddSymbolToSector(CONNECTION_NAME, SYMBOL_SECTOR, name),
                  "ADC_AddSymbolToSector")
        check(api.ADC_NewMemdataSector(
            CONNECTION_NAME, MEMORY_SECTOR, MEMORY_ADDRESS, MEMORY_COUNT, on_memory_read,
        ), "ADC_NewMemdataSector")
        api.ADC_ShowConnection()
        check(api.ADC_StartDataPolling(), "ADC_StartDataPolling")
        polling = True
        # This changes ADC native worker priorities, not the Python main thread.
        # The current Linux library keeps defaults for non-root callers, even
        # when the result is ErrorCode.SUCCESS.
        check(api.ADC_SetADCPriority(ThreadPriority.NORMAL), "ADC_SetADCPriority")
        print("ADC start polling data...\nPress <ESC> to stop (or Ctrl+C).")
        with Console() as console:
            while not console.key_pressed(escape_only=True):
                time.sleep(0.001)
    except KeyboardInterrupt:
        pass
    except RuntimeError as exc:
        print(exc)
        return 1
    finally:
        finish(api, polling=polling)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
