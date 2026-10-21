# Linux ADC Library 測試程式

以 Windows `ADC_Source/ADCTester` 的 native Python 測試程式為基礎複製，保留原本九類測試與案例，再增加 `%ML`。不包含 ADC.NET8 測試器。本目錄可直接複製到執行機器，不需要 Library 原始碼、編譯器或 pip 套件；需要 Python 3.8 以上。

## 動態庫與設定

測試器依 **執行 Python 的位元數** 固定載入：

- 64 位元：`/usr/lib/libADCLibrary-x64.so`
- 32 位元：`/usr/lib/libADCLibrary-x86.so`

Library 必須是包含新同步 API 與 `ADC_FreeSymbolList` 的版本。安裝相同架構的 `libCmpPLCHandler-x64.so` 或 `libCmpPLCHandler-x86.so` 等相依動態庫至系統 loader 可找到的位置。Python 與 Library 架構必須相符；選擇依據是測試程式的執行機器，與遠端 PLC 的架構無關。

在編譯機器建置 Library，將產出的動態庫安裝到執行機器，再複製整個 `ADCTester/`。不要將尚未更新的舊版動態庫當成新版本部署。

修改 `config.py` 的 `PLC_IP`、`PLC_USERNAME`、`PLC_PASSWORD`。原版設定值僅為沿用的測試設定，請填入實際 PLC 資料。複製至 PLC 本機執行時 IP 可設為 `127.0.0.1`；另一台 Linux 機器連線測試時填入 PLC 的 IP。

PLC 請準備 `CODESYS/PLC_PRG.st`：將 TYPE 定義建成 DUT，PROGRAM 放入 PLC_PRG，於 Symbol Configuration 開放對應變數與結構／陣列的讀寫存取。測試沿用 Windows 的 little-endian 資料布局。PLC 循環邏輯不要持續覆寫這些測試值；Memory 測試需要對應的 Modbus 服務（原版 Port 503）。

## 執行

在 PLC Linux 本機，執行全部九類測試：

```bash
cd ADCTester
python3 adc_tester.py --test all --mode local
```

在另一台 Linux 機器連線到 PLC（先修改 `config.py`）：

```bash
python3 adc_tester.py --test all --mode remote
```

remote 模式明確跳過 `local-memory`，因為 Local API 只存取執行機器的共享記憶體，無法透過 IP 存取遠端 PLC。要涵蓋全部 API，仍須在 PLC 本機執行 Local Memory 測試：

```bash
python3 adc_tester.py --test local-memory --mode local
```

Local Memory 執行前檢查 `/dev/shm/advModbusShm` 存在、至少 2 MiB 且可讀寫，避免 Library 自行建立空共享記憶體而誤判實機測試成功。仍須確認 RTE 正在使用該共享記憶體。

單項測試與選擇架構：

```bash
python3 adc_tester.py --test sync-memory --platform x64
python3 adc_tester.py --test sync-memory --full-memory
python3 adc_tester.py --help
```

`--platform x86` 必須搭配 32 位元 Python；參數不會轉換 Python 架構。未指定 `--mode` 時預設 local，與 Windows `all` 保留全部分類的行為一致。

## 保留的測試項目

| 名稱 | 內容 |
| --- | --- |
| async-symbols | Symbol sector、基本型別、非同步讀寫與 callback、polling、priority |
| async-memory | Memory sector、single／multiple 非同步讀寫、callback、B/W/D 與新增 L |
| sync-symbols | 基本型別、STRUCT、ARRAY 同步讀寫 |
| sync-memory | B/W/D 與新增 L 同步讀寫、原有首尾／bank 邊界、選用完整 2 MiB 測試 |
| local-memory | 本機 single／multiple Memory 讀寫、B/W/D 與新增 L |
| symbol-list | 列舉名稱／型別／大小、STRUCT／ARRAY 與其成員、釋放清單 |
| mixed-plc | 同步連線與 polling 共用連線的生命週期 |
| mem-port | Port 參數、連線與 polling 狀態限制 |
| other | 版本、初始化、連線顯示與原有錯誤碼檢查 |

新增 `%ML128` LINT、`%ML129` LWORD、`%ML130` LREAL、`%ML132` 兩個 ULINT，共用於同步、非同步與 Local Memory 測試。`%MLn` 對應 byte offset `n * 8`，multiple 的單位是 8 bytes；PLC 範例同步增加對應宣告。原有 CASES 不變。

保留 Windows 原版寫入行為：一般資料案例會留下測試值；原版邊界與 `--full-memory` 測試有備份還原。完整 2 MiB 測試會寫入整個 Memory 區，應使用測試 PLC；程序中断時無法保證還原。

Linux 適配：`long`／`unsigned long` 使用 `ctypes.c_long`／`ctypes.c_ulong`，配合 Linux 原生 ABI；Symbol List 改由 `ADC_FreeSymbolList` 釋放。測試涵蓋 header 的 31 個公開 C API。另外依 Windows 測試流程直接綁定並呼叫 `ADC_DelSymdataSector`／`ADC_DelMemdataSector`。Linux 已在這兩個函式定義補上 `extern "C"`，header 維持不公開；它們不再 SKIP。測試器啟動時要求全部 33 個匯出函式，必須部署更新後的 Library。

測試失敗回傳非零 exit code；`all` 的個別案例失敗會列出摘要。完成訊息僅表示未跳過的項目通過，請同時檢查 SKIP 輸出。實際 PLC 通訊與共享記憶體測試仍須在目標機器驗證。

## 實機問題修正（2026-10-08）

- `ADC_Test_Struct` 接受 Runtime 回傳的 `DATA` 或 `ADC_TEST_STRUCT`，仍檢查 12-byte 大小及成員型別／大小。
- Local Memory 前置檢查會分別報告不存在、大小不足或讀寫權限不足。在 PLC 本機以 `ls -l /dev/shm/advModbusShm` 確認；不要自行建立空檔來略過檢查。遠端測試使用 `--mode remote`。
- 裝置名稱／Target／Vendor 資訊改以 SDK UTF-16 轉 UTF-8 輸出，不再將 SDK 字串轉型成 `wchar_t*` 傳給 Linux libc `%ls`。此項需要重新部署 Library；只更新 Python 檔案無法修正。終端機需使用 UTF-8。
