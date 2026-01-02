import network
import utime

def connect_wifi(ssid, password, timeout=10):
    """
    建立基礎 WiFi 連線。
    這是為了後續狀態機開發所準備的基礎邏輯。
    """
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print(f"正在連線至 {ssid}...")
        wlan.connect(ssid, password)
        
        # 等待連線或超時
        start_time = utime.time()
        while not wlan.isconnected() and (utime.time() - start_time) < timeout:
            utime.sleep(1)
            
    if wlan.isconnected():
        print(f"連線成功！IP: {wlan.ifconfig()[0]}")
        return True
    else:
        print("連線失敗或超時。")
        return False
