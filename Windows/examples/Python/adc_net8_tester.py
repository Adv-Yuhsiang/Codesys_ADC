from __future__ import annotations

import argparse
import random
import struct
import sys
import threading
import time
from contextlib import contextmanager

from adc_net8 import close_adc_net8, load_adc_net8
from config import (
    CALLBACK_TIMEOUT_SECONDS,
    CONNECT_TIMEOUT_MS,
    CONNECTION_NAME,
    MEMORY_SIZE_BYTES,
    PLC_IP,
    PLC_PASSWORD,
    PLC_USERNAME,
    SCAN_INTERVAL_MS,
    TRANSACTION_TIMEOUT_MS,
)
from test_data import CASES, values_equal


DEFAULT_MODBUS_PORT = 503
ALTERNATE_TEST_PORT = 1503
MARSHAL_STRUCT_SYMBOL = "Application.PLC_PRG.ADC_Test_MarshalStruct"

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
    "PLC_PRG.ADC_Test_MarshalStruct": ("DATA", 80),
}


def result_code(result) -> int:
    try:
        return int(result)
    except TypeError:
        return int(result.value__)


def check(name: str, result, accepted=(0,)) -> None:
    code = result_code(result)
    if code not in accepted:
        raise RuntimeError(f"{name} failed: {code} ({result})")


def managed_bytes(adc, data: bytes):
    return adc.Array[adc.Byte](data)


def empty_managed_bytes(adc):
    return adc.Array[adc.Byte]([])


def empty_symbol_array(adc):
    return adc.Array[adc.ADC_SYMBOL_INFO]([])


def python_bytes(data) -> bytes:
    return bytes(int(value) for value in data)


def managed_type_for_case(adc, case):
    return {
        "<?": adc.Boolean,
        "<b": adc.SByte,
        "<B": adc.Byte,
        "<h": adc.Int16,
        "<H": adc.UInt16,
        "<i": adc.Int32,
        "<I": adc.UInt32,
        "<q": adc.Int64,
        "<Q": adc.UInt64,
        "<f": adc.Single,
        "<d": adc.Double,
    }[case.fmt]


def managed_value_for_case(adc, case):
    return managed_type_for_case(adc, case)(case.value)


def managed_default_for_case(adc, case):
    value_type = managed_type_for_case(adc, case)
    return adc.Activator.CreateInstance(adc.GetClrType(value_type))


def python_value_for_case(case, value):
    if case.fmt == "<?":
        return bool(value)
    if case.fmt in ("<f", "<d"):
        return float(value)
    return int(value)


def assert_case_value(case, actual, api_name):
    if not values_equal(case.value, actual):
        raise RuntimeError(
            f"{api_name} {case.name}: wrote {case.value}, read {actual}"
        )


def require_marshal_struct(adc):
    if adc.ADC_TEST_MARSHAL_STRUCT is None:
        raise RuntimeError(
            f"Managed test type assembly not found: {adc.test_assembly_path}. "
            "Build ADCTester/ManagedTestTypes/ADCManagedTestTypes.csproj first."
        )
    structure_type = adc.ADC_TEST_MARSHAL_STRUCT
    actual_size = int(adc.Marshal.SizeOf[structure_type]())
    if actual_size != 80:
        raise RuntimeError(
            f"ADC_TEST_MARSHAL_STRUCT size mismatch: expected 80, got {actual_size}"
        )
    return structure_type


def create_marshal_struct(adc, seed: int):
    structure_type = require_marshal_struct(adc)
    value = adc.Activator.CreateInstance(adc.GetClrType(structure_type))
    value.IsEnabled = (seed % 2) == 0
    value.Label = f"T{seed:04d}"[-5:]
    value.HasUpperLimit = True
    value.HasLowerLimit = (seed % 2) != 0
    value.UpperLimitIndex = seed + 10
    value.LowerLimitIndex = seed + 20
    value.OperatingMode = seed + 30
    value.StatusCode = seed + 40
    value.CommandCode = seed + 50
    value.ActualValues = adc.Array[adc.Double](
        [seed + 0.25, seed + 1.25, seed + 2.25]
    )
    value.TargetValues = adc.Array[adc.Double](
        [seed + 10.5, seed + 20.5, seed + 30.5]
    )
    return value


