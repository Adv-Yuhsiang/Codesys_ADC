from __future__ import annotations

import ctypes
import threading
import time

from adc_api import CONNECT_CB, DISCONNECT_CB, SECTOR_CB, WRITE_CB, check
from config import CALLBACK_TIMEOUT_SECONDS
from test_common import CONNECTION, buffer_from, initialized, new_connection
from test_data import CASES, MEMORY_CASES, values_equal


class CallbackState:
    def __init__(self):
        self.sector_event = threading.Event()
        self.write_event = threading.Event()
        self.last_sector_result = None
        self.last_write_result = None

        @CONNECT_CB
        def on_connect(result, name, _):
            print(f"connection callback {name.decode(errors='replace')}: {result}")

        @DISCONNECT_CB
        def on_disconnect(result, name, _):
            print(f"disconnect callback {name.decode(errors='replace')}: {result}")

        @SECTOR_CB
        def on_sector(result, name, total, _):
            self.last_sector_result = result
            if result == 0:
                self.sector_event.set()

        @WRITE_CB
        def on_write(result, _):
            self.last_write_result = result
            self.write_event.set()

        self.on_connect = on_connect
        self.on_disconnect = on_disconnect
        self.on_sector = on_sector
        self.on_write = on_write

    def wait_sector(self):
        if not self.sector_event.wait(CALLBACK_TIMEOUT_SECONDS):
            raise RuntimeError(f"sector callback timeout, last result={self.last_sector_result}")
        self.sector_event.clear()

    def wait_write(self):
        if not self.write_event.wait(CALLBACK_TIMEOUT_SECONDS):
            raise RuntimeError("write callback timeout")
        self.write_event.clear()
        check("asynchronous write callback", self.last_write_result)


def _wait_cached_value(read_value, case, state):
    deadline = time.monotonic() + CALLBACK_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        state.wait_sector()
        actual = read_value()
        if values_equal(case.value, actual):
            return actual
    raise RuntimeError(f"{case.name}: asynchronous value did not update")


def test_symbols(dll):
    state = CallbackState()
    with initialized(dll):
        new_connection(dll, state.on_connect, state.on_disconnect)
        sector = b"AllBasicSymbols"
        check("ADC_NewSymdataSector", dll.ADC_NewSymdataSector(CONNECTION, sector, state.on_sector))
        for case in CASES:
            check(f"add {case.name}", dll.ADC_AddSymbolToSector(
                CONNECTION, sector, case.symbol.encode()))
        check("ADC_StartDataPolling", dll.ADC_StartDataPolling())
        check("ADC_SetADCPriority", dll.ADC_SetADCPriority(0))
        try:
            state.wait_sector()
            for case in CASES:
                write_buffer = buffer_from(case.pack())
                state.write_event.clear()
                check(f"write Symbol {case.name}", dll.ADC_WriteSymbolValue(
                    CONNECTION, case.symbol.encode(), write_buffer, state.on_write))
                state.wait_write()

                def read_value():
                    output = ctypes.create_string_buffer(case.size)
                    length = ctypes.c_int(case.size)
                    check(f"read Symbol {case.name}", dll.ADC_ReadSymbolValue(
                        CONNECTION, case.symbol.encode(), output, ctypes.byref(length)))
                    return case.unpack(output.raw)

                actual = _wait_cached_value(read_value, case, state)
                print(f"PASS async Symbol {case.name}: {actual}")
        finally:
            dll.ADC_StopDataPolling()
            check("ADC_DelSymdataSector", dll.ADC_DelSymdataSector(CONNECTION, sector))


def test_memory(dll):
    state = CallbackState()
    with initialized(dll):
        new_connection(dll, state.on_connect, state.on_disconnect)
        for index, case in enumerate(MEMORY_CASES):
            check(f"new Memory sector {case.name}", dll.ADC_NewMemdataSector(
                CONNECTION, f"Mem{index}".encode(), case.memory.encode(), case.units, state.on_sector))
        check("ADC_StartDataPolling", dll.ADC_StartDataPolling())
        check("ADC_SetADCPriority", dll.ADC_SetADCPriority(0))
        try:
            state.wait_sector()
            for case in MEMORY_CASES:
                write_buffer = buffer_from(case.pack())
                length = ctypes.c_int(case.size)
                state.write_event.clear()
                if case.units == 1:
                    result = dll.ADC_WriteSingleMemoryValue(
                        CONNECTION, case.memory.encode(), write_buffer, ctypes.byref(length), state.on_write)
                else:
                    result = dll.ADC_WriteMultipleMemoryValue(
                        CONNECTION, case.memory.encode(), case.units, write_buffer,
                        ctypes.byref(length), state.on_write)
                check(f"write Memory {case.name}", result)
                state.wait_write()

                def read_value():
                    output = ctypes.create_string_buffer(case.size)
                    read_length = ctypes.c_int(case.size)
                    if case.units == 1:
                        result = dll.ADC_ReadSingleMemoryValue(
                            CONNECTION, case.memory.encode(), output, ctypes.byref(read_length))
                    else:
                        result = dll.ADC_ReadMultipleMemoryValue(
                            CONNECTION, case.memory.encode(), case.units, output, ctypes.byref(read_length))
                    check(f"read Memory {case.name}", result)
                    return case.unpack(output.raw)

                actual = _wait_cached_value(read_value, case, state)
                print(f"PASS async Memory {case.name} {case.memory}: {actual}")
        finally:
            dll.ADC_StopDataPolling()
            for index, case in enumerate(MEMORY_CASES):
                check(f"delete Memory sector {case.name}", dll.ADC_DelMemdataSector(
                    CONNECTION, f"Mem{index}".encode()))
