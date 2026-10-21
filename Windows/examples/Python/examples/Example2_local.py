"""CPlusPlus/Example3: read/write local flag memory, optionally all 32768 bytes."""

import ctypes as C

if __package__:
    from ._common import check, finish
else:
    from _common import check, finish
from advantech_adc import ADCAPI, ErrorCode

# Edit these settings directly. READ_WRITE_ALL corresponds to C++ ReadWriteAll.
MAX_FLAG_MEMORY_SIZE = 32768
READ_WRITE_ALL = False
MEMORY_ADDRESS = b"%MW0"
ALL_MEMORY_ADDRESS = b"%MB0"


def main():
    api = ADCAPI
    result = api.ADC_Initialize()
    if result != ErrorCode.SUCCESS:
        print(f"Initialize failed, result = {result}")
        return 1
    try:
        value = C.c_uint32()
        length = C.c_int(C.sizeof(value))
        check(api.ADC_ReadSingleMemoryValue_Local(
            MEMORY_ADDRESS, C.byref(value), C.byref(length),
        ), "ADC_ReadSingleMemoryValue_Local")
        if value.value == 1000:
            value.value = 1200
            length.value = C.sizeof(value)
            result = api.ADC_WriteSingleMemoryValue_Local(
                MEMORY_ADDRESS, C.byref(value), C.byref(length),
            )
            print(f"write memory result = {result} size={length.value}")
            check(result, "ADC_WriteSingleMemoryValue_Local")
        if READ_WRITE_ALL:
            data = (C.c_ubyte * MAX_FLAG_MEMORY_SIZE)()
            length = C.c_int(C.sizeof(data))
            check(api.ADC_ReadMultipleMemoryValue_Local(
                ALL_MEMORY_ADDRESS, MAX_FLAG_MEMORY_SIZE, data, C.byref(length),
            ), "ADC_ReadMultipleMemoryValue_Local")
            C.memset(data, 0xFF, C.sizeof(data))
            length.value = C.sizeof(data)
            result = api.ADC_WriteMultipleMemoryValue_Local(
                ALL_MEMORY_ADDRESS, MAX_FLAG_MEMORY_SIZE, data, C.byref(length),
            )
            print(f"write entire memory result = {result} size={length.value}")
            check(result, "ADC_WriteMultipleMemoryValue_Local")
    except RuntimeError as exc:
        print(exc)
        return 1
    finally:
        finish(api)
    input("Press Enter to exit...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
