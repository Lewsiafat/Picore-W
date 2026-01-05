import network
import uasyncio as asyncio
import time
from config_manager import ConfigManager

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
    
    # AP Mode Settings
    AP_SSID = "Picore-W-Setup"
    AP_PASSWORD = "" # Open network for ease of setup
    AP_IP = "192.168.4.1"

# --- State Constants ---
STATE_IDLE = 0
STATE_CONNECTING = 1
STATE_CONNECTED = 2
STATE_FAIL = 3
STATE_AP_MODE = 4

class WiFiManager:
    """
    Manages the WiFi connection using the ESP32/Pico W 'network' module.
    Implements an asynchronous State Machine to handle connection in the background.
    """
    def __init__(self):
        # Station Interface
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        
        # AP Interface
        self.ap = network.WLAN(network.AP_IF)
        self.ap.active(False) # Default to off
        
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
        
        # Attempt to load config on startup
        self._load_and_connect()
        
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
                    
                elif self._state == STATE_AP_MODE:
                    await self._handle_ap_mode()
                    
            except Exception as e:
                print(f"WiFiManager: Critical Error in State Machine: {e}")
                await asyncio.sleep(5)
            
            # Yield to other tasks
            await asyncio.sleep(0.1)

    def _load_and_connect(self):
        """
        Internal helper to load config and trigger connection if available.
        If no config, switch to AP Mode.
        """
        print("WiFiManager: Checking for saved credentials...")
        config = ConfigManager.load_config()
        if config and "ssid" in config and "password" in config:
            print(f"WiFiManager: Found saved config for '{config['ssid']}'. Connecting...")
            self.connect(config["ssid"], config["password"])
        else:
            print("WiFiManager: No saved config found. Switching to AP Mode.")
            self._state = STATE_AP_MODE

    async def _handle_connecting(self):
        # Ensure AP is off when trying to connect as Station
        if self.ap.active():
            print("WiFiManager: Disabling AP Mode for Station connection...")
            self.ap.active(False)

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
        For now, we still try auto-recovery. 
        (Future: Could switch to AP Mode here too if desired)
        """
        print(f"WiFiManager: In FAIL state. Waiting {WiFiConfig.FAIL_RECOVERY_DELAY}s before auto-recovery...")
        
        # Wait for recovery delay
        for _ in range(WiFiConfig.FAIL_RECOVERY_DELAY):
            if self._state != STATE_FAIL:
                return 
            await asyncio.sleep(1)
            
        print("WiFiManager: Attempting Auto-Recovery...")
        self._retry_count = 0
        self._state = STATE_CONNECTING

    async def _handle_ap_mode(self):
        """
        Handle AP Mode.
        Keeps AP active and waits for user configuration (via Web Server).
        """
        if not self.ap.active():
            print(f"WiFiManager: Enabling AP Mode (SSID: {WiFiConfig.AP_SSID})...")
            try:
                # Configure AP
                # Note: 'security=0' means open network.
                self.ap.config(essid=WiFiConfig.AP_SSID, password=WiFiConfig.AP_PASSWORD)
                self.ap.ifconfig((WiFiConfig.AP_IP, '255.255.255.0', WiFiConfig.AP_IP, '8.8.8.8'))
                
                self.ap.active(True)
                print(f"WiFiManager: AP Mode Started. IP: {self.ap.ifconfig()[0]}")
            except Exception as e:
                print(f"WiFiManager: Error starting AP Mode: {e}")
        
        # AP Mode loop - just wait for credentials to be provided via connect()
        # The web server (to be implemented) will call connect() when user submits form.
        await asyncio.sleep(2)

    def connect(self, ssid, password):
        """
        Public API to request a connection.
        """
        self._target_ssid = ssid
        self._target_password = password
        self._retry_count = 0
        self._state = STATE_CONNECTING
        
        ConfigManager.save_config(ssid, password)

    def disconnect(self):
        if self.wlan.isconnected():
            self.wlan.disconnect()
        self._state = STATE_IDLE
        self._retry_count = 0
        self.ap.active(False)

    def is_connected(self):
        return self._state == STATE_CONNECTED

    def get_status(self):
        return self._state
        
    def get_config(self):
        return self.wlan.ifconfig()
