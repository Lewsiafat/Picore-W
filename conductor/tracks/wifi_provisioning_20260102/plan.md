# Plan: WiFi State Machine & Provisioning

## Phase 1: Core Connectivity & State Management [checkpoint: a8529fd]
- [x] Task: Implement basic WiFi connection logic using `network` module (e69f821)
- [x] Task: Create the asynchronous State Machine structure with `uasyncio` (af7f09c)
- [x] Task: Implement auto-reconnection logic and error handling (83c1103)
- [x] Task: Conductor - User Manual Verification 'Phase 1: Core Connectivity' (Protocol in workflow.md)

## Phase 2: Configuration & Persistence [checkpoint: bba649a]
- [x] Task: Implement a simple flash-based storage for WiFi credentials (SSID/Password) (7d29f42)
- [x] Task: Integrate storage with the State Machine (load on boot) (1807721)
- [x] Task: Conductor - User Manual Verification 'Phase 2: Configuration' (Protocol in workflow.md)

## Phase 3: AP Mode & Web Provisioning [checkpoint: 74e66fd]
- [x] Task: Implement AP mode activation when credentials are missing (3c78bba)
- [x] Task: Build a lightweight async Web Server and Captive Portal logic (36a69f0)
- [x] Task: Create the HTML/CSS provisioning page and credential save logic (f7a1990)
- [x] Task: Conductor - User Manual Verification 'Phase 3: AP Mode & Web Provisioning' (Protocol in workflow.md)

## Phase 4: Integration & Polish
- [-] Task: Create a unified API for the main application (`main.py`) to use
- [x] Task: Final code cleanup and documentation within code (daa53e8)
- [x] Task: Conductor - User Manual Verification 'Phase 4: Integration' (Protocol in workflow.md)
