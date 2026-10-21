# ADCTester 運行步驟

ADCTester 統一使用 Python 測試程式，分成下列入口：

- `adc_tester.py` 與 `test_*.py`：透過 `ctypes` 直接測試 native C++ Library，支援 Windows/Linux。
- `adc_net8_tester.py`：透過 Python.NET/CoreCLR 測試 ADC.NET8 managed Library，支援 Windows x86/x64。

Python 測試的 PLC IP、帳號、密碼與 timeout 統一設定在 `config.py`。測試前請先依目標 PLC 修改設定。

## Python 直接測試 ADC.NET8

`adc_net8_tester.py` 透過 Python.NET/CoreCLR 直接載入 `ADCClassLibrary.dll`，會實際經過 ADC.NET8 managed wrapper、P/Invoke、marshaling 與 `ADC_FreeSymbolList`。每次執行只測試目前 Python process 的架構；Python、ADC.NET8 assembly 與 native `AdvHandler.dll` 必須使用相同架構。

先安裝 Python.NET：

```powershell
py -3 -m pip install pythonnet
```

使用 x86 Library 時需要 32-bit Python 與 x86 .NET 8 Runtime；使用 x64 Library 時需要 64-bit Python 與 x64 .NET 8 Runtime。測試程式不會自動切換 Python 版本。

建置對應平台的 ADC.NET8：

```powershell
dotnet build .\ADCLibrary\ADC.NET8\ADC.NET8\ADCClassLibrary.csproj -c Release -p:Platform=x64
dotnet build .\ADCLibrary\ADC.NET8\ADC.NET8\ADCClassLibrary.csproj -c Release -p:Platform=x86
dotnet build .\ADCTester\ManagedTestTypes\ADCManagedTestTypes.csproj -c Release
```

建置後會將 `ADCClassLibrary.dll`、PDB、XML 與測試用 `ADCManagedTestTypes.dll` 複製到 `ADCTester/library/x64` 或 `ADCTester/library/x86`。Library 路徑固定，因此不提供 `--managed-library`、`--native-dir`；保留 `--platform auto|x86|x64` 用來選擇並驗證目前 Python 架構。`auto` 會使用並顯示目前 Python process 的平台，不會啟動其他 Python。`ADCManagedTestTypes.dll` 只提供 Python.NET 關閉泛型方法所需的固定配置 struct 型別，不包含 C# 測試程序；實際測試仍全部由 Python 執行。

```powershell
# 使用目前 Python 架構並在測試開頭顯示 x86 或 x64
py -3 .\ADCTester\adc_net8_tester.py --test all --platform auto

# 明確驗證目前是 32-bit Python；不符合時直接回報錯誤
py -3-32 .\ADCTester\adc_net8_tester.py --test all --platform x86

# 明確驗證目前是 64-bit Python；不符合時直接回報錯誤
py -3-64 .\ADCTester\adc_net8_tester.py --test all --platform x64
```

執行 managed tests：

```powershell
# 非同步 Symbol 寫入、讀回與比對
py -3 .\ADCTester\adc_net8_tester.py --test async-symbols

# 非同步 Memory 寫入、讀回與比對
py -3 .\ADCTester\adc_net8_tester.py --test async-memory

# 同步 Symbol 寫入、讀回與比對
py -3 .\ADCTester\adc_net8_tester.py --test sync-symbols

# 同步 Memory 寫入、讀回、比對與邊界測試
py -3 .\ADCTester\adc_net8_tester.py --test sync-memory

# Local Memory 寫入、讀回與比對
py -3 .\ADCTester\adc_net8_tester.py --test local-memory

# Symbol List；managed wrapper 會在 finally 呼叫 ADC_FreeSymbolList
py -3 .\ADCTester\adc_net8_tester.py --test symbol-list

# 測試 polling 與同步連線共用 PLC Handler
py -3 .\ADCTester\adc_net8_tester.py --test mixed-plc

# Port 生命週期測試
py -3 .\ADCTester\adc_net8_tester.py --test mem-port

# 其他公開 API
py -3 .\ADCTester\adc_net8_tester.py --test other

# 執行全部測試；會直接寫入 Symbol、Memory 與 Local Memory
py -3 .\ADCTester\adc_net8_tester.py --test all

# 額外寫入、驗證並還原完整 2 MB Modbus Memory
py -3 .\ADCTester\adc_net8_tester.py --test sync-memory --full-memory
```

原本的 `adc_tester.py` 仍直接使用 `ctypes` 測試 native C++ Library；`adc_net8_tester.py` 則專門測試 ADC.NET8 managed Library。兩者使用相同的測試分類與讀寫資料；ADC.NET8 wrapper 未公開的 API 不列入 managed test。

