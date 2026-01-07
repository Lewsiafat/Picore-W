# Spec: WiFiManager Decoupling & Memory Optimization

## Overview
本軌道的目標是將 `src/wifi_manager.py` 中的展示層（HTML 模板）與設定層（硬編碼常數）進行解耦。透過將大型字串移至外部檔案並將配置模組化，以減少系統常駐記憶體佔用，並提升客製化與維護的便利性。

## Functional Requirements
1. **展示層分離 (HTML Templates)**:
    - 建立 `src/templates/` 目錄。
    - 將 `PROVISIONING_HTML` 移至 `src/templates/provision.html`。
    - 將 `SUCCESS_HTML` 移至 `src/templates/success.html`。
    - 修改 `WiFiManager`，使其在需要時從檔案系統讀取這些 HTML，而非保留在記憶體常數中。
2. **配置模組化 (Constants & Config)**:
    - 建立 `src/constants.py`：存放 WiFi 狀態機常數（例如 `STATE_IDLE`, `STATE_CONNECTING` 等）。
    - 建立 `src/config.py`：存放 WiFi 預設配置常數（如 `MAX_RETRIES`, `AP_SSID`, `AP_PASSWORD` 等）。
    - 修改所有相關模組以引用這些新檔案。
3. **記憶體優化**:
    - 移除 `wifi_manager.py` 中所有冗餘的大型字串與硬編碼配置。

## Acceptance Criteria
- `src/wifi_manager.py` 程式碼行數顯著減少，且不再包含任何 HTML 標記。
- 裝置進入 AP 模式時，能成功從 `templates/` 讀取並顯示正確的配網頁面。
- 系統啟動時能正確讀取 `src/config.py` 中的預設值。
- 配網功能與連線流程維持正常運作，無功能倒退。

## Out of Scope
- 本軌道不涉及 `ConfigManager` (JSON 讀寫) 邏輯的變更。
- 不涉及 Web Server 核心解析邏輯的重構。
