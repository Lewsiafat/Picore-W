# Picore-W

Picore-W 是一個為 **Raspberry Pi Pico 2 W (RP2350)** 與 **Raspberry Pi Pico W (RP2040)** 打造的強韌基礎設施函式庫，基於 MicroPython 開發。它提供了一個穩定且高可用性的網路層，專為 IoT 應用設計。

## 核心特性

- **非同步狀態機**：使用 `uasyncio` 管理 WiFi 完整生命週期（連線、斷線、重連、錯誤處理）。
- **智慧配網模式 (Smart Provisioning)**：當未偵測到連線設定時，自動開啟 AP 模式並提供網頁界面。
- **事件驅動 API**：註冊回調函式監聽連線事件（`connected`、`disconnected`、`state_change`）。
- **運行時配置**：無需修改原始碼即可自訂超時、重試次數及 AP 設定。
- **非阻塞設計**：確保網路管理在背景執行，不會阻塞您的主應用程式邏輯。
- **自動恢復**：自動偵測網路斷線並嘗試恢復連線。

---

## 快速開始 (整合指引)

若要將 Picore-W 作為您專案的底層，請遵循以下步驟：

### 1. 上傳檔案
將 `src/` 目錄下的所有檔案上傳至 Pico 的**根目錄**。請確保包含 `templates/` 資料夾。

### 2. 基礎連線範例
使用以下最簡代碼將 WiFi 管理整合至您的應用程式：

```python
import uasyncio as asyncio
from wifi_manager import WiFiManager

async def main():
    # 1. 初始化 WiFiManager
    # 自動啟動背景連線邏輯或配網模式
    wm = WiFiManager()

    print("正在等待 WiFi 連線...")

    # 2. 等待直到連線成功
    while not wm.is_connected():
        await asyncio.sleep(1)

    print(f"已連線！IP 位址: {wm.get_config()[0]}")

    # 3. 您的應用程式邏輯
    while True:
        await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
```

### 3. 事件驅動範例
使用回調函式取代輪詢，實現更簡潔的架構：

```python
import uasyncio as asyncio
from wifi_manager import WiFiManager

async def main():
    connected = asyncio.Event()

    def on_connected(ip):
        print(f"已連線！IP: {ip}")
        connected.set()

    def on_disconnected():
        print("WiFi 連線中斷！")
        connected.clear()

    wm = WiFiManager()
    wm.on("connected", on_connected)
    wm.on("disconnected", on_disconnected)

    await connected.wait()  # 無需輪詢

    # 您的應用程式邏輯

if __name__ == "__main__":
    asyncio.run(main())
```

### 4. 自訂配置
在運行時覆蓋預設設定：

```python
wm = WiFiManager(
    max_retries=10,           # 連線嘗試次數
    connect_timeout=20,       # 每次嘗試的超時秒數
    ap_ssid="MyDevice-Setup", # 自訂 AP 名稱
    ap_password="SecurePass123!"
)
```

---

## 生命週期管理 (狀態機)

Picore-W 使用內部狀態機來追蹤網路狀態。您可以透過 `wm.get_status()` 或 `wm.get_status_name()` 獲取目前狀態。

| 狀態 | 數值 | 描述 |
| :--- | :--- | :--- |
| `WiFiState.IDLE` | 0 | 初始狀態或等待指令。 |
| `WiFiState.CONNECTING` | 1 | 正在嘗試加入 WiFi 網路。 |
| `WiFiState.CONNECTED` | 2 | 連線成功並已取得 IP。 |
| `WiFiState.FAIL` | 3 | 連線失敗。系統將進入冷卻期並重試。 |
| `WiFiState.AP_MODE` | 4 | 配網模式已啟動（熱點模式）。 |

```python
from constants import WiFiState

# 程式化取得狀態名稱
name = WiFiState.get_name(wm.get_status())  # "CONNECTED"
```

### 事件系統

註冊回調函式監聽狀態變化：

| 事件 | 參數 | 描述 |
| :--- | :--- | :--- |
| `connected` | `(ip_address)` | WiFi 連線建立。 |
| `disconnected` | 無 | WiFi 連線中斷。 |
| `state_change` | `(old_state, new_state)` | 任何狀態轉換。 |
| `ap_mode_started` | `(ap_ssid)` | AP 配網模式已啟動。 |
| `connection_failed` | `(retry_count)` | 達到最大重試次數，進入 FAIL 狀態。 |

### 錯誤處理與自動恢復
- **連線中斷**：若在 `CONNECTED` 狀態下斷線，管理員會自動切換回 `CONNECTING` 嘗試恢復連線。
- **重試機制**：系統會嘗試多次連線（可透過構造函數設定），若持續失敗則進入 `FAIL` 冷卻期。
- **AP 備援**：若無有效憑證，系統會安全地進入 `AP_MODE` 等待使用者輸入。

### 外部顯示器整合

取得 AP 憑證以顯示在外部螢幕（OLED、LCD 等）：

```python
def on_ap_started(ssid):
    # 取得 AP 配置用於顯示
    ap_ssid, ap_password, ap_ip = wm.get_ap_config()

    # 顯示在 OLED/LCD 上
    display.text(f"SSID: {ap_ssid}", 0, 0)
    display.text(f"Pass: {ap_password}", 0, 16)
    display.show()

wm.on("ap_mode_started", on_ap_started)

# 檢查是否處於 AP 模式
if wm.is_ap_mode():
    ssid, password, ip = wm.get_ap_config()
```

---

## 回到配網 (AP) 模式

如果您已經設定過裝置，但想要重新進入配網模式（例如更換網路），您可以使用提供的 `src/restore.py` 腳本：

1. 將 `src/restore.py` 上傳至您的 Pico。
2. 透過 REPL 或您的 IDE 執行它。

該腳本會刪除設定檔 (`wifi_config.json`) 並自動重啟裝置。

```python
# 亦可在 REPL 中手動執行：
import os, machine
try:
    os.remove('wifi_config.json')
except:
    pass
machine.reset()
```

---

## 除錯與疑難排解

若您在連線或配網時遇到問題：

1. **斷電重啟**：若網路堆疊似乎卡住，請拔掉 USB 線，等待 5-10 秒後再插回。冷啟動通常能解決硬體層級的掛起。
2. **韌體完整性**：確保您使用的是最新穩定版的 MicroPython 韌體。若行為不穩，請嘗試重新刷入韌體（必要時擦除 Flash）。
3. **模板路徑**：確保 `templates/` 資料夾與 `wifi_manager.py` 上傳至同一個目錄。
4. **訊號強度與供電**：確保 Pico 在路由器的有效範圍內，且供電穩定（AP 模式在高峰期耗電較大）。

---

## 架構與檔案說明

- **`wifi_manager.py`**：核心業務邏輯、狀態機與事件系統。
- **`config.py`**：預設設定（超時、重試次數、AP 名稱）。支援運行時覆蓋。
- **`constants.py`**：`WiFiState` 類別，包含狀態定義與工具方法。
- **`config_manager.py`**：處理版本化 JSON 設定的持久化讀寫，支援自動遷移。
- **`logger.py`**：輕量級日誌系統，支援全局與模組級別控制。
- **`provisioning.py`**：網頁式 WiFi 配網處理器。
- **`templates/`**：配網網頁界面的 HTML 檔案。

---

## 授權 (License)
本專案採用 MIT 授權。