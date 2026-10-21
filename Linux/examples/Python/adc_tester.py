from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

from adc_api import load_library
from test_async import test_memory as test_async_memory
from test_async import test_symbols as test_async_symbols
from test_local import test_local_memory
from test_mem_port import test_mem_port
from test_mixed_plc import test_mixed_plc
from test_other import test_other
from test_symbol_list import test_symbol_list
from test_sync import test_memory as test_sync_memory
from test_sync import test_symbols as test_sync_symbols


BASE_DIR = Path(__file__).resolve().parent

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


def process_platform() -> str:
    return "x64" if struct.calcsize("P") == 8 else "x86"


def fixed_library_path(platform: str) -> Path:
    if sys.platform.startswith("linux"):
        return Path(f"/usr/lib/libADCLibrary-{platform}.so")
    raise RuntimeError(f"Unsupported platform: {sys.platform}")


def main():
    parser = argparse.ArgumentParser(description="ADC Library functional tester")
    parser.add_argument("--test", choices=[*TESTS, "all"], required=True)
    parser.add_argument("--full-memory", action="store_true",
                        help="Write, verify, and restore every byte in the 2 MB Modbus space")
    parser.add_argument("--platform", choices=("auto", "x86", "x64"), default="auto")
    parser.add_argument("--mode", choices=("local", "remote"), default="local",
                        help="remote skips local-memory; local keeps all Windows test categories")
    args = parser.parse_args()
    if args.mode == "remote" and args.test == "local-memory":
        parser.error("local-memory must run on the PLC machine with --mode local")

    actual_platform = process_platform()
    selected_platform = actual_platform if args.platform == "auto" else args.platform
    if selected_platform != actual_platform:
        parser.error(
            f"Python is {actual_platform}, but {selected_platform} was selected. "
            "Python and the native ADC Library must use the same architecture."
        )

    library_path = fixed_library_path(selected_platform)
    dll, loader_handles = load_library(library_path)
    selected = list(TESTS) if args.test == "all" else [args.test]
    failures = []
    try:
        print(f"Platform: {selected_platform}")
        print(f"Native library: {library_path}")
        for name in selected:
            if name == "local-memory" and args.mode == "remote":
                print("SKIP local-memory: run this category on the PLC machine")
                continue
            print(f"\n=== {name} ===")
            try:
                if name == "sync-memory":
                    TESTS[name](dll, args.full_memory)
                else:
                    TESTS[name](dll)
            except Exception as error:
                failures.append((name, error))
                print(f"FAIL {name}: {error}", file=sys.stderr)
                if args.test != "all":
                    break
    finally:
        loader_handles.clear()

    if failures:
        print("\nFailure summary:", file=sys.stderr)
        for name, error in failures:
            print(f"- {name}: {error}", file=sys.stderr)
        return 1
    print("\nALL APPLICABLE TESTS PASSED (see SKIP entries above)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
