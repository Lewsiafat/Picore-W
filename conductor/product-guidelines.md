# Product Guidelines - Picore-W

## Code Style & Structure
- **Async-First**: Utilize `uasyncio` as the primary mechanism for managing the WiFi State Machine and any background services (like the provisioning web server). Ensure non-blocking execution to allow integration with user applications.
- **Minimalist Documentation**: Follow a "code as documentation" approach. Use clear, descriptive variable and function names. Write comments only for complex logic or specific hardware-related workarounds.
- **Pure & Clean**: Avoid unnecessary external dependencies. Maintain a flat and intuitive directory structure.

## Development Principles
- **Resilience Over Features**: Prioritize the stability of the network state machine. Every possible network state (including edge cases) must be handled gracefully.
- **Maintainable & Extensible**: Write modular code that can be easily understood and integrated into other projects without significant refactoring.
- **Hardware-Aware**: Design specifically for the RP2350 / Pico 2 W, respecting its memory and power constraints while leveraging its capabilities.

## Communication & Feedback
- **Implicit Feedback**: Use status codes or clear state transitions within the code to communicate with the consuming application.
- **Transparent Logic**: The WiFi connection logic should be predictable and easy to trace for debugging.
