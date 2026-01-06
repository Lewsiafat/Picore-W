import network
import uasyncio as asyncio
import time
import machine
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
    AP_PASSWORD = "password123" # Default secure password
    AP_IP = "192.168.4.1"

# --- State Constants ---
STATE_IDLE = 0
STATE_CONNECTING = 1
STATE_CONNECTED = 2
STATE_FAIL = 3
STATE_AP_MODE = 4

# --- HTML Template ---
PROVISIONING_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Picore-W Setup</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: #f0f2f5; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .container { background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); width: 100%; max-width: 320px; }
        h1 { text-align: center; color: #1a73e8; margin-bottom: 1.5rem; font-size: 1.5rem; }
        form { display: flex; flex-direction: column; gap: 1rem; }
        input { padding: 0.75rem; border: 1px solid #ddd; border-radius: 6px; font-size: 1rem; }
        button { background: #1a73e8; color: white; border: none; padding: 0.75rem; border-radius: 6px; font-size: 1rem; font-weight: bold; cursor: pointer; transition: background 0.2s; }
        button:hover { background: #1557b0; }
        .note { font-size: 0.8rem; color: #666; text-align: center; margin-top: 1rem; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Picore-W Setup</h1>
        <form action="/configure" method="POST">
            <input type="text" name="ssid" placeholder="WiFi Name (SSID)" required>
            <input type="password" name="password" placeholder="WiFi Password" required>
            <button type="submit">Connect</button>
        </form>
        <div class="note">Enter your WiFi credentials to connect the device.</div>
    </div>
</body>
</html>
"""

SUCCESS_HTML = """"
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Connecting...</title>
    <style>
        body { font-family: sans-serif; background: #f0f2f5; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; text-align: center; }
        .container { background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        h1 { color: #34a853; }
    </style>
    <script>
        setTimeout(function() { window.close(); }, 5000);
    </script>
</head>
<body>
    <div class="container">
        <h1>Settings Saved!</h1>
        <p>The device is attempting to connect to the WiFi network.</p>
        <p>Please check the device status LED or reconnect your phone to your normal WiFi.</p>
    </div>
</body>
</html>
"""

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
        self.web_server.add_route("/", self._handle_root_request)
        self.web_server.add_route("/hotspot-detect.html", self._handle_root_request) # Apple
        self.web_server.add_route("/generate_204", self._handle_root_request) # Android
        self.web_server.add_route("/configure", self._handle_configure, method="POST")

    async def _handle_root_request(self, request):
        return ("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n" + PROVISIONING_HTML).encode()

    async def _handle_configure(self, request):
        """Handle form submission."""
        params = request.get("params", {})
        ssid = params.get("ssid")
        password = params.get("password")
        
        if ssid:
            print(f"WiFiManager: Received configuration for SSID: {ssid}")
            
            # 1. Save Config IMMEDIATELY
            success = ConfigManager.save_config(ssid, password)
            if success:
                print("WiFiManager: Configuration saved successfully.")
                # 2. Schedule Reboot
                asyncio.create_task(self._reboot_device())
                return ("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n" + SUCCESS_HTML).encode()
            else:
                print("WiFiManager: Failed to save configuration.")
                return b"HTTP/1.1 500 Internal Server Error\r\n\r\nFailed to save config"
        else:
            return b"HTTP/1.1 400 Bad Request\r\n\r\nMissing SSID"

    async def _reboot_device(self):
        """Wait for response to send, then reboot."""
        print("WiFiManager: Rebooting in 3 seconds...")
        await asyncio.sleep(3)
        print("WiFiManager: Rebooting NOW.")
        machine.reset()

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
        self._stop_ap_services() 
        
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
            
            # Simple AP Setup
            self.ap.config(essid=WiFiConfig.AP_SSID, password=WiFiConfig.AP_PASSWORD)
            self.ap.active(True)
            
            # Wait until active
            while not self.ap.active():
                await asyncio.sleep(0.1)
            
            current_ip = self.ap.ifconfig()[0]
            print(f"WiFiManager: AP Started. IP: {current_ip}")
            
            # Start Services
            self.dns_server.ip_address = current_ip
            self.dns_server.start()
            await self.web_server.start(host='0.0.0.0', port=80)
        
        await asyncio.sleep(2)

    def _stop_ap_services(self):
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