def assert_marshal_struct_equal(expected, actual) -> None:
    scalar_fields = (
        "IsEnabled",
        "Label",
        "HasUpperLimit",
        "HasLowerLimit",
        "UpperLimitIndex",
        "LowerLimitIndex",
        "OperatingMode",
        "StatusCode",
        "CommandCode",
    )
    for field in scalar_fields:
        expected_value = getattr(expected, field)
        actual_value = getattr(actual, field)
        if str(actual_value) != str(expected_value):
            raise RuntimeError(
                f"marshal struct {field} mismatch: "
                f"expected {expected_value}, got {actual_value}"
            )

    for field in ("ActualValues", "TargetValues"):
        expected_values = [float(value) for value in getattr(expected, field)]
        actual_values = [float(value) for value in getattr(actual, field)]
        if expected_values != actual_values:
            raise RuntimeError(
                f"marshal struct {field} mismatch: "
                f"expected {expected_values}, got {actual_values}"
            )


def pack_marshal_struct(value) -> bytes:
    label = str(value.Label).encode("ascii")[:5]
    label = (label + b"\0").ljust(6, b"\0")
    return struct.pack(
        "<B6sBB3xiiiii3d3d",
        int(bool(value.IsEnabled)),
        label,
        int(bool(value.HasUpperLimit)),
        int(bool(value.HasLowerLimit)),
        int(value.UpperLimitIndex),
        int(value.LowerLimitIndex),
        int(value.OperatingMode),
        int(value.StatusCode),
        int(value.CommandCode),
        *(float(item) for item in value.ActualValues),
        *(float(item) for item in value.TargetValues),
    )


def create_connection(adc):
    connection = adc.DataConnect(
        CONNECTION_NAME + "_NET8",
        PLC_IP,
        PLC_USERNAME,
        PLC_PASSWORD,
    )
    connection.ScanInterval = SCAN_INTERVAL_MS
    connection.ConnectTimeout = CONNECT_TIMEOUT_MS
    connection.TransactTimeout = TRANSACTION_TIMEOUT_MS
    return connection


@contextmanager
def initialized(adc):
    basic = adc.ADCBasic()
    try:
        yield basic
    finally:
        adc.GC.SuppressFinalize(basic)
        adc.ADCAPI.ADC_ReleaseADCResource()
        adc.ADCAPI.ADC_Terminate()


@contextmanager
def sync_connection(adc):
    with initialized(adc) as basic:
        connection = create_connection(adc)
        check("NewDataConnect", connection.NewDataConnect())
        check("ConnectSync", connection.ConnectSync())
        try:
            yield basic, connection
        finally:
            disconnect_result = connection.DisconnectSync()
            if sys.exc_info()[0] is None:
                check("DisconnectSync", disconnect_result)


class CallbackState:
    def __init__(self, adc):
        self.sector_event = threading.Event()
        self.write_event = threading.Event()
        self.last_sector_result = None
        self.last_write_result = None

        self.on_symbol_sector = adc.OnSymdataReadCompletedEvent(self._on_sector)
        self.on_memory_sector = adc.OnMemdataReadCompletedEvent(self._on_sector)
        self.on_symbol_write = adc.OnSymdataWriteCompletedEvent(self._on_write)
        self.on_memory_write = adc.OnMemdataWriteCompletedEvent(self._on_write)

    def _on_sector(self, result, _name, _total, _param):
        self.last_sector_result = result_code(result)
        if self.last_sector_result == 0:
            self.sector_event.set()

    def _on_write(self, result, _param):
        self.last_write_result = result_code(result)
        self.write_event.set()

    def wait_sector(self):
        if not self.sector_event.wait(CALLBACK_TIMEOUT_SECONDS):
            raise RuntimeError(
                f"sector callback timeout, last result={self.last_sector_result}"
            )
        self.sector_event.clear()

    def wait_write(self):
        if not self.write_event.wait(CALLBACK_TIMEOUT_SECONDS):
            raise RuntimeError("write callback timeout")
        self.write_event.clear()
        check("asynchronous write callback", self.last_write_result)


def wait_cached_value(read_value, case, state):
    deadline = time.monotonic() + CALLBACK_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        state.wait_sector()
        actual = read_value()
        if values_equal(case.value, actual):
            return actual
    raise RuntimeError(f"{case.name}: asynchronous value did not update")