> `--test all` 不是唯讀測試，會改寫測試 PLC 的 Symbol、Modbus Memory 與 Local Memory。請勿在生產用 PLC 上執行。

## CODESYS RTE 準備

1. 將 `CODESYS/PLC_PRG.st` 的變數加入 RTE 專案。
2. 在 Symbol Configuration 啟用 `PLC_PRG` 中以 `ADC_Test_` 開頭的變數。
3. 確認 Port 503 的 Modbus TCP Memory 存取已啟用。
4. 下載專案並讓 PLC 進入 RUN。

測試涵蓋 BOOL、SINT、USINT/BYTE、INT、UINT/WORD、DINT、UDINT/DWORD、LINT、ULINT/LWORD、REAL 與 LREAL；不測試時間與字串類型。每個基本型別都會先呼叫原本的 `byte[]` API，再呼叫 `Read/WriteSymbolValue<T>`、`Read/WriteMultipleMemoryValue<T>` 或 Local Memory 泛型 API，兩者都執行寫入、讀回與比對。`async-symbols` 與 `sync-symbols` 也會分別以原始 byte API 和泛型 API 測試 `ADC_TEST_MARSHAL_STRUCT`，其內容包含 BOOL、固定長度 STRING、DINT 與 struct 內固定長度 LREAL array。既有 `ADC_Test_Struct` 與 `ADC_Test_Array` 原始 byte-range 測試仍保留。

## Windows

1. 安裝與 `AdvHandler.dll` 相同架構的 Python 3。
2. 建置 `AdvHandlerLibrary.sln`，例如 `Debug|x64`。
3. 目前輸出的 `AdvHandler.dll` 已包含 PLC Handler、CmpPLCHandler 與 ADSMOD 所需程式，不需另外部署對應 DLL。Debug build 需要 Visual C++ Debug Runtime；Release build 需要一般 Visual C++ Runtime。
4. 在 repository 的 `ADC_Source` 目錄執行下列命令。

## 測試分類

```powershell
# 1. 非同步型 Symbols
python .\ADCTester\adc_tester.py --test async-symbols

# 2. 非同步型 Memory
python .\ADCTester\adc_tester.py --test async-memory

# 3. 同步型 Symbols
python .\ADCTester\adc_tester.py --test sync-symbols

# 4. 同步型 Memory（包含各型別與重要 Modbus 邊界）
python .\ADCTester\adc_tester.py --test sync-memory

# 5. Local Memory；必須在可存取 RTE shared memory 的環境執行
python .\ADCTester\adc_tester.py --test local-memory

# 6. 其他 API、版本、connection 顯示及錯誤參數
python .\ADCTester\adc_tester.py --test other

# 依序執行全部分類
python .\ADCTester\adc_tester.py --test all
```

`adc_tester.py` 的 native Library 路徑固定，不提供 `--library` 或 `--dependency-dir`。`--platform auto|x86|x64` 的行為與 managed tester 相同：`auto` 使用並顯示目前 Python process 架構；明確指定的平台與 Python 架構不同時會直接回報錯誤。Windows 固定載入 `ADCTester/library/x86/AdvHandler.dll` 或 `ADCTester/library/x64/AdvHandler.dll`。

## 完整 Modbus 空間測試

```powershell
python .\ADCTester\adc_tester.py --test sync-memory --full-memory
```

此模式涵蓋 byte offset `0` 到 `0x1FFFFF`：每次備份 4096 bytes、寫入 pattern、讀回比對，然後立即還原原始內容。

警告：這個測試會實際暫時改寫完整 2 MB `%M` 空間。只能在允許測試的 PLC 上執行；測試過程若斷電、網路中斷或程序被終止，當前 block 可能來不及還原。

## Linux 目標

測試程式只使用 Python 標準函式庫，可搬到 Linux 執行。Linux 依目前 Python process 架構從下列固定路徑載入 Library：

- x86：`/usr/lib/libADCLibrary-x86.so`
- x64：`/usr/lib/libADCLibrary-x64.so`

1. 將 `libADCLibrary-x86.so`、`libADCLibrary-x64.so` 安裝到 `/usr/lib`。
2. 確認選擇的 Library 架構與 Linux Python／作業系統一致。
3. 使用 `ldd /usr/lib/libADCLibrary-x86.so` 或 `ldd /usr/lib/libADCLibrary-x64.so` 確認相依套件皆可找到。
4. 在 `config.py` 設定 PLC IP、帳號與密碼。
5. 使用與 Windows 相同的測試分類：

