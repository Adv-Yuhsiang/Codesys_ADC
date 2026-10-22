"""CPlusPlus/Example4: synchronous Symbol and Memory read/write."""

import ctypes as C
import random
import time

if __package__:
    from ._common import Console, check, finish
else:
    from _common import Console, check, finish
from advantech_adc import (
    ADCAPI, ErrorCode, ADC_SYMBOL_INFO, OnConnectCompletedEvent,
    OnDisconnectCompletedEvent,
)

# Edit these settings directly to match your controller.
CONNECTION_NAME = b"CONN1"
PLC_IP = b"192.168.11.80"
USERNAME = b"root"
PASSWORD = b"1234"
SCAN_INTERVAL = 1000
CONNECT_TIMEOUT = 3000
TRANSACT_TIMEOUT = 1000
MEMORY_PORT = 503
MEMORY_WORD_ADDRESS = b"%MW0"
MEMORY_DWORD_ADDRESS = b"%MD1"
LOOP_INTERVAL = 1.0


def main():
    api = ADCAPI
    symbols = C.POINTER(ADC_SYMBOL_INFO)()
    count = C.c_ulong()
    connected = False
    result = api.ADC_Initialize()
    if result != ErrorCode.SUCCESS:
        print(f"Initialize failed, result = {result}")
        return 1
    try:
        check(api.ADC_NewDataConnect(
            CONNECTION_NAME, PLC_IP, USERNAME, PASSWORD, SCAN_INTERVAL,
            CONNECT_TIMEOUT, TRANSACT_TIMEOUT,
            OnConnectCompletedEvent(), OnDisconnectCompletedEvent(), None,
        ), "ADC_NewDataConnect")
        result = api.ADC_SetMemConnectPort(CONNECTION_NAME, MEMORY_PORT)
        print(f"Set memory connection port result = {result}")
        check(result, "ADC_SetMemConnectPort")
        result = api.ADC_ConnectSync(CONNECTION_NAME)
        print(f"Connect result = {result}")
        check(result, "ADC_ConnectSync")
        connected = True
        result = api.ADC_GetSymbolList(CONNECTION_NAME, C.byref(symbols), C.byref(count))
        print(f"Get symbol list result = {result}, count = {count.value}")
        check(result, "ADC_GetSymbolList")
        for index in range(count.value):
            symbol = symbols[index]
            print(f"Symbol: {symbol.szName.decode(errors='replace')}, "
                  f"type = {symbol.szType.decode(errors='replace')}, size = {symbol.ulSize} bytes")

        print("Synchronous read/write is running. Press any key to stop (or Ctrl+C).")
        with Console() as console:
            while not console.key_pressed():
                for index in range(count.value):
                    symbol = symbols[index]
                    supported = {b"BYTE": 1, b"WORD": 2, b"DWORD": 4}
                    if supported.get(symbol.szType) != symbol.ulSize:
                        continue
                    # Match the C++ BYTE/WORD/DWORD random value ranges.
                    number = (random.randrange(256) if symbol.ulSize == 1 else
                              random.randrange(10000) if symbol.ulSize == 2 else
                              (random.randrange(32768) << 16) ^ random.randrange(32768))
                    value = C.c_uint32(number)
                    result = api.ADC_WriteSymbolValueSync(
                        CONNECTION_NAME, symbol.szName, C.byref(value), symbol.ulSize,
                    )
                    print(f"Write symbol result = {result}, name = {symbol.szName.decode(errors='replace')}, "
                          f"value = {value.value}")
                    check(result, "ADC_WriteSymbolValueSync")
                    value.value = 0
                    result = api.ADC_ReadSymbolValueSync(
                        CONNECTION_NAME, symbol.szName, C.byref(value), symbol.ulSize,
                    )
                    check(result, "ADC_ReadSymbolValueSync")
                    print(f"Read symbol result = {result}, name = {symbol.szName.decode(errors='replace')}, "
                          f"value = {value.value}")

                # Use explicit PLC widths: WORD = 16 bits, DWORD = 32 bits.
                for address, value in (
                    (MEMORY_WORD_ADDRESS, C.c_uint16(random.randrange(10000))),
                    (MEMORY_DWORD_ADDRESS, C.c_uint32(
                        (random.randrange(32768) << 16) ^ random.randrange(32768))),
                ):
                    result = api.ADC_WriteMemoryValueSync(
                        CONNECTION_NAME, address, C.byref(value), C.sizeof(value),
                    )
                    print(f"Write memory result = {result}, address = {address.decode()}, value = {value.value}")
                    check(result, "ADC_WriteMemoryValueSync")
                    value.value = 0
                    result = api.ADC_ReadMemoryValueSync(
                        CONNECTION_NAME, address, C.byref(value), C.sizeof(value),
                    )
                    print(f"Read memory result = {result}, address = {address.decode()}, value = {value.value}")
                    check(result, "ADC_ReadMemoryValueSync")
                time.sleep(LOOP_INTERVAL)
    except KeyboardInterrupt:
        pass
    except RuntimeError as exc:
        print(exc)
        return 1
    finally:
        try:
            if symbols:
                api.ADC_FreeSymbolList(symbols)
        finally:
            finish(api, connection=CONNECTION_NAME if connected else None)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
