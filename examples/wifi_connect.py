import uasyncio as asyncio
from wifi_manager import WiFiManager
from constants import STATE_CONNECTED

async def main():
    print("--- Picore-W Simple Connection Example ---")
    
    # 1. Initialize WiFiManager
    # It automatically loads saved config and starts background state machine
    wm = WiFiManager()
    
    print("Waiting for WiFi connection...")
    
    # 2. Wait until connected
    # In a real app, you can use wm.is_connected() to poll or wait
    while not wm.is_connected():
        await asyncio.sleep(1)
        
    print(f"Connected! IP Address: {wm.get_config()[0]}")
    
    # 3. Your application logic here
    while True:
        print("Application logic running...")
        await asyncio.sleep(10)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopped")
