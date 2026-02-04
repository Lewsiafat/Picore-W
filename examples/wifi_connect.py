"""
Picore-W Connection Examples.

Demonstrates basic usage, event-driven patterns, and custom configuration.
"""
import uasyncio as asyncio
from wifi_manager import WiFiManager
from constants import WiFiState
from logger import Logger, LogLevel


# --- Example 1: Basic Usage (Polling) ---
async def basic_example():
    """Simple polling-based connection example."""
    print("--- Picore-W Basic Example ---")

    wm = WiFiManager()

    print("Waiting for WiFi connection...")
    while not wm.is_connected():
        await asyncio.sleep(1)

    print(f"Connected! IP: {wm.get_config()[0]}")


# --- Example 2: Event-Driven Usage ---
async def event_driven_example():
    """Event-driven connection using callbacks."""
    print("--- Picore-W Event-Driven Example ---")

    connected_event = asyncio.Event()

    def on_connected(ip_address):
        print(f"[EVENT] Connected with IP: {ip_address}")
        connected_event.set()

    def on_disconnected():
        print("[EVENT] WiFi disconnected!")
        connected_event.clear()

    def on_state_change(old_state, new_state):
        old_name = WiFiState.get_name(old_state)
        new_name = WiFiState.get_name(new_state)
        print(f"[EVENT] State changed: {old_name} -> {new_name}")

    def on_ap_started(ssid):
        print(f"[EVENT] AP mode started: {ssid}")

    wm = WiFiManager()

    # Register event listeners
    wm.on("connected", on_connected)
    wm.on("disconnected", on_disconnected)
    wm.on("state_change", on_state_change)
    wm.on("ap_mode_started", on_ap_started)

    # Wait for connection via event (no polling needed)
    await connected_event.wait()
    print("Application can now start networking tasks!")


# --- Example 3: Custom Configuration ---
async def custom_config_example():
    """Example with custom configuration parameters."""
    print("--- Picore-W Custom Config Example ---")

    # Option A: Pass parameters directly
    wm = WiFiManager(
        max_retries=10,
        connect_timeout=20,
        ap_ssid="MyDevice-Setup",
        ap_password="MySecurePass123!"
    )

    # Option B: Debug specific modules only
    Logger.set_level(LogLevel.INFO)
    Logger.set_module_level("WiFiManager", LogLevel.DEBUG)

    while not wm.is_connected():
        print(f"Status: {wm.get_status_name()}")
        await asyncio.sleep(2)

    print(f"Connected! IP: {wm.get_config()[0]}")


# --- Example 4: Display AP Config on External Screen ---
async def display_ap_example():
    """
    Example for showing AP credentials on OLED/LCD display.
    Useful for devices with screens to show setup instructions.
    """
    print("--- Picore-W Display AP Example ---")

    wm = WiFiManager(
        ap_ssid="MyDevice",
        ap_password="Setup1234"
    )

    def on_ap_started(ssid):
        # Get AP config for display
        ap_ssid, ap_password, ap_ip = wm.get_ap_config()

        # Example: Print to console (replace with your display code)
        print("=" * 30)
        print("WiFi Setup Mode")
        print(f"SSID: {ap_ssid}")
        print(f"Pass: {ap_password}")
        print(f"URL:  http://{ap_ip}")
        print("=" * 30)

        # For OLED/LCD display:
        # display.fill(0)
        # display.text(f"SSID:{ap_ssid}", 0, 0)
        # display.text(f"Pass:{ap_password}", 0, 16)
        # display.show()

    def on_connected(ip):
        print(f"Connected! IP: {ip}")
        # display.fill(0)
        # display.text(f"IP:{ip}", 0, 0)
        # display.show()

    wm.on("ap_mode_started", on_ap_started)
    wm.on("connected", on_connected)

    # Keep running
    while True:
        await asyncio.sleep(10)


# --- Main Entry Point ---
async def main():
    """Run the basic example by default."""
    await basic_example()

    # Application loop
    while True:
        print("Application running...")
        await asyncio.sleep(10)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopped")
