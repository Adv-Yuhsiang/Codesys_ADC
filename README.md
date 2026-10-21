# Codesys_ADC

Advantech Data Connect (ADC) libraries, examples and documents for accessing CODESYS PLC symbols and memory on Windows and Linux.

## Contents

| Directory | Contents |
|---|---|
| `Windows/examples/CPlusPlus/` | C++ projects, headers, import libraries and native DLLs |
| `Windows/examples/CSharp/` | C# examples and managed/native DLLs |
| `Windows/examples/CSharp_net8/` | .NET 8 examples and x86/x64 libraries |
| `Windows/examples/Python/` | Python testers and their library dependencies |
| `Linux/examples/CPlusPlus/` | C++ examples, headers, Makefile and x86/x64/arm64 shared libraries |
| `Linux/examples/Python/` | Python testers |
| `docs/` | Windows C++, Windows C# and Linux API manuals |

`sync-manifest.json` records the source commits, independent Windows DLL/Linux library versions, selected document versions and file checksums. Required libraries retain their paths relative to the examples. Configure the example/tester settings for your target PLC before running them.

## Windows

Open the solution/project in the corresponding example directory. Keep its `library/` directory in place. Python, the managed runtime and the native DLLs must use matching architectures. See the Python directory's README for prerequisites and test commands.

## Linux

Download both libraries for the platform running the application:

```text
libADCLibrary-<platform>.so
libCmpPLCHandler-<platform>.so
```

Available platforms are `x86`, `x64` and `arm64`. The files are in `Linux/examples/CPlusPlus/`; keep the matching pair together. Build the C++ examples on the corresponding machine, for example:

```sh
cd Linux/examples/CPlusPlus
make CPU=x64
```

Linux Python retains its `/usr/lib` loading paths. Install the matching libraries before using it, for example on x64:

```sh
sudo install -m 0644 Linux/examples/CPlusPlus/libADCLibrary-x64.so /usr/lib/
sudo install -m 0644 Linux/examples/CPlusPlus/libCmpPLCHandler-x64.so /usr/lib/
sudo ldconfig
```

The supplied Linux Python tester currently selects x86/x64. The ARM64 shared libraries are available for native clients. Consult each tester's README and the API manuals for usage. Linux validation includes library compilation, ELF architecture/API inspection and C++ example linking; PLC communication and ARM64 runtime execution require separate device testing. Libraries retain the upstream `-O0 -g` build settings.
