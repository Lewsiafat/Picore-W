# AP Mode WiFi SSID 掃描功能

- **分支:** `feat/add-wifi-ssid-scan-result`
- **日期:** 2026-02-11

## 描述
在 AP mode 的 provisioning 網頁中新增 WiFi SSID 掃描結果列表。使用者可以重新整理掃描、點擊 SSID 自動填入表單，再輸入密碼完成設定。掃描期間顯示 loading 狀態，避免畫面看起來凍結。

## 任務清單
- [ ] `wifi_manager.py` — 將 `self.wlan` (STA_IF) 傳給 `ProvisioningHandler`，讓它能執行掃描
- [ ] `provisioning.py` — 新增 `/scan` GET route，呼叫 `wlan.scan()` 回傳 JSON（SSID、RSSI、加密類型），去重複並按 RSSI 排序
- [ ] `provisioning.py` — 新增 `_build_json_response()` 輔助方法，回傳 JSON content-type 的 HTTP response
- [ ] `templates/provision.html` — 新增「掃描 WiFi」按鈕和掃描結果列表區域
- [ ] `templates/provision.html` — 掃描進行中顯示 loading 指示器（spinner 或文字提示），避免畫面看似凍結
- [ ] `templates/provision.html` — 點擊 SSID 項目自動填入表單的 SSID 欄位
- [ ] `templates/provision.html` — 列表顯示 SSID 名稱和訊號強度指示
- [ ] 確認 AP mode 下 STA_IF 保持 `active(True)` 以支援掃描
