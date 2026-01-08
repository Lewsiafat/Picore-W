# Picore-W

Picore-W is a robust infrastructure library for Raspberry Pi Pico 2 W (RP2350) powered by MicroPython. It provides a resilient network layer designed for high-availability IoT applications.

## Key Features

- **Asynchronous State Machine**: Manages WiFi lifecycle (Connect, Disconnect, Reconnect, Error Handling) using `uasyncio`.
- **Smart Provisioning**: Automatically launches an Access Point (AP) with a web interface when no credentials are found.
- **Non-Blocking Design**: Engineered to run background network management without stalling your main application logic.
- **Auto-Recovery**: Detects network drops and restores connectivity automatically.

---

## Quick Start (Integration)

To use Picore-W as a base layer for your project, follow these steps:

### 1. Upload Files
Upload all files from the `src/` directory to the **root** of your Pico device. Ensure you include the `templates/` folder.

### 2. Basic Connection Example
Use the following minimal code to integrate WiFi management into your application:

```python
import uasyncio as asyncio
from wifi_manager import WiFiManager

async def main():
    # 1. Initialize WiFiManager
    # Starts background connection logic or provisioning mode automatically
    wm = WiFiManager()
    
    print("Waiting for WiFi...")
    
    # 2. Wait until connected
    while not wm.is_connected():
        await asyncio.sleep(1)
        
    print(f"Connected! IP: {wm.get_config()[0]}")
    
    # 3. Your application logic
    while True:
        await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Lifecycle Management (State Machine)

Picore-W uses an internal state machine to track network status. You can access the current state using `wm.get_status()`.

| State Constant | Value | Description |
| :--- | :--- | :--- |
| `STATE_IDLE` | 0 | Initial state or waiting for command. |
| `STATE_CONNECTING` | 1 | Attempting to join a WiFi network. |
| `STATE_CONNECTED` | 2 | Successfully connected with assigned IP. |
| `STATE_FAIL` | 3 | Connection failed. The system will cool down and retry. |
| `STATE_AP_MODE` | 4 | Provisioning mode active (Hotspot mode). |

### Error Handling & Auto-Recovery
- **Connection Lost**: If the network drops while in `STATE_CONNECTED`, the manager will automatically transition back to `STATE_CONNECTING` and try to restore the link.
- **Retries**: The system attempts to connect multiple times (configured in `config.py`) before entering a temporary `STATE_FAIL` cooldown.
- **AP Fallback**: If no valid credentials exist, the system safely enters `STATE_AP_MODE` to wait for user input.

---

## Architecture & Files

The project is designed with a clear separation of concerns:

- **`wifi_manager.py`**: The core business logic and state machine.
- **`config.py`**: Contains default settings (Timeouts, Max Retries, AP SSID). Modify this for basic customization.
- **`constants.py`**: Shared state definitions.
- **`config_manager.py`**: Handles low-level JSON read/write to the flash filesystem.
- **`templates/`**: HTML files for the provisioning web interface.
- **`dns_server.py` & `web_server.py`**: Lightweight services for the Captive Portal.

---

## Provisioning Mode
If it's the first boot or no configuration is found, the device will:
1. Start a WiFi hotspot named `Picore-W-Setup`.
2. Use the default password: `password123`.
3. Redirect any web request to the setup page (Captive Portal).
4. Save your credentials and reboot automatically.

---

## License
This project is licensed under the MIT License.
