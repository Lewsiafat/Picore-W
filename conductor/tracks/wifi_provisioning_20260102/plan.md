# Plan: WiFi State Machine & Provisioning

## Phase 1: Core Connectivity & State Management
- [x] Task: Implement basic WiFi connection logic using `network` module (e69f821)
- [x] Task: Create the asynchronous State Machine structure with `uasyncio` (af7f09c)
- [ ] Task: Implement auto-reconnection logic and error handling
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Core Connectivity' (Protocol in workflow.md)

## Phase 2: Configuration & Persistence
- [ ] Task: Implement a simple flash-based storage for WiFi credentials (SSID/Password)
- [ ] Task: Integrate storage with the State Machine (load on boot)
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Configuration' (Protocol in workflow.md)

## Phase 3: AP Mode & Web Provisioning
- [ ] Task: Implement AP mode activation when credentials are missing
- [ ] Task: Build a lightweight async Web Server and Captive Portal logic
- [ ] Task: Create the HTML/CSS provisioning page and credential save logic
- [ ] Task: Conductor - User Manual Verification 'Phase 3: AP Mode & Web Provisioning' (Protocol in workflow.md)

## Phase 4: Integration & Polish
- [ ] Task: Create a unified API for the main application (`main.py`) to use
- [ ] Task: Final code cleanup and documentation within code
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Integration' (Protocol in workflow.md)