def wait_cached_marshal_struct(read_value, expected, state):
    deadline = time.monotonic() + CALLBACK_TIMEOUT_SECONDS
    last_error = None
    while time.monotonic() < deadline:
        state.wait_sector()
        actual = read_value()
        try:
            assert_marshal_struct_equal(expected, actual)
            return actual
        except RuntimeError as error:
            last_error = error
    raise RuntimeError(
        f"marshal struct asynchronous value did not update: {last_error}"
    )


def wait_cached_bytes(read_value, expected, state, name):
    deadline = time.monotonic() + CALLBACK_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        state.wait_sector()
        actual = read_value()
        if actual == expected:
            return actual
    raise RuntimeError(f"{name}: asynchronous byte value did not update")


def test_async_symbols(adc) -> None:
    state = CallbackState(adc)
    polling_started = False
    with initialized(adc) as basic:
        connection = create_connection(adc)
        check("NewDataConnect", connection.NewDataConnect())

        sector = adc.SymdataSector("AllBasicSymbols")
        for case in CASES:
            sector.AddSymbol(case.symbol)
        sector.AddSymbol(MARSHAL_STRUCT_SYMBOL)
        sector.SymdataReadCompleted += state.on_symbol_sector
        check("AddSymdataSector", connection.AddSymdataSector(sector))

        check("StartDataPolling", basic.StartDataPolling())
        polling_started = True
        check("SetADCPriority", basic.SetADCPriority(adc.ADC_Priority.NORMAL))
        try:
            state.wait_sector()
            for case in CASES:
                state.write_event.clear()
                check(
                    f"legacy write Symbol {case.name}",
                    connection.WriteSymbolValue(
                        case.symbol,
                        managed_bytes(adc, case.pack()),
                        state.on_symbol_write,
                    ),
                )
                state.wait_write()

                def read_legacy_value():
                    result, data = connection.ReadSymbolValue(
                        case.symbol, empty_managed_bytes(adc)
                    )
                    check(f"legacy read Symbol {case.name}", result)
                    return case.unpack(python_bytes(data))

                legacy_actual = wait_cached_value(read_legacy_value, case, state)
                print(f"PASS legacy async Symbol {case.name}: {legacy_actual}")

                value_type = managed_type_for_case(adc, case)
                state.write_event.clear()
                check(
                    f"generic write Symbol {case.name}",
                    connection.WriteSymbolValue[value_type](
                        case.symbol,
                        managed_value_for_case(adc, case),
                        state.on_symbol_write,
                    ),
                )
                state.wait_write()

                def read_value():
                    result, value = connection.ReadSymbolValue[value_type](
                        case.symbol, managed_default_for_case(adc, case)
                    )
                    check(f"generic read Symbol {case.name}", result)
                    return python_value_for_case(case, value)

                actual = wait_cached_value(read_value, case, state)
                print(f"PASS generic async Symbol {case.name}: {actual}")

            legacy_expected = create_marshal_struct(adc, 100)
            legacy_data = pack_marshal_struct(legacy_expected)
            state.write_event.clear()
            check(
                "legacy write Symbol marshal STRUCT",
                connection.WriteSymbolValue(
                    MARSHAL_STRUCT_SYMBOL,
                    managed_bytes(adc, legacy_data),
                    state.on_symbol_write,
                ),
            )
            state.wait_write()

            def read_legacy_structure():
                result, data = connection.ReadSymbolValue(
                    MARSHAL_STRUCT_SYMBOL, empty_managed_bytes(adc)
                )
                check("legacy read Symbol marshal STRUCT", result)
                return python_bytes(data)

            wait_cached_bytes(
                read_legacy_structure,
                legacy_data,
                state,
                "legacy marshal STRUCT",
            )
            print("PASS legacy async Symbol marshal STRUCT")

            structure_type = require_marshal_struct(adc)
            expected = create_marshal_struct(adc, 101)
            state.write_event.clear()
            check(
                "generic write Symbol marshal STRUCT",
                connection.WriteSymbolValue[structure_type](
                    MARSHAL_STRUCT_SYMBOL,
                    expected,
                    state.on_symbol_write,
                ),
            )
            state.wait_write()

            def read_structure():
                result, value = connection.ReadSymbolValue[structure_type](
                    MARSHAL_STRUCT_SYMBOL,
                    adc.Activator.CreateInstance(adc.GetClrType(structure_type)),
                )
                check("generic read Symbol marshal STRUCT", result)
                return value

            wait_cached_marshal_struct(read_structure, expected, state)
            print("PASS generic async Symbol marshal STRUCT")
        finally:
            if polling_started:
                basic.StopDataPolling()


