from __future__ import annotations

import ctypes
import os
from pathlib import Path

from config import MEMORY_SIZE_BYTES

from adc_api import check
from test_common import buffer_from, initialized
from test_data import MEMORY_CASES, values_equal


def test_local_memory(dll):
    shm = Path("/dev/shm/advModbusShm")
    try:
        info = shm.stat()
    except FileNotFoundError:
        raise RuntimeError(f"Local shared memory is missing: {shm}. Run on the PLC host with "
                           "its RTE/shared-memory provider running; use --mode remote on another host.") from None
    except OSError as error:
        raise RuntimeError(f"Cannot inspect local shared memory {shm}: {error}") from error
    if not shm.is_file():
        raise RuntimeError(f"Local shared memory is not a regular file: {shm}")
    if info.st_size < MEMORY_SIZE_BYTES:
        raise RuntimeError(f"Local shared memory {shm} has {info.st_size} bytes; "
                           f"at least {MEMORY_SIZE_BYTES} bytes required. Check the RTE configuration.")
    if not os.access(shm, os.R_OK | os.W_OK):
        raise RuntimeError(f"No read/write access to {shm}: euid={os.geteuid()}, "
                           f"owner={info.st_uid}:{info.st_gid}, mode={oct(info.st_mode & 0o777)}. "
                           "Check the RTE shared-memory ownership and permissions.")
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
