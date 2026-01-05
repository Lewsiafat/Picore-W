import network
import uasyncio as asyncio
import time

# --- Configuration Constants ---
class WiFiConfig:
    # Maximum number of connection attempts before entering FAIL state
    MAX_RETRIES = 5
    
    # Time (seconds) to wait for connection per attempt
    CONNECT_TIMEOUT = 15
    
    # Time (seconds) to wait between retries in CONNECTING state
    RETRY_DELAY = 2
    
    # Time (seconds) to wait in FAIL state before trying again (Auto-recovery)
    FAIL_RECOVERY_DELAY = 30
    
    # Interval (seconds) to check connection health in CONNECTED state
    HEALTH_CHECK_INTERVAL = 2

# --- State Constants ---
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
        self._retry_count = 0
        
        # Start the background task
        asyncio.create_task(self._run_state_machine())

    async def _run_state_machine(self):
        """
        The core loop of the WiFi Manager. 
        Monitors state and transitions accordingly.
        """
        print("WiFiManager: State Machine Started")
        while True:
            try:
                if self._state == STATE_IDLE:
                    await asyncio.sleep(1)
                    
                elif self._state == STATE_CONNECTING:
                    await self._handle_connecting()
                    
                elif self._state == STATE_CONNECTED:
                    await self._handle_connected()
                    
                elif self._state == STATE_FAIL:
                    await self._handle_fail()
                    
            except Exception as e:
                print(f"WiFiManager: Critical Error in State Machine: {e}")
                await asyncio.sleep(5)
            
            # Yield to other tasks
            await asyncio.sleep(0.1)

    async def _handle_connecting(self):
        print(f"WiFiManager: Connecting to {self._target_ssid} (Attempt {self._retry_count + 1}/{WiFiConfig.MAX_RETRIES})...")
        
        # Trigger connection
        self.wlan.connect(self._target_ssid, self._target_password)
        
        # Wait for connection or failure
        start_time = time.time()
        while (time.time() - start_time) < WiFiConfig.CONNECT_TIMEOUT:
            if self.wlan.isconnected():
                print("WiFiManager: Connection Successful!")
                self._state = STATE_CONNECTED
                self._retry_count = 0 # Reset retries on success
                return
            
            status = self.wlan.status()
            # If explicit failure detected, break early (don't wait full timeout)
            # Note: STAT_WRONG_PASSWORD might be tricky on some firmwares, but trying to catch it.
            if status == network.STAT_CONNECT_FAIL or status == network.STAT_NO_AP_FOUND or status == network.STAT_WRONG_PASSWORD:
                print(f"WiFiManager: Connection Failed explicitly (Status: {status})")
                break
                
            await asyncio.sleep(0.5)
            
        # If we get here, connection failed or timed out
        self._retry_count += 1
        
        if self._retry_count >= WiFiConfig.MAX_RETRIES:
            print("WiFiManager: Max retries reached. Entering FAIL state.")
            self._state = STATE_FAIL
        else:
            print(f"WiFiManager: Retrying in {WiFiConfig.RETRY_DELAY}s...")
            self.wlan.disconnect() # Reset interface
            await asyncio.sleep(WiFiConfig.RETRY_DELAY)
            # Stay in CONNECTING state to loop again

    async def _handle_connected(self):
        # Monitor connection health
        if not self.wlan.isconnected():
            print("WiFiManager: Connection Lost! Attempting to reconnect...")
            self.wlan.disconnect()
            self._retry_count = 0 # Reset retries for a fresh start
            self._state = STATE_CONNECTING
        else:
            await asyncio.sleep(WiFiConfig.HEALTH_CHECK_INTERVAL)

    async def _handle_fail(self):
        """
        Handle the FAIL state. 
        Wait for a cooldown period then try to auto-recover (go back to CONNECTING).
        """
        print(f"WiFiManager: In FAIL state. Waiting {WiFiConfig.FAIL_RECOVERY_DELAY}s before auto-recovery...")
        
        # Wait for recovery delay
        # We check repeatedly to allow manual override (e.g. user calls connect() with new creds)
        for _ in range(WiFiConfig.FAIL_RECOVERY_DELAY):
            if self._state != STATE_FAIL:
                return # State changed externally (e.g. by connect())
            await asyncio.sleep(1)
            
        print("WiFiManager: Attempting Auto-Recovery...")
        self._retry_count = 0
        self._state = STATE_CONNECTING

    def connect(self, ssid, password):
        """
        Public API to request a connection.
        """
        self._target_ssid = ssid
        self._target_password = password
        self._retry_count = 0
        self._state = STATE_CONNECTING

    def disconnect(self):
        """Disconnect from the current network."""
        if self.wlan.isconnected():
            self.wlan.disconnect()
        self._state = STATE_IDLE
        self._retry_count = 0

    def is_connected(self):
        return self._state == STATE_CONNECTED

    def get_status(self):
        return self._state
        
    def get_config(self):
        return self.wlan.ifconfig()
