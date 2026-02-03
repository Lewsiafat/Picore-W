# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Picore-W is a MicroPython infrastructure library for **Raspberry Pi Pico 2 W (RP2350)** and **Raspberry Pi Pico W (RP2040)**. It implements a resilient WiFi State Machine that manages network connection lifecycle with automatic recovery and AP-mode provisioning.

## Development Environment

This is a MicroPython project - no traditional build system exists. Code is deployed directly to hardware.

**Required Tools:**
- VS Code with MicroPico extension (or `mpremote` CLI)
- MicroPython firmware on target Pico device

**Deployment:**
- Upload all files from `src/` to the root of the Pico device
- The `templates/` folder must be included for provisioning UI

## Code Style

Follow the Google Python Style Guide (see `conductor/code_styleguides/python.md`):
- **Linting:** `pylint`
- **Line length:** 80 characters max
- **Indentation:** 4 spaces (never tabs)
- **Naming:** `snake_case` for functions/variables, `PascalCase` for classes, `ALL_CAPS` for constants
- **Type annotations:** Encouraged for public APIs
- **Docstrings:** Triple double quotes, include `Args:`, `Returns:`, `Raises:` sections

## Architecture

### Core State Machine

The WiFi lifecycle is managed through 5 states in `src/wifi_manager.py`:

| State | Value | Description |
|-------|-------|-------------|
| STATE_IDLE | 0 | Initial/waiting state |
| STATE_CONNECTING | 1 | Attempting WiFi connection |
| STATE_CONNECTED | 2 | Connected with IP assigned |
| STATE_FAIL | 3 | Failed, cooling down before retry |
| STATE_AP_MODE | 4 | Provisioning hotspot active |

### Key Files

- `src/wifi_manager.py` - Core state machine and WiFi lifecycle management
- `src/provisioning.py` - Web-based WiFi provisioning handler (routes, templates, form processing)
- `src/config_manager.py` - JSON persistence for WiFi credentials
- `src/web_server.py` - Async HTTP server for provisioning UI
- `src/dns_server.py` - Captive portal DNS server
- `src/logger.py` - Lightweight logging system with configurable levels
- `src/config.py` - Configuration constants (timeouts, retries, AP SSID)
- `src/constants.py` - Shared state definitions

### Design Principles

- **Async-First:** All network operations use `uasyncio`, non-blocking execution
- **Pure MicroPython:** No external dependencies, only built-in modules (`network`, `uasyncio`, `usocket`, `json`, `machine`)
- **Resilience Over Features:** Every network state must be handled gracefully with auto-recovery
- **Hardware-Aware:** Designed for RP2350/RP2040 memory and power constraints

### Logging System

The project uses a lightweight logging system (`src/logger.py`) with configurable levels:

```python
from logger import Logger, LogLevel

log = Logger("MyModule")
log.debug("Verbose details")    # [DEBUG] MyModule: ...
log.info("Normal operation")    # [INFO] MyModule: ...
log.warning("Potential issue")  # [WARN] MyModule: ...
log.error("Failure occurred")   # [ERROR] MyModule: ...

# Change global log level
Logger.set_level(LogLevel.DEBUG)  # Show all messages
Logger.set_level(LogLevel.ERROR)  # Only show errors
```

### Dependency Injection

`WiFiManager` supports dependency injection for testing and customization:

```python
# Default usage
manager = WiFiManager()

# Custom services
custom_dns = DNSServer("192.168.1.1")
custom_web = WebServer()
manager = WiFiManager(dns_server=custom_dns, web_server=custom_web)
```

## Project Guidelines

- **No testing in production code:** Test files are kept separate (per `product-guidelines.md`)
- **Minimalist documentation:** Use clear naming; comments only for complex logic or hardware workarounds
- **All source code in `src/`:** Maintain flat, intuitive directory structure

## Workflow

Tasks are tracked in `conductor/tracks/*/plan.md`. Follow the workflow in `conductor/workflow.md`:
1. Mark tasks `[~]` when in progress, `[x]` when complete
2. Append commit SHA to completed tasks
3. Use git notes to attach task summaries to commits

### Commit Message Format
```
<type>(<scope>): <description>
```
Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### Versioning

Semantic Versioning with manual `CHANGELOG.md` updates. Release tags use annotated format: `git tag -a vX.Y.Z -m "Release vX.Y.Z: [summary]"`

## Project Structure

```
src/                    # Library code (deployed to Pico)
  templates/            # HTML for provisioning UI
examples/               # Integration examples
conductor/              # Project management
  workflow.md           # Development workflow
  product.md            # Product overview
  product-guidelines.md # Development principles
  code_styleguides/     # Style guides
  tracks/               # Active work tracks
  archive/              # Completed tracks
```
