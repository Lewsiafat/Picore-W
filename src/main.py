import uasyncio as asyncio
from wifi_manager import WiFiManager, STATE_IDLE, STATE_CONNECTING, STATE_CONNECTED, STATE_FAIL, STATE_AP_MODE

async def blink_led():
    """
    Simulates a user application task.
    """
    while True:
        await asyncio.sleep(2)

async def monitor_status(wm):
    """
    Periodically prints the system status.
    """
    last_state = -1
    while True:
        current_state = wm.get_status()
        if current_state != last_state:
            state_name = "UNKNOWN"
            if current_state == STATE_IDLE: state_name = "IDLE"
            elif current_state == STATE_CONNECTING: state_name = "CONNECTING"
            elif current_state == STATE_CONNECTED: state_name = "CONNECTED (Station)"
            elif current_state == STATE_FAIL: state_name = "FAIL"
            elif current_state == STATE_AP_MODE: state_name = "AP MODE (Provisioning)"
            
            print(f"Main: System State Changed to -> {state_name}")
            last_state = current_state
            
            if current_state == STATE_AP_MODE:
                print("Main: Please connect to WiFi 'Picore-W-Setup' to configure device.")
            
        await asyncio.sleep(1)

async def main():
    print("--- Picore-W System Start (Phase 3: AP Mode) ---")
    
    # Initialize WiFiManager
    wm = WiFiManager()
    
    # Start tasks
    asyncio.create_task(blink_led())
    asyncio.create_task(monitor_status(wm))
    
    # Main loop
    while True:
        await asyncio.sleep(10)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("System Stopped")