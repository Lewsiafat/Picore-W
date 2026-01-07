# Spec: Project Maintenance & Release Preparation

## Overview
本軌道的目標是整理專案環境、完善文件說明，並建立正式的發佈流程（版本系統與遠端同步），為專案的長期維護與分享做好準備。

## Functional Requirements
1. **環境清理 (.gitignore)**:
    - 建立 `.gitignore` 檔案。
    - 排除 `.vscode/`, `.micropico` 等編輯器設定。
    - 排除 `.DS_Store` 等作業系統雜訊。
    - 排除 `wifi_config.json` 等機密連線資訊。
2. **撰寫 README.md**:
    - 包含 **快速開始 (Getting Started)**：指引使用者如何設定環境與執行專案。
    - 包含 **系統架構 (Architecture)**：解釋 WiFi 狀態機與 AP 配網模式的運作邏輯。
3. **建立版號系統**:
    - 採用 **語義化版本 (SemVer)** 規範。
    - 為目前穩定的功能建立第一個 Git Tag (例如 `v1.0.0`)。
4. **遠端同步 (Force Push)**:
    - 清理遠端廢棄版本。
    - 將目前的本機穩定狀態強制推送到遠端 `main` 分支。

## Acceptance Criteria
- 執行 `git status` 時，不應再看到 `.vscode` 或 `wifi_config.json` 等被忽略的檔案。
- 專案根目錄存在完善的 `README.md`。
- Git 歷史中存在 `v1.0.0` 標籤。
- 遠端儲存庫與本機狀態完全一致。

## Out of Scope
- 本軌道不涉及程式碼邏輯重構 (Refactoring)。
- 不涉及新的功能開發。
