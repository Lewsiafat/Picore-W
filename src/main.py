from wifi_manager import WiFiManager
import time

# Configuration (Replace with actual credentials for testing)
SSID = "YOUR_WIFI_SSID"
PASSWORD = "YOUR_WIFI_PASSWORD"

def main():
    print("--- Picore-W System Start ---")
    
    wm = WiFiManager()
    
    # Basic connection test
    print(f"Attempting to connect to {SSID}")
    wm.connect(SSID, PASSWORD)
    
    # Simple polling loop to demonstrate connection wait (blocking style for now)
    max_wait = 10
    while max_wait > 0:
        if wm.is_connected():
            print(f"Connected! IP config: {wm.get_config()}")
            break
        
        max_wait -= 1
        print("Waiting for connection...")
        time.sleep(1)
        
    if not wm.is_connected():
        print("Connection timed out or failed.")
        print(f"Status code: {wm.get_status()}")

    print("--- End of Main ---")

if __name__ == "__main__":
    main()
