from __future__ import annotations

import ctypes

from adc_api import check
from test_common import buffer_from, initialized
from test_data import MEMORY_CASES, values_equal


def test_local_memory(dll):
    with initialized(dll):
        for case in MEMORY_CASES:
            address = case.memory.encode()
            length = ctypes.c_int(case.size)
            write_buffer = buffer_from(case.pack())
            if case.units == 1:
                result = dll.ADC_WriteSingleMemoryValue_Local(address, write_buffer, ctypes.byref(length))
            else:
                result = dll.ADC_WriteMultipleMemoryValue_Local(
                    address, case.units, write_buffer, ctypes.byref(length))
            check(f"local write {case.name}", result)

            read_buffer = ctypes.create_string_buffer(case.size)
            length = ctypes.c_int(case.size)
            if case.units == 1:
                result = dll.ADC_ReadSingleMemoryValue_Local(address, read_buffer, ctypes.byref(length))
            else:
                result = dll.ADC_ReadMultipleMemoryValue_Local(
                    address, case.units, read_buffer, ctypes.byref(length))
            check(f"local read {case.name}", result)
            actual = case.unpack(read_buffer.raw)
            if not values_equal(case.value, actual):
                raise RuntimeError(f"local {case.name}: wrote {case.value}, read {actual}")
            print(f"PASS Local Memory {case.name} {case.memory}: {actual}")
