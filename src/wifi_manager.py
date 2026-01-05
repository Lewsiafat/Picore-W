import network
import time

class WiFiManager:
    """
    Manages the WiFi connection using the ESP32/Pico W 'network' module.
    Currently handles Station (STA) mode basic operations.
    """
    def __init__(self):
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)

    def connect(self, ssid, password):
        """
        Trigger a connection attempt. 
        This is non-blocking in terms of the handshake, but triggers the driver.
        """
        if not self.wlan.isconnected():
            print(f"WiFiManager: Connecting to {ssid}...")
            self.wlan.connect(ssid, password)
        else:
            print("WiFiManager: Already connected.")

    def disconnect(self):
        """Disconnect from the current network."""
        if self.wlan.isconnected():
            self.wlan.disconnect()

    def is_connected(self):
        """Check if IP is assigned and link is up."""
        return self.wlan.isconnected()

    def get_status(self):
        """Return the interface status code."""
        return self.wlan.status()
        
    def get_config(self):
        """Return the IP configuration (ip, netmask, gw, dns)."""
        return self.wlan.ifconfig()
