# Codesys_ADC

Advantech Data Connect (ADC) libraries, examples and documents for accessing CODESYS PLC symbols and memory on Windows and Linux.

## Contents

```text
Codesys_Project/
  example.project
  example_linux.project
docs/
Windows/examples/
  CPlusPlus/
  CSharp_net8/
  Python/
    examples/
    advantech_adc/library/{x86,x64}/
Linux/
  examples/
    CPlusPlus/
    Python/
      examples/
      advantech_adc/
  library/
    x86/
    x64/
    arm64/
```

Windows provides C++, .NET 8 C# and Python examples. Both platforms' Python examples, helper files and runtime modules come from `ADCLibrary/ADCPython` in the Windows ADC source. Keep each Python directory's `examples/` and `advantech_adc/` directories together. Python 3.7 or later is required; the local runtime uses the standard library and does not require installation from PyPI. See each Python directory's README and `API_GUIDE.md`.

`sync-manifest.json` records source commits, independent native-library versions, Python source location, selected document versions and SHA256 checksums. Configure the examples for your target PLC before running them.

## Windows

Open the C++ or .NET 8 solution/project in its example directory. Keep the native/import libraries in place. Python uses the matching DLL in `advantech_adc/library/{x86,x64}/` according to the Python process architecture. Run Python examples from `Windows/examples/Python`, for example:

```sh
python examples/Example1_async.py
```

## Shared Linux libraries

Both C++ and Python use the libraries distributed once under `Linux/library/<platform>/`:

```text
libADCLibrary-<platform>.so
libCmpPLCHandler-<platform>.so
```

Available platforms are x86, x64 and arm64. Keep the matching pair together. The C++ Makefile uses `../../library/$(CPU)` and a relative runtime search path:

```sh
cd Linux/examples/CPlusPlus
make CPU=x64
```

Python retains its original `/usr/lib` loading paths. From the repository root, install the matching pair for the Python process architecture, for example on x64:

```sh
sudo install -m 0644 Linux/library/x64/libADCLibrary-x64.so /usr/lib/
sudo install -m 0644 Linux/library/x64/libCmpPLCHandler-x64.so /usr/lib/
sudo ldconfig
cd Linux/examples/Python
python3 examples/Example1_async.py
```

The Python runtime currently selects x86/x64; ARM64 libraries are also provided for native clients. Library compilation, architecture/API checks, C++ linking with the distributed directory layout and Linux x64 Python binding/version checks are validated. PLC communication and ARM64 runtime execution require separate device testing. Linux native libraries retain the upstream `-O0 -g` settings.

## CODESYS projects and manuals

Open `Codesys_Project/example.project` or `Codesys_Project/example_linux.project` in CODESYS, configure the target device, then download/run the application. These two files come from the Windows C++ example directory and are not duplicated inside other example directories. The Windows C++, Windows C# API and Linux manuals are in `docs/` with version-free filenames.
