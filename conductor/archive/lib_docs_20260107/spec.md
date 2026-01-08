# Spec: Library Integration Support & Multilingual Documentation

## Overview
本軌道的目標是將 Picore-W 轉化為一個易於被其他專案引用的「底層模組」。我們將透過提供精簡的運行範例、詳細的串接文件以及多語言支援，降低開發者的整合門檻。

## Functional Requirements
1. **精簡運行範例**:
    - 建立 `examples/wifi_connect.py`。
    - 實作最少代碼量且可運行的 `uasyncio` 連線範例。
    - 範例需展示如何初始化 `WiFiManager` 並等待連線成功。
2. **多語言文件化**:
    - 將目前的 `README.md` 重新命名為 `README.zh-TW.md`。
    - 撰寫全新的英文版本 `README.md`。
3. **完善串接指引 (兩份 README 均需包含)**:
    - **快速串接 (Integration)**：使用 `examples/wifi_connect.py` 的代碼作為範例。
    - **生命週期管理**：解釋狀態機各個狀態 (IDLE, CONNECTED, AP_MODE 等) 的意義。
    - **異常處理**：說明當連線失敗或進入配網模式時，主程式應如何應對。
    - **架構說明**：解釋 `src/config.py` (預設值) 與 `src/constants.py` (狀態定義) 的角色。

## Acceptance Criteria
- `examples/wifi_connect.py` 檔案存在，且邏輯正確。
- 根目錄存在 `README.md` (EN) 與 `README.zh-TW.md` (CN)。
- 文件中包含明確的狀態碼說明與整合步驟。
- 使用者只需閱讀文件並參考範例，即可在 5 分鐘內將 Picore-W 整合至其專案。

## Out of Scope
- 本軌道不涉及 `wifi_manager.py` 的邏輯修改。
- 不涉及新的配網網頁開發。
