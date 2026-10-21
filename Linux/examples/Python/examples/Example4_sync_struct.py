"""CPlusPlus/Example5: synchronous ADC_DEMO_STRUCT Symbol read/write."""

import ctypes as C
import random
import time

if __package__:
    from ._common import Console, check, finish
else:
    from _common import Console, check, finish
from advantech_adc import ADCAPI, ErrorCode, OnConnectCompletedEvent, OnDisconnectCompletedEvent

# Edit these settings directly to match your controller.
CONNECTION_NAME = b"Connect1"
PLC_IP = b"192.168.11.80"
USERNAME = b"root"
PASSWORD = b"1234"
SYMBOL_NAME = b"Application.PLC_PRG.sym_struct"
SCAN_INTERVAL = 1000
CONNECT_TIMEOUT = 3000
TRANSACT_TIMEOUT = 1000
LOOP_INTERVAL = 1.0


class ADC_DEMO_STRUCT(C.Structure):
    # Match C++ default alignment: offsets 0, 2, 4; total 8 bytes.
    # The PLC structure must use the same field sizes and alignment.
    _fields_ = [("var_byte", C.c_uint8), ("var_word", C.c_uint16), ("var_dword", C.c_uint32)]


def main():
    api = ADCAPI
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
        result = api.ADC_ConnectSync(CONNECTION_NAME)
        print(f"Connect result = {result}")
        check(result, "ADC_ConnectSync")
        connected = True
        print("Synchronous struct read/write is running. Press any key to stop (or Ctrl+C).")
        with Console() as console:
            while not console.key_pressed():
                value = ADC_DEMO_STRUCT()
                value.var_byte = random.randrange(256)
                value.var_word = random.randrange(10000)
                value.var_dword = (random.randrange(32768) << 16) ^ random.randrange(32768)
                result = api.ADC_WriteSymbolValueSync(
                    CONNECTION_NAME, SYMBOL_NAME, C.byref(value), C.sizeof(value),
                )
                print(f"Write struct result = {result}, var_byte = {value.var_byte}, "
                      f"var_word = {value.var_word}, var_dword = {value.var_dword}")
                check(result, "ADC_WriteSymbolValueSync")
                C.memset(C.byref(value), 0, C.sizeof(value))
                result = api.ADC_ReadSymbolValueSync(
                    CONNECTION_NAME, SYMBOL_NAME, C.byref(value), C.sizeof(value),
                )
                check(result, "ADC_ReadSymbolValueSync")
                print(f"Read struct result = {result}, var_byte = {value.var_byte}, "
                      f"var_word = {value.var_word}, var_dword = {value.var_dword}")
                time.sleep(LOOP_INTERVAL)
    except KeyboardInterrupt:
        pass
    except RuntimeError as exc:
        print(exc)
        return 1
    finally:
        finish(api, connection=CONNECTION_NAME if connected else None)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