def test_async_memory(adc) -> None:
    state = CallbackState(adc)
    polling_started = False
    sectors = []
    with initialized(adc) as basic:
        connection = create_connection(adc)
        check("NewDataConnect", connection.NewDataConnect())

        for index, case in enumerate(CASES):
            sector = adc.MemdataSector(f"Mem{index}", case.memory, case.units)
            sector.MemdataReadCompleted += state.on_memory_sector
            check(f"add Memory sector {case.name}", connection.AddMemdataSector(sector))
            sectors.append(sector)

        check("StartDataPolling", basic.StartDataPolling())
        polling_started = True
        check("SetADCPriority", basic.SetADCPriority(adc.ADC_Priority.NORMAL))
        try:
            state.wait_sector()
            for case in CASES:
                legacy_data = managed_bytes(adc, case.pack())
                state.write_event.clear()
                if case.units == 1:
                    result = connection.WriteSingleMemoryValue(
                        case.memory, legacy_data, state.on_memory_write
                    )
                else:
                    result = connection.WriteMultipleMemoryValue(
                        case.memory,
                        case.units,
                        legacy_data,
                        state.on_memory_write,
                    )
                check(f"legacy write Memory {case.name}", result)
                state.wait_write()

                def read_legacy_value():
                    if case.units == 1:
                        result, data = connection.ReadSingleMemoryValue(
                            case.memory, empty_managed_bytes(adc)
                        )
                    else:
                        result, data = connection.ReadMultipleMemoryValue(
                            case.memory, case.units, empty_managed_bytes(adc)
                        )
                    check(f"legacy read Memory {case.name}", result)
                    return case.unpack(python_bytes(data))

                legacy_actual = wait_cached_value(read_legacy_value, case, state)
                print(
                    f"PASS legacy async Memory {case.name} "
                    f"{case.memory}: {legacy_actual}"
                )

                value_type = managed_type_for_case(adc, case)
                state.write_event.clear()
                result = connection.WriteMultipleMemoryValue[value_type](
                    case.memory,
                    managed_value_for_case(adc, case),
                    state.on_memory_write,
                )
                check(f"generic write Memory {case.name}", result)
                state.wait_write()

                def read_value():
                    result, value = connection.ReadMultipleMemoryValue[value_type](
                        case.memory, managed_default_for_case(adc, case)
                    )
                    check(f"generic read Memory {case.name}", result)
                    return python_value_for_case(case, value)

                actual = wait_cached_value(read_value, case, state)
                print(
                    f"PASS generic async Memory {case.name} "
                    f"{case.memory}: {actual}"
                )
        finally:
            if polling_started:
                basic.StopDataPolling()


