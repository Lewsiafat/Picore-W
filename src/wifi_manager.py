import network
import uasyncio as asyncio
import time

# WiFi Connection States
STATE_IDLE = 0
STATE_CONNECTING = 1
STATE_CONNECTED = 2
STATE_FAIL = 3

class WiFiManager:
    """
    Manages the WiFi connection using the ESP32/Pico W 'network' module.
    Implements an asynchronous State Machine to handle connection in the background.
    """
    def __init__(self):
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        
        # State Machine variables
        self._state = STATE_IDLE
        self._target_ssid = None
        self._target_password = None
        
        # Start the background task
        asyncio.create_task(self._run_state_machine())

    async def _run_state_machine(self):
        """
        The core loop of the WiFi Manager. 
        Monitors state and transitions accordingly.
        """
        print("WiFiManager: State Machine Started")
        while True:
            if self._state == STATE_IDLE:
                # Do nothing, wait for command
                await asyncio.sleep(1)
                
            elif self._state == STATE_CONNECTING:
                await self._handle_connecting()
                
            elif self._state == STATE_CONNECTED:
                await self._handle_connected()
                
            elif self._state == STATE_FAIL:
                # In basic implementation, just wait or reset to IDLE manually
                # Future: Auto-reconnect logic goes here
                await asyncio.sleep(1)
                
            # Yield to other tasks
            await asyncio.sleep(0.1)

    async def _handle_connecting(self):
        print(f"WiFiManager: Connecting to {self._target_ssid}...")
        self.wlan.connect(self._target_ssid, self._target_password)
        
        # Wait for connection or failure (timeout handled by simple loop for now)
        max_wait = 15 # seconds
        while max_wait > 0:
            status = self.wlan.status()
            
            if self.wlan.isconnected():
                print("WiFiManager: Connection Successful!")
                self._state = STATE_CONNECTED
                return
            
            if status == network.STAT_CONNECT_FAIL or status == network.STAT_WRONG_PASSWORD or status == network.STAT_NO_AP_FOUND:
                print(f"WiFiManager: Connection Failed (Status: {status})")
                self._state = STATE_FAIL
                return
            
            max_wait -= 1
            await asyncio.sleep(1)
            
        print("WiFiManager: Connection Timed Out")
        self._state = STATE_FAIL

    async def _handle_connected(self):
        # Monitor connection health
        if not self.wlan.isconnected():
            print("WiFiManager: Connection Lost!")
            self._state = STATE_FAIL # Or back to CONNECTING if auto-reconnect
        else:
            await asyncio.sleep(2) # Check every 2 seconds

    def connect(self, ssid, password):
        """
        Public API to request a connection.
        """
        self._target_ssid = ssid
        self._target_password = password
        self._state = STATE_CONNECTING

    def disconnect(self):
        """Disconnect from the current network."""
        if self.wlan.isconnected():
            self.wlan.disconnect()
        self._state = STATE_IDLE

    def is_connected(self):
        return self._state == STATE_CONNECTED

    def get_status(self):
        return self._state
        
    def get_config(self):
        return self.wlan.ifconfig()