```bash
python3 ./ADCTester/adc_tester.py --test async-symbols
python3 ./ADCTester/adc_tester.py --test async-memory
python3 ./ADCTester/adc_tester.py --test sync-symbols
python3 ./ADCTester/adc_tester.py --test sync-memory
python3 ./ADCTester/adc_tester.py --test local-memory
python3 ./ADCTester/adc_tester.py --test other
python3 ./ADCTester/adc_tester.py --test all --platform auto
```

完整 Modbus 空間測試也使用相同參數：

```bash
python3 ./ADCTester/adc_tester.py --test sync-memory --full-memory
```

Linux 額外相依 `.so` 應透過系統 library path、`ldconfig` 或 `LD_LIBRARY_PATH` 提供。

## ADC_GetSymbolList 測試

連線設定沿用 `config.py`。測試程式會一次取得 Symbol 名稱陣列及數量、列出所有名稱，並於結束前釋放陣列。

```powershell
py .\ADCTester\test_symbol_list.py
```

也可透過統一 Tester 執行；`--test all` 也會包含此項：

```powershell
py .\ADCTester\adc_tester.py --test symbol-list
```

Linux 單項測試程式也會依目前 Python 架構載入 `/usr/lib/libADCLibrary-x86.so` 或 `/usr/lib/libADCLibrary-x64.so`：

```bash
python3 ./ADCTester/test_symbol_list.py
```

Windows `ADC_GetSymbolList` 回傳的陣列由 Library 配置；C/C++ 與 C# 呼叫端必須使用 `ADC_FreeSymbolList` 釋放，確保配置與釋放發生於相同的 C runtime。目前 Linux Library 尚未加入此 API，因此既有跨平台 Python 測試仍依平台使用對應的 C runtime 釋放。

每個項目使用 `ADC_SYMBOL_INFO`，包含 `szName`（Symbol 名稱）、`szType`（PLC Handler `pszType` 的類型名稱副本）與 `ulSize`（資料大小，單位為 byte）。測試輸出會同時顯示這三項資訊。

`CODESYS/PLC_PRG.st` 另外提供 Symbol List 專用的複合型別測試資料：

- `ADC_TEST_STRUCT`：由三個 32-bit 欄位組成的自訂 STRUCT。
- `PLC_PRG.ADC_Test_Struct`：`ADC_TEST_STRUCT` 變數；PLC Handler 對父項目的類型名稱回傳 `DATA`，大小為 12 bytes，並另外列出三個成員 Symbol。
- `PLC_PRG.ADC_Test_Array`：`ARRAY[0..3] OF DINT`，預期大小為 16 bytes。

請將 STRUCT 型別及兩個變數加入 CODESYS 專案，並在 Symbol Configuration 中啟用 `ADC_Test_Struct` 與 `ADC_Test_Array`。`symbol-list` 測試會檢查兩個父項目、三個 STRUCT 成員及四個 ARRAY 元素的名稱、類型名稱和大小。

## PLC Handler 同步／非同步共享連線測試

此項與 Symbol List 測試分開，驗證同步連線可直接交由 polling 共用、polling 執行時釋放同步使用權不會中斷 sector，以及同步端仍持有連線時停止 polling 不會斷開 PLC Handler。Modbus 同步與非同步 Client 仍維持彼此獨立。

```powershell
py .\ADCTester\adc_tester.py --test mixed-plc
```

也可單獨執行：

```powershell
py .\ADCTester\test_mixed_plc.py
```

## Memory 連線 Port 設定測試

`ADC_SetMemConnectPort` 必須在 `ADC_NewDataConnect` 後、同步 Modbus 斷線且 polling 停止時呼叫。未設定時預設為 503。

```powershell
py .\ADCTester\adc_tester.py --test mem-port
```

也可單獨執行：

```powershell
py .\ADCTester\test_mem_port.py
```

## Windows %ML Memory 測試

Windows Library 支援 `%MLn`（byte offset = n × 8）。同步、非同步及 Local Memory 共用直接從 Linux ADCTester 複製的四組案例：`%ML128` LINT、`%ML129` LWORD、`%ML130` LREAL、`%ML132` 兩筆 ULINT。

```powershell
py -3 .\ADCTester\adc_tester.py --test sync-memory
py -3 .\ADCTester\adc_tester.py --test async-memory
py -3 .\ADCTester\adc_tester.py --test local-memory
```

請使用新建置的 Windows AdvHandler.dll，並將 `CODESYS/PLC_PRG.st` 的對應變數加入測試 PLC。Local Memory 需要在提供 shared memory 的 Windows RTE 環境執行。
