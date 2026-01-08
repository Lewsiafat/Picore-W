# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
