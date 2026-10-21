from __future__ import annotations

import importlib
import os
import struct
import sys
from pathlib import Path
from types import SimpleNamespace


BASE_DIR = Path(__file__).resolve().parent
RUNTIME_CONFIG = BASE_DIR / "ADC.NET8.runtimeconfig.json"


def process_platform() -> str:
    return "x64" if struct.calcsize("P") == 8 else "x86"


def default_managed_library(platform: str) -> Path:
    return BASE_DIR / "library" / platform / "ADCClassLibrary.dll"


def default_native_directory(platform: str) -> Path:
    return BASE_DIR / "library" / platform


def load_adc_net8(platform: str = "auto"):
    actual_platform = process_platform()
    selected_platform = actual_platform if platform == "auto" else platform
    if selected_platform != actual_platform:
        raise RuntimeError(
            f"Python is {actual_platform}, but {selected_platform} was selected. "
            "Python, ADCClassLibrary.dll, and AdvHandler.dll must use the same architecture."
        )

    assembly_path = default_managed_library(selected_platform).resolve()
    native_path = default_native_directory(selected_platform).resolve()

    if not assembly_path.is_file():
        raise FileNotFoundError(
            f"ADC.NET8 assembly not found: {assembly_path}. "
            f"Build ADCClassLibrary.csproj with Platform={selected_platform} first."
        )
    if not (native_path / "AdvHandler.dll").is_file():
        raise FileNotFoundError(f"Native AdvHandler.dll not found in: {native_path}")
    if not RUNTIME_CONFIG.is_file():
        raise FileNotFoundError(RUNTIME_CONFIG)

    dll_handle = None
    if sys.platform == "win32" and hasattr(os, "add_dll_directory"):
        dll_handle = os.add_dll_directory(str(native_path))

    from pythonnet import load

    load("coreclr", runtime_config=str(RUNTIME_CONFIG))

    import clr

    sys.path.insert(0, str(assembly_path.parent))
    clr.AddReference(assembly_path.stem)
    namespace = importlib.import_module("ADCClassLibrary")

    test_type = None
    test_assembly_path = assembly_path.parent / "ADCManagedTestTypes.dll"
    if test_assembly_path.is_file():
        clr.AddReference(test_assembly_path.stem)
        test_namespace = importlib.import_module("ADCManagedTestTypes")
        test_type = test_namespace.ADC_TEST_MARSHAL_STRUCT

    system = importlib.import_module("System")
    interop = importlib.import_module("System.Runtime.InteropServices")

    return SimpleNamespace(
        ADCAPI=namespace.ADCAPI,
        ADC_ErrorCode=namespace.ADC_ErrorCode,
        ADC_SYMBOL_INFO=namespace.ADC_SYMBOL_INFO,
        ADCBasic=namespace.ADCBasic,
        ADC_Priority=namespace.ADCBasic.ADC_Priority,
        DataConnect=namespace.DataConnect,
        SymdataSector=namespace.SymdataSector,
        MemdataSector=namespace.MemdataSector,
        OnSymdataReadCompletedEvent=namespace.OnSymdataReadCompletedEvent,
        OnMemdataReadCompletedEvent=namespace.OnMemdataReadCompletedEvent,
        OnSymdataWriteCompletedEvent=namespace.OnSymdataWriteCompletedEvent,
        OnMemdataWriteCompletedEvent=namespace.OnMemdataWriteCompletedEvent,
        ADC_TEST_MARSHAL_STRUCT=test_type,
        Boolean=system.Boolean,
        SByte=system.SByte,
        Byte=system.Byte,
        Int16=system.Int16,
        UInt16=system.UInt16,
        Int32=system.Int32,
        UInt32=system.UInt32,
        Int64=system.Int64,
        UInt64=system.UInt64,
        Single=system.Single,
        Double=system.Double,
        IntPtr=system.IntPtr,
        Array=system.Array,
        Activator=system.Activator,
        GC=system.GC,
        Marshal=interop.Marshal,
        GetClrType=clr.GetClrType,
        assembly_path=assembly_path,
        native_path=native_path,
        test_assembly_path=test_assembly_path,
        platform=selected_platform,
        dll_handle=dll_handle,
    )


def close_adc_net8(adc) -> None:
    if adc.dll_handle is not None:
        adc.dll_handle.close()

