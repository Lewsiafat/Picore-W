import network
import uasyncio as asyncio
import time
from config_manager import ConfigManager
from dns_server import DNSServer
from web_server import WebServer

# --- Configuration Constants ---
class WiFiConfig:
    MAX_RETRIES = 5
    CONNECT_TIMEOUT = 15
    RETRY_DELAY = 2
    FAIL_RECOVERY_DELAY = 30
    HEALTH_CHECK_INTERVAL = 2
    
    # AP Mode Settings
    AP_SSID = "Picore-W-Setup"
    AP_PASSWORD = ""
    AP_IP = "192.168.4.1"

# --- State Constants ---
STATE_IDLE = 0
STATE_CONNECTING = 1
STATE_CONNECTED = 2
STATE_FAIL = 3
STATE_AP_MODE = 4

class WiFiManager:
    def __init__(self):
        # Station Interface
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        
        # AP Interface
        self.ap = network.WLAN(network.AP_IF)
        self.ap.active(False)
        
        # Network Services
        self.dns_server = DNSServer(WiFiConfig.AP_IP)
        self.web_server = WebServer()
        self._setup_routes()

        # State Machine variables
        self._state = STATE_IDLE
        self._target_ssid = None
        self._target_password = None
        self._retry_count = 0
        
        # Start the background task
        asyncio.create_task(self._run_state_machine())

    def _setup_routes(self):
        """Register Web Server routes."""
        # Simple test route
        self.web_server.add_route("/", self._handle_root_request)
        self.web_server.add_route("/hotspot-detect.html", self._handle_root_request) # Apple
        self.web_server.add_route("/generate_204", self._handle_root_request) # Android (simplified)

    async def _handle_root_request(self, request):
        return b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<h1>Picore-W Setup</h1><p>Provisioning page coming soon...</p>"

    async def _run_state_machine(self):
        print("WiFiManager: State Machine Started")
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
            await asyncio.sleep(0.1)

    def _load_and_connect(self):
        print("WiFiManager: Checking for saved credentials...")
        config = ConfigManager.load_config()
        if config and "ssid" in config and "password" in config:
            print(f"WiFiManager: Found saved config for '{config['ssid']}'. Connecting...")
            self.connect(config["ssid"], config["password"])
        else:
            print("WiFiManager: No saved config found. Switching to AP Mode.")
            self._state = STATE_AP_MODE

    async def _handle_connecting(self):
        self._stop_ap_services() # Ensure AP/Services are off
        
        print(f"WiFiManager: Connecting to {self._target_ssid} (Attempt {self._retry_count + 1}/{WiFiConfig.MAX_RETRIES})...")
        self.wlan.connect(self._target_ssid, self._target_password)
        
        start_time = time.time()
        while (time.time() - start_time) < WiFiConfig.CONNECT_TIMEOUT:
            if self.wlan.isconnected():
                print("WiFiManager: Connection Successful!")
                self._state = STATE_CONNECTED
                self._retry_count = 0
                return
            
            status = self.wlan.status()
            if status == network.STAT_CONNECT_FAIL or status == network.STAT_NO_AP_FOUND or status == network.STAT_WRONG_PASSWORD:
                print(f"WiFiManager: Connection Failed explicitly (Status: {status})")
                break
            await asyncio.sleep(0.5)
            
        self._retry_count += 1
        if self._retry_count >= WiFiConfig.MAX_RETRIES:
            print("WiFiManager: Max retries reached. Entering FAIL state.")
            self._state = STATE_FAIL
        else:
            print(f"WiFiManager: Retrying in {WiFiConfig.RETRY_DELAY}s...")
            self.wlan.disconnect()
            await asyncio.sleep(WiFiConfig.RETRY_DELAY)

    async def _handle_connected(self):
        if not self.wlan.isconnected():
            print("WiFiManager: Connection Lost! Attempting to reconnect...")
            self.wlan.disconnect()
            self._retry_count = 0
            self._state = STATE_CONNECTING
        else:
            await asyncio.sleep(WiFiConfig.HEALTH_CHECK_INTERVAL)

    async def _handle_fail(self):
        print(f"WiFiManager: In FAIL state. Waiting {WiFiConfig.FAIL_RECOVERY_DELAY}s before auto-recovery...")
        for _ in range(WiFiConfig.FAIL_RECOVERY_DELAY):
            if self._state != STATE_FAIL: return 
            await asyncio.sleep(1)
        print("WiFiManager: Attempting Auto-Recovery...")
        self._retry_count = 0
        self._state = STATE_CONNECTING

    async def _handle_ap_mode(self):
        if not self.ap.active():
            print(f"WiFiManager: Enabling AP Mode (SSID: {WiFiConfig.AP_SSID})...")
            try:
                self.ap.config(essid=WiFiConfig.AP_SSID, password=WiFiConfig.AP_PASSWORD)
                self.ap.ifconfig((WiFiConfig.AP_IP, '255.255.255.0', WiFiConfig.AP_IP, '8.8.8.8'))
                self.ap.active(True)
                print(f"WiFiManager: AP Mode Started. IP: {self.ap.ifconfig()[0]}")
                
                # Start Services
                self.dns_server.start()
                await self.web_server.start(host='0.0.0.0', port=80)
                
            except Exception as e:
                print(f"WiFiManager: Error starting AP Mode: {e}")
        
        await asyncio.sleep(2)

    def _stop_ap_services(self):
        """Helper to stop AP, DNS, and Web Server."""
        if self.ap.active():
            print("WiFiManager: Stopping AP Mode and Services...")
            self.dns_server.stop()
            self.web_server.stop()
            self.ap.active(False)

    def connect(self, ssid, password):
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
        self._stop_ap_services()

    def is_connected(self):
        return self._state == STATE_CONNECTED

    def get_status(self):
        return self._state
        
    def get_config(self):
        return self.wlan.ifconfig()