def test_sync_symbols(adc) -> None:
    with sync_connection(adc) as (_basic, connection):
        for case in CASES:
            check(
                f"legacy write Symbol {case.name}",
                connection.WriteSymbolValueSync(
                    case.symbol, managed_bytes(adc, case.pack())
                ),
            )
            result, output = connection.ReadSymbolValueSync(
                case.symbol, case.size, empty_managed_bytes(adc)
            )
            check(f"legacy read Symbol {case.name}", result)
            legacy_actual = case.unpack(python_bytes(output))
            assert_case_value(case, legacy_actual, "legacy sync Symbol")
            print(f"PASS legacy sync Symbol {case.name}: {legacy_actual}")

            value_type = managed_type_for_case(adc, case)
            check(
                f"generic write Symbol {case.name}",
                connection.WriteSymbolValueSync[value_type](
                    case.symbol, managed_value_for_case(adc, case)
                ),
            )
            result, value = connection.ReadSymbolValueSync[value_type](
                case.symbol, managed_default_for_case(adc, case)
            )
            check(f"generic read Symbol {case.name}", result)
            actual = python_value_for_case(case, value)
            assert_case_value(case, actual, "generic sync Symbol")
            print(f"PASS generic sync Symbol {case.name}: {actual}")

        legacy_expected = create_marshal_struct(adc, 201)
        legacy_data = pack_marshal_struct(legacy_expected)
        check(
            "legacy write Symbol marshal STRUCT",
            connection.WriteSymbolValueSync(
                MARSHAL_STRUCT_SYMBOL, managed_bytes(adc, legacy_data)
            ),
        )
        result, output = connection.ReadSymbolValueSync(
            MARSHAL_STRUCT_SYMBOL,
            len(legacy_data),
            empty_managed_bytes(adc),
        )
        check("legacy read Symbol marshal STRUCT", result)
        if python_bytes(output) != legacy_data:
            raise RuntimeError("legacy sync marshal STRUCT byte mismatch")
        print("PASS legacy sync Symbol marshal STRUCT")

        structure_type = require_marshal_struct(adc)
        expected = create_marshal_struct(adc, 202)
        check(
            "generic write Symbol marshal STRUCT",
            connection.WriteSymbolValueSync[structure_type](
                MARSHAL_STRUCT_SYMBOL, expected
            ),
        )
        result, actual = connection.ReadSymbolValueSync[structure_type](
            MARSHAL_STRUCT_SYMBOL,
            adc.Activator.CreateInstance(adc.GetClrType(structure_type)),
        )
        check("generic read Symbol marshal STRUCT", result)
        assert_marshal_struct_equal(expected, actual)
        print("PASS generic sync Symbol marshal STRUCT")

        test_complex_symbols(adc, connection)


def test_complex_symbols(adc, connection) -> None:
    generator = random.SystemRandom()
    struct_values = (
        generator.randint(-2_000_000_000, 2_000_000_000),
        generator.uniform(-100_000.0, 100_000.0),
        generator.randint(0, 4_000_000_000),
    )
    array_values = tuple(
        generator.randint(-2_000_000_000, 2_000_000_000) for _ in range(4)
    )

    write_read_complex_symbol(
        adc,
        connection,
        "STRUCT",
        "Application.PLC_PRG.ADC_Test_Struct",
        "<ifI",
        struct_values,
    )
    write_read_complex_symbol(
        adc,
        connection,
        "ARRAY",
        "Application.PLC_PRG.ADC_Test_Array",
        "<4i",
        array_values,
    )


def write_read_complex_symbol(adc, connection, name, symbol_name, fmt, expected):
    packed = struct.pack(fmt, *expected)
    check(
        f"write Symbol {name}",
        connection.WriteSymbolValueSync(symbol_name, managed_bytes(adc, packed)),
    )
    result, output = connection.ReadSymbolValueSync(
        symbol_name, len(packed), empty_managed_bytes(adc)
    )
    check(f"read Symbol {name}", result)
    actual = struct.unpack(fmt, python_bytes(output))
    if not all(
        values_equal(expected_value, actual_value)
        for expected_value, actual_value in zip(expected, actual)
    ):
        raise RuntimeError(f"{name}: wrote {expected}, read {actual}")
    print(f"PASS sync Symbol {name}: {actual}")


def test_sync_memory(adc, full_memory=False) -> None:
    with sync_connection(adc) as (_basic, connection):
        for case in CASES:
            check(
                f"legacy write Memory {case.name}",
                connection.WriteMemoryValueSync(
                    case.memory, managed_bytes(adc, case.pack())
                ),
            )
            result, output = connection.ReadMemoryValueSync(
                case.memory, case.size, empty_managed_bytes(adc)
            )
            check(f"legacy read Memory {case.name}", result)
            legacy_actual = case.unpack(python_bytes(output))
            assert_case_value(case, legacy_actual, "legacy sync Memory")
            print(
                f"PASS legacy sync Memory {case.name} "
                f"{case.memory}: {legacy_actual}"
            )

            value_type = managed_type_for_case(adc, case)
            check(
                f"generic write Memory {case.name}",
                connection.WriteMemoryValueSync[value_type](
                    case.memory, managed_value_for_case(adc, case)
                ),
            )
            result, value = connection.ReadMemoryValueSync[value_type](
                case.memory, managed_default_for_case(adc, case)
            )
            check(f"generic read Memory {case.name}", result)
            actual = python_value_for_case(case, value)
            assert_case_value(case, actual, "generic sync Memory")
            print(
                f"PASS generic sync Memory {case.name} "
                f"{case.memory}: {actual}"
            )

        test_memory_boundaries(adc, connection)
        if full_memory:
            test_entire_modbus_space(adc, connection)


