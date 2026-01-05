import network
import uasyncio as asyncio
import utime

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
        
    async def set_credentials(self, ssid, password):
        self.ssid = ssid
        self.password = password
        
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
                print(f"嘗試連線至 {self.ssid}...")
                self.wlan.connect(self.ssid, self.password)
                
                # 等待連線
                for _ in range(15): # 最多等待 15 秒
                    if self.wlan.isconnected():
                        self.state = WiFiState.CONNECTED
                        break
                    await asyncio.sleep(1)
                
                if self.state != WiFiState.CONNECTED:
                    print("連線超時，切換至 DISCONNECTED 狀態")
                    self.state = WiFiState.DISCONNECTED
            
            elif self.state == WiFiState.CONNECTED:
                if not self.wlan.isconnected():
                    print("連線丟失")
                    self.state = WiFiState.DISCONNECTED
            
            elif self.state == WiFiState.DISCONNECTED:
                # 這裡後續會加入自動重連邏輯
                await asyncio.sleep(5)
                self.state = WiFiState.CONNECTING
                
            await asyncio.sleep(0.5)

    async def run(self):
        """啟動 WiFi 管理器"""
        await self._update_state()