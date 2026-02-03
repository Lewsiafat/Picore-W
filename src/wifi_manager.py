"""
Core WiFi management system with state machine.
Handles connection lifecycles, retries, and web-based provisioning.
"""
import network
import uasyncio as asyncio
import time
from config_manager import ConfigManager
from dns_server import DNSServer
from web_server import WebServer
from provisioning import ProvisioningHandler
from constants import (
    STATE_IDLE, STATE_CONNECTING, STATE_CONNECTED, STATE_FAIL, STATE_AP_MODE
)
from config import WiFiConfig
from logger import Logger

# AP activation timeout (in 100ms ticks)
AP_ACTIVATION_TIMEOUT = 50  # 5 seconds

# State name mapping for logging
_STATE_NAMES = {
    STATE_IDLE: 'IDLE',
    STATE_CONNECTING: 'CONNECTING',
    STATE_CONNECTED: 'CONNECTED',
    STATE_FAIL: 'FAIL',
    STATE_AP_MODE: 'AP_MODE'
}


class WiFiManager:
    """
    Core WiFi management system.
    Handles connection lifecycles, retries, and web-based provisioning.
    """

    def __init__(self, dns_server: DNSServer = None, web_server: WebServer = None):
        """
        Initialize the WiFi manager.

        Args:
            dns_server: Optional DNSServer instance (created if None).
            web_server: Optional WebServer instance (created if None).
        """
        self._log = Logger("WiFiManager")

        # Station interface for connecting to existing networks
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)

        # Access Point interface for provisioning mode
        self.ap = network.WLAN(network.AP_IF)
        self.ap.active(False)

        # Network services (dependency injection)
        self.dns_server = dns_server if dns_server else DNSServer(WiFiConfig.AP_IP)
        self.web_server = web_server if web_server else WebServer()

        # Provisioning handler
        self._provisioning = ProvisioningHandler(self.web_server)

        # Internal state
        self._state = STATE_IDLE
        self._target_ssid = None
        self._target_password = None
        self._retry_count = 0

        # Keep reference to background task to prevent GC
        self._state_machine_task = asyncio.create_task(self._run_state_machine())

    def _set_state(self, new_state: int) -> None:
        """
        Set the state machine state with logging.

        Args:
            new_state: The new state constant.
        """
        if self._state != new_state:
            old_name = _STATE_NAMES.get(self._state, '?')
            new_name = _STATE_NAMES.get(new_state, '?')
            self._log.info(f"State: {old_name} -> {new_name}")
            self._state = new_state

    async def _run_state_machine(self) -> None:
        """Main asynchronous loop for WiFi state transitions."""
        self._log.info("State machine started")
        self._load_and_connect()
        while True:
            try:
                if self._state == STATE_IDLE:
                    await self._handle_idle()
                elif self._state == STATE_CONNECTING:
                    await self._handle_connecting()
                elif self._state == STATE_CONNECTED:
                    await self._handle_connected()
                elif self._state == STATE_FAIL:
                    await self._handle_fail()
                elif self._state == STATE_AP_MODE:
                    await self._handle_ap_mode()
            except Exception as e:
                self._log.error(f"State machine error: {e}")
                await asyncio.sleep(5)
            await asyncio.sleep(0.1)

    def _load_and_connect(self) -> None:
        """Attempt to load credentials and start connection sequence."""
        config = ConfigManager.load_config()
        if config and "ssid" in config and "password" in config:
            self._log.info(f"Found config for '{config['ssid']}'")
            self.connect(config["ssid"], config["password"])
        else:
            self._log.info("No config found, entering AP mode")
            self._set_state(STATE_AP_MODE)

    async def _handle_idle(self) -> None:
        """
        Handle IDLE state - waiting for explicit connect() call.
        This state is entered after disconnect() is called.
        """
        await asyncio.sleep(1)

    async def _handle_connecting(self) -> None:
        """Manage connection attempts and retries."""
        self._stop_ap_services()

        self._log.info(f"Connecting to '{self._target_ssid}' (attempt {self._retry_count + 1}/{WiFiConfig.MAX_RETRIES})")
        self.wlan.connect(self._target_ssid, self._target_password)

        start_time = time.time()
        while (time.time() - start_time) < WiFiConfig.CONNECT_TIMEOUT:
            if self.wlan.isconnected():
                ip = self.wlan.ifconfig()[0]
                self._log.info(f"Connected! IP: {ip}")
                self._set_state(STATE_CONNECTED)
                self._retry_count = 0
                return

            status = self.wlan.status()
            # Stop early if explicit failure is detected
            if status == network.STAT_CONNECT_FAIL or status == network.STAT_NO_AP_FOUND or status == network.STAT_WRONG_PASSWORD:
                self._log.debug(f"Connection failed with status {status}")
                break
            await asyncio.sleep(0.5)

        self._retry_count += 1
        if self._retry_count >= WiFiConfig.MAX_RETRIES:
            self._log.warning("Max retries reached")
            self._set_state(STATE_FAIL)
        else:
            self.wlan.disconnect()
            await asyncio.sleep(WiFiConfig.RETRY_DELAY)

    async def _handle_connected(self) -> None:
        """Monitor connection health when connected."""
        if not self.wlan.isconnected():
            self._log.warning("Connection lost, reconnecting...")
            self.wlan.disconnect()
            self._retry_count = 0
            self._set_state(STATE_CONNECTING)
        else:
            await asyncio.sleep(WiFiConfig.HEALTH_CHECK_INTERVAL)

    async def _handle_fail(self) -> None:
        """Handle failure state with recovery delay, then enter AP mode."""
        self._log.info(f"Cooldown {WiFiConfig.FAIL_RECOVERY_DELAY}s before AP mode")
        for _ in range(WiFiConfig.FAIL_RECOVERY_DELAY):
            if self._state != STATE_FAIL:
                return
            await asyncio.sleep(1)
        self._retry_count = 0
        self._set_state(STATE_AP_MODE)

    async def _handle_ap_mode(self) -> None:
        """Manage Access Point and related services."""
        if not self.ap.active():
            self._log.info(f"Starting AP '{WiFiConfig.AP_SSID}'")
            self.ap.config(essid=WiFiConfig.AP_SSID, password=WiFiConfig.AP_PASSWORD)
            self.ap.active(True)

            # Wait for AP activation with timeout
            for _ in range(AP_ACTIVATION_TIMEOUT):
                if self.ap.active():
                    break
                await asyncio.sleep(0.1)
            else:
                self._log.error("AP activation timeout")
                self._set_state(STATE_FAIL)
                return

            current_ip = self.ap.ifconfig()[0]
            self._log.info(f"AP active at {current_ip}")

            self.dns_server.ip_address = current_ip
            self.dns_server.start()
            await self.web_server.start(host='0.0.0.0', port=80)

        await asyncio.sleep(2)

    def _stop_ap_services(self) -> None:
        """Ensure AP and its services are stopped."""
        if self.ap.active():
            self._log.debug("Stopping AP services")
            self.dns_server.stop()
            self.web_server.stop()
            self.ap.active(False)

    def connect(self, ssid: str, password: str) -> None:
        """
        Trigger a connection request.

        Args:
            ssid: WiFi network name.
            password: WiFi password.
        """
        self._target_ssid = ssid
        self._target_password = password
        self._retry_count = 0
        self._set_state(STATE_CONNECTING)

    def disconnect(self) -> None:
        """Disconnect from WiFi and enter IDLE state."""
        if self.wlan.isconnected():
            self.wlan.disconnect()
        self._set_state(STATE_IDLE)
        self._retry_count = 0
        self._stop_ap_services()

    def enter_ap_mode(self) -> None:
        """Manually enter AP provisioning mode."""
        self._stop_ap_services()
        if self.wlan.isconnected():
            self.wlan.disconnect()
        self._set_state(STATE_AP_MODE)

    def is_connected(self) -> bool:
        """Check if currently connected to WiFi."""
        return self._state == STATE_CONNECTED

    def get_status(self) -> int:
        """Get the current state machine state."""
        return self._state

    def get_status_name(self) -> str:
        """Get the current state name as string."""
        return _STATE_NAMES.get(self._state, 'UNKNOWN')

    def get_config(self) -> tuple:
        """Get current IP configuration (ip, subnet, gateway, dns)."""
        return self.wlan.ifconfig()