def test_memory_boundaries(adc, connection) -> None:
    offsets = (0, 1, 0x1FFFE, 0x1FFFF, 0x20000, MEMORY_SIZE_BYTES - 2,
               MEMORY_SIZE_BYTES - 1)
    for offset in offsets:
        size = min(2, MEMORY_SIZE_BYTES - offset)
        address = f"%MB{offset}"
        result, original = connection.ReadMemoryValueSync(
            address, size, empty_managed_bytes(adc)
        )
        check("boundary backup", result)
        pattern = bytes((offset + index + 0x5A) & 0xFF for index in range(size))
        try:
            check(
                "boundary write",
                connection.WriteMemoryValueSync(address, managed_bytes(adc, pattern)),
            )
            result, verify = connection.ReadMemoryValueSync(
                address, size, empty_managed_bytes(adc)
            )
            check("boundary read", result)
            if python_bytes(verify) != pattern:
                raise RuntimeError(f"boundary mismatch at byte {offset}")
        finally:
            check("boundary restore", connection.WriteMemoryValueSync(address, original))
        print(f"PASS Modbus boundary byte {offset} size {size}")


def test_entire_modbus_space(adc, connection) -> None:
    block_size = 4096
    print(f"Testing and restoring the complete {MEMORY_SIZE_BYTES}-byte Modbus space...")
    for offset in range(0, MEMORY_SIZE_BYTES, block_size):
        size = min(block_size, MEMORY_SIZE_BYTES - offset)
        address = f"%MB{offset}"
        result, original = connection.ReadMemoryValueSync(
            address, size, empty_managed_bytes(adc)
        )
        check("full-space backup", result)
        pattern = bytes(((offset + index) * 37 + 0xA5) & 0xFF for index in range(size))
        try:
            check(
                "full-space write",
                connection.WriteMemoryValueSync(address, managed_bytes(adc, pattern)),
            )
            result, verify = connection.ReadMemoryValueSync(
                address, size, empty_managed_bytes(adc)
            )
            check("full-space read", result)
            if python_bytes(verify) != pattern:
                raise RuntimeError(f"full-space mismatch at byte {offset}")
        finally:
            check("full-space restore", connection.WriteMemoryValueSync(address, original))
        if offset % (256 * 1024) == 0:
            print(f"  verified through byte {offset + size - 1}")
    print("PASS complete Modbus space")


def test_local_memory(adc) -> None:
    with initialized(adc) as basic:
        for case in CASES:
            legacy_data = managed_bytes(adc, case.pack())
            if case.units == 1:
                result = basic.WriteSingleMemoryValue_Local(
                    case.memory, legacy_data
                )
            else:
                result = basic.WriteMultipleMemoryValue_Local(
                    case.memory, case.units, legacy_data
                )
            check(f"legacy local write {case.name}", result)

            if case.units == 1:
                result, output = basic.ReadSingleMemoryValue_Local(
                    case.memory, empty_managed_bytes(adc)
                )
            else:
                result, output = basic.ReadMultipleMemoryValue_Local(
                    case.memory, case.units, empty_managed_bytes(adc)
                )
            check(f"legacy local read {case.name}", result)
            legacy_actual = case.unpack(python_bytes(output))
            assert_case_value(case, legacy_actual, "legacy Local Memory")
            print(
                f"PASS legacy Local Memory {case.name} "
                f"{case.memory}: {legacy_actual}"
            )

            value_type = managed_type_for_case(adc, case)
            result = basic.WriteMultipleMemoryValue_Local[value_type](
                case.memory, managed_value_for_case(adc, case)
            )
            check(f"generic local write {case.name}", result)

            result, value = basic.ReadMultipleMemoryValue_Local[value_type](
                case.memory, managed_default_for_case(adc, case)
            )
            check(f"generic local read {case.name}", result)
            actual = python_value_for_case(case, value)
            assert_case_value(case, actual, "generic Local Memory")
            print(
                f"PASS generic Local Memory {case.name} "
                f"{case.memory}: {actual}"
            )


