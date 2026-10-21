# Advantech Data Connect Python API

`advantech-adc` provides Python access to Advantech Data Connect (ADC) for
reading and writing CODESYS PLC symbols and memory on Windows and Linux.
It supports synchronous communication, asynchronous polling, local memory
access.

## Requirements

- Python 3.7 or later.
- Windows x86/x64 or Linux x86/x64.
- A configured CODESYS controller for remote communication, or the local ADC
  shared memory environment for local memory access.

The native library architecture must match the Python process architecture.
For example, 32-bit Python on 64-bit Windows uses the x86 DLL.

## Installation

```bash
python -m pip install advantech-adc
```

### Windows

The matching x86 or x64 `AdvHandler.dll` is included in the Python package
and loaded automatically. No manual DLL copying or path selection is required.

### Linux

Install CODESYS RTE or `adc-package` first. These installers place the ADC
shared libraries in `/usr/lib`. The Python package uses the matching library:

| Python architecture | Library path |
| --- | --- |
| 32-bit | `/usr/lib/libADCLibrary-x86.so` |
| 64-bit | `/usr/lib/libADCLibrary-x64.so` |

Linux shared libraries are provided by the CODESYS RTE or `adc-package`
installation, not by the Python package.

## Using the API

```python
from advantech_adc import ADCAPI, ErrorCode, ThreadPriority

api = ADCAPI
```

Call the ADC functions directly through `api`. Most operations return a status
code; compare it with `ErrorCode.SUCCESS` before continuing. `ErrorCode` groups
success, error, and connection-status codes. Its members can be compared directly
with integer API results without using `.value`.

- **Synchronous access:** initialize ADC, create a connection with
  `ADC_NewDataConnect()`, connect with `ADC_ConnectSync()`, then read or write
  symbols and memory using the synchronous APIs.
- **Asynchronous polling:** create a connection and data sectors, register
  callbacks, and call `ADC_StartDataPolling()`.
- **Local memory access:** initialize ADC and use the `*_Local()` memory APIs.

When finished, stop polling if active, disconnect synchronous connections,
release ADC resources, and call `ADC_Terminate()`. Pass connection names,
symbol names, and memory addresses as bytes, such as `b"CONN1"` and `b"%MW0"`.
See the example programs for complete usage.

After polling starts, use `api.ADC_SetADCPriority(ThreadPriority.NORMAL)` to
change the native ADC worker-thread priority. `ThreadPriority` includes `IDLE`,
`LOWEST`, `BELOW_NORMAL`, `NORMAL`, `ABOVE_NORMAL`, `HIGHEST`, and `TIME_CRITICAL`.
This does not change the Python main-thread priority. The current Linux library
requires root for this setting; a non-root call keeps the default priority and
still returns success. Windows applies the native thread-priority setting.

The original constants, such as `ADC_SUCCESS` and `THREAD_PRIORITY_NORMAL`,
remain available for existing applications.

## Example programs

Download the **source distribution** (`advantech_adc-<version>.tar.gz`) from the
[PyPI files page](https://pypi.org/project/advantech-adc/#files).
For a TestPyPI installation, use the corresponding
[TestPyPI files page](https://test.pypi.org/project/advantech-adc/#files).
Choose the same version as your installed package.

After extracting the archive, the examples are located in:

```text
advantech_adc-<version>/examples/
```

| Example path | Description |
| --- | --- |
| `examples/Example1_async.py` | Reads and writes PLC symbols and memory using asynchronous polling and callbacks. |
| `examples/Example2_local.py` | Reads and writes local flag memory. Optional full-memory access is disabled by default. |
| `examples/Example3_sync.py` | Lists PLC symbols and performs synchronous symbol and memory reads and writes. |
| `examples/Example4_sync_struct.py` | Synchronously reads and writes a PLC structure containing BYTE, WORD, and DWORD fields. |
| `../../../Codesys_Project/example_linux.project` | CODESYS sample project for use with the Python examples and a Linux CODESYS runtime. |

Open `../../../Codesys_Project/example_linux.project` in CODESYS, configure the target device,
and download and run the application before using the remote Python examples.
Adjust the connection settings in the Python examples to match your controller.

Keep `_common.py` in the `examples` directory. Edit the IP address, credentials,
symbols, and memory settings in each example before running it. The examples
perform writes to the configured PLC or local memory.

From the extracted directory, run an example with the Python environment where
the package is installed:

```bash
python examples/Example1_async.py
```

## Downloads and support

- [Library downloads, manuals and documentation](https://github.com/Adv-Yuhsiang/Codesys_ADC)
- [Official releases](https://github.com/Adv-Yuhsiang/Codesys_ADC/releases)
- Author: Advantech/MA
- Contact: yuhsiang.lin@advantech.com.tw
- License: Apache License 2.0
