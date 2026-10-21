from __future__ import annotations

import ctypes
from pathlib import Path

from adc_api import ADC_SYMBOL_INFO, check, free_symbol_list, load_library
from config import DEFAULT_LIBRARY
from test_common import CONNECTION, sync_connection


EXPECTED_COMPLEX_SYMBOLS = {
    "PLC_PRG.ADC_Test_Struct": ("DATA", 12),
    "PLC_PRG.ADC_Test_Struct.SignedValue": ("DINT", 4),
    "PLC_PRG.ADC_Test_Struct.RealValue": ("REAL", 4),
    "PLC_PRG.ADC_Test_Struct.UnsignedValue": ("UDINT", 4),
    "PLC_PRG.ADC_Test_Array": ("ARRAY", 16),
    "PLC_PRG.ADC_Test_Array[0]": ("DINT", 4),
    "PLC_PRG.ADC_Test_Array[1]": ("DINT", 4),
    "PLC_PRG.ADC_Test_Array[2]": ("DINT", 4),
    "PLC_PRG.ADC_Test_Array[3]": ("DINT", 4),
}


def _find_symbol(symbols, expected_name):
    expected_name = expected_name.casefold()
    for name, type_name, size in symbols:
        normalized_name = name.casefold()
        if normalized_name == expected_name or normalized_name.endswith("." + expected_name):
            return name, type_name, size
    return None


def test_symbol_list(dll):
    symbol_list = ctypes.POINTER(ADC_SYMBOL_INFO)()
    symbol_count = ctypes.c_ulong(0)
    try:
        with sync_connection(dll):
            check("ADC_GetSymbolList", dll.ADC_GetSymbolList(
                CONNECTION, ctypes.byref(symbol_list), ctypes.byref(symbol_count)))

            print(f"Symbol count: {symbol_count.value}")
            symbols_with_type_and_size = 0
            returned_symbols = []
            for index in range(symbol_count.value):
                symbol = symbol_list[index]
                name = bytes(symbol.szName).split(b"\0", 1)[0].decode(
                    "utf-8", errors="replace")
                type_name = bytes(symbol.szType).split(b"\0", 1)[0].decode(
                    "utf-8", errors="replace")
                size = symbol.ulSize
                returned_symbols.append((name, type_name, size))
                if name and type_name and size > 0:
                    symbols_with_type_and_size += 1
                print(f"[{index}] {name} type={type_name} size={size}")
            if symbol_count.value == 0:
                raise RuntimeError("ADC_GetSymbolList returned no symbols")
            if symbols_with_type_and_size == 0:
                raise RuntimeError("No symbol contains a name, type, and non-zero size")

            for expected_name, (expected_type, expected_size) in EXPECTED_COMPLEX_SYMBOLS.items():
                returned = _find_symbol(returned_symbols, expected_name)
                if returned is None:
                    raise RuntimeError(f"Required Symbol List test variable not found: {expected_name}")
                actual_name, actual_type, actual_size = returned
                if expected_type.casefold() not in actual_type.casefold():
                    raise RuntimeError(
                        f"{actual_name} type mismatch: expected {expected_type}, got {actual_type}")
                if actual_size != expected_size:
                    raise RuntimeError(
                        f"{actual_name} size mismatch: expected {expected_size}, got {actual_size}")
                print(f"PASS complex symbol: {actual_name} type={actual_type} size={actual_size}")
    finally:
        free_symbol_list(symbol_list, Path(dll._name))


def main():
    dll, loader_handles = load_library(Path(DEFAULT_LIBRARY))
    try:
        test_symbol_list(dll)
    finally:
        loader_handles.clear()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
