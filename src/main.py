import uasyncio as asyncio
from wifi_manager import WiFiManager

# Configuration (Replace with actual credentials for testing)
SSID = "YOUR_WIFI_SSID"
PASSWORD = "YOUR_WIFI_PASSWORD"

async def blink_led():
    """
    Simulates a user application task (e.g., blinking an LED)
    running concurrently with the WiFi connection.
    """
    while True:
        print("Main: User App Running (Blink)...")
        await asyncio.sleep(2)

async def main():
    print("--- Picore-W System Start (Async) ---")
    
    # Initialize WiFiManager (starts its own background task)
    wm = WiFiManager()
    
    # Start a dummy user task
    asyncio.create_task(blink_led())
    
    # Trigger connection
    print(f"Main: Requesting connection to {SSID}")
    wm.connect(SSID, PASSWORD)
    
    # Main loop just to keep the script alive and monitor status
    while True:
        if wm.is_connected():
            # In a real app, you might start network services here
            pass
        await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("System Stopped")