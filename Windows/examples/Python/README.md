# ADC Python examples

These examples and the `advantech_adc` runtime modules come from `ADCLibrary/ADCPython` in the Windows ADC source. Python 3.7 or later is required. The runtime uses Python's standard library; no development or publishing tools are needed.

Run from this directory:

```sh
python examples/Example1_async.py
python examples/Example2_local.py
python examples/Example3_sync.py
python examples/Example4_sync_struct.py
```

Keep `examples/_common.py` and the sibling `advantech_adc/` directory in place. The helper imports this local module directly, so installing the package from PyPI is optional. Configure the PLC settings in the examples before running them; the examples can write PLC/local memory.

On Windows, matching x86/x64 DLLs are in `advantech_adc/library/` and are loaded automatically according to the Python process architecture.

On Linux, both C++ and Python use the downloadable libraries in `Linux/library/{x86,x64,arm64}/`. Python retains the upstream `/usr/lib` loading behavior and its x86/x64 selection. From this Python directory, install the matching pair, for example for x64:

```sh
sudo install -m 0644 ../../library/x64/libADCLibrary-x64.so /usr/lib/
sudo install -m 0644 ../../library/x64/libCmpPLCHandler-x64.so /usr/lib/
sudo ldconfig
```

The CODESYS projects are centralized at [`Codesys_Project/`](../../../Codesys_Project/), including `example.project` and `example_linux.project`. They are not duplicated inside the Python or C++ examples. See `API_GUIDE.md` for API usage and the root `docs/` directory for manuals. The local Python runtime's `LICENSE` and `NOTICE` are included.
