from dataclasses import dataclass
import struct


@dataclass(frozen=True)
class ValueCase:
    name: str
    symbol: str
    memory: str
    fmt: str
    value: object

    @property
    def size(self):
        return struct.calcsize(self.fmt)

    @property
    def units(self):
        if self.memory.startswith("%ML"):
            return self.size // 8
        if self.memory.startswith("%MD"):
            return self.size // 4
        if self.memory.startswith("%MW"):
            return self.size // 2
        return self.size

    def pack(self):
        return struct.pack(self.fmt, *(self.value if isinstance(self.value, tuple) else (self.value,)))

    def unpack(self, data):
        values = struct.unpack(self.fmt, data)
        return values if isinstance(self.value, tuple) else values[0]


CASES = [
    ValueCase("BOOL", "Application.PLC_PRG.ADC_Test_BOOL", "%MB100", "<?", True),
    ValueCase("SINT", "Application.PLC_PRG.ADC_Test_SINT", "%MB101", "<b", -101),
    ValueCase("USINT/BYTE", "Application.PLC_PRG.ADC_Test_USINT", "%MB102", "<B", 203),
    ValueCase("INT", "Application.PLC_PRG.ADC_Test_INT", "%MW100", "<h", -12345),
    ValueCase("UINT/WORD", "Application.PLC_PRG.ADC_Test_UINT", "%MW101", "<H", 54321),
    ValueCase("DINT", "Application.PLC_PRG.ADC_Test_DINT", "%MD100", "<i", -123456789),
    ValueCase("UDINT/DWORD", "Application.PLC_PRG.ADC_Test_UDINT", "%MD101", "<I", 3456789012),
    ValueCase("LINT", "Application.PLC_PRG.ADC_Test_LINT", "%MD102", "<q", -1234567890123456789),
    ValueCase("ULINT/LWORD", "Application.PLC_PRG.ADC_Test_ULINT", "%MD104", "<Q", 12345678901234567890),
    ValueCase("REAL", "Application.PLC_PRG.ADC_Test_REAL", "%MD106", "<f", 1234.25),
    ValueCase("LREAL", "Application.PLC_PRG.ADC_Test_LREAL", "%MD107", "<d", -98765.125),
]


MEMORY_CASES = CASES + [
    ValueCase("ML LINT", "", "%ML128", "<q", -1234567890123456789),
    ValueCase("ML LWORD", "", "%ML129", "<Q", 12345678901234567890),
    ValueCase("ML LREAL", "", "%ML130", "<d", -98765.125),
    ValueCase("ML multiple", "", "%ML132", "<2Q", (0x123456789ABCDEF0, 0xFEDCBA9876543210)),
]


def values_equal(expected, actual):
    if isinstance(expected, tuple):
        return len(expected) == len(actual) and all(values_equal(e, a) for e, a in zip(expected, actual))
    if isinstance(expected, float):
        return abs(expected - actual) <= max(1e-5, abs(expected) * 1e-6)
    return expected == actual
