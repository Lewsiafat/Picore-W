# Picore-W

Picore-W is a robust infrastructure library for **Raspberry Pi Pico 2 W (RP2350)** and **Raspberry Pi Pico W (RP2040)** powered by MicroPython. It provides a resilient network layer designed for high-availability IoT applications.

## Key Features

- **Asynchronous State Machine**: Manages WiFi lifecycle (Connect, Disconnect, Reconnect, Error Handling) using `uasyncio`.
- **Smart Provisioning**: Automatically launches an Access Point (AP) with a web interface when no credentials are found.
- **Event-Driven API**: Register callbacks for connection events (`connected`, `disconnected`, `state_change`).
- **Runtime Configuration**: Customize timeouts, retries, and AP settings without modifying source code.
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

### 3. Event-Driven Example
Use callbacks instead of polling for a cleaner architecture:

```python
import uasyncio as asyncio
from wifi_manager import WiFiManager

async def main():
    connected = asyncio.Event()

    def on_connected(ip):
        print(f"Connected! IP: {ip}")
        connected.set()

    def on_disconnected():
        print("WiFi lost!")
        connected.clear()

    wm = WiFiManager()
    wm.on("connected", on_connected)
    wm.on("disconnected", on_disconnected)

    await connected.wait()  # No polling needed

    # Your application logic here

if __name__ == "__main__":
    asyncio.run(main())
```

### 4. Custom Configuration
Override default settings at runtime:

```python
wm = WiFiManager(
    max_retries=10,           # Connection attempts before fail
    connect_timeout=20,       # Seconds per attempt
    ap_ssid="MyDevice-Setup", # Custom AP name
    ap_password="SecurePass123!"
)
```

---

## Lifecycle Management (State Machine)

Picore-W uses an internal state machine to track network status. You can access the current state using `wm.get_status()` or `wm.get_status_name()`.

| State | Value | Description |
| :--- | :--- | :--- |
| `WiFiState.IDLE` | 0 | Initial state or waiting for command. |
| `WiFiState.CONNECTING` | 1 | Attempting to join a WiFi network. |
| `WiFiState.CONNECTED` | 2 | Successfully connected with assigned IP. |
| `WiFiState.FAIL` | 3 | Connection failed. The system will cool down and retry. |
| `WiFiState.AP_MODE` | 4 | Provisioning mode active (Hotspot mode). |

```python
from constants import WiFiState

# Get state name programmatically
name = WiFiState.get_name(wm.get_status())  # "CONNECTED"
```

### Events

Register callbacks for state transitions:

| Event | Arguments | Description |
| :--- | :--- | :--- |
| `connected` | `(ip_address)` | WiFi connection established. |
| `disconnected` | None | WiFi connection lost. |
| `state_change` | `(old_state, new_state)` | Any state transition. |
| `ap_mode_started` | `(ap_ssid)` | AP provisioning mode activated. |
| `connection_failed` | `(retry_count)` | Entered FAIL state after max retries. |

### Error Handling & Auto-Recovery
- **Connection Lost**: If the network drops while in `CONNECTED`, the manager will automatically transition back to `CONNECTING`.
- **Retries**: The system attempts to connect multiple times (configurable via constructor) before entering a temporary `FAIL` cooldown.
- **AP Fallback**: If no valid credentials exist, the system safely enters `AP_MODE`.

### Display Integration

Retrieve AP credentials for external displays (OLED, LCD, etc.):

```python
def on_ap_started(ssid):
    # Get AP config for display
    ap_ssid, ap_password, ap_ip = wm.get_ap_config()

    # Show on OLED/LCD
    display.text(f"SSID: {ap_ssid}", 0, 0)
    display.text(f"Pass: {ap_password}", 0, 16)
    display.show()

wm.on("ap_mode_started", on_ap_started)

# Check if currently in AP mode
if wm.is_ap_mode():
    ssid, password, ip = wm.get_ap_config()
```

---

## Returning to Provisioning (AP) Mode

If you have already configured the device but wish to enter Provisioning Mode again (e.g., to join a new network), you can run the provided `restore.py` script:

1. Upload `src/restore.py` to your Pico.
2. Run it via REPL or your IDE.

This script deletes the configuration file (`wifi_config.json`) and reboots the device automatically.

```python
# Manual method via REPL:
import os, machine
try:
    os.remove('wifi_config.json')
except:
    pass
machine.reset()
```

---

## Troubleshooting Tips

If you encounter issues during connection or provisioning:

1. **Power Cycle**: If the network stack seems stuck, unplug the USB cable, wait for 5-10 seconds, and plug it back in. A cold boot often resolves hardware-level hangs.
2. **Firmware Integrity**: Ensure you are using the latest stable MicroPython firmware. If behavior is inconsistent, try re-flashing the firmware (erasing flash if necessary).
3. **Template Paths**: Make sure the `templates/` folder is uploaded to the same directory as `wifi_manager.py`.
4. **Signal Strength**: Ensure the Pico is within a reasonable distance of the router and that the power supply is stable (AP mode consumes significant peak current).

---

## Architecture & Files

- **`wifi_manager.py`**: The core business logic, state machine, and event system.
- **`config.py`**: Default settings (Timeouts, Max Retries, AP SSID). Supports runtime overrides.
- **`constants.py`**: `WiFiState` class with state definitions and utility methods.
- **`config_manager.py`**: Handles versioned JSON persistence with automatic migration.
- **`logger.py`**: Lightweight logging with global and per-module level control.
- **`provisioning.py`**: Web-based WiFi provisioning handler.
- **`templates/`**: HTML files for the web interface.

---

## License
This project is licensed under the MIT License.