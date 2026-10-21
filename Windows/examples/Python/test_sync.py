from __future__ import annotations

import ctypes
import random
import struct

from adc_api import check
from config import MEMORY_SIZE_BYTES
from test_common import CONNECTION, buffer_from, sync_connection
from test_data import CASES, MEMORY_CASES, values_equal


def test_symbols(dll):
    with sync_connection(dll):
        for case in CASES:
            symbol = case.symbol.encode()
            write_buffer = buffer_from(case.pack())
            check(f"write Symbol {case.name}", dll.ADC_WriteSymbolValueSync(
                CONNECTION, symbol, write_buffer, case.size))
            read_buffer = ctypes.create_string_buffer(case.size)
            check(f"read Symbol {case.name}", dll.ADC_ReadSymbolValueSync(
                CONNECTION, symbol, read_buffer, case.size))
            actual = case.unpack(read_buffer.raw)
            if not values_equal(case.value, actual):
                raise RuntimeError(f"{case.name}: wrote {case.value}, read {actual}")
            print(f"PASS sync Symbol {case.name}: {actual}")

        _test_complex_symbols(dll)


def _test_complex_symbols(dll):
    generator = random.SystemRandom()
    struct_values = (
        generator.randint(-2_000_000_000, 2_000_000_000),
        generator.uniform(-100_000.0, 100_000.0),
        generator.randint(0, 4_000_000_000),
    )
    array_values = tuple(generator.randint(-2_000_000_000, 2_000_000_000) for _ in range(4))

    _write_read_complex_symbol(
        dll,
        "STRUCT",
        "Application.PLC_PRG.ADC_Test_Struct",
        "<ifI",
        struct_values,
    )
    _write_read_complex_symbol(
        dll,
        "ARRAY",
        "Application.PLC_PRG.ADC_Test_Array",
        "<4i",
        array_values,
    )


def _write_read_complex_symbol(dll, name, symbol_name, fmt, expected):
    packed = struct.pack(fmt, *expected)
    symbol = symbol_name.encode()
    check(f"write Symbol {name}", dll.ADC_WriteSymbolValueSync(
        CONNECTION, symbol, buffer_from(packed), len(packed)))

    read_buffer = ctypes.create_string_buffer(len(packed))
    check(f"read Symbol {name}", dll.ADC_ReadSymbolValueSync(
        CONNECTION, symbol, read_buffer, len(packed)))
    actual = struct.unpack(fmt, read_buffer.raw)
    if not all(values_equal(expected_value, actual_value)
               for expected_value, actual_value in zip(expected, actual)):
        raise RuntimeError(f"{name}: wrote {expected}, read {actual}")
    print(f"PASS sync Symbol {name}: {actual}")


def test_memory(dll, full_memory=False):
    with sync_connection(dll):
        for case in MEMORY_CASES:
            address = case.memory.encode()
            write_buffer = buffer_from(case.pack())
            check(f"write Memory {case.name}", dll.ADC_WriteMemoryValueSync(
                CONNECTION, address, write_buffer, case.size))
            read_buffer = ctypes.create_string_buffer(case.size)
            check(f"read Memory {case.name}", dll.ADC_ReadMemoryValueSync(
                CONNECTION, address, read_buffer, case.size))
            actual = case.unpack(read_buffer.raw)
            if not values_equal(case.value, actual):
                raise RuntimeError(f"{case.name}: wrote {case.value}, read {actual}")
            print(f"PASS sync Memory {case.name} {case.memory}: {actual}")

        _test_memory_boundaries(dll)
        if full_memory:
            _test_entire_modbus_space(dll)


def _test_memory_boundaries(dll):
    for offset in (0, 1, 0x1FFFE, 0x1FFFF, 0x20000, MEMORY_SIZE_BYTES - 2, MEMORY_SIZE_BYTES - 1):
        size = min(2, MEMORY_SIZE_BYTES - offset)
        address = f"%MB{offset}".encode()
        original = ctypes.create_string_buffer(size)
        check("boundary backup", dll.ADC_ReadMemoryValueSync(CONNECTION, address, original, size))
        pattern = bytes(((offset + index + 0x5A) & 0xFF) for index in range(size))
        try:
            check("boundary write", dll.ADC_WriteMemoryValueSync(
                CONNECTION, address, buffer_from(pattern), size))
            verify = ctypes.create_string_buffer(size)
            check("boundary read", dll.ADC_ReadMemoryValueSync(CONNECTION, address, verify, size))
            if verify.raw != pattern:
                raise RuntimeError(f"boundary mismatch at byte {offset}")
        finally:
            check("boundary restore", dll.ADC_WriteMemoryValueSync(
                CONNECTION, address, original, size))
        print(f"PASS Modbus boundary byte {offset} size {size}")


def _test_entire_modbus_space(dll):
    block_size = 4096
    print(f"Testing and restoring the complete {MEMORY_SIZE_BYTES}-byte Modbus space...")
    for offset in range(0, MEMORY_SIZE_BYTES, block_size):
        size = min(block_size, MEMORY_SIZE_BYTES - offset)
        address = f"%MB{offset}".encode()
        original = ctypes.create_string_buffer(size)
        check("full-space backup", dll.ADC_ReadMemoryValueSync(CONNECTION, address, original, size))
        pattern = bytes(((offset + index) * 37 + 0xA5) & 0xFF for index in range(size))
        try:
            check("full-space write", dll.ADC_WriteMemoryValueSync(
                CONNECTION, address, buffer_from(pattern), size))
            verify = ctypes.create_string_buffer(size)
            check("full-space read", dll.ADC_ReadMemoryValueSync(CONNECTION, address, verify, size))
            if verify.raw != pattern:
                raise RuntimeError(f"full-space mismatch at byte {offset}")
        finally:
            check("full-space restore", dll.ADC_WriteMemoryValueSync(
                CONNECTION, address, original, size))
        if offset % (256 * 1024) == 0:
            print(f"  verified through byte {offset + size - 1}")
    print("PASS complete Modbus space")