def find_returned_symbol(symbols, expected_name):
    expected = expected_name.casefold()
    for name, type_name, size in symbols:
        normalized = name.casefold()
        if normalized == expected or normalized.endswith("." + expected):
            return name, type_name, size
    return None


def test_symbol_list(adc) -> None:
    with sync_connection(adc) as (_basic, connection):
        result, managed_symbols = connection.GetSymbolList(empty_symbol_array(adc))
        check("GetSymbolList", result)
        if managed_symbols is None or len(managed_symbols) == 0:
            raise RuntimeError("GetSymbolList returned no Symbols")

        returned_symbols = []
        symbols_with_type_and_size = 0
        print(f"Symbol count: {len(managed_symbols)}")
        for index, symbol in enumerate(managed_symbols):
            name = str(symbol.szName)
            type_name = str(symbol.szType)
            size = int(symbol.ulSize)
            returned_symbols.append((name, type_name, size))
            if name and type_name and size > 0:
                symbols_with_type_and_size += 1
            print(f"[{index}] {name} type={type_name} size={size}")

        if symbols_with_type_and_size == 0:
            raise RuntimeError("No symbol contains a name, type, and non-zero size")

        for expected_name, (expected_type, expected_size) in EXPECTED_COMPLEX_SYMBOLS.items():
            returned = find_returned_symbol(returned_symbols, expected_name)
            if returned is None:
                raise RuntimeError(
                    f"Required Symbol List test variable not found: {expected_name}"
                )
            actual_name, actual_type, actual_size = returned
            if expected_type.casefold() not in actual_type.casefold():
                raise RuntimeError(
                    f"{actual_name} type mismatch: expected {expected_type}, "
                    f"got {actual_type}"
                )
            if actual_size != expected_size:
                raise RuntimeError(
                    f"{actual_name} size mismatch: expected {expected_size}, "
                    f"got {actual_size}"
                )
            print(
                f"PASS complex symbol: {actual_name} "
                f"type={actual_type} size={actual_size}"
            )

    print("PASS ADC.NET8 Symbol List and native list release path")


def test_mixed_plc(adc) -> None:
    case = CASES[0]
    state = CallbackState(adc)
    polling_started = False
    sync_connected = False

    with initialized(adc) as basic:
        connection = create_connection(adc)
        check("NewDataConnect", connection.NewDataConnect())
        try:
            check("ConnectSync", connection.ConnectSync())
            sync_connected = True

            sector = adc.SymdataSector("MixedPLCConnection")
            sector.AddSymbol(case.symbol)
            sector.SymdataReadCompleted += state.on_symbol_sector
            check("AddSymdataSector", connection.AddSymdataSector(sector))

            check("StartDataPolling", basic.StartDataPolling())
            polling_started = True
            state.wait_sector()
            check("mixed PLC sector callback", state.last_sector_result)

            check("DisconnectSync", connection.DisconnectSync())
            sync_connected = False
            state.sector_event.clear()
            state.wait_sector()
            check("post-disconnect sector callback", state.last_sector_result)
            print("PASS polling continued after DisconnectSync")

            check("ConnectSync while polling", connection.ConnectSync())
            sync_connected = True
            check("StopDataPolling", basic.StopDataPolling())
            polling_started = False

            result, _output = connection.ReadSymbolValueSync(
                case.symbol, case.size, empty_managed_bytes(adc)
            )
            check("legacy ReadSymbolValueSync after polling stopped", result)

            value_type = managed_type_for_case(adc, case)
            result, _value = connection.ReadSymbolValueSync[value_type](
                case.symbol, managed_default_for_case(adc, case)
            )
            check("generic ReadSymbolValueSync after polling stopped", result)
            print(
                "PASS legacy and generic synchronous access continued "
                "after StopDataPolling"
            )
        finally:
            if polling_started:
                basic.StopDataPolling()
            if sync_connected:
                connection.DisconnectSync()


