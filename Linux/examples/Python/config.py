"""Edit this file for the target CODESYS RTE before running tests."""

import struct
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

PLC_IP = "172.16.13.57"
PLC_USERNAME = "oem"
PLC_PASSWORD = "oem"

CONNECTION_NAME = "ADCTEST"
SCAN_INTERVAL_MS = 100
CONNECT_TIMEOUT_MS = 3000
TRANSACTION_TIMEOUT_MS = 1000
CALLBACK_TIMEOUT_SECONDS = 10.0

MEMORY_SIZE_BYTES = 0x200000
PROCESS_PLATFORM = "x64" if struct.calcsize("P") == 8 else "x86"
DEFAULT_LIBRARY = f"/usr/lib/libADCLibrary-{PROCESS_PLATFORM}.so"
