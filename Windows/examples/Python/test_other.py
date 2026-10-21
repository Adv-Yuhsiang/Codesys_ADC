from __future__ import annotations

import ctypes

from adc_api import ADC_SUCCESS, check
from test_common import initialized, new_connection


def test_other(dll):
    with initialized(dll):
        version = dll.ADC_GetVersion()
        if version <= 0:
            raise RuntimeError(f"invalid ADC version: {version}")
        print(f"PASS ADC_GetVersion: 0x{version:04X}")
        new_connection(dll)
        check("ADC_ShowConnection", dll.ADC_ShowConnection())
        print("PASS ADC_ShowConnection")

        result = dll.ADC_ReadMemoryValueSync(b"missing", b"%MW0", None, 2)
        if result == ADC_SUCCESS:
            raise RuntimeError("invalid-parameter test unexpectedly succeeded")
        print(f"PASS invalid parameter handling: {result}")
