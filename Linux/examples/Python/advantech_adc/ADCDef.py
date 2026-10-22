"""ADC result codes and thread priorities, with legacy constant aliases."""

from enum import IntEnum, unique

ADCERROR_BASE = 1000
PLCHANDLERERR_BASE = 2000
MEMORYERR_BASE = 3000
INTERNALERR_BASE = 4000
MODEXCEPT_BASE = (MEMORYERR_BASE + 900)


@unique
class ErrorCode(IntEnum):
    """Native ADC success, error and connection-status codes."""

    SUCCESS = 0
    HANDLE_INVALID = (ADCERROR_BASE + 1)
    PARAMETER_INVALID = (ADCERROR_BASE + 2)
    THREAD_RUNNING = (ADCERROR_BASE + 3)
    THREAD_STOP = (ADCERROR_BASE + 4)
    MEMALLOC_FAILED = (ADCERROR_BASE + 5)
    OBJECT_DUPLICATED = (ADCERROR_BASE + 6)
    OBJECT_NOT_EXIST = (ADCERROR_BASE + 7)
    SETPRIO_FAILED = (ADCERROR_BASE + 8)
    CREATE_THREAD_FAILED = (ADCERROR_BASE + 9)
    EXCEED_SECTOR_SIZE = (ADCERROR_BASE + 10)
    BUFFER_TOO_SMALL = (ADCERROR_BASE + 11)
    SIZE_MISMATCH = (ADCERROR_BASE + 12)
    INCOMPLETE_DATA = (ADCERROR_BASE + 13)
    WRONG_CONTEXT = (ADCERROR_BASE + 14)
    PLC_CONNECTED = (PLCHANDLERERR_BASE + 1)
    PLC_NOT_CONNECTED = (PLCHANDLERERR_BASE + 2)
    PLC_NO_SYMBOLS = (PLCHANDLERERR_BASE + 3)
    PLC_SYMBOLS_LOADED = (PLCHANDLERERR_BASE + 4)
    PLC_DISCONNECT = (PLCHANDLERERR_BASE + 5)
    PLC_NO_CONFIGURATION = (PLCHANDLERERR_BASE + 6)
    PLC_NOT_CONNECTED_SYMBOLS_LOADED = (PLCHANDLERERR_BASE + 7)
    PLC_SYMBOL_NOT_MATCH = (PLCHANDLERERR_BASE + 8)
    PLC_SYMBOL_SIZE_NOT_MATCH = (PLCHANDLERERR_BASE + 9)
    PLC_SYMBOL_VALUE_NOT_READY = (PLCHANDLERERR_BASE + 10)
    PLC_NOT_VALID_DEVICE = (PLCHANDLERERR_BASE + 11)
    PLC_SYMBOL_LOAD_FAILED = (PLCHANDLERERR_BASE + 12)
    PLC_INTERNAL_ERROR = (PLCHANDLERERR_BASE + 99)
    MEM_CONNECTED = (MEMORYERR_BASE + 1)
    MEM_WSASTART_FAILED = (MEMORYERR_BASE + 2)
    MEM_WSACLEAN_FAILED = (MEMORYERR_BASE + 3)
    MEM_CREATESOCK_FAILED = (MEMORYERR_BASE + 4)
    MEM_WAIT_TIMEOUT = (MEMORYERR_BASE + 5)
    MEM_CONNECT_FAILED = (MEMORYERR_BASE + 6)
    MEM_TCPSEND_FAILED = (MEMORYERR_BASE + 7)
    MEM_TCPRECV_FAILED = (MEMORYERR_BASE + 8)
    MEM_SOCKET_CLOSED = (MEMORYERR_BASE + 9)
    MEM_THREAD_BUSY = (MEMORYERR_BASE + 10)
    MEM_MODEXCEPT_01 = (MODEXCEPT_BASE + 1)
    MEM_MODEXCEPT_02 = (MODEXCEPT_BASE + 2)
    MEM_MODEXCEPT_03 = (MODEXCEPT_BASE + 3)
    MEM_MODEXCEPT_04 = (MODEXCEPT_BASE + 4)
    MEM_MODEXCEPT_05 = (MODEXCEPT_BASE + 5)
    MEM_MODEXCEPT_06 = (MODEXCEPT_BASE + 6)
    MEM_MODEXCEPT_07 = (MODEXCEPT_BASE + 7)
    MEM_MODEXCEPT_08 = (MODEXCEPT_BASE + 8)
    MEM_MODEXCEPT_99 = (MODEXCEPT_BASE + 99)


@unique
class ThreadPriority(IntEnum):
    """ADC native polling-thread priorities, using the Windows API values.

    Linux maps these values to SCHED_FIFO priorities. The current Linux
    library requires root; non-root calls keep defaults and return success.
    """

    LOWEST = -2
    BELOW_NORMAL = -1
    NORMAL = 0
    ABOVE_NORMAL = 1
    HIGHEST = 2
    TIME_CRITICAL = 15
    IDLE = -15


# Compatibility names for applications using the original ADC.h constants.
for _member in ErrorCode:
    globals()["ADC_" + _member.name] = _member
for _member in ThreadPriority:
    globals()["THREAD_PRIORITY_" + _member.name] = _member
del _member

# Windows API error sentinel, not a selectable thread priority.
THREAD_PRIORITY_ERROR_RETURN = 0x7FFFFFFF

__all__ = ["ErrorCode", "ThreadPriority"] + [
    name for name in globals() if name.isupper() and not name.startswith("_")
]
