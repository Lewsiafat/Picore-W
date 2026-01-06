# Spec: WiFi State Machine & Provisioning

## Purpose
Provide a robust, asynchronous WiFi management system for Raspberry Pi Pico 2 W that handles connection lifecycles and provides a web-based provisioning interface when no credentials are found.

## Functional Requirements
- **WiFi State Machine**:
    - States: IDLE, CONNECTING, CONNECTED, DISCONNECTED, ERROR, PROVISIONING (AP Mode).
    - Automatic retry with exponential backoff for connection failures.
    - Status reporting via a clean API for main application consumption.
- **Provisioning Mode**:
    - Triggered when no WiFi credentials (SSID/Password) are stored.
    - Start a DNS server (Captive Portal) and a lightweight Web Server.
    - Web page to scan and list available WiFi networks and accept credentials.
    - Persist credentials to internal flash memory.

## Technical Constraints
- Hardware: Raspberry Pi Pico 2 W (RP2350).
- Language: MicroPython.
- Framework: `uasyncio` for non-blocking operation.
- Memory: Efficient usage of limited RAM.