def test_mem_port(adc) -> None:
    polling_started = False
    sync_connected = False

    with initialized(adc) as basic:
        connection = create_connection(adc)
        check("NewDataConnect", connection.NewDataConnect())
        try:
            check(
                "SetMemConnectPort before connection",
                connection.SetMemConnectPort(adc.UInt16(DEFAULT_MODBUS_PORT)),
            )
            check(
                "SetMemConnectPort port zero",
                connection.SetMemConnectPort(adc.UInt16(0)),
                accepted=(1002,),
            )

            check("ConnectSync", connection.ConnectSync())
            sync_connected = True
            check(
                "SetMemConnectPort during synchronous connection",
                connection.SetMemConnectPort(adc.UInt16(ALTERNATE_TEST_PORT)),
                accepted=(3001,),
            )
            check("DisconnectSync", connection.DisconnectSync())
            sync_connected = False

            check(
                "SetMemConnectPort after synchronous disconnect",
                connection.SetMemConnectPort(adc.UInt16(DEFAULT_MODBUS_PORT)),
            )

            check("StartDataPolling", basic.StartDataPolling())
            polling_started = True
            check(
                "SetMemConnectPort during polling",
                connection.SetMemConnectPort(adc.UInt16(ALTERNATE_TEST_PORT)),
                accepted=(3001,),
            )
            check("StopDataPolling", basic.StopDataPolling())
            polling_started = False

            check(
                "SetMemConnectPort after polling stopped",
                connection.SetMemConnectPort(adc.UInt16(DEFAULT_MODBUS_PORT)),
            )
            print("PASS Memory connection port lifecycle protection")
        finally:
            if polling_started:
                basic.StopDataPolling()
            if sync_connected:
                connection.DisconnectSync()


def test_other(adc) -> None:
    with initialized(adc) as basic:
        version = int(basic.GetVersion())
        if version <= 0:
            raise RuntimeError(f"invalid ADC version: {version}")
        print(f"PASS GetVersion: 0x{version:04X}")

        connection = create_connection(adc)
        check("NewDataConnect", connection.NewDataConnect())
        check("ShowConnection", basic.ShowConnection())
        print("PASS ShowConnection")

        missing = adc.DataConnect("missing", "127.0.0.1")
        result, _output = missing.ReadMemoryValueSync(
            "%MW0", 2, empty_managed_bytes(adc)
        )
        if result_code(result) == 0:
            raise RuntimeError("invalid-parameter test unexpectedly succeeded")
        print(f"PASS invalid parameter handling: {result_code(result)}")

        result, _value = missing.ReadMultipleMemoryValue[adc.Boolean](
            "%MW0", adc.Activator.CreateInstance(adc.GetClrType(adc.Boolean))
        )
        check("generic Memory unit mismatch", result, accepted=(1012,))
        print("PASS generic Memory unit mismatch handling")


TESTS = {
    "async-symbols": test_async_symbols,
    "async-memory": test_async_memory,
    "sync-symbols": test_sync_symbols,
    "sync-memory": test_sync_memory,
    "local-memory": test_local_memory,
    "symbol-list": test_symbol_list,
    "mixed-plc": test_mixed_plc,
    "mem-port": test_mem_port,
    "other": test_other,
}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Test fixed-path ADC.NET8 libraries through Python.NET"
    )
    parser.add_argument("--test", choices=[*TESTS, "all"], required=True)
    parser.add_argument("--full-memory", action="store_true",
                        help="Write, verify, and restore every byte in the 2 MB Modbus space")
    parser.add_argument("--platform", choices=("auto", "x86", "x64"), default="auto")
    args = parser.parse_args()

    adc = load_adc_net8(platform=args.platform)
    selected = list(TESTS) if args.test == "all" else [args.test]
    failures = []
    try:
        print(f"Platform: {adc.platform}")
        print(f"Managed assembly: {adc.assembly_path}")
        print(f"Native directory: {adc.native_path}")
        for name in selected:
            print(f"\n=== ADC.NET8 {adc.platform} {name} ===")
            try:
                if name == "sync-memory":
                    TESTS[name](adc, args.full_memory)
                else:
                    TESTS[name](adc)
            except Exception as error:
                failures.append((name, error))
                print(f"FAIL {name}: {error}", file=sys.stderr)
                if args.test != "all":
                    break
    finally:
        close_adc_net8(adc)

    if failures:
        print(f"\n{adc.platform} failure summary:", file=sys.stderr)
        for name, error in failures:
            print(f"- {name}: {error}", file=sys.stderr)
        return 1

    print(f"\nALL SELECTED ADC.NET8 {adc.platform} TESTS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
