# Spec: Versioning & Release Management Establishment

## Overview
本軌道的目標是建立正式的版號管理機制。透過建立 `CHANGELOG.md` 並更新開發工作流，確保專案的每一次重大變更都有跡可循，並符合語義化版本 (SemVer) 規範。

## Functional Requirements
1. **建立 CHANGELOG.md**:
    - 採用 "Keep a Changelog" 格式。
    - 記錄從 `v1.0.0` (核心功能) 到 `v1.1.0` (底層支援與文件) 的變更。
2. **建立正式標籤 v1.1.0**:
    - 使用標註標籤 (Annotated Tag) 記錄此次發佈。
3. **更新開發工作流 (workflow.md)**:
    - 加入 `Versioning & Release` 規範章節。
    - 明確規定標籤命名格式 (`vMAJOR.MINOR.PATCH`)。
    - 強制規定在 Track 結束時需同步更新 `CHANGELOG.md`。

## Acceptance Criteria
- 根目錄存在 `CHANGELOG.md`，內容包含 v1.0.0 與 v1.1.0 的紀錄。
- Git 標籤中存在 `v1.1.0`。
- `conductor/workflow.md` 已包含版本管理相關指引。

## Out of Scope
- 本軌道不修改任何 `src/` 目錄下的執行程式碼。
