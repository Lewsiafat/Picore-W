import uasyncio as asyncio
from wifi_manager import WiFiManager, STATE_IDLE, STATE_CONNECTED

# Configuration (Replace with actual credentials for testing)
# In a real scenario, these would come from a Web UI or Mobile App
TEST_SSID = "Lewsi"
TEST_PASSWORD = "ab322060"

async def blink_led():
    """
    Simulates a user application task.
    """
    while True:
        # print("Main: User App Running (Blink)...") # Reduce noise
        await asyncio.sleep(2)

async def main():
    print("--- Picore-W System Start (Async + Config) ---")

    # Initialize WiFiManager (starts background task and loads config)
    wm = WiFiManager()

    # Start user task
    asyncio.create_task(blink_led())

    # Give it a moment to try auto-connect
    print("Main: Waiting for auto-connect...")
    await asyncio.sleep(5)

    if wm.get_status() == STATE_IDLE:
        print("Main: No saved config or auto-connect failed. Starting Provisioning...")

        # Simulate receiving credentials (e.g., from user input or AP mode)
        # For testing purposes, we use the hardcoded values here ONCE.
        if TEST_SSID != "YOUR_WIFI_SSID":
            print(f"Main: Provisioning with test credentials: {TEST_SSID}")
            wm.connect(TEST_SSID, TEST_PASSWORD)
        else:
            print("Main: No test credentials provided in code. Waiting for user action...")

    # Main loop
    while True:
        if wm.is_connected():
            # System is online
            pass
        await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("System Stopped")
