"""Console and cleanup helpers shared by the C++ example translations."""

import os
from pathlib import Path
import sys

# Support both `python Example1_async.py` and `python -m Example1_async`.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from advantech_adc import ErrorCode


def check(result, operation):
    if result != ErrorCode.SUCCESS:
        raise RuntimeError(f"{operation} failed, result = {result}")
    return result


def finish(api, connection=None, polling=False):
    if polling:
        result = api.ADC_StopDataPolling()
        if result not in (ErrorCode.SUCCESS, ErrorCode.THREAD_STOP):
            print(f"Stop polling failed, result = {result}")
            return  # Keep resources alive if the native worker is still running.
    if connection is not None:
        result = api.ADC_DisconnectSync(connection)
        if result != ErrorCode.SUCCESS:
            print(f"Disconnect failed, result = {result}")
    result = api.ADC_ReleaseADCResource()
    if result != ErrorCode.SUCCESS:
        print(f"Release resources failed, result = {result}")
    result = api.ADC_Terminate()
    if result != ErrorCode.SUCCESS:
        print(f"Terminate failed, result = {result}")


class Console:
    """Windows key polling; Linux terminal cbreak polling with state restoration."""

    def __enter__(self):
        self._saved = None
        if os.name != "nt" and sys.stdin.isatty():
            import termios
            import tty
            self._fd = sys.stdin.fileno()
            self._saved = termios.tcgetattr(self._fd)
            tty.setcbreak(self._fd)
        return self

    def key_pressed(self, escape_only=False):
        if os.name == "nt":
            import msvcrt
            if not msvcrt.kbhit():
                return False
            key = msvcrt.getwch()
        else:
            import select
            if self._saved is None or not select.select([self._fd], [], [], 0)[0]:
                return False
            key = os.read(self._fd, 1).decode(errors="replace")
        return key == "\x1b" if escape_only else True

    def __exit__(self, *args):
        if self._saved is not None:
            import termios
            termios.tcsetattr(self._fd, termios.TCSADRAIN, self._saved)
