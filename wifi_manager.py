import network
import uasyncio as asyncio
import utime
import random

class WiFiState:
    IDLE = "IDLE"
    CONNECTING = "CONNECTING"
    CONNECTED = "CONNECTED"
    DISCONNECTED = "DISCONNECTED"
    ERROR = "ERROR"
    PROVISIONING = "PROVISIONING"

class WiFiManager:
    def __init__(self):
        self.wlan = network.WLAN(network.STA_IF)
        self.state = WiFiState.IDLE
        self.ssid = None
        self.password = None
        self.reconnect_delay = 5
        self.max_reconnect_delay = 300
        self.reconnect_attempts = 0
        self.max_attempts = 10
        
    async def set_credentials(self, ssid, password):
        self.ssid = ssid
        self.password = password
        self.reconnect_attempts = 0
        self.reconnect_delay = 5
        
    def get_state(self):
        return self.state

    async def _update_state(self):
        """核心狀態機迴圈"""
        while True:
            if self.state == WiFiState.IDLE:
                if self.ssid:
                    self.state = WiFiState.CONNECTING
            
            elif self.state == WiFiState.CONNECTING:
                self.wlan.active(True)
                print(f"嘗試連線至 {self.ssid} (第 {self.reconnect_attempts + 1} 次)...")
                self.wlan.connect(self.ssid, self.password)
                
                # 等待連線
                connected = False
                for _ in range(15): 
                    if self.wlan.isconnected():
                        connected = True
                        break
                    await asyncio.sleep(1)
                
                if connected:
                    print("連線成功！")
                    self.state = WiFiState.CONNECTED
                    self.reconnect_attempts = 0
                    self.reconnect_delay = 5
                else:
                    self.reconnect_attempts += 1
                    print(f"連線失敗。")
                    if self.reconnect_attempts >= self.max_attempts:
                        self.state = WiFiState.ERROR
                    else:
                        self.state = WiFiState.DISCONNECTED
            
            elif self.state == WiFiState.CONNECTED:
                if not self.wlan.isconnected():
                    print("連線丟失，切換至 DISCONNECTED 狀態")
                    self.state = WiFiState.DISCONNECTED
            
            elif self.state == WiFiState.DISCONNECTED:
                # 指數退避邏輯
                delay = self.reconnect_delay + random.randint(0, 5)
                print(f"等待 {delay} 秒後嘗試重連...")
                await asyncio.sleep(delay)
                
                # 增加下次延遲時間
                self.reconnect_delay = min(self.reconnect_delay * 2, self.max_reconnect_delay)
                self.state = WiFiState.CONNECTING
            
            elif self.state == WiFiState.ERROR:
                # 在錯誤狀態下，可以選擇等待更長時間或等待使用者介入
                await asyncio.sleep(60)
                # 嘗試重設重連計數並重新開始
                # self.reconnect_attempts = 0
                # self.state = WiFiState.CONNECTING
                
            await asyncio.sleep(0.5)

    async def run(self):
        """啟動 WiFi 管理器"""
        await self._update_state()
