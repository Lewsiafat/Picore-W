# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2026-02-04

### Added
- **Event System:** `WiFiManager.on()` and `WiFiManager.off()` methods for event-driven programming.
  - Events: `connected`, `disconnected`, `state_change`, `ap_mode_started`, `connection_failed`.
- **Runtime Configuration:** `WiFiManager` constructor now accepts configuration parameters:
  - `max_retries`, `connect_timeout`, `retry_delay`, `fail_recovery_delay`, `health_check_interval`
  - `ap_ssid`, `ap_password`, `ap_ip`
- **Module-Level Logging:** `Logger.set_module_level()` for per-module log level control.
- **Config Versioning:** `ConfigManager` now tracks config file version for migration support.
- `WiFiState` class in `constants.py` with `get_name()`, `is_valid()`, and `all_states()` methods.
- `ConfigManager.get_wifi_credentials()` convenience method.
- `ConfigManager.get_version()` to check config file version.

### Changed
- `WiFiConfig` class now supports instance creation with parameter overrides.
- Config file format upgraded to version 2 with structured `wifi` section.
- Legacy v1 configs are automatically migrated to v2 format on load.
- Updated `examples/wifi_connect.py` with event-driven and custom config examples.

### Deprecated
- Direct use of `STATE_*` constants from `constants.py` (use `WiFiState.*` instead).

## [1.2.0] - 2026-02-03

### Added
- `src/logger.py` - Lightweight logging system with configurable levels (DEBUG, INFO, WARNING, ERROR).
- `src/provisioning.py` - Extracted provisioning handler for WiFi configuration via web interface.
- Type hints for all public APIs across modules.
- State transition logging in WiFiManager (`_set_state()` method).
- `get_status_name()` method for human-readable state names.
- `enter_ap_mode()` method for manual provisioning mode entry.

### Changed
- **Architecture Refactor:** Extracted route handling, template reading, and form processing from `WiFiManager` to `ProvisioningHandler`.
- **Dependency Injection:** `WiFiManager` now accepts optional `dns_server` and `web_server` parameters.
- **Background Task Reference:** State machine task is now stored to prevent garbage collection.
- **FAIL State Behavior:** After cooldown, enters AP_MODE instead of CONNECTING (allows user reconfiguration).
- Unified logging format: `[LEVEL] Module: message` across all modules.
- Replaced star import with explicit imports in `wifi_manager.py`.
- Simplified redundant `os.stat()` check in `config_manager.py`.

### Security
- Fixed bare `except:` clauses in `restore.py` and `web_server.py`.
- Added AP activation timeout (5 seconds) to prevent infinite wait.
- Added SSID validation (1-32 characters) and password validation (8-63 characters or empty).
- Added `Content-Length` limit (1KB) to prevent memory exhaustion attacks.
- Added DNS packet minimum length validation (12 bytes).
- Added IP address format validation in `DNSServer`.
- Added template name validation to prevent path traversal.
- Changed default AP password to stronger value (`PicoreSetup2024!`).

### Fixed
- Added UTF-8 decode error handling in `WebServer` for malformed requests.

## [1.1.0] - 2026-01-07

### Added
- Added `examples/wifi_connect.py` providing a minimal integration example for library usage.
- Added English version of `README.md` as the default documentation.
- Created `src/constants.py` and `src/config.py` to decouple configuration and state definitions from core logic.
- Created `src/templates/` directory to host external HTML templates for the provisioning web interface.

### Changed
- Renamed original Chinese `README.md` to `README.zh-TW.md`.
- Refactored `WiFiManager` to use file-based template reading, reducing常駐 memory usage.
- Improved path resilience in `WiFiManager` to support both flat and nested directory deployments on Pico.

### Fixed
- Fixed an issue where WiFi configuration saving could be unreliable during rapid state transitions (implemented Save-then-Reboot flow).
- Standardized HTML string syntax in `wifi_manager.py`.

## [1.0.0] - 2026-01-05

### Added
- Initial release of the core WiFi management system.
- Robust Asynchronous WiFi State Machine using `uasyncio`.
- Automated AP Mode Provisioning with a Captive Portal interface.
- Persistent JSON-based configuration storage on the flash filesystem.
- Automatic reconnection logic with error handling and retry limits.
