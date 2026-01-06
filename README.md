# Picore-W

Picore-W 是一個為 Raspberry Pi Pico 2 W (RP2350) 打造的基礎基礎設施專案，基於 MicroPython 開發。它提供了一個強韌且可重複使用的網路層，專注於 IoT 應用的連線可靠性。

## 核心特性

- **強韌的 WiFi 狀態機**：管理 WiFi 連線的完整生命週期（連線、斷線、重連、錯誤處理）。
- **智慧配網模式 (Smart Provisioning)**：當未偵測到連線設定時，自動開啟 AP 模式並提供網頁界面供使用者輸入 WiFi 資訊。
- **非阻塞設計**：採用 `uasyncio` 驅動，確保網路管理不會阻塞主應用程式邏輯。
- **自動重連**：自動偵測網路斷線並嘗試恢復連線。

---

## 快速開始 (Getting Started)

### 1. 環境需求
- Raspberry Pi Pico 2 W (RP2350)。
- 安裝有 MicroPython 韌體的設備。
- 開發工具：推薦使用 VS Code 搭配 **MicroPico** 擴充功能。

### 2. 安裝與執行
1. 將本儲存庫中的 `src/` 目錄下的所有檔案上傳至 Pico 的根目錄。
2. 重新啟動 Pico。
3. 如果是首次使用，Pico 會開啟一個名為 `Picore-W-Setup` 的 WiFi 熱點（預設密碼：`password123`）。
4. 使用手機或電腦連線至該熱點，瀏覽器應會自動彈出配網頁面（Captive Portal）。
5. 輸入您的 WiFi SSID 與密碼並點擊 Connect。裝置將儲存設定並自動重啟連網。

---

## 系統架構 (Architecture)

### WiFi 狀態機 (State Machine)
系統採用非同步狀態機管理網路狀態：
- **IDLE**: 初始狀態或等待指令。
- **CONNECTING**: 嘗試連線至已儲存的網路。
- **CONNECTED**: 已取得 IP，正常運作。
- **FAIL**: 連線失敗後的冷卻期，之後會自動重試。
- **AP_MODE**: 配網模式，啟動 DNS 劫持與 Web Server。

### 配網邏輯 (Provisioning Flow)
1. **檢查設定**：啟動時讀取 `wifi_config.json`。
2. **啟動熱點**：若無設定，啟動 AP 模式 (`network.AP_IF`)。
3. **DNS 劫持**：啟動簡易 DNS Server 將所有域名解析至 Pico (192.168.4.1)，實現強制門戶。
4. **設定儲存**：Web Server 接收 POST 請求，將 SSID/Password 寫入 Flash。
5. **重啟生效**：系統執行 `machine.reset()` 以確保硬體狀態乾淨地切換至連線模式。

---

## 授權 (License)
本專案採用 MIT 授